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
    def update(cls, text):
        """ speichert eine neue Version der AGBs in der Datenbank """
        latest = Terms.get_latest()
        version = latest.version + 1 if latest else 1
        terms = Terms(version=version,
                      text=text)
        terms.put()

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
        try:
            request = self.request
            kundennr = self.credential_empfaenger.kundennr
            if not Agreement.has_agreed_to_latest(kundennr):
                path = urllib.quote(self.request.path)
                r= self.redirect('/terms?next=%s&kundennr=%s' % (path, kundennr))
                return r
        except Exception, ex:
            # wenn wir noch keine Credentials vorliegen haben kann auch die
            # Ueberpruefung nicht stattfinden, also koennen wir diesen Fall
            # ignorieren
            pass
        return handler_func(self, *args, **kwargs)
    return _wrapper


class AgreementHandler(BasicHandler):
    def get(self):
        """ zeigt das Formular mit den AGBs an und laesst den Benutzer bestaetigen """
        self.login_required()
        try:
            terms = Terms.get_latest()
            html = self.convert_markdown(terms.text)
            self.render({'terms': html,
                         'kundennr': self.request.GET['kundennr'],
                         'version': terms.version}, TERMS_TEMPLATE)
        except AttributeError:
            raise Exception('kein gueltiges (oder ein fehlerhaftes) TERMS_TEMPLATE in der config.py angegeben!')

    def post(self):
        """ ueberprueft, ob der Benutzer seine Zustimmung gegeben hat """
        # wollen wir eine neue Terms-Version hochladen?
        if self.request.path.endswith('/upload/'):
            return self.handle_terms_upload()
           
        # oder doch nur eine Bestaetigung speichern?
        kundennr = self.request.POST.get('kundennr')
        if kundennr:
            Agreement(kundennr=kundennr, terms=Terms.get_latest()).put()
        self.redirect('/')

    def handle_terms_upload(self):
        """ speichert eine neue Version der AGBs. Um die Funktion moeglichst universell zu
            halten (also unabhaengig von irgendwelchen Auth-Mechanismen der restlichen App)
            und gleichzeitig ein bischen Sicherheit einzubauen erwarten wir per Basic Auth
            ein hart kodiertes Token "Aevoes3H:wahQu2Xa", damit der Aufruf akzeptiert wird. """
        auth = self.request.headers.get('Authorization')
        self.response.headers["Content-Type"] = "application/json"
        if auth != 'Basic QWV2b2VzM0g6d2FoUXUyWGE=':
            self.error(403)
        else:
            text = unicode(self.request.body, 'utf-8')
            Terms.update(text)
            self.response.out.write('{"success": true}')

    def convert_markdown(self, markup):
        """ versucht den uebergebenen String als Markdown-Text zu interpretieren und
            dann das konvertierte HTML zurueckliefern. Im Fehlerfall wird der Eingabestring
            zurueckgeliefert """
        try:
            from markdown import markdown
            return markdown(markup)
        except:
            # wenn kein Markdown installiert ist oder andere Fehler auftauchen
            # dann wird das reine Markup zurueckgegeben, damit zumindestens der
            # eigentliche Text lesbar bleibt.
            return markup.replace("\n", '</br>')


def main():
    application = webapp.WSGIApplication([('.*', AgreementHandler)], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
