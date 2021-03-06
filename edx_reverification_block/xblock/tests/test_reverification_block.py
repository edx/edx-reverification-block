"""
Tests the edX Reverification XBlock functionality.
"""

import datetime
import json
import os
import pytz

import ddt
from mock import Mock, PropertyMock, patch

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from workbench.test_utils import XBlockHandlerTestCaseMixin, scenario
from stub_verification.models import VerificationStatus


TESTS_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestStudioPreview(XBlockHandlerTestCaseMixin, TestCase):
    """
    Test the display of the Reverification XBlock in Studio Preview.
    """
    # simulate that we are in Studio preview by un-installing the verification
    # service
    @patch.dict(settings.WORKBENCH['services'], {}, clear=True)
    def setUp(self):
        super(TestStudioPreview, self).setUp()

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_preview(self, xblock):
        """
        Test Reverification XBlock preview in Studio.
        """
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue('edx-reverification-block' in xblock_fragment.body_html())

        # Now set 'related_assessment' and 'attempts' fields and check that
        # values of these fields set correctly and also test that configuration
        # message does not appear
        data = json.dumps({'related_assessment': 'FinalExam', 'attempts': 5, 'grace_period': 0})
        resp = self.request(xblock, 'studio_submit', data, response_format='json')
        self.assertTrue(resp.get('result'))
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertIn('select View Live Version or Preview', xblock_fragment.body_html())

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_preview_validation(self, xblock):
        """
        Test reverification block validation in Studio.
        """
        # Test that on creating Reverification XBlock for the first time and
        # calling its 'validate' method gives warning message to user to
        # configure it.
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue('edx-reverification-block' in xblock_fragment.body_html())

        validation_messages = xblock.validate()
        self.assertEqual(len(validation_messages.to_json().get('messages')), 1)
        self.assertEqual(validation_messages.to_json().get('messages')[0].get('type'), 'warning')
        self.assertIn(
            "This verification checkpoint does not have a name.",
            validation_messages.to_json().get('messages')[0].get('text')
        )

        # now set fields on Reverification XBlock and check that 'validate'
        # method does not give warning message to configure it
        data = json.dumps({'related_assessment': 'FinalExam', 'attempts': 5, 'grace_period': 1})
        resp = self.request(xblock, 'studio_submit', data, response_format='json')
        self.assertTrue(resp.get('result'))
        validation_messages = xblock.validate()
        self.assertEqual(len(validation_messages.to_json().get('messages')), 0)


@ddt.ddt
class TestStudioEditing(XBlockHandlerTestCaseMixin, TestCase):
    """
    Test editing the Reverification XBlock in Studio.
    """

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_editing_view(self, xblock):
        xblock_fragment = self.runtime.render(xblock, "studio_view")
        editing_html = xblock_fragment.body_html()

        self.assertIn("Checkpoint Name", editing_html)
        self.assertIn(xblock.related_assessment, editing_html)
        self.assertIn("attempts", editing_html)
        self.assertIn(unicode(xblock.attempts), editing_html)

    @ddt.data(
        {'attempts': 5, 'related_assessment': 'final_exam', 'grace_period': 5},
        {'attempts': 5, 'related_assessment': u'\u2603', 'grace_period': 0},
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
        # Negative grace_period
        {'grace_period': -1, 'related_assessment': 'final_exam', 'attempts': 1},
        # Wrong type
        {'grace_period': None, 'related_assessment': 'final_exam', 'attempts': 1},
        {'grace_period': '1.5', 'related_assessment': 'final_exam', 'attempts': 1},
        {'grace_period': 'testing', 'related_assessment': 'final_exam', 'attempts': 1},
    )
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_studio_submit_error(self, xblock, payload):
        response = self.request(xblock, "studio_submit", json.dumps(payload), response_format="json")
        self.assertEqual(response['result'], 'error')

        # The XBlock should still have the default values
        self.assertEqual(xblock.related_assessment, "Assessment 1")
        self.assertEqual(xblock.attempts, 0)
        self.assertFalse(xblock.is_configured)
        self.assertEqual(xblock.grace_period, 5)


@ddt.ddt
class TestStudentView(XBlockHandlerTestCaseMixin, TestCase):
    """Test the display of the reverification block in an LMS. """

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_student_view_ready_to_reverify(self, xblock):
        self._assert_in_student_view(xblock, "Verify Your Identity")

        reverify_url = reverse('stub_reverify_flow', args=(
            xblock.course_id,
            xblock.scope_ids.usage_id,
            xblock.scope_ids.user_id),
        )
        self._assert_in_student_view(xblock, reverify_url)

    @ddt.data(
        ("submitted", "submitted"),
        ("approved", "approved"),
        ("denied", "unsuccessful"),
        ("error", "error"),
        ("unexpected", "error"),
        ("not-verified", "reverify-not-verified"),
    )
    @ddt.unpack
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_student_view_reverification_status(self, xblock, status, expected_content):
        # Simulate the verification status
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_location=unicode(xblock.scope_ids.usage_id),
            user_id=xblock.scope_ids.user_id,
            status=status
        )

        # Check that the status is displayed correctly
        self._assert_in_student_view(xblock, expected_content)

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_skip_reverification(self, xblock):
        # Skip verification
        payload = {
            'user_id': xblock.scope_ids.user_id,
            'course_id': xblock.course_id,
            'checkpoint_location': unicode(xblock.scope_ids.usage_id)
        }
        response = self.request(xblock, "skip_verification", json.dumps(payload), response_format="json")
        self.assertTrue(response['success'])

        # Reloading the student view, we should see that we've skipped
        self._assert_in_student_view(xblock, "skipped")

    @ddt.data(0, 1, 2, 3, 4)
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_grace_period_with_expired_due_date(self, xblock, grace_days):
        # Verify that user can view the icrv for next 5 days even due data is expired.
        # If due date is 1st Jan then user can view icrv till 5th Jan.

        xblock.due = (datetime.datetime.today()-datetime.timedelta(grace_days)).replace(tzinfo=pytz.UTC)
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_location=unicode(xblock.scope_ids.usage_id),
            user_id=xblock.scope_ids.user_id,
            status="not-verified"
        )

        # Check that the status is displayed correctly
        self._assert_in_student_view(xblock, "reverify-not-verified")

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_closed_reverification(self, xblock):
        # Check closed status when xblock due date passed
        xblock.due = (datetime.datetime.today()-datetime.timedelta(5)).replace(tzinfo=pytz.UTC)
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_location=unicode(xblock.scope_ids.usage_id),
            user_id=xblock.scope_ids.user_id,
            status="not-verified"
        )

        # Check that the status is displayed correctly
        self._assert_in_student_view(xblock, "closed")

    @ddt.data(
        ("submitted", "submitted"),
        ("approved", "approved"),
        ("denied", "unsuccessful"),
    )
    @ddt.unpack
    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_precedence_reverification_status(self, xblock, status, expected_content):
        # Check reverification statuses that have precedence over closed status
        xblock.due = (datetime.datetime.today()-datetime.timedelta(1)).replace(tzinfo=pytz.UTC)
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_location=unicode(xblock.scope_ids.usage_id),
            user_id=xblock.scope_ids.user_id,
            status=status
        )

        # Check that the status is displayed correctly
        self._assert_in_student_view(xblock, expected_content)

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml', user_id='bob')
    def test_render_support_email(self, xblock):
        # Simulate an error verification status
        VerificationStatus.objects.create(
            course_id=xblock.course_id,
            checkpoint_location=unicode(xblock.scope_ids.usage_id),
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
