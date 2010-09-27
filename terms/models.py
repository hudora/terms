# encoding: utf-8
"""
models.py

Created by Christian Klein on 2010-09-22.
Copyright (c) 2010 HUDORA. All rights reserved.
"""

from django.contrib.auth.models import User
from django.core import urlresolvers
from django.db import models


class Terms(models.Model):
    version = models.PositiveIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        get_latest_by = 'version'
        verbose_name = u'Terms'
        verbose_name_plural = u'Terms'

    def __unicode__(self):
        return unicode(self.version)


class Agreement(models.Model):
    """Agreement of <something> to a specific version of the terms"""
    
    user = models.ForeignKey(User, related_name='agreements')
    terms = models.ForeignKey('Terms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'terms__version'
