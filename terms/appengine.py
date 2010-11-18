#!/usr/bin/env python
# encoding: utf-8
""" Port der Django-Terms auf die AppEngine """

import config
config.imported = True

import logging
import urllib
from functools import update_wrapper, wraps
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import util
from gaetk.handler import BasicHandler


# wir stellen zuerst fest, in welches Template wir die Bestaetigung 
# zu den aktuellen AGSs rendern sollen
try:
    TERMS_TEMPLATE = config.TERMS_TEMPLATE
except:
    TERMS_TEMPLATE = None


class Terms(db.Model):
    """ eine einzelne Version der allgemeinen Geschaeftsbedinungen """
    created_at = db.DateTimeProperty(auto_now_add=True)
    version = db.IntegerProperty(required=True)
    text = db.TextProperty(required=True)

    @classmethod
    def get_latest(cls):
        """ liefert die neueste Version der AGBs zurueck """
        terms = cls.all().order('-created_at').fetch(1)
        return terms[0] if len(terms)>0 else None


class Agreement(db.Model):
    """ eine Zustimmung des Kunden zu einer allgemeinen Geschaeftsbedingung """
    created_at = db.DateTimeProperty(auto_now_add=True)
    terms = db.ReferenceProperty(Terms, required=True)
    kundennr = db.StringProperty(required=True)

    @classmethod
    def has_agreed_to_latest(cls, kundennr):
        """ ueberprueft, ob der Kunde zu den neuesten AGBs zugestimmt hat """
        terms = Terms.get_latest()
        if not terms:
            return True
        query = cls.all().filter('kundennr =', kundennr).filter('terms =', terms)
        agreements = query.fetch(1)
        return len(agreements)>0


def latest_terms_required(handler_func):
    """ Decorator for handlers that checks that the customer agreed to the latest terms. """

    @wraps(handler_func)
    def _wrapper(self, *args, **kwargs):
        request = self.request
        kundennr = self.credential.empfaenger.kundennr
        if not Agreement.has_agreed_to_latest(kundennr):
            path = urllib.quote(self.request.path)
            return self.redirect('/terms?next=%s' % path)
        return handler_func(self, *args, **kwargs)
    return _wrapper


class AgreementHandler(BasicHandler):
    def get(self):
        """ zeigt das Formular mit den AGBs an und laesst den Benutzer bestaetigen """
        self.login_required()
        try:
            terms = Terms.get_latest()
            self.render({'terms': terms.text,
                         'version': terms.version}, TERMS_TEMPLATE)
        except AttributeError:
            raise Exception('kein gueltiges (oder ein fehlerhaftes) TERMS_TEMPLATE in der config.py angegeben!')

    def post(self):
        """ ueberprueft, ob der Benutzer seine Zustimmung gegeben hat """
        self.login_required()
        kundennr = self.credential.empfaenger.kundennr
        Agreement(kundennr=kundennr, terms=Terms.get_latest()).put()
        self.redirect('/')


def main():
    application = webapp.WSGIApplication([('.*', AgreementHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
