# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


if settings.BADGES_BASE_URL is None:
    raise ImproperlyConfigured("ERROR: Please set BADGES_BASE_URL in your settings file")
