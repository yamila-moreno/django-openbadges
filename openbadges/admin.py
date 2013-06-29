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

from django.contrib import admin

from django.utils.translation import ugettext_lazy as _

from moocng.badges.models import Badge, Award, Revocation, Issuer, \
            Alignment, Tag, Identity, Criterion


def show_image(obj):
    if isinstance(obj, Badge):
        url = obj.image.url
    elif isinstance(obj, Issuer):
        url = obj.image.url
    else:
        url = obj.badge.image.url
    return '<img src="%s" width="30" height="30" />' % url


show_image.allow_tags = True
show_image.short_description = _("Image")


class BadgeAdmin(admin.ModelAdmin):
    model = Badge
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('title', show_image, 'created',)


class AwardAdmin(admin.ModelAdmin):
    model = Award
    raw_id_fields = ('user',)
    autocomplete_lookup_fields = { 'fk': ['user'], }
    list_display = ('user', 'badge', show_image, 'awarded', 'revoked')

class RevocationAdmin(admin.ModelAdmin):
    model = Revocation
    list_display = ('award', 'reason',)


class IssuerAdmin(admin.ModelAdmin):
    model = Issuer
    list_display = ('name', show_image, 'url', 'email')


class AlignmentAdmin(admin.ModelAdmin):
    model = Alignment
    list_display = ('name', 'url')

class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name',)

class IdentityAdmin(admin.ModelAdmin):
    model = Identity
    list_display = ('user', 'type', 'identity_hash', 'hashed', 'salt')


class CriterionAdmin(admin.ModelAdmin):
    model = Criterion
    prepopulated_fields = {'slug': ('name', )}
    list_display = ('name', 'get_absolute_url')


admin.site.register(Badge, BadgeAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(Revocation, RevocationAdmin)
admin.site.register(Issuer, IssuerAdmin)
admin.site.register(Alignment, AlignmentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Identity, IdentityAdmin)
admin.site.register(Criterion, CriterionAdmin)
"""
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
class IdentityInline(admin.TabularInline):
    model = Identity

admin.site.unregister(User)
UserAdmin.inlines = [
    IdentityInline,
]
admin.site.register(User, UserAdmin)
"""
