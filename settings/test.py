"""Test-specific settings for the reverification block. """

# Inherit from base settings
from .base import *     # pylint:disable=W0614,W0401

TEST_APPS = (
    'edx_reverification_block',
    'edx_reverification_block.xblock',
    'stub_verification',
)

# Configure nose
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=' + ",".join(TEST_APPS),
    '--cover-branches',
    '--cover-erase',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_reverificationdb',
        'TEST_NAME': 'test_reverificationdb',
    },
}

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Install test-specific Django apps
INSTALLED_APPS += ('stub_verification', 'django_nose')

WORKBENCH['services'] = {
    'reverification': 'stub_verification.service.StubVerificationService'
}

# Silence cache key warnings
# https://docs.djangoproject.com/en/1.4/topics/cache/#cache-key-warnings
import warnings
from django.core.cache import CacheKeyWarning
warnings.simplefilter("ignore", CacheKeyWarning)
