from tastypie.resources import ModelResource

from models import Station


class StationResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        queryset = Station.objects.all()
        resource_name = 'station'

