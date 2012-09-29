# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'City'
        db.create_table('userprofile_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('userprofile', ['City'])

        # Adding model 'UserProfile'
        db.create_table('userprofile_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.IntegerField')()),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.City'], null=True, blank=True)),
            ('twitter_url', self.gf('django.db.models.fields.URLField')(max_length=100, null=True, blank=True)),
            ('facebook_url', self.gf('django.db.models.fields.URLField')(max_length=100, null=True, blank=True)),
            ('linked_url', self.gf('django.db.models.fields.URLField')(max_length=100, null=True, blank=True)),
            ('website_url', self.gf('django.db.models.fields.URLField')(max_length=100, null=True, blank=True)),
            ('profile_status', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('userprofile', ['UserProfile'])

        # Adding model 'Branch'
        db.create_table('userprofile_branch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('course', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('userprofile', ['Branch'])

        # Adding model 'StudentSection'
        db.create_table('userprofile_studentsection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.UserProfile'])),
            ('roll_num', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('year_of_graduation', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('branch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.Branch'], null=True, blank=True)),
        ))
        db.send_create_signal('userprofile', ['StudentSection'])

        # Adding model 'Employer'
        db.create_table('userprofile_employer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('userprofile', ['Employer'])

        # Adding model 'JobDesignation'
        db.create_table('userprofile_jobdesignation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('userprofile', ['JobDesignation'])

        # Adding model 'JobDomain'
        db.create_table('userprofile_jobdomain', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('userprofile', ['JobDomain'])

        # Adding model 'EmployementDetail'
        db.create_table('userprofile_employementdetail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.UserProfile'])),
            ('employer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.Employer'])),
            ('designation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.JobDesignation'])),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.JobDomain'])),
            ('date_of_joining', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('date_of_leaving', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('userprofile', ['EmployementDetail'])

        # Adding model 'College'
        db.create_table('userprofile_college', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('userprofile', ['College'])

        # Adding model 'Degree'
        db.create_table('userprofile_degree', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('userprofile', ['Degree'])

        # Adding model 'HigherEducationDetail'
        db.create_table('userprofile_highereducationdetail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.UserProfile'])),
            ('college', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.College'])),
            ('degree', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.Degree'])),
            ('year_of_graduation', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('userprofile', ['HigherEducationDetail'])

        # Adding model 'Department'
        db.create_table('userprofile_department', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('userprofile', ['Department'])

        # Adding model 'FacultyDesignation'
        db.create_table('userprofile_facultydesignation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('userprofile', ['FacultyDesignation'])

        # Adding model 'FacultySection'
        db.create_table('userprofile_facultysection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.UserProfile'])),
            ('deparment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.Department'])),
            ('designation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.FacultyDesignation'])),
        ))
        db.send_create_signal('userprofile', ['FacultySection'])

        # Adding model 'UserTag'
        db.create_table('userprofile_usertag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userprofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['userprofile.UserProfile'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tag.Tag'])),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('userprofile', ['UserTag'])


    def backwards(self, orm):
        # Deleting model 'City'
        db.delete_table('userprofile_city')

        # Deleting model 'UserProfile'
        db.delete_table('userprofile_userprofile')

        # Deleting model 'Branch'
        db.delete_table('userprofile_branch')

        # Deleting model 'StudentSection'
        db.delete_table('userprofile_studentsection')

        # Deleting model 'Employer'
        db.delete_table('userprofile_employer')

        # Deleting model 'JobDesignation'
        db.delete_table('userprofile_jobdesignation')

        # Deleting model 'JobDomain'
        db.delete_table('userprofile_jobdomain')

        # Deleting model 'EmployementDetail'
        db.delete_table('userprofile_employementdetail')

        # Deleting model 'College'
        db.delete_table('userprofile_college')

        # Deleting model 'Degree'
        db.delete_table('userprofile_degree')

        # Deleting model 'HigherEducationDetail'
        db.delete_table('userprofile_highereducationdetail')

        # Deleting model 'Department'
        db.delete_table('userprofile_department')

        # Deleting model 'FacultyDesignation'
        db.delete_table('userprofile_facultydesignation')

        # Deleting model 'FacultySection'
        db.delete_table('userprofile_facultysection')

        # Deleting model 'UserTag'
        db.delete_table('userprofile_usertag')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tag.tag': {
            'Meta': {'object_name': 'Tag'},
            'category': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'userprofile.branch': {
            'Meta': {'object_name': 'Branch'},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'userprofile.city': {
            'Meta': {'object_name': 'City'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'userprofile.college': {
            'Meta': {'object_name': 'College'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'userprofile.degree': {
            'Meta': {'object_name': 'Degree'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'userprofile.department': {
            'Meta': {'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'userprofile.employementdetail': {
            'Meta': {'object_name': 'EmployementDetail'},
            'date_of_joining': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_leaving': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'designation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.JobDesignation']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.JobDomain']"}),
            'employer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.Employer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.UserProfile']"})
        },
        'userprofile.employer': {
            'Meta': {'object_name': 'Employer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'userprofile.facultydesignation': {
            'Meta': {'object_name': 'FacultyDesignation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'userprofile.facultysection': {
            'Meta': {'object_name': 'FacultySection'},
            'deparment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.Department']"}),
            'designation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.FacultyDesignation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.UserProfile']"})
        },
        'userprofile.highereducationdetail': {
            'Meta': {'object_name': 'HigherEducationDetail'},
            'college': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.College']"}),
            'degree': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.Degree']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.UserProfile']"}),
            'year_of_graduation': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'userprofile.jobdesignation': {
            'Meta': {'object_name': 'JobDesignation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'userprofile.jobdomain': {
            'Meta': {'object_name': 'JobDomain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'userprofile.studentsection': {
            'Meta': {'object_name': 'StudentSection'},
            'branch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.Branch']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roll_num': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.UserProfile']"}),
            'year_of_graduation': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'userprofile.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.City']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'linked_url': ('django.db.models.fields.URLField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'profile_status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.IntegerField', [], {}),
            'twitter_url': ('django.db.models.fields.URLField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'website_url': ('django.db.models.fields.URLField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'userprofile.usertag': {
            'Meta': {'object_name': 'UserTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tag.Tag']"}),
            'userprofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['userprofile.UserProfile']"})
        }
    }

    complete_apps = ['userprofile']