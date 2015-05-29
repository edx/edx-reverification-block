"""Tests for fake reverification flow views. """

from django.test import TestCase
from django.core.urlresolvers import reverse

from stub_verification.models import VerificationStatus


class StubReverificationViewsTest(TestCase):
    """Test the fake reverification flow views. """

    USER_ID = "bob"
    COURSE_ID = "edX/DemoX/Demo_Course"
    ITEM_ID = u"i4x://edX/DemoX/edx-reverification-block/checkpoint_location"

    def test_stub_reverify(self):
        # Enter the fake reverification flow
        url = reverse("stub_reverify_flow", args=(
            self.COURSE_ID,
            self.ITEM_ID,
            self.USER_ID
        ))
        self.assertContains(self.client.get(url), "Reverify")

        # Simulate submitting a photo
        url = reverse('stub_submit_reverification_photos')
        resp = self.client.post(url, {
            'course_id': self.COURSE_ID,
            'checkpoint_location': self.ITEM_ID,
            'user_id': self.USER_ID,
        })
        self.assertContains(resp, "Photos Submitted")

        # Check that the status has been updated
        status = VerificationStatus.objects.get(
            course_id=self.COURSE_ID,
            checkpoint_location=self.ITEM_ID,
            user_id=self.USER_ID
        )
        self.assertEqual(status.status, "submitted")
