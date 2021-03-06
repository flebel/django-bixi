from django.contrib import admin
from django.contrib.admin import BooleanFieldListFilter
from django.db import connection
from django.db.models import Max
from django.http import HttpResponseRedirect
from models import City, Station, Update


class CityAdmin(admin.ModelAdmin):
    fields = ('name', 'code', 'url', 'active',)
    list_display = ('name', 'code', 'url', 'last_recorded_update', 'active',)
    search_fields = ('name', 'code', 'active',)
admin.site.register(City, CityAdmin)


class StationAdmin(admin.ModelAdmin):
    list_display = ('city', 'name', 'last_recorded_communication', 'installed',
        'locked', 'temporary', 'public')
    list_filter = ('city', 'installed', 'locked', 'temporary', 'public')
    readonly_fields = ('city', 'public_id', 'name', 'vicinity',
        'last_recorded_communication', 'latitude', 'longitude', 'installed',
        'locked', 'installation_date', 'removal_date', 'temporary', 'public',)
    search_fields = ('name',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Station, StationAdmin)


class LatestUpdatesListFilter(BooleanFieldListFilter):
    title = 'Latest updates only'
    parameter_name = 'latest_update_time'

    def choices(self, cl):
        choices = super(LatestUpdatesListFilter, self).choices(cl)
        # Remove 'All' from the list of choices
        return list(choices)[1:]

    def queryset(self, request, queryset):
        if self.lookup_val is None or not bool(int(self.lookup_val)):
            return queryset
        if connection.vendor == 'sqlite':
            # SQLite does not support 'DISTINCT ON'
            latest_updates = queryset.values('station__pk').annotate(pk=Max('pk'))
            return queryset.filter(pk__in=[lut['pk'] for lut in latest_updates])
        else:
            return queryset.order_by('station__pk', '-latest_update_time').distinct('station__pk')


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('station', 'bikes', 'empty_docks',
        'latest_update_time',)
    list_filter = (('latest_update_time', LatestUpdatesListFilter,),
        'station__city__name',)
    readonly_fields = ('station', 'bikes', 'empty_docks',
        'latest_update_time', 'raw_data',)
    search_fields = ('station__name',)

    def changelist_view(self, request, extra_context=None):
        if not request.META['QUERY_STRING'] and \
            not request.META.get('HTTP_REFERER', '').startswith(request.build_absolute_uri()):
            return HttpResponseRedirect(request.path + '?latest_update_time__exact=1')
        return super(UpdateAdmin, self).changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Update, UpdateAdmin)

