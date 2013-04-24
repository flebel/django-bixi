from tastypie.resources import ModelResource

from models import Station, Update


class StationResource(ModelResource):
    def dehydrate(self, bundle):
        update = Update.objects.filter(station__id=bundle.data['id']).latest()
        bundle.data['nb_bikes'] = update.nb_bikes
        bundle.data['nb_empty_docks'] = update.nb_empty_docks
        return bundle

    class Meta:
        allowed_methods = ['get']
        excludes = ['public_id', 'terminal_name']
        queryset = Station.objects.all()
        resource_name = 'station'

