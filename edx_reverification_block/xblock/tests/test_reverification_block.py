"""
Tests the edX Reverification XBlock functionality.
"""
import json
import os
from mock import patch
import ddt

from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from workbench.test_utils import XBlockHandlerTestCaseMixin, scenario

from stub_verification.models import VerificationStatus


TESTS_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestStudioPreview(XBlockHandlerTestCaseMixin, TestCase):
    """Test the display of the reverification block in Studio Preview. """

    # Simulate that we are in Studio preview by un-installing the verification service
    @patch.dict(settings.WORKBENCH['services'], {}, clear=True)
    def setUp(self):
        super(TestStudioPreview, self).setUp()

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_preview(self, xblock):
        # Test that creating Reverification XBlock for the first time user gets
        # message to configure it
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue('edx-reverification-block' in xblock_fragment.body_html())
        self.assertIn('This checkpoint is not associated with an assessment yet.', xblock_fragment.body_html())

        # Now set 'related_assessment' and 'attempts' fields and check that
        # values of these fields set correctly and also test that configuration
        # message does not appear
        data = json.dumps({'related_assessment': 'FinalExam', 'attempts': 5})
        resp = self.request(xblock, 'studio_submit', data, response_format='json')
        self.assertTrue(resp.get('result'))
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertIn('click Preview or View Live', xblock_fragment.body_html())


@ddt.ddt
class TestStudentView(XBlockHandlerTestCaseMixin, TestCase):
    """Test the display of the reverification block in an LMS. """

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_student_view_ready_to_reverify(self, xblock):
        xblock_fragment = self.runtime.render(xblock, "student_view")
        html = xblock_fragment.body_html()
        self.assertIn('Re-Verify Now', html)

        reverify_url = reverse('stub_reverify_flow', args=(
            xblock.course_id,
            xblock.scope_ids.usage_id,
            xblock.related_assessment,
            xblock.scope_ids.user_id),
        )
        self.assertIn(reverify_url, html)

    @ddt.data("submitted", "approved", "denied", "error")
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_student_view_reverification_status(self, xblock, status):
        # Simulate the verification status
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_name=xblock.related_assessment,
            user_id=xblock.scope_ids.user_id,
            status=status
        )

        # Check that the status is displayed correctly
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertIn(status, xblock_fragment.body_html())
