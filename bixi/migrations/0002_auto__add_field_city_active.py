# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'City.active'
        db.add_column(u'bixi_city', 'active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'City.active'
        db.delete_column(u'bixi_city', 'active')


    models = {
        u'bixi.city': {
            'Meta': {'object_name': 'City'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'bixi.station': {
            'Meta': {'object_name': 'Station'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bixi.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'install_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'installed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_comm_with_server': ('django.db.models.fields.DateTimeField', [], {}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'long': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'public_id': ('django.db.models.fields.IntegerField', [], {}),
            'removal_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terminal_name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'bixi.update': {
            'Meta': {'object_name': 'Update'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_update_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'nb_bikes': ('django.db.models.fields.IntegerField', [], {}),
            'nb_empty_docks': ('django.db.models.fields.IntegerField', [], {}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bixi.Station']"})
        }
    }

    complete_apps = ['bixi']