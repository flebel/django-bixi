import importlib
import urllib2
from datetime import datetime
from xml.etree import ElementTree

from django.core.management.base import BaseCommand, CommandError

from bixi.models import City, Station, Update


def timestampToDateTime(timestamp):
    if timestamp:
        return datetime.fromtimestamp(int(timestamp) / 1e3)
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


class Command(BaseCommand):
    args = '<city_code city_code ...>'
    help = 'Updates the current bike and dock counts for a given list of cities.'

    def __init__(self):
        self.created = 0
        self.status_quo = 0
        self.updated = 0
        return super(Command, self).__init__()

    def _increase_created_count(self):
        self.created = self.created + 1
        self.progress('c')

    def _increase_status_quo_count(self):
        self.status_quo = self.status_quo + 1
        self.progress('.')

    def _increase_updated_count(self):
        self.updated = self.updated + 1
        self.progress('u')

    def handle(self, *args, **options):
        city_codes = args or map(lambda x: x[0], City.available.all().values_list('code'))
        parsers_module = importlib.import_module(self.__class__.__module__)

        for city_code in city_codes:
            try:
                city = City.objects.get(code=city_code)
            except City.DoesNotExist:
                raise CommandError("City '%s' does not exist." % city_code)

            xml = urllib2.urlopen(city.url)

            parsers = {City.parser_code_to_value(value): getattr(parsers_module, 'StationListParserType' + value) for value in City.PARSER_TYPES_VALUES}
            try:
                parser = parsers[city.parser_type](xml)
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
                        self._update_status_quo()
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
                    self._increase_created_count()
                    self.progress('c')

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

                if not station.last_comm_with_server:
                    skip_station = True
                    for (attr, value,) in attrs.items():
                        if not getattr(station, attr) == value:
                            # Skip the station altogether
                            import ipdb; ipdb.set_trace()
                            skip_station = False
                            continue
                    if skip_station:
                        self._increase_status_quo_count()
                        continue

                self._increase_updated_count()

                for (k, v) in attrs.items():
                    assert k in station.__dict__, "The attribute '%s' must be an existing model field." % (k,)
                    setattr(station, k, v)
                station.save()

                latest_update_time = parser.get_latest_update_time(s)
                if Update.objects.filter(station=station,
                    latest_update_time=latest_update_time).exists():
                    continue

                nb_bikes = parser.get_number_available_bikes(s)
                nb_empty_docks = parser.get_number_empty_docks(s)
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

    def progress(self, str):
        self.stdout.write(str, ending='')

