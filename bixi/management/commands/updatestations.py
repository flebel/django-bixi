import importlib
import json
import urllib2
from datetime import datetime
from xml.etree import cElementTree

from django.core.management.base import BaseCommand, CommandError

from bixi.models import City, Station, Update
from bixi.utils import forgiving_urlopen


def timestamp_to_datetime(timestamp, ms=False):
    try:
        ts = int(timestamp)
    except TypeError, ValueError:
        ts = 0
    if ts:
        if ms:
            ts_seconds = ts / 1e3
        else:
            ts_seconds = ts
        return datetime.utcfromtimestamp(ts_seconds)
    return None


class StationListParser(object):
    def get_installation_date(self, station):
        return timestamp_to_datetime(self.find(station, 'installDate'), ms=True)

    def get_last_recorded_communication(self, station):
        raise NotImplementedError

    def get_latest_update_time(self, station):
        raise NotImplementedError

    def get_latitude(self, station):
        return float(self.find(station, 'lat'))

    def get_longitude(self, station):
        return float(self.find(station, 'long'))

    def get_number_available_bikes(self, station):
        return int(self.find(station, 'nbBikes'))

    def get_number_empty_docks(self, station):
        return int(self.find(station, 'nbEmptyDocks'))

    def get_public_id(self, station):
        return int(self.find(station, 'id'))

    def get_removal_date(self, station):
        return timestamp_to_datetime(self.find(station, 'removalDate'), ms=True)

    def get_station_name(self, station):
        return self.find(station, 'name')

    def get_vicinity(self, station):
        return self.find(station, 'terminalName')

    def is_locked(self, station):
        return self.find(station, 'locked') == 'true'

    def is_installed(self, station):
        return self.find(station, 'installed') == 'true'

    def is_public(self, station):
        raise NotImplementedError

    def is_temporary(self, station):
        return self.find(station, 'temporary') == 'true'


class JsonParser(object):
    def __init__(self, data, *args, **kwargs):
        unicode_data = data.read().decode('unicode-escape')
        self.json = json.loads(unicode_data)

    def find(self, element, field_name):
        value = element.get(field_name)
        if value:
            return value.strip()

    def get_last_recorded_update_time(self):
        execution_time = self.json.get('executionTime')
        dt_format = '%Y-%m-%d %I:%M:%S %p'
        return datetime.strptime(execution_time, dt_format)

    def get_raw_station(self, station):
        return unicode(station)

    def get_stations(self):
        return self.json.get('stationBeanList')


class XmlParser(object):
    def __init__(self, data, *args, **kwargs):
        tree = cElementTree.parse(data)
        self.root = tree.getroot()

    def get_raw_station(self, station):
        return cElementTree.tostring(station, method='xml')

    def find(self, element, field_name):
        value = element.find(field_name).text
        if value:
            return value.strip()

    def get_last_recorded_update_time(self):
        return timestamp_to_datetime(self.root.attrib['lastUpdate'], ms=True)

    def get_stations(self):
        return self.root.findall('station')


class StationListParserTypeA(XmlParser, StationListParser):
    def get_last_recorded_communication(self, station):
        return timestamp_to_datetime(self.find(station, 'lastCommWithServer'), ms=True)

    def get_latest_update_time(self, station):
        return timestamp_to_datetime(self.find(station, 'latestUpdateTime'), ms=True)

    def is_public(self, station):
        return self.find(station, 'public') == 'true'


class StationListParserTypeB(XmlParser, StationListParser):
    def get_last_recorded_communication(self, station):
        return None

    def get_latest_update_time(self, station):
        return None

    def is_public(self, station):
        return None


class StationListParserTypeC(JsonParser, StationListParser):
    STATUSES = (('In Service', 1,),)

    def get_installation_date(self, station):
        return None

    def get_last_recorded_communication(self, station):
        return timestamp_to_datetime(self.find(station, 'lastCommunicationTime'), ms=True)

    def get_latest_update_time(self, station):
        return None

    def get_latitude(self, station):
        return self.find(station, 'latitude')

    def get_longitude(self, station):
        return self.find(station, 'longitude')

    def get_number_available_bikes(self, station):
        return self.find(station, 'availableBikes')

    def get_number_empty_docks(self, station):
        return self.find(station, 'availableDocks')

    def get_removal_date(self, station):
        return None

    def get_station_name(self, station):
        return self.find(station, 'stationName')

    def get_vicinity(self, station):
        return self.find(station, 'location')

    def is_locked(self, station):
        return None

    def is_installed(self, station):
        return int(self.find(station, 'statusKey')) == 1

    def is_public(self, station):
        return None

    def is_temporary(self, station):
        return self.find(station, 'testStation')


class StationListParserTypeD(XmlParser, StationListParser):
    def __init__(self, data, station_details_url, *args, **kwargs):
        super(StationListParserTypeD, self).__init__(data, *args, **kwargs)
        self._station_details_cache = {}
        self.station_details_url = station_details_url

    def _get_station_details(self, station):
        public_id = self.get_public_id(station)
        if not public_id in self._station_details_cache:
            url = self.station_details_url % (public_id,)
            data = forgiving_urlopen(url)
            root = cElementTree.parse(data).getroot()
            self._station_details_cache[public_id] = {el.tag: el.text for el in root}
        return self._station_details_cache[public_id]

    def find(self, element, field_name):
        return element.attrib.get(field_name).strip()

    def find_station(self, station, field_name):
        station_details = self._get_station_details(station)
        if station_details:
            return station_details[field_name]

    def get_installation_date(self, station):
        return None

    def get_last_recorded_communication(self, station):
        return None

    def get_latest_update_time(self, station):
        return timestamp_to_datetime(self.find_station(station, 'updated'), ms=False)

    def get_latitude(self, station):
        return self.find(station, 'lat')

    def get_last_recorded_update_time(self):
        stations = self.get_stations()
        latest_updated = None
        for station in self._station_details_cache.values():
            latest_updated = max(station['updated'], latest_updated)
        if latest_updated:
            return timestamp_to_datetime(latest_updated, ms=False)

    def get_longitude(self, station):
        return self.find(station, 'lng')

    def get_number_available_bikes(self, station):
        return self.find_station(station, 'available')

    def get_number_empty_docks(self, station):
        return self.find_station(station, 'free')

    def get_public_id(self, station):
        return int(self.find(station, 'number'))

    def get_raw_station(self, station):
        details = cElementTree.tostring(station, method='xml')
        station_details = self._get_station_details(station)
        if station_details:
            # `details` is XML and ended with a line feed
            # `station_details` is JSON
            return details + unicode(station_details)
        return details

    def get_removal_date(self, station):
        return None

    def get_stations(self):
        return self.root.find('markers').findall('marker')

    def get_station_name(self, station):
        return self.find(station, 'name')

    def get_vicinity(self, station):
        return self.find(station, 'address')

    def is_locked(self, station):
        return None

    def is_installed(self, station):
        station_open = self.find_station(station, 'open')
        if not station_open is None:
            return int(station_open) == 1

    def is_public(self, station):
        return None

    def is_temporary(self, station):
        return None


class Command(BaseCommand):
    args = '<city_code city_code ...>'
    help = 'Updates the current bike and dock counts for a given list of cities.'

    def __init__(self):
        self._reset_counts()
        return super(Command, self).__init__()

    def _progress(self, str):
        self.stdout.write(str, ending='')

    def _increase_created_count(self):
        self.created = self.created + 1
        self._progress('c')

    def _increase_status_quo_count(self):
        self.status_quo = self.status_quo + 1
        self._progress('.')

    def _increase_updated_count(self):
        self.updated = self.updated + 1
        self._progress('u')

    def _reset_counts(self):
        self.created = 0
        self.status_quo = 0
        self.updated = 0

    def handle(self, *args, **options):
        city_codes = args or map(lambda x: x[0], City.available.all().values_list('code'))
        parsers_module = importlib.import_module(self.__class__.__module__)

        for city_code in city_codes:
            try:
                city = City.objects.get(code=city_code)
            except City.DoesNotExist:
                raise CommandError("City '%s' does not exist." % city_code)

            data = urllib2.urlopen(city.url)

            parsers = {City.parser_code_to_value(value): getattr(parsers_module, 'StationListParserType' + value) for value in City.PARSER_TYPES_VALUES}
            try:
                parser = parsers[city.parser_type](data, city.station_url)
            except IndexError:
                raise NotImplementedError("The parser for '%s' hasn't been implemented yet." % (city.name,))

            self._reset_counts()

            for s in parser.get_stations():
                attrs = dict()
                public_id = parser.get_public_id(s)
                last_recorded_communication = parser.get_last_recorded_communication(s)
                try:
                    station = Station.objects.get(city=city, public_id=public_id)
                    # Skip if we have a timestamp to compare against
                    if last_recorded_communication and station.last_recorded_communication == last_recorded_communication:
                        self._increase_status_quo_count()
                        continue
                    # Else, update the station
                except Station.DoesNotExist:
                    station = Station()
                    attrs.update({
                        'city_id': city.pk,
                        'name': parser.get_station_name(s),
                        'public_id': public_id,
                        'vicinity': parser.get_vicinity(s),
                    })

                attrs.update({
                    'installation_date': parser.get_installation_date(s),
                    'installed': parser.is_installed(s),
                    'last_recorded_communication': parser.get_last_recorded_communication(s),
                    'latitude': parser.get_latitude(s),
                    'locked': parser.is_locked(s),
                    'longitude': parser.get_longitude(s),
                    'public': parser.is_public(s),
                    'removal_date': parser.get_removal_date(s),
                    'temporary': parser.is_temporary(s),
                })

                bikes = parser.get_number_available_bikes(s)
                empty_docks = parser.get_number_empty_docks(s)

                # Try to find if there has been changes since the last time
                # this station was updated
                latest_update_time = parser.get_latest_update_time(s)
                if latest_update_time:
                    if not station.last_recorded_communication:
                        skip_station = True
                        for (attr, value,) in attrs.items():
                            if not getattr(station, attr) == value:
                                # Skip the station altogether
                                skip_station = False
                                continue
                        if skip_station:
                            self._increase_status_quo_count()
                            continue
                    if Update.objects.filter(station=station,
                            latest_update_time=latest_update_time).exists():
                        self._increase_status_quo_count()
                        continue
                else:
                    # Too little information is available for this station,
                    # compare against the most recent update
                    mru_qs = Update.objects.filter(station=station)
                    if mru_qs.exists():
                        mru = mru_qs.latest()
                        if (mru.bikes, mru.empty_docks,) == (bikes, empty_docks,):
                            self._increase_status_quo_count()
                            continue

                for (k, v) in attrs.items():
                    assert k in station.__dict__, "The attribute '%s' must be an existing model field." % (k,)
                    setattr(station, k, v)
                station.save()

                if latest_update_time and Update.objects.filter(station=station,
                    latest_update_time=latest_update_time).exists():
                    continue

                if station.pk:
                    self._increase_updated_count()
                else:
                    self._increase_created_count()

                Update.objects.create(station=station, bikes=bikes,
                    empty_docks=empty_docks,
                    latest_update_time=latest_update_time,
                    raw_data=parser.get_raw_station(s))

            last_recorded_update = parser.get_last_recorded_update_time()
            city.last_recorded_update = last_recorded_update
            city.save()

            self.stdout.write("\nSuccessfully updated bike and dock counts for " +
                "'%s'." % city.name)
            self.stdout.write('Created: %s' % self.created)
            self.stdout.write('Updated: %s' % self.updated)
            self.stdout.write('Status quo: %s' % self.status_quo)

