from django.db import models

from utils import distance


class AvailableCityManager(models.Manager):
    def get_query_set(self):
        return super(AvailableCityManager, self).get_query_set().filter(
            active=True)

class City(models.Model):
    code = models.SlugField(max_length=20)
    name = models.CharField(max_length=200)
    url = models.URLField()
    active = models.BooleanField(default=True)
    last_update = models.DateTimeField(null=True)

    objects = models.Manager()
    available = AvailableCityManager()

    class Meta:
        get_latest_by = 'last_update'
        verbose_name_plural = 'cities'

    def __unicode__(self):
        return self.name

class AvailableStationManager(models.Manager):
    def get_query_set(self):
        return super(AvailableStationManager, self).get_query_set().filter(
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
    available = AvailableStationManager()

    class Meta:
        get_latest_by = 'last_comm_with_server'

    def __unicode__(self):
        return self.name

    def neighbor_stations(self, num_stations=None):
        """
        Upon giving it a number of stations to look for, return a list of
        tuples containing the distance of the neighbor stations sorted by
        proximity.
        """
        return Station.closest_stations(self.lat, self.long, self.city,
            num_stations)

    @staticmethod
    def closest_stations(lat, long, city=None, num_stations=None):
        """
        Upon giving it a city, latitude, longitude coordinates and a number of
        stations to look for, return a list of tuples containing the distance
        and station sorted by proximity.
        """
        stations = dict()
        stations_qs = Station.objects.exclude(lat=lat, long=long)
        if (city):
            stations_qs = stations_qs.filter(city=city)
        for s in stations_qs:
            stations[distance(lat, long, s.lat, s.long)] = s
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

