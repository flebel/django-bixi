# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'City'
        db.create_table(u'bixi_city', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.SlugField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'bixi', ['City'])

        # Adding model 'Station'
        db.create_table(u'bixi_station', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bixi.City'])),
            ('public_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('terminal_name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('last_comm_with_server', self.gf('django.db.models.fields.DateTimeField')()),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('long', self.gf('django.db.models.fields.FloatField')()),
            ('installed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('install_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('removal_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('temporary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'bixi', ['Station'])

        # Adding model 'Update'
        db.create_table(u'bixi_update', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bixi.Station'])),
            ('nb_bikes', self.gf('django.db.models.fields.IntegerField')()),
            ('nb_empty_docks', self.gf('django.db.models.fields.IntegerField')()),
            ('latest_update_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'bixi', ['Update'])


    def backwards(self, orm):
        # Deleting model 'City'
        db.delete_table(u'bixi_city')

        # Deleting model 'Station'
        db.delete_table(u'bixi_station')

        # Deleting model 'Update'
        db.delete_table(u'bixi_update')


    models = {
        u'bixi.city': {
            'Meta': {'object_name': 'City'},
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