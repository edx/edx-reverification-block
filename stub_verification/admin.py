"""Admin interface for stub reverification models.

This makes it easier to test different verification states.
To simulate a response from the verification service,
just flip the status in Django admin!
"""

from django.contrib import admin
from .models import VerificationStatus, SkipVerification, DisableSubmission

admin.site.register(VerificationStatus)
admin.site.register(SkipVerification)
admin.site.register(DisableSubmission)
