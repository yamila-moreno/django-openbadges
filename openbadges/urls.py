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

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^revoked/$', views.RevocationList.as_view(), name='revocation_list'),
    url(r'^organization/$', views.Issuer.as_view(), name='issuer'),
    url(r'^assertion/(?P<assertion_uuid>[-\w]+)/$', views.Assertion.as_view(), name='assertion'),
    url(r'^criterion/(?P<criterion_slug>[-\w]+)/$', views.Criterion.as_view(), name='criterion'),
    url(r'^badge/(?P<badge_slug>[-\w]+)/$', views.Badge.as_view(), name='badge'),

    url(r'^user_badges/(?P<user_pk>[\d]+)/?$', views.UserBadges.as_view(), {'mode': 'id'}, name='user_badges', ),
    url(r'^user_badge/(?P<badge_slug>[-\w]+)/(?P<user_pk>[\d]+)/?$', views.UserBadge.as_view(), {'mode': 'id'}, name='user_badge', ),
    url(r'^badge_image/(?P<badge_slug>[-\w]+)/(?P<user_pk>[\d]+)/image/?$', views.BadgeImage.as_view(), {'mode': 'id'}, name='badge_image'),

    url(r'^user_badges_email/(?P<user_pk>[^/]+)/?$', views.UserBadges.as_view(), {'mode': 'email'}, name='user_badges_email'),
    url(r'^user_badge_email/(?P<badge_slug>[-\w]+)/(?P<user_pk>[^/]+)/?$', views.UserBadge.as_view(), {'mode': 'email'}, name='user_badge_email'),
    url(r'^badge_image_email/(?P<badge_slug>[-\w]+)/(?P<user_pk>[^/]+)/image/?$', views.BadgeImage.as_view(), {'mode': 'email'}, name='badge_image_email'),
)
