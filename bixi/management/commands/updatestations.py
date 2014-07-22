import importlib
import json
import urllib2
from datetime import datetime
from xml.etree import ElementTree

from django.core.management.base import BaseCommand, CommandError

from bixi.models import City, Station, Update


def timestampToDateTime(timestamp):
    try:
        ts = int(timestamp)
    except TypeError, ValueError:
        ts = 0
    if ts:
        return datetime.fromtimestamp(ts / 1e3)
    return None


class StationListParser:
    def get_install_date(self, station):
        return timestampToDateTime(self.find(station, 'installDate'))

    def get_last_communication_time_with_server(self, station):
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
        return timestampToDateTime(self.find(station, 'removalDate'))

    def get_station_name(self, station):
        return self.find(station, 'name')

    def get_terminal_name(self, station):
        return self.find(station, 'terminalName')

    def is_locked(self, station):
        return self.find(station, 'locked') == 'true'

    def is_installed(self, station):
        return self.find(station, 'installed') == 'true'

    def is_public(self, station):
        raise NotImplementedError

    def is_temporary(self, station):
        return self.find(station, 'temporary') == 'true'


class JsonParser:
    def __init__(self, data, *args, **kwargs):
        unicode_data = data.read().decode('unicode-escape')
        self.json = json.loads(unicode_data)

    def find(self, element, field_name):
        return element.get(field_name)

    def get_last_update_time(self):
        execution_time = self.json.get('executionTime')
        dt_format = '%Y-%m-%d %I:%M:%S %p'
        return datetime.strptime(execution_time, dt_format)

    def get_stations(self):
        return self.json.get('stationBeanList')


class XmlParser:
    def __init__(self, data, *args, **kwargs):
        tree = ElementTree.parse(data)
        self.root = tree.getroot()

    def find(self, element, field_name):
        return element.find(field_name).text

    def get_last_update_time(self):
        return timestampToDateTime(self.root.attrib['lastUpdate'])

    def get_stations(self):
        return self.root.findall('station')


class StationListParserTypeA(XmlParser, StationListParser):
    def get_last_communication_time_with_server(self, station):
        return timestampToDateTime(self.find(station, 'lastCommWithServer'))

    def get_latest_update_time(self, station):
        return timestampToDateTime(self.find(station, 'latestUpdateTime'))

    def is_public(self, station):
        return self.find(station, 'public') == 'true'


class StationListParserTypeB(XmlParser, StationListParser):
    def get_last_communication_time_with_server(self, station):
        return None

    def get_latest_update_time(self, station):
        return None

    def is_public(self, station):
        return None


class StationListParserTypeC(JsonParser, StationListParser):
    STATUSES = (('In Service', 1,),)

    def get_install_date(self, station):
        return None

    def get_last_communication_time_with_server(self, station):
        return timestampToDateTime(self.find(station, 'lastCommunicationTime'))

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

    def get_terminal_name(self, station):
        return self.find(station, 'location')

    def is_locked(self, station):
        return None

    def is_installed(self, station):
        return self.find(station, 'statusKey') == 1

    def is_public(self, station):
        return None

    def is_temporary(self, station):
        return self.find(station, 'testStation')


class Command(BaseCommand):
    args = '<city_code city_code ...>'
    help = 'Updates the current bike and dock counts for a given list of cities.'

    def __init__(self):
        self.created = 0
        self.status_quo = 0
        self.updated = 0
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
                parser = parsers[city.parser_type](data)
            except IndexError:
                raise NotImplementedError("The parser for '%s' hasn't been implemented yet." % (city.name,))

            for s in parser.get_stations():
                attrs = dict()
                public_id = parser.get_public_id(s)
                last_comm_with_server = parser.get_last_communication_time_with_server(s)
                try:
                    station = Station.objects.get(city=city, public_id=public_id)
                    # Skip if we have a timestamp to compare against
                    if last_comm_with_server and station.last_comm_with_server == last_comm_with_server:
                        self._increase_status_quo_count()
                        continue
                    # Else, update the station
                except Station.DoesNotExist:
                    station = Station()
                    attrs.update({
                        'city_id': city.pk,
                        'name': parser.get_station_name(s),
                        'public_id': public_id,
                        'terminal_name': parser.get_terminal_name(s),
                    })

                attrs.update({
                    'install_date': parser.get_install_date(s),
                    'installed': parser.is_installed(s),
                    'last_comm_with_server': parser.get_last_communication_time_with_server(s),
                    'lat': parser.get_latitude(s),
                    'locked': parser.is_locked(s),
                    'long': parser.get_longitude(s),
                    'public': parser.is_public(s),
                    'removal_date': parser.get_removal_date(s),
                    'temporary': parser.is_temporary(s),
                })

                nb_bikes = parser.get_number_available_bikes(s)
                nb_empty_docks = parser.get_number_empty_docks(s)

                # Try to find if there has been changes since the last time
                # this station was updated
                latest_update_time = parser.get_latest_update_time(s)
                if latest_update_time:
                    if not station.last_comm_with_server:
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
                    mru = Update.objects.filter(station=station).latest()
                    if (mru.nb_bikes, mru.nb_empty_docks,) == (nb_bikes, nb_empty_docks,):
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

                Update.objects.create(station=station, nb_bikes=nb_bikes,
                    nb_empty_docks=nb_empty_docks,
                    latest_update_time=latest_update_time)

            last_update = parser.get_last_update_time()
            city.last_update = last_update
            city.save()

            self.stdout.write("\nSuccessfully updated bike and dock counts for " +
                "'%s'." % city.name)
            self.stdout.write('Created: %s' % self.created)
            self.stdout.write('Updated: %s' % self.updated)
            self.stdout.write('Status quo: %s' % self.status_quo)

