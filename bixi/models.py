from math import radians, cos, sin, asin, sqrt

from django.db import models


class City(models.Model):
    code = models.SlugField(max_length=20)
    name = models.CharField(max_length=200)
    url = models.URLField()
    last_update = models.DateTimeField(null=True)

    class Meta:
        get_latest_by = 'last_update'
        verbose_name_plural = 'cities'

    def __unicode__(self):
        return self.name

class AvailableManager(models.Manager):
    def get_query_set(self):
        return super(AvailableManager, self).get_query_set().filter(
            installed=True, locked=False)

class Station(models.Model):
    city = models.ForeignKey(City)
    public_id = models.IntegerField()
    name = models.CharField(max_length=200)
    terminal_name = models.CharField(max_length=10)
    last_comm_with_server = models.DateTimeField()
    lat = models.FloatField()
    long = models.FloatField()
    installed = models.BooleanField()
    locked = models.BooleanField()
    install_date = models.DateTimeField(null=True)
    removal_date = models.DateTimeField(null=True)
    temporary = models.BooleanField()
    public = models.BooleanField()

    objects = models.Manager()
    available = AvailableManager()

    class Meta:
        get_latest_by = 'last_comm_with_server'

    def __unicode__(self):
        return self.name

    def distance(self, lat, long):
        """
        Calculate the great circle distance in meters between two points on the
        Earth (specified in decimal degrees.)
        Taken on May 1st 2013 from:
        http://stackoverflow.com/a/4913653
        """
        # Convert decimal degrees to radians
        long1, lat1, long2, lat2 = map(radians, [self.long, self.lat, long, lat])
        # Haversine formula
        dlon = long2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return 6367 * c

    def closest_stations(self, num_stations=None):
        """
        Upon giving it a number of stations to look for, return a list of
        tuples containing the distance and station sorted by proximity.
        """
        stations = dict()
        for s in Station.objects.filter(city=self.city).exclude(pk=self.pk):
            stations[self.distance(s.lat, s.long)] = s
        sorted_stations = []
        for (i, s) in enumerate(sorted(stations.keys())):
            if num_stations and i == num_stations:
                break
            sorted_stations.append((s, stations[s],))
        return sorted_stations

class Update(models.Model):
    station = models.ForeignKey(Station)
    nb_bikes = models.IntegerField()
    nb_empty_docks = models.IntegerField()
    latest_update_time = models.DateTimeField(null=True)

    class Meta:
        get_latest_by = 'latest_update_time'

    def __unicode__(self):
        return self.station.name

