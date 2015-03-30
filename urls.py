"""URLs for local development of the reverification block. """

from django.conf import settings
from django.conf.urls import include, patterns, url
from django.contrib import admin

import workbench.urls

admin.autodiscover()

urlpatterns = patterns(
    '',

    # Django built-in
    url(r'^admin/', include(admin.site.urls)),

    # Provided by XBlock
    url(r'^/?', include(workbench.urls)),
)
