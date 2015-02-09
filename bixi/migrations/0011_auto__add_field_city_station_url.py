# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'City.station_url'
        db.add_column(u'bixi_city', 'station_url',
                      self.gf('django.db.models.fields.URLField')(max_length=200, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'City.station_url'
        db.delete_column(u'bixi_city', 'station_url')


    models = {
        u'bixi.city': {
            'Meta': {'object_name': 'City'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_recorded_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parser_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'station_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'bixi.station': {
            'Meta': {'object_name': 'Station'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bixi.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'installation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'installed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'last_recorded_communication': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'locked': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'public': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'public_id': ('django.db.models.fields.IntegerField', [], {}),
            'removal_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'temporary': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'vicinity': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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