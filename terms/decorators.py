#!/usr/bin/env python
# encoding: utf-8
"""
decorators.py

Created by Christian Klein on 2010-09-27.
Copyright (c) 2010 HUDORA. All rights reserved.
"""

try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.4 fallback.

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import available_attrs
from django.utils.http import urlquote
from terms.models import Agreement, Terms


def check(customer):
    """Check if a given instance agreed to the most recent terms"""

    try:
        agreement = customer.agreements.latest()
    except customer.agreements.model.DoesNotExist:
        return False
    return agreement.terms == Terms.objects.latest()


def latest_terms_required(view_func):
    """Decorator for views that checks that the customer agreed to the latest terms."""

    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request, 'customer'):
            # We decide to fail open instead of fail close
            # meaning htat if something is broken with finding the customer
            # we allow access WITHOUT agreeing to the Terms & conditions.
            logging.error("request has no 'customer' attribute")
            return view_func(request, *args, **kwargs)
        else:
            if check(request.customer):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            tup = reverse('terms.agree'), path
            return HttpResponseRedirect('%s?next=%s' % tup)
    return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
