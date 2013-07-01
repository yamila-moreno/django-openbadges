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

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

import Image
import PngImagePlugin
import hashlib
import uuid
import tempfile


if settings.BADGES_BASE_URL is None:
    raise ImproperlyConfigured("ERROR: Please set BADGES_BASE_URL in your settings file")


def validate_png_image(value):
    if value.file.content_type != 'image/png':
        raise ValidationError(_(u'The image is not a png'))


def build_absolute_url(url):
    base_url = settings.BADGES_BASE_URL
    url = url
    return '%s%s' % (base_url, url)


IDENTITY_CHOICES = (
    ('email', _(u'User email')),
)


class Identity(models.Model):
    user = models.OneToOneField(get_user_model(), verbose_name=_(u'User identity'),
                                blank=False, null=False,
                                related_name='identity')
    type = models.CharField(verbose_name=_(u'Identity type'), blank=False,
                            null=False, max_length=255,
                            choices=IDENTITY_CHOICES,
                            default=IDENTITY_CHOICES[0][0])
    identity_hash = models.CharField(verbose_name=_(u'Identity hash'),
                                     blank=True, null=False, max_length=255)
    hashed = models.BooleanField(verbose_name=_(u'Hashed'), default=True)
    salt = models.CharField(verbose_name=_(u'Identity salt'), blank=True,
                            null=True, max_length=255)

    class Meta:
        verbose_name = _(u'identity')
        verbose_name_plural = _(u'identities')

    def __unicode__(self):
        return ugettext(u'Identity of {0}').format(self.user.username)

    def to_dict(self):
        return {
            'identity': self.identity_hash,
            'type': self.type,
            'hashed': self.hashed,
            'salt': self.salt
        }


class Badge(models.Model):
    title = models.CharField(verbose_name=_(u'Name'), blank=False, null=False,
                             unique=True, max_length=255,
                             help_text=_(u'Short, descriptive title'))
    description = models.TextField(verbose_name=_('Badge description'),
                                   blank=False, null=False,
                                   help_text=_(u'Longer description of the badge and its criteria'))
    image = models.ImageField(verbose_name=_(u'Badge image'), blank=False,
                              null=False, upload_to='badges',
                              validators=[validate_png_image],
                              help_text=_(u'Upload an image to represent the badge, it must be png'))
    criteria = models.CharField(verbose_name=_(u'Criteria'), blank=False,
                                null=False, max_length=255,
                                help_text=_(u'URL of the criteria for earning the achievement (recomended: marked up this up with LRMI)'))
    alignments = models.ManyToManyField('Alignment',
                                        verbose_name=_(u'Alignments'),
                                        blank=True, null=True,
                                        related_name=_(u'alignments'))
    tags = models.ManyToManyField('Tag', verbose_name=_(u'Tags'), blank=True,
                                  null=True, related_name=_(u'tags'))
    slug = models.SlugField(verbose_name=_(u'Badge slug'),
                            blank=False, unique=True, null=False,
                            help_text=_(u'Very short name, for use in URLs and links'))
    created = models.DateTimeField(verbose_name=_(u'Creation date and time'),
                                   auto_now_add=True, blank=False)
    modified = models.DateTimeField(verbose_name=_(u'Last modification date and time'),
                                    auto_now=True, blank=False)

    class Meta:
        ordering = ['-modified', '-created']
        verbose_name = _(u'badge')
        verbose_name_plural = _(u'badges')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return build_absolute_url(reverse('badge', args=[self.slug]))

    def to_dict(self):
        return {
            'name': self.title,
            'description': self.description,
            'image': build_absolute_url(self.image.url),
            'criteria': self.criteria,
            'issuer': build_absolute_url(reverse('issuer')),
            'alignment': [a.to_dict() for a in self.alignments.all()],
            'tags': [t.name for t in self.tags.all()]
        }


class Award(models.Model):
    """
    Only available verification type 'hosted' by design decision.
    If 'signed' type is needed, it's necessary to add
    corresponding fields and methods, and refactor in to_dict()
    """
    uuid = models.CharField(verbose_name=_(u'Award uuid'), db_index=True,
                            max_length=255, default=lambda: str(uuid.uuid1()))
    user = models.ForeignKey(get_user_model(), verbose_name=_(u'Awardee'), blank=False,
                             null=False, related_name='user_awards')
    badge = models.ForeignKey('Badge', verbose_name=_(u'Badge'), blank=False,
                              null=False, related_name='awards_set')
    awarded = models.DateTimeField(verbose_name=_(u'Awarding date and time'),
                                   blank=False, null=False, auto_now_add=True)
    evidence = models.CharField(verbose_name=_(u'URL with assertion evidence'),
                                blank=True, null=True, max_length=255)
    image = models.ImageField(verbose_name=_(u'Image evidence'), blank=True,
                              null=True, upload_to='badges',
                              validators=[validate_png_image],
                              help_text=_("Image evidence, it must be png"))
    expires = models.DateTimeField(verbose_name=_(u'When a badge should no longer be considered valid'),
                                   blank=True, null=True)
    modified = models.DateTimeField(verbose_name=_(u'Last modification date and time'),
                                    blank=False, null=False, auto_now=True)
    identity_type = models.CharField(verbose_name=_(u'Identity type'),
                                     blank=True, null=False, max_length=255,
                                     choices=IDENTITY_CHOICES,
                                     default=IDENTITY_CHOICES[0][0])
    identity_hash = models.CharField(verbose_name=_(u'Identity hash'),
                                     blank=True, null=False, max_length=255)
    identity_hashed = models.BooleanField(verbose_name=_(u'Hashed'),
                                          default=True)
    identity_salt = models.CharField(verbose_name=_(u'Identity salt'),
                                     blank=True, null=True, max_length=255)

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-modified', '-awarded']
        verbose_name = _(u'award')
        verbose_name_plural = _(u'awards')

    def __unicode__(self):
        return ugettext(u'{0} awarded to {1}').format(self.badge.title, self.user.username)

    @property
    def revoked(self):
        try:
            Revocation.objects.get(award=self)
            return True
        except Revocation.DoesNotExist:
            return False

    def get_image_url(self):
        return self.badge.image.url

    def get_image_public_url(self):
        return build_absolute_url(reverse('badge_image_email', args=[self.badge.slug, self.user.email]))

    def get_absolute_url(self):
        return build_absolute_url(reverse('assertion', args=[self.uuid]))

    def to_dict(self):
        return {
            'uid': self.uuid,
            'recipient': {
                'identity': self.identity_hash,
                'type': self.identity_type,
                'hashed': self.identity_hashed,
                'salt': self.identity_salt
            },
            'badge': self.badge.get_absolute_url(),
            'verify': {
                'type': 'hosted',
                'url': self.get_absolute_url()
            },
            'issuedOn': self.awarded.strftime('%Y-%m-%d'),
            'image': self.image and build_absolute_url(self.image.url) or '',
            'evidence': self.evidence,
            'expires': self.expires and self.expires.strftime('%Y-%m-%d') or ''
        }


class Issuer(models.Model):
    name = models.CharField(verbose_name=_(u'Issuer name'), blank=False,
                            null=False, max_length=255)
    url = models.CharField(verbose_name=_('Issuer url'), blank=False,
                           null=False, max_length=255)
    description = models.TextField(verbose_name=_(u'Description'), blank=True,
                                   null=True)
    image = models.ImageField(verbose_name=_(u'Logo'), blank=True, null=True,
                              upload_to='badges',
                              validators=[validate_png_image],
                              help_text=_("Issuer logo, it must be png"))
    email = models.CharField(verbose_name=_(u'Issuer email'), blank=True,
                             null=True, max_length=255)

    class Meta:
        verbose_name = _(u'issuer')
        verbose_name_plural = _(u'issuers')

    def __unicode__(self):
        return ugettext(u'Info about issuer')

    def to_dict(self):
        return {
            'name': self.name,
            'image': build_absolute_url(self.image.url),
            'url': self.url,
            'email': self.email,
            'revocationList': build_absolute_url(reverse('revocation_list'))
        }


class Revocation(models.Model):
    award = models.ForeignKey('Award', verbose_name=_(u'Award'), blank=False,
                              null=False, related_name='revocations')
    reason = models.CharField(verbose_name=_(u'Reason for revocation'),
                              blank=False, null=False, max_length=255)

    class Meta:
        verbose_name = _(u'revocation list')
        verbose_name_plural = _(u'revocations list')

    def __unicode__(self):
        return (u'{0} - {1}').format(self.award.uuid, self.reason)

    def to_dict(self):
        return {
            self.award.uuid: self.reason,
        }


class Alignment(models.Model):
    name = models.CharField(verbose_name=_(u'Name'), blank=False, null=False,
                            max_length=255)
    url = models.CharField(verbose_name=_(u'Url'), blank=False, null=False,
                           max_length=255)
    description = models.TextField(verbose_name=_('Description'), blank=True,
                                   null=True)

    class Meta:
        verbose_name = _(u'alignment')
        verbose_name_plural = _('alignments')

    def __unicode__(self):
        return self.name

    def to_dict(self):
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description
        }


class Tag(models.Model):
    name = models.CharField(verbose_name=_(u'Tag name'), blank=False,
                            null=False, max_length=255)

    class Meta:
        verbose_name = _(u'tag')
        verbose_name_plural = _(u'tags')

    def __unicode__(self):
        return self.name


class Criterion(models.Model):
    name = models.CharField(verbose_name=_(u'Criterion name'), blank=False,
                            null=False, max_length=255)
    slug = models.SlugField(verbose_name=_(u'Criterion slug'), blank=False,
                            unique=True, null=False,
                            help_text=_(u'Very short name, for use in URLs and links'))
    description = models.TextField(verbose_name=_(u'Criterion description'),
                                   blank=False, null=False)

    class Meta:
        verbose_name = _(u'criterion')
        verbose_name_plural = _(u'criteria')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return build_absolute_url(reverse('criterion', args=[self.slug]))


@receiver(post_save, sender=Award, dispatch_uid="award_post_save_obi")
def generate_obi_badge(sender, instance, created, **kwargs):
    #print requests.get(settings.BADGES_OBI_BAKER_URL % instance.get_absolute_url())
    pass


@receiver(post_save, sender=Award, dispatch_uid="award_post_save_copy_image")
def copy_image_to_award(sender, instance, created, **kwargs):
    if created:
        im = Image.open(instance.badge.image)
        meta = PngImagePlugin.PngInfo()
        meta.add_text('openbadges', instance.get_absolute_url(), 0)

        with tempfile.NamedTemporaryFile() as tmpfile:
            im.save(tmpfile, "PNG", pnginfo=meta)
            tmpfile.seek(0)
            instance.image.save(str.replace(str(instance.badge.image.name), '.png', '_assertion.png'), File(tmpfile), save=False)
            instance.save()


@receiver(post_save, sender=Award, dispatch_uid="award_post_save_identity")
def save_identity_for_user(sender, instance, created, **kwargs):
    """
    Handler for copying current identity into award,
    for future consistency
    """
    if created:
        instance.identity_hash = instance.user.identity.identity_hash
        instance.identity_type = instance.user.identity.type
        instance.identity_hashed = instance.user.identity.hashed
        instance.identity_salt = instance.user.identity.salt
        instance.save()


@receiver(post_save, sender=get_user_model(), dispatch_uid="user_post_save")
def create_identity_for_user(sender, instance, created, **kwargs):
    """
    Handler for create an identity on new users.
    If email changes, identity_hash must change also
    """
    try:
        instance.identity
        current_identity_hash = instance.identity.identity_hash
        new_candidate_identity_hash = u'sha256$' + hashlib.sha256(instance.email + instance.identity.salt).hexdigest()
        if current_identity_hash != new_candidate_identity_hash:
            salt = uuid.uuid4().hex[:5]
            instance.identity.salt = salt
            instance.identity.identity_hash = u'sha256$' + hashlib.sha256(instance.email + salt).hexdigest()
            instance.identity.save()
    except:
        salt = uuid.uuid4().hex[:5]
        Identity.objects.create(
            user=instance,
            identity_hash=u'sha256$' + hashlib.sha256(instance.email + salt).hexdigest(),
            salt=salt
        )
