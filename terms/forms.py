# encoding: utf-8
"""
forms.py

Created by Christian Klein on 2010-09-22.
Copyright (c) 2010 HUDORA. All rights reserved.
"""

import time
import datetime

from django import forms
from django.forms.util import ErrorDict
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from terms.models import Agreement, Terms
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor


class AgreementForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for agreement forms.
    """
    
    user_pk     = forms.CharField(widget=forms.HiddenInput)
    terms_pk      = forms.CharField(widget=forms.HiddenInput)
    timestamp     = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)
    
    accept = forms.BooleanField()

    def __init__(self, user, terms, data=None, initial=None):
        self.user = user
        self.terms = terms
        if initial is None:
            initial = {}
                
        initial.update(self.generate_security_data())
        super(AgreementForm, self).__init__(data=data, initial=initial)

    def security_errors(self):
        """Return just those errors associated with security"""
        errors = ErrorDict()
        for f in ["timestamp", "security_hash"]:
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors

    def clean_security_hash(self):
        """Check the security hash."""
        security_hash_dict = {
            'user_pk' : self.data.get("user_pk", ""),
            'terms_pk' : self.data.get("terms_pk", ""),
            'timestamp' : self.data.get("timestamp", ""),
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if expected_hash != actual_hash:
            raise forms.ValidationError("Security hash check failed.")
        return actual_hash

    def clean_timestamp(self):
        """Make sure the timestamp isn't too far (> 2 hours) in the past."""
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > (2 * 60 * 60):
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def generate_security_data(self):
        """Generate a dict of security data for "initial" data."""
        timestamp = int(time.time())
        security_dict =   {
            'user_pk'       : str(self.user._get_pk_val()),
            'terms_pk'      : str(self.terms._get_pk_val()),
            'timestamp'     : str(timestamp),
            'security_hash' : self.initial_security_hash(timestamp),
        }
        return security_dict

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from self.content_object
        and a (unix) timestamp.
        """

        initial_security_dict = {
            'user_pk' : str(self.user._get_pk_val()),
            'terms_pk' : str(self.terms._get_pk_val()),
            'timestamp' : str(timestamp),
          }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, user_pk, terms_pk, timestamp):
        """Generate a (SHA1) security hash from the provided info."""
        info = (user_pk, terms_pk, timestamp, settings.SECRET_KEY)
        return sha_constructor("".join(info)).hexdigest()

    def get_agreement_object(self):
        """
        Return a new (unsaved) agreement object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.
        """
        
        if not self.is_valid():
            raise ValueError("get_agreement_object may only be called on valid forms")

        new = Agreement(**self.get_agreement_create_data())
        return new

    def get_agreement_create_data(self):
        """Returns the dict of data to be used to create an agreement."""
        
        return dict(
            user_id  = force_unicode(self.user._get_pk_val()),
            terms_id = force_unicode(self.terms._get_pk_val()),
        )
