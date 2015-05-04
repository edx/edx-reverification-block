"""Stub verification models.

These models track the user's verification status.  The goal is to
approximate the actual implementation in the LMS, while making it
easy to simulate different states in order to test the Reverification XBlock's UI.

"""
from django.db import models


class VerificationStatus(models.Model):
    """Track the user's verification status for a checkpoint in a course. """

    STATUS_CHOICES = (
        ("submitted", "submitted"),
        ("approved", "approved"),
        ("denied", "denied"),
        ("error", "error")
    )

    course_id = models.CharField(max_length=255, db_index=True)
    checkpoint_name = models.CharField(max_length=32)
    user_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    response = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    location_id = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        unique_together = ('course_id', 'checkpoint_name', 'user_id')
        verbose_name = "verification status"
        verbose_name_plural = "verification statuses"


class SkipVerification(models.Model):
    """Track whether the user skipped verification for a course. """
    course_id = models.CharField(max_length=255, db_index=True)
    user_id = models.CharField(max_length=255)
