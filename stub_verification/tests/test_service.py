"""Tests for the stub verification service. """

import mock

from django.test import TestCase

from stub_verification.service import StubVerificationService
from stub_verification.models import VerificationStatus


class StubVerificationServiceTest(TestCase):
    """Test the stub verification service. """

    COURSE_ID = "edX/DemoX/Demo_Course"
    USER_ID = "bob"
    ITEM_ID = "abcd1234"
    RELATED_ASSESSMENT = "midterm"

    def setUp(self):
        """Create an instance of the stub verification service. """
        super(StubVerificationServiceTest, self).setUp()
        runtime = mock.Mock()
        runtime.user_id = self.USER_ID
        self.service = StubVerificationService()
        self.service.runtime = runtime

    def test_start_verification(self):
        # Initial status should be None
        self.assertIs(self._get_status(), None)

        # Start verification, checking that the URL we get is valid
        url = self.service.start_verification(self.COURSE_ID, self.USER_ID, self.ITEM_ID)
        self.assertContains(self.client.get(url), "Reverify")

        # Simulate submitting photos
        VerificationStatus.objects.create(
            course_id=self.COURSE_ID,
            checkpoint_name=self.RELATED_ASSESSMENT,
            user_id=self.USER_ID,
            status="submitted"
        )

        # Check that the status is updated
        self.assertEqual(self._get_status(), "submitted")

    def test_skip_verification(self):
        # Skip verification
        self.service.skip_verification(self.RELATED_ASSESSMENT, self.USER_ID, self.COURSE_ID)

        # Check that the status is "skipped"
        self.assertEqual(self._get_status(), "skipped")

    def _get_status(self):
        """Retrieve the verification status from the stub service. """
        return self.service.get_status(self.USER_ID, self.COURSE_ID, self.RELATED_ASSESSMENT)
