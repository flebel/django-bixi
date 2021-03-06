from django.conf import settings
from django.conf.urls.defaults import url

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.throttle import CacheThrottle
from tastypie.utils import trailing_slash
from tastypie import fields

from models import City, Station, Update


class BixiResource(ModelResource):
  def determine_format(self, request):
    return 'application/json'


class CityResource(BixiResource):
    class Meta:
        allowed_methods = ['get']
        excludes = ['active']
        queryset = City.available.all()
        resource_name = 'city'
        filtering = {
            'code': ALL
        }
        throttle = CacheThrottle(
            throttle_at=settings.BIXI_THROTTLE_AT,
            timeframe=settings.BIXI_TIMEFRAME,
            expiration=settings.BIXI_EXPIRATION
        )


class StationResource(BixiResource):
    city = fields.ForeignKey(CityResource, 'city')

    class Meta:
        allowed_methods = ['get']
        excludes = ['public_id', 'terminal_name']
        max_limit = 0
        queryset = Station.available.all()
        resource_name = 'station'
        filtering = {
            'city': ALL_WITH_RELATIONS
        }
        throttle = CacheThrottle(
            throttle_at=settings.BIXI_THROTTLE_AT,
            timeframe=settings.BIXI_TIMEFRAME,
            expiration=settings.BIXI_EXPIRATION
        )

    def dehydrate(self, bundle):
        update = Update.objects.filter(station__id=bundle.data['id']).latest()
        bundle.data['nb_bikes'] = update.nb_bikes
        bundle.data['nb_empty_docks'] = update.nb_empty_docks
        return bundle

    def get_closest_stations(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.throttle_check(request)

        lat = float(request.GET['lat'])
        long = float(request.GET['long'])
        city_code = request.GET.get('city', None)
        num_stations = int(request.GET.get('num', 1))

        city = None
        if city_code:
            city = City.available.get(code=city_code)

        stations = Station.closest_stations(lat, long, city, num_stations)
        objects = []

        for (distance, station) in stations:
            bundle = self.build_bundle(obj=station, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append({ 'distance': distance, 'station': bundle })

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/closest%s$" % (
                self._meta.resource_name,
                trailing_slash()
            ),
            self.wrap_view('get_closest_stations'),
            name='api_get_closest_stations'),
        ]

