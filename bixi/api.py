from django.conf import settings

from tastypie.resources import ModelResource
from tastypie.throttle import CacheThrottle

from models import City, Station, Update


class CityResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        queryset = City.objects.all()
        resource_name = 'city'
        throttle = CacheThrottle(
            throttle_at=settings.BIXI_THROTTLE_AT,
            timeframe=settings.BIXI_TIMEFRAME,
            expiration=settings.BIXI_EXPIRATION
        )

class StationResource(ModelResource):
    def dehydrate(self, bundle):
        update = Update.objects.filter(station__id=bundle.data['id']).latest()
        bundle.data['nb_bikes'] = update.nb_bikes
        bundle.data['nb_empty_docks'] = update.nb_empty_docks
        return bundle

    class Meta:
        allowed_methods = ['get']
        excludes = ['public_id', 'terminal_name']
        queryset = Station.available.all()
        resource_name = 'station'
        throttle = CacheThrottle(
            throttle_at=settings.BIXI_THROTTLE_AT,
            timeframe=settings.BIXI_TIMEFRAME,
            expiration=settings.BIXI_EXPIRATION
        )

