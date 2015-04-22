"""
Tests the edX Reverification XBlock functionality.
"""
import json
import os
from mock import Mock

from django.test import TestCase

from workbench.test_utils import XBlockHandlerTestCaseMixin, scenario


TESTS_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestReverificationBlock(XBlockHandlerTestCaseMixin, TestCase):

    @scenario(TESTS_BASE_DIR + '/data/basic_scenario.xml')
    def test_load_student_view(self, xblock):
        """
        Reverification XBlock basic test for verifying that the user gets some
        HTML.
        """
        # Test that creating Reverification XBlock for the first time user gets
        # message to configure it
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue('edx-reverification-block' in xblock_fragment.body_html())
        self.assertTrue('This checkpoint is not associated with an assessment yet.' in xblock_fragment.body_html())

        # Now set 'related_assessment' and 'attempts' fields and check that
        # values of these fields set correctly and also test that configuration
        # message does not appear
        data = json.dumps({'related_assessment': 'FinalExam', 'attempts': 5})
        resp = self.request(xblock, 'studio_submit', data, response_format='json')
        self.assertTrue(resp.get('result'))
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertFalse('This checkpoint is not associated with an assessment yet.' in xblock_fragment.body_html())

        # Configure a dummy "ReverificationService" with dummy responses
        DummyReverificationService = Mock()
        dummy_link = '/reverify/COURSE_ID/CHECKPOINT_NAME/COURSEWARE_LOCATION'
        attrs = {'get_status.return_value': None, 'start_verification.return_value': dummy_link}
        DummyReverificationService.configure_mock(**attrs)
        self.runtime._services['reverification'] = DummyReverificationService

        # Case #1: 'VerificationStatus' of user is None
        # Test that verification link is present in response
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue(dummy_link in xblock_fragment.body_html())

        # Case #2: 'VerificationStatus' of user is 'submitted'
        # Test that verification status is present in response
        DummyReverificationService.get_status.return_value = "submitted"
        xblock_fragment = self.runtime.render(xblock, "student_view")
        self.assertTrue('submitted' in xblock_fragment.body_html())
