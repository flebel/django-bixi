from xml.etree import ElementTree
from datetime import datetime
import urllib2

from django.core.management.base import BaseCommand, CommandError

from bixi.models import City, Station, Update


class Command(BaseCommand):
    args = '<city_code city_code ...>'
    help = 'Updates the current bike and dock counts for a given list of cities.'

    def handle(self, *args, **options):
        if not args:
            raise CommandError('At least one city_code must be given.')

        for city_code in args:
            try:
                city = City.objects.get(code=city_code)
            except City.DoesNotExist:
                raise CommandError('City "%s" does not exist.' % city_code)

            xml = urllib2.urlopen(city.url)
            tree = ElementTree.parse(xml)
            root = tree.getroot()

            stations = root.findall('station')
            for s in stations:
                public_id = int(s.find('id').text)
                last_comm_with_server = Command.timestampToDateTime(
                    s.find('lastCommWithServer').text)
                try:
                    station = Station.objects.get(city=city,
                        public_id=public_id)
                    if station.last_comm_with_server == last_comm_with_server:
                        continue
                except Station.DoesNotExist:
                    name = s.find('name').text
                    terminal_name = s.find('terminalName').text
                    station = Station()
                    station.city = city
                    station.public_id = public_id
                    station.name = name
                    station.terminal_name = terminal_name
                lat = float(s.find('lat').text)
                long = float(s.find('long').text)
                installed = s.find('installed').text == 'true'
                locked = s.find('locked').text == 'true'
                install_date = Command.timestampToDateTime(
                    s.find('installDate').text)
                removal_date = Command.timestampToDateTime(
                    s.find('removalDate').text)
                temporary = s.find('temporary').text == 'true'
                public = s.find('public').text == 'true'
                nb_bikes = int(s.find('nbBikes').text)
                nb_empty_docks = int(s.find('nbEmptyDocks').text)
                latest_update_time = Command.timestampToDateTime(
                    s.find('latestUpdateTime').text)
                station.last_comm_with_server = last_comm_with_server
                station.lat = lat
                station.long = long
                station.installed = installed
                station.locked = locked
                station.install_date = install_date
                station.removal_date = removal_date
                station.temporary = temporary
                station.public = public
                station.save()

                if Update.objects.filter(station=station,
                    latest_update_time=latest_update_time).exists():
                    continue

                Update.objects.create(station=station, nb_bikes=nb_bikes,
                    nb_empty_docks=nb_empty_docks,
                    latest_update_time=latest_update_time)

            last_update = Command.timestampToDateTime(root.attrib['lastUpdate'])
            city.last_update = last_update
            city.save()

            self.stdout.write('Successfully updated bike and dock counts for ' +
                '%s.' % city.name)

    @staticmethod
    def timestampToDateTime(timestamp):
        if timestamp:
            return datetime.fromtimestamp(int(timestamp) / 1e3)
        return None

