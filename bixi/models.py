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

class Update(models.Model):
    station = models.ForeignKey(Station)
    nb_bikes = models.IntegerField()
    nb_empty_docks = models.IntegerField()
    latest_update_time = models.DateTimeField(null=True)

    class Meta:
        get_latest_by = 'latest_update_time'

    def __unicode__(self):
        return self.station.name

