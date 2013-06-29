# -*- coding: utf-8 -*-

# Copyright 2012 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseGone
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from moocng.badges.models import Badge, Award, Revocation, Issuer, \
            Alignment, Tag, Identity, Criterion
import json

def user_badges(request, user_pk, mode):
    if mode == 'email':
        user = get_object_or_404(User, email=user_pk)
    else:
        user = get_object_or_404(User, id=user_pk)
    try:
        award_list = Award.objects.filter(user=user)
        return render_to_response('badges/user_badges.html', {
            'award_list': award_list,
            'user': user,
        }, context_instance=RequestContext(request))
    except Award.DoesNotExist:
        return HttpResponse(status=404)


def user_badge(request, badge_slug, user_pk, mode):
    badge = get_object_or_404(Badge, slug=badge_slug)
    if mode == 'email':
        user = get_object_or_404(User, email=user_pk)
    else:
        user = get_object_or_404(User, id=user_pk)
    try:
        award = get_object_or_404(Award, badge=badge, user=user)
        return render_to_response('badges/user_badge.html', {
            'award': award,
            'user': user,
        }, context_instance=RequestContext(request))
    except Award.DoesNotExist:
        return HttpResponse(status=404)


def badge_image(request, badge_slug, user_pk, mode):
    badge = get_object_or_404(Badge, slug=badge_slug)
    if mode == 'email':
        user = get_object_or_404(User, email=user_pk)
    else:
        user = get_object_or_404(User, id=user_pk)
    try:
        Award.objects.filter(user=user).get(badge=badge)
        return HttpResponse(badge.image.read(), content_type="image/png")
    except Award.DoesNotExist:
        return HttpResponse(status=404)


def badge(request, badge_slug):
    badge = get_object_or_404(Badge, slug=badge_slug)
    return HttpResponse(json.dumps(badge.to_dict()))


def revocation_list(request):
    revocations = [r.to_dict()
        for r in Revocation.objects.all()]

    return HttpResponse(json.dumps(revocations))


def issuer(request):
    issuer = Issuer.objects.all()[0].to_dict()
    return HttpResponse(json.dumps(issuer))


def assertion(request, assertion_uuid):
    assertion = get_object_or_404(Award, uuid=assertion_uuid)
    if assertion.revoked:
        return HttpResponseGone(json.dumps({'revoked':True}))

    return HttpResponse(json.dumps(assertion.to_dict()))


def criterion(request, criterion_slug):
    criterion = get_object_or_404(Criterion, slug=criterion_slug)
    context = {'criterion': criterion}
    return render_to_response('badges/criterion.html', context,
                                context_instance=RequestContext(request))

