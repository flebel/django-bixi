from django.contrib import admin
from models import City, Station, Update


class CityAdmin(admin.ModelAdmin):
    fields = ('name', 'code', 'url', 'active',)
    list_display = ('name', 'code', 'url', 'last_update', 'active',)
    search_fields = ('name', 'code', 'active',)
admin.site.register(City, CityAdmin)


class StationAdmin(admin.ModelAdmin):
    list_display = ('city', 'name', 'last_comm_with_server', 'installed',
        'locked', 'temporary', 'public')
    list_filter = ('city', 'installed', 'locked', 'temporary', 'public')
    readonly_fields = ('city', 'public_id', 'name', 'terminal_name',
        'last_comm_with_server', 'lat', 'long', 'installed', 'locked',
        'install_date', 'removal_date', 'temporary', 'public',)
    search_fields = ('name',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Station, StationAdmin)


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('station', 'nb_bikes', 'nb_empty_docks',
        'latest_update_time',)
    list_filter = ('station__city__name',)
    readonly_fields = ('station', 'nb_bikes', 'nb_empty_docks',
        'latest_update_time',)
    search_fields = ('station__name',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(Update, UpdateAdmin)

