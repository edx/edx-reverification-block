"""Stub implementation of the verification service.

This implements the same interface as the verification service in
the edx-platform LMS, but it sends the user to a fake reverification flow.
We can test the Reverification XBlock without actually submitting
photos!

"""
from django.core.urlresolvers import reverse

from .models import VerificationStatus, SkipVerification


class StubVerificationService(object):
    """Stub version of the verification service.

    See `verify_student/services.py` for the actual implementation.

    """

    def get_status(self, user_id, course_id, related_assessment_location):
        """Retrieve the user's verification status. """
        if SkipVerification.objects.filter(course_id=course_id, user_id=user_id).exists():
            return u"skipped"

        try:
            return VerificationStatus.objects.get(
                course_id=course_id,
                checkpoint_location=related_assessment_location,
                user_id=user_id
            ).status
        except VerificationStatus.DoesNotExist:
            return None

    def start_verification(self, course_id, related_assessment_location):
        """Return the link to the (fake) reverification flow. """
        return reverse('stub_reverify_flow', args=(
            unicode(course_id),
            unicode(related_assessment_location),
            unicode(self.runtime.user_id)
        ))

    def skip_verification(self, user_id, course_id):
        """Mark that the user has skipped verification for the course. """
        SkipVerification.objects.get_or_create(
            course_id=course_id,
            user_id=user_id,
        )

    def get_attempts(self, user_id, course_id, related_assessment_location):
        """
        Return the number of re-verification attempts of a user for a
        checkpoint.
        """
        return VerificationStatus.objects.filter(
            user_id=user_id,
            course_id=course_id,
            checkpoint_location=related_assessment_location,
            status="submitted"
        ).count()
