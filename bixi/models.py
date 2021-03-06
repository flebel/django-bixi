from django.db import models

from utils import distance


class AvailableCityManager(models.Manager):
    def get_query_set(self):
        return super(AvailableCityManager, self).get_query_set().filter(
            active=True)


class City(models.Model):
    PARSER_TYPES_VALUES = ('A', 'B', 'C', 'D',)
    PARSER_TYPES = [(val[1], val[0],) for val in enumerate(PARSER_TYPES_VALUES)]

    code = models.SlugField(
        help_text='Lowercase slug identifying the city.',
        max_length=20
    )
    name = models.CharField(max_length=200)
    url = models.URLField(help_text='JSON or XML URL containing station updates. Both HTTP and HTTPS are supported.')
    station_url = models.URLField(help_text="Optional JSON or XML URL containing individual station updates for supported parsers. Both HTTP and HTTPS are supported.", null=True)
    parser_type = models.PositiveSmallIntegerField(
        choices=PARSER_TYPES,
        default=0,
        help_text='Parser to use for the given URL.'
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether or not the city operates the bicycle sharing system.'
    )
    last_recorded_update = models.DateTimeField(
        help_text='Date and time at which an update was recorded on the bicycle sharing system. Null if this information is unavailable.',
        null=True
    )

    objects = models.Manager()
    available = AvailableCityManager()

    class Meta:
        get_latest_by = 'last_update'
        verbose_name_plural = 'cities'

    def __unicode__(self):
        return self.name

    def clean(self):
        self.code = self.code.lower()

    @staticmethod
    def parser_code_to_value(code):
        return [pt[1] for pt in City.PARSER_TYPES if pt[0] == code][0]


class AvailableStationManager(models.Manager):
    def get_query_set(self):
        return super(AvailableStationManager, self).get_query_set().filter(
            installed=True, locked=False)


class Station(models.Model):
    city = models.ForeignKey(City)
    public_id = models.IntegerField(help_text='Unique identifier on the bicycle sharing system.')
    name = models.CharField(max_length=200)
    vicinity = models.CharField(
        help_text='The general area where the station is located. A vicinity can be shared by multiple stations.',
        max_length=50
    )
    last_recorded_communication = models.DateTimeField(
        help_text='Date and time of the last communication with the bicycle sharing system.',
        null=True
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    installed = models.NullBooleanField(help_text='Whether or not this station is currently deployed.')
    locked = models.NullBooleanField(help_text='Whether or not this station is accessible.')
    installation_date = models.DateTimeField(null=True)
    removal_date = models.DateTimeField(null=True)
    temporary = models.NullBooleanField(help_text='Whether or not this station is permanent.')
    public = models.NullBooleanField(help_text='Whether or not this station is available for public use.')

    objects = models.Manager()
    available = AvailableStationManager()

    class Meta:
        get_latest_by = 'last_recorded_communication'

    def __unicode__(self):
        return self.name

    def neighbor_stations(self, num_stations=None):
        """
        Upon giving it a number of stations to look for, return a list of
        tuples containing the distance of the neighbor stations sorted by
        proximity.
        """
        return Station.closest_stations(self.latitude, self.longitude, self.city,
            num_stations)

    @staticmethod
    def closest_stations(latitude, longitude, city=None, num_stations=None):
        """
        Upon giving it a city, latitude, longitude coordinates and a number of
        stations to look for, return a list of tuples containing the distance
        and station sorted by proximity.
        """
        stations = dict()
        stations_qs = Station.objects.exclude(latitude=latitude, longitude=longitude)
        if city:
            stations_qs = stations_qs.filter(city=city)
        for s in stations_qs:
            stations[distance(latitude, longitude, s.latitude, s.longitude)] = s
        sorted_stations = []
        for (i, s) in enumerate(sorted(stations.keys())):
            if num_stations and i == num_stations:
                break
            sorted_stations.append((s, stations[s],))
        return sorted_stations


class Update(models.Model):
    station = models.ForeignKey(Station)
    bikes = models.IntegerField(help_text='Number of bicycles docked at that moment.')
    empty_docks = models.IntegerField(help_text='Number of empty docks at that moment.')
    latest_update_time = models.DateTimeField(
        help_text='Date and time this update was recorded on the bicycle sharing system. Null if this information is unavailable.',
        null=True
    )
    raw_data = models.TextField(
        help_text="Unparsed update data acquired from the city's bicycle sharing system.",
        null=True
    )

    class Meta:
        get_latest_by = 'pk'

    def __unicode__(self):
        return self.station.name

