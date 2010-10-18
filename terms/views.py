# encoding: utf-8
"""
views.py

Created by Christian Klein on 2010-09-27.
Copyright (c) 2010 HUDORA. All rights reserved.
"""

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from terms.forms import AgreementForm
from terms.models import Terms


def agree(request):
    
    next = request.REQUEST.get('next', '/')
    
    qs = Terms.objects.filter(active=True)
    if 'terms_pk' in request.POST:
        terms = qs.get(pk=request.POST.get('terms_pk'))
    else:
        terms = qs.latest()
    
    if request.method == "POST":
        form = AgreementForm(request.user, terms, request.POST)
        if form.is_valid():
            agreement = form.get_agreement_object()
            agreement.save()
            return HttpResponseRedirect(next)
    else:
        form = AgreementForm(request.user, terms)
    
    return render_to_response('terms/agree.html',
                              {'form': form, 'next': next, 'terms': terms},
                              context_instance=RequestContext(request))


def show(request, terms_pk=None, template_name='terms/show.html'):
    """Show terms"""

    qs = Terms.objects.filter(active=True)
    try:
        if terms_pk:
            terms = qs.get(pk=terms_pk)
        else:
            terms = qs.latest()
    except Terms.DoesNotExist:
        raise Http404
    
    return render_to_response(template_name, {'terms': terms},
                              context_instance=RequestContext(request))
