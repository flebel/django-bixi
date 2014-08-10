from django.db import models

from utils import distance


class AvailableCityManager(models.Manager):
    def get_query_set(self):
        return super(AvailableCityManager, self).get_query_set().filter(
            active=True)


class City(models.Model):
    PARSER_FORMATS_VALUES = ('JSON', 'XML',)
    PARSER_FORMATS = [(val[1], val[0],) for val in enumerate(PARSER_FORMATS_VALUES)]
    PARSER_VARIATIONS_VALUES = ('A', 'B', 'C',)
    PARSER_VARIATIONS = [(val[1], val[0],) for val in enumerate(PARSER_VARIATIONS_VALUES)]

    code = models.SlugField(
        help_text='Lowercase slug identifying the city.',
        max_length=20
    )
    name = models.CharField(max_length=200)
    url = models.URLField(help_text='JSON or XML URL containing station updates. Both HTTP and HTTPS are supported.')
    parser_format = models.PositiveSmallIntegerField(
        choices=PARSER_FORMATS,
        default=1, # XML seems to be the most common
        help_text='Parser format to use for the given URL.'
    )
    parser_variation = models.PositiveSmallIntegerField(
        choices=PARSER_VARIATIONS,
        default=0,
        help_text="Named variation of the updates format. Refer to the 'updatestations' management command source code for the differences between the available formats."
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether or not the city operates the bicycle sharing system.'
    )
    last_update = models.DateTimeField(
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
    def parser_format_code_to_value(code):
        return [pt[1] for pt in City.PARSER_FORMATS if pt[0] == code][0]

    @staticmethod
    def parser_variation_code_to_value(code):
        return [pt[1] for pt in City.PARSER_VARIATIONS if pt[0] == code][0]


class AvailableStationManager(models.Manager):
    def get_query_set(self):
        return super(AvailableStationManager, self).get_query_set().filter(
            installed=True, locked=False)


class Station(models.Model):
    city = models.ForeignKey(City)
    public_id = models.IntegerField(help_text='Unique identifier on the bicycle sharing system.')
    name = models.CharField(max_length=200)
    terminal_name = models.CharField(
        help_text='The general area where the station is located. A terminal name can be shared by multiple stations.',
        max_length=50
    )
    last_comm_with_server = models.DateTimeField(
        help_text='Date and time of the last communication with the bicycle sharing system.',
        null=True
    )
    lat = models.FloatField()
    long = models.FloatField()
    installed = models.BooleanField(help_text='Whether or not this station is currently deployed.')
    locked = models.NullBooleanField(help_text='Whether or not this station is accessible.')
    install_date = models.DateTimeField(null=True)
    removal_date = models.DateTimeField(null=True)
    temporary = models.BooleanField(help_text='Whether or not this station is permanent.')
    public = models.NullBooleanField(help_text='Whether or not this station is available for public use.')

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
        if city:
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
    nb_bikes = models.IntegerField(help_text='Number of bicycles docked at that moment.')
    nb_empty_docks = models.IntegerField(help_text='Number of empty docks at that moment.')
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

