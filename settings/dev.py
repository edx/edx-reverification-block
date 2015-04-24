"""Reverification block settings for local development. """

# Inherit from base settings
from .base import *  # pylint: disable=W0614,W0401

INSTALLED_APPS += ('stub_verification',)

WORKBENCH['services'] = {
    'reverification': 'stub_verification.service.StubVerificationService'
}

