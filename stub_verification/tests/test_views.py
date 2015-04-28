"""Tests for fake reverification flow views. """

from django.test import TestCase
from django.core.urlresolvers import reverse

from stub_verification.models import VerificationStatus


class StubReverificationViewsTest(TestCase):
    """Test the fake reverification flow views. """

    COURSE_ID = "edX/DemoX/Demo_Course"
    RELATED_ASSESSMENT = "midterm"
    ITEM_ID = "abcd1234"
    USER_ID = "bob"

    def test_stub_reverify(self):
        # Enter the fake reverification flow
        url = reverse("stub_reverify_flow", args=(
            self.COURSE_ID,
            self.RELATED_ASSESSMENT,
            self.ITEM_ID,
            self.USER_ID
        ))
        self.assertContains(self.client.get(url), "Reverify")

        # Simulate submitting a photo
        url = reverse('stub_submit_reverification_photos')
        resp = self.client.post(url, {
            'course_id': self.COURSE_ID,
            'checkpoint_name': self.RELATED_ASSESSMENT,
            'user_id': self.USER_ID,
        })
        self.assertContains(resp, "Photos Submitted")

        # Check that the status has been updated
        status = VerificationStatus.objects.get(
            course_id=self.COURSE_ID,
            checkpoint_name=self.RELATED_ASSESSMENT,
            user_id=self.USER_ID
        )
        self.assertEqual(status.status, "submitted")
