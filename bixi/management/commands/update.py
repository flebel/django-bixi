from xml.etree import ElementTree
from datetime import datetime
import urllib2

from django.core.management.base import BaseCommand, CommandError

from bixi.models import City, Station, Update


class Command(BaseCommand):
    args = '<city_code city_code ...>'
    help = 'Updates the current bike and dock counts for a given list of cities.'

    def handle(self, *args, **options):
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
                last_comm_with_server = datetime.fromtimestamp(int(
                    s.find('lastCommWithServer').text) / 1e3)
                try:
                    station = Station.objects.get(city=city,
                        public_id=public_id)
                    if station.last_comm_with_server == last_comm_with_server:
                        continue
                except Station.DoesNotExist:
                    name = s.find('name').text
                    station = Station()
                    station.city = city
                    station.public_id = public_id
                    station.name = name
                lat = float(s.find('lat').text)
                long = float(s.find('long').text)
                installed = s.find('installed').text
                locked = s.find('locked').text
                nb_bikes = int(s.find('nbBikes').text)
                nb_empty_docks = int(s.find('nbEmptyDocks').text)
                latest_update_time = s.find('latestUpdateTime').text
                if latest_update_time:
                    latest_update_time = datetime.fromtimestamp(
                        int(s.find('latestUpdateTime').text) / 1e3)

                station.last_comm_with_server = last_comm_with_server
                station.lat = lat
                station.long = long
                station.installed = installed
                station.locked = locked
                station.save()

                if Update.objects.filter(station=station,
                    latest_update_time=latest_update_time).exists():
                    continue

                Update.objects.create(station=station, nb_bikes=nb_bikes,
                    nb_empty_docks=nb_empty_docks,
                    latest_update_time=latest_update_time)

            last_update = datetime.fromtimestamp(
                int(root.attrib['lastUpdate']) / 1e3)
            city.last_update = last_update
            city.save()

            self.stdout.write('Successfully updated bike and dock counts for ' +
                '%s.' % city.name)

