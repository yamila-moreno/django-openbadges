# -*- coding: utf-8 -*-

# Copyright 2013 Rooter Analysis S.L.
# Copyright 2013 Yamila Moreno <yamila.moreno@kaleidos.net>
# Copyright 2013 Jesús Espino <jespinog@gmail.com>
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

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseGone
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import View

from . import models
import json


class UserBadges(View):
    def get(self, request, user_pk, mode):
        if mode == 'email':
            user = get_object_or_404(get_user_model(), email=user_pk)
        else:
            user = get_object_or_404(get_user_model(), id=user_pk)
        try:
            award_list = models.Award.objects.filter(user=user)
            return render_to_response('badges/user_badges.html', {
                'award_list': award_list,
                'user': user,
            }, context_instance=RequestContext(request))
        except models.Award.DoesNotExist:
            return HttpResponse(status=404)


class UserBadge(View):
    def get(self, request, badge_slug, user_pk, mode):
        badge = get_object_or_404(models.Badge, slug=badge_slug)
        if mode == 'email':
            user = get_object_or_404(get_user_model(), email=user_pk)
        else:
            user = get_object_or_404(get_user_model(), id=user_pk)
        try:
            award = get_object_or_404(models.Award, badge=badge, user=user)
            return render_to_response('badges/user_badge.html', {
                'award': award,
                'user': user,
            }, context_instance=RequestContext(request))
        except models.Award.DoesNotExist:
            return HttpResponse(status=404)


class BadgeImage(View):
    def get(self, request, badge_slug, user_pk, mode):
        badge = get_object_or_404(models.Badge, slug=badge_slug)
        if mode == 'email':
            user = get_object_or_404(get_user_model(), email=user_pk)
        else:
            user = get_object_or_404(get_user_model(), id=user_pk)
        try:
            models.Award.objects.filter(user=user).get(badge=badge)
            return HttpResponse(badge.image.read(), content_type="image/png")
        except models.Award.DoesNotExist:
            return HttpResponse(status=404)


class Badge(View):
    def get(self, request, badge_slug):
        badge = get_object_or_404(models.Badge, slug=badge_slug)
        return HttpResponse(json.dumps(badge.to_dict()))


class RevocationList(View):
    def get(self, request):
        revocations = [r.to_dict() for r in models.Revocation.objects.all()]

        return HttpResponse(json.dumps(revocations))


class Issuer(View):
    def get(self, request):
        issuer = models.Issuer.objects.all()[0].to_dict()
        return HttpResponse(json.dumps(issuer))


class Assertion(View):
    def get(self, request, assertion_uuid):
        assertion = get_object_or_404(models.Award, uuid=assertion_uuid)
        if assertion.revoked:
            return HttpResponseGone(json.dumps({'revoked': True}))

        return HttpResponse(json.dumps(assertion.to_dict()))


class Criterion(View):
    def get(self, request, criterion_slug):
        criterion = get_object_or_404(models.Criterion, slug=criterion_slug)
        context = {'criterion': criterion}
        return render_to_response('badges/criterion.html', context,
                                  context_instance=RequestContext(request))
