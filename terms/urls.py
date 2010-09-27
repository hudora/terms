from django.conf.urls.defaults import *

urlpatterns = patterns('terms.views',
    url(r'^agree/$', 'agree', name='terms.agree'),
)
