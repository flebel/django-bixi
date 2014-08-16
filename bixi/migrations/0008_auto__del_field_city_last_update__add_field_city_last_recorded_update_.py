# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'City.last_update'
        db.delete_column(u'bixi_city', 'last_update')

        # Adding field 'City.last_recorded_update'
        db.add_column(u'bixi_city', 'last_recorded_update',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Deleting field 'Station.lat'
        db.delete_column(u'bixi_station', 'lat')

        # Deleting field 'Station.install_date'
        db.delete_column(u'bixi_station', 'install_date')

        # Deleting field 'Station.long'
        db.delete_column(u'bixi_station', 'long')

        # Deleting field 'Station.last_comm_with_server'
        db.delete_column(u'bixi_station', 'last_comm_with_server')

        # Deleting field 'Station.terminal_name'
        db.delete_column(u'bixi_station', 'terminal_name')

        # Adding field 'Station.vicinity'
        db.add_column(u'bixi_station', 'vicinity',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Station.last_recorded_communication'
        db.add_column(u'bixi_station', 'last_recorded_communication',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Adding field 'Station.latitude'
        db.add_column(u'bixi_station', 'latitude',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Station.longitude'
        db.add_column(u'bixi_station', 'longitude',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'Station.installation_date'
        db.add_column(u'bixi_station', 'installation_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Deleting field 'Update.nb_bikes'
        db.delete_column(u'bixi_update', 'nb_bikes')

        # Deleting field 'Update.nb_empty_docks'
        db.delete_column(u'bixi_update', 'nb_empty_docks')

        # Adding field 'Update.bikes'
        db.add_column(u'bixi_update', 'bikes',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Update.empty_docks'
        db.add_column(u'bixi_update', 'empty_docks',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'City.last_update'
        db.add_column(u'bixi_city', 'last_update',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)

        # Deleting field 'City.last_recorded_update'
        db.delete_column(u'bixi_city', 'last_recorded_update')


        # User chose to not deal with backwards NULL issues for 'Station.lat'
        raise RuntimeError("Cannot reverse this migration. 'Station.lat' and its values cannot be restored.")
        # Adding field 'Station.install_date'
        db.add_column(u'bixi_station', 'install_date',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Station.long'
        raise RuntimeError("Cannot reverse this migration. 'Station.long' and its values cannot be restored.")
        # Adding field 'Station.last_comm_with_server'
        db.add_column(u'bixi_station', 'last_comm_with_server',
                      self.gf('django.db.models.fields.DateTimeField')(null=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Station.terminal_name'
        raise RuntimeError("Cannot reverse this migration. 'Station.terminal_name' and its values cannot be restored.")
        # Deleting field 'Station.vicinity'
        db.delete_column(u'bixi_station', 'vicinity')

        # Deleting field 'Station.last_recorded_communication'
        db.delete_column(u'bixi_station', 'last_recorded_communication')

        # Deleting field 'Station.latitude'
        db.delete_column(u'bixi_station', 'latitude')

        # Deleting field 'Station.longitude'
        db.delete_column(u'bixi_station', 'longitude')

        # Deleting field 'Station.installation_date'
        db.delete_column(u'bixi_station', 'installation_date')


        # User chose to not deal with backwards NULL issues for 'Update.nb_bikes'
        raise RuntimeError("Cannot reverse this migration. 'Update.nb_bikes' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Update.nb_empty_docks'
        raise RuntimeError("Cannot reverse this migration. 'Update.nb_empty_docks' and its values cannot be restored.")
        # Deleting field 'Update.bikes'
        db.delete_column(u'bixi_update', 'bikes')

        # Deleting field 'Update.empty_docks'
        db.delete_column(u'bixi_update', 'empty_docks')


    models = {
        u'bixi.city': {
            'Meta': {'object_name': 'City'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_recorded_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parser_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'bixi.station': {
            'Meta': {'object_name': 'Station'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bixi.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'installation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'installed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_recorded_communication': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'vicinity': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'public': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'public_id': ('django.db.models.fields.IntegerField', [], {}),
            'removal_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'bixi.update': {
            'Meta': {'object_name': 'Update'},
            'bikes': ('django.db.models.fields.IntegerField', [], {}),
            'empty_docks': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_update_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bixi.Station']"})
        }
    }

    complete_apps = ['bixi']
