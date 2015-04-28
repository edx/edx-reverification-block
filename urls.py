"""URLs for local development of the reverification block. """

from django.conf.urls import include, patterns, url
from django.contrib import admin

import workbench.urls
import stub_verification.urls

admin.autodiscover()

urlpatterns = patterns(
    '',

    # Django built-in
    url(r'^admin/', include(admin.site.urls)),

    # Provided by XBlock
    url(r'^/?', include(workbench.urls)),

    # Stub verification service for testing
    url(r'^stub_verification/', include(stub_verification.urls))
)
