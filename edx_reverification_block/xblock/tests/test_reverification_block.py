"""
Tests the edX Reverification XBlock functionality.
"""
import json
import os
from mock import Mock, PropertyMock, patch
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
        # Test that creating Reverification XBlock
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue('edx-reverification-block' in xblock_fragment.body_html())

        # Now set 'related_assessment' and 'attempts' fields and check that
        # values of these fields set correctly and also test that configuration
        # message does not appear
        data = json.dumps({'related_assessment': 'FinalExam', 'attempts': 5})
        resp = self.request(xblock, 'studio_submit', data, response_format='json')
        self.assertTrue(resp.get('result'))
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertIn('click Preview or View Live', xblock_fragment.body_html())

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_preview_validation(self, xblock):
        # Test that on creating Reverification XBlock for the first time and
        # calling its 'validate' method gives warning message to user to
        # configure it.
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue('edx-reverification-block' in xblock_fragment.body_html())

        validation_messages = xblock.validate()
        self.assertEqual(len(validation_messages.to_json().get('messages')), 1)
        self.assertEqual(validation_messages.to_json().get('messages')[0].get('type'), 'warning')
        self.assertIn(
            "This checkpoint is not associated with an assessment yet. Please select an Assessment.",
            validation_messages.to_json().get('messages')[0].get('text')
        )

        # now set fields on Reverification XBlock and check that 'validate'
        # method does not give warning message to configure it
        data = json.dumps({'related_assessment': 'FinalExam', 'attempts': 5})
        resp = self.request(xblock, 'studio_submit', data, response_format='json')
        self.assertTrue(resp.get('result'))
        validation_messages = xblock.validate()
        self.assertEqual(len(validation_messages.to_json().get('messages')), 0)


@ddt.ddt
class TestStudioEditing(XBlockHandlerTestCaseMixin, TestCase):
    """Test editing the XBlock in Studio. """

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_editing_view(self, xblock):
        xblock_fragment = self.runtime.render(xblock, "studio_view")
        editing_html = xblock_fragment.body_html()

        self.assertIn("Related Assessment", editing_html)
        self.assertIn(xblock.related_assessment, editing_html)
        self.assertIn("Attempts", editing_html)
        self.assertIn(unicode(xblock.attempts), editing_html)

    @ddt.data(
        {'attempts': 5, 'related_assessment': 'final_exam'},
        {'attempts': 5, 'related_assessment': u'\u2603'},
    )
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_submit_success(self, xblock, payload):
        # Initially, the XBlock should not be configured
        self.assertFalse(xblock.is_configured)

        response = self.request(xblock, "studio_submit", json.dumps(payload), response_format="json")
        self.assertEqual(response['result'], 'success')

        # Check that the XBlock was updated correctly
        self.assertEqual(xblock.related_assessment, payload['related_assessment'])
        self.assertEqual(xblock.attempts, payload['attempts'])
        self.assertTrue(xblock.is_configured)

    @ddt.data(
        # Missing required fields
        {},
        {'attempts': 5},
        {'related_assessment': 'final_exam'},

        # Negative attempts
        {'attempts': -1, 'related_assessment': 'final_exam'},

        # Empty related assessment string
        {'attempts': 1, 'related_assessment': ''},

        # Wrong type
        {'attempts': 'foo', 'related_assessment': 'final_exam'},
        {'attempts': '45.67', 'related_assessment': 'final_exam'},
        {'attempts': 1, 'related_assessment': 5},
    )
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_submit_error(self, xblock, payload):
        response = self.request(xblock, "studio_submit", json.dumps(payload), response_format="json")
        self.assertEqual(response['result'], 'error')

        # The XBlock should still have the default values
        self.assertEqual(xblock.related_assessment, "Assessment 1")
        self.assertEqual(xblock.attempts, 0)
        self.assertFalse(xblock.is_configured)


@ddt.ddt
class TestStudentView(XBlockHandlerTestCaseMixin, TestCase):
    """Test the display of the reverification block in an LMS. """

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_student_view_ready_to_reverify(self, xblock):
        self._assert_in_student_view(xblock, "Verify Your Identity")

        reverify_url = reverse('stub_reverify_flow', args=(
            xblock.course_id,
            xblock.scope_ids.usage_id,
            xblock.related_assessment,
            xblock.scope_ids.user_id),
        )
        self._assert_in_student_view(xblock, reverify_url)

    @ddt.data(
        ("submitted", "submitted"),
        ("approved", "approved"),
        ("denied", "unsuccessful"),
        ("error", "error"),
        ("unexpected", "error"),
    )
    @ddt.unpack
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_student_view_reverification_status(self, xblock, status, expected_content):
        # Simulate the verification status
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_name=xblock.related_assessment,
            user_id=xblock.scope_ids.user_id,
            status=status
        )

        # Check that the status is displayed correctly
        self._assert_in_student_view(xblock, expected_content)

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_skip_reverification(self, xblock):
        # Skip verification
        response = self.request(xblock, "skip_verification", json.dumps(""), response_format="json")
        self.assertTrue(response['success'])

        # Reloading the student view, we should see that we've skipped
        self._assert_in_student_view(xblock, "skipped")

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_render_support_email(self, xblock):
        # Simulate an error verification status
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_name=xblock.related_assessment,
            user_id=xblock.scope_ids.user_id,
            status="error"
        )

        # Check that the support email is displayed correctly
        expected_content = '<a href="mailto:support@edx.org">support@edx.org</a>'
        self._assert_in_student_view(xblock, expected_content)

    @ddt.data('ltr', 'rtl')
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_rtl_support(self, xblock, text_direction):
        bidi = (text_direction == 'rtl')

        # Configure "i18n_service" of xblock runtime with dummy response
        i18nService = Mock()
        attrs = {'get_language_bidi.return_value': bidi}
        i18nService.configure_mock(**attrs)
        xblock.runtime._services['i18n'] = i18nService

        css_path = xblock.student_view_css_path()
        self.assertEqual(css_path, "static/reverification-{dir}.min.css".format(dir=text_direction))

    def _assert_in_student_view(self, xblock, expected_content):
        """Check that the student view contains the expected content. """
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertIn(expected_content, xblock_fragment.body_html())
