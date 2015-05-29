"""An XBlock for in-course reverification. """

import datetime
import logging
import pytz

from django.template import Context, Template

import pkg_resources
from xblock.core import XBlock
from xblock.fields import Scope, String, Boolean, Integer, DateTime
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage


log = logging.getLogger(__name__)
CHECKPOINT_NAME = "Assessment 1"
CREDIT_REQUIREMENT_NAMESPACE = "reverification"


@XBlock.wants("reverification")
@XBlock.needs("i18n")
class ReverificationBlock(XBlock):
    """An XBlock for in-course reverification. """

    # Fields
    display_name = String(
        scope=Scope.settings,
        default='Re-Verification Checkpoint',
        help="This name appears in the horizontal navigation at the top of "
             "the page."
    )

    attempts = Integer(
        display_name="Verification Attempts",
        default=0,
        scope=Scope.settings,
        help="This is the number of attempts that students are permitted to "
             "get a valid re-verification."
    )

    related_assessment = String(
        display_name="Related Assessment",
        scope=Scope.content,
        default=CHECKPOINT_NAME,
        help="This name will allow you to distinguish distinct checkpoints "
             "that show up in the reporting about student verification status."
    )

    is_configured = Boolean(
        scope=Scope.content,
        default=False,
        help="Reverification XBlock is configured or not."
    )

    due = DateTime(
        display_name="Related Assessment due date",
        scope=Scope.settings,
        default=None,
        help="ISO-8601 formatted string representing the due date of this related assessment."
    )

    TEMPLATE_FOR_STATUS = {
        "skipped": "static/html/skipped.html",
        "submitted": "static/html/submitted.html",
        "approved": "static/html/approved.html",
        "closed": "static/html/closed.html",
        "denied": "static/html/reverification.html",
        "error": "static/html/reverification.html",
    }

    # Status values that allow reverification
    ALLOW_REVERIFICATION_STATUSES = set([None, "denied", "error"])

    # TODO: there isn't currently a way to get this from Django settings
    # in the edx-platform LMS.  We're hard-coding this for now,
    # but long-term it probably makes sense to move this into a service
    # provided by the runtime.
    SUPPORT_EMAIL = "support@edx.org"

    @property
    def course_id(self):
        """Retrieve the course ID.

        Returns:
            CourseKey

        """
        # Note: this relies on an unsupported API (xmodule_runtime),
        # which is currently the only way to retrieve the course ID
        # from the LMS.  If the course ID is not available,
        # we use a default course ID for testing (usually in workbench).
        return (
            unicode(self.xmodule_runtime.course_id)
            if hasattr(self, "xmodule_runtime")
            else "edX/Enchantment_101/April_1"
        )

    def student_view(self, context=None):
        """Student view to render the re-verification link

        This will render the url to display in lms along with marketing text.

        """
        # Assume that if service is not available then it is
        # in studio_preview because service are defined in LMS
        if not self.runtime.service(self, "reverification"):
            return self.get_studio_preview()

        course_id = self.course_id
        item_id = unicode(self.scope_ids.usage_id)
        related_assessment = self.related_assessment
        user_id = unicode(self.scope_ids.user_id)
        fragment = Fragment()
        if self.due and self.due < datetime.datetime.today().replace(tzinfo=pytz.UTC):
            verification_status = 'closed'
        else:
            verification_status = self.runtime.service(self, "reverification").get_status(
                user_id=user_id,
                course_id=course_id,
                related_assessment=related_assessment
            )

        user_attempts = self.runtime.service(self, "reverification").get_attempts(
            user_id=user_id,
            course_id=course_id,
            related_assessment=related_assessment,
            location_id=item_id
        )
        remaining_attempts = self.remaining_attempts(user_attempts)

        context = {
            'status': verification_status,
            'remaining_attempts': remaining_attempts,
            'support_email_link': '<a href="mailto:{email}">{email}</a>'.format(email=self.SUPPORT_EMAIL),
        }

        if verification_status in self.ALLOW_REVERIFICATION_STATUSES:
            reverification_link = self.runtime.service(self, "reverification").start_verification(
                course_id=course_id,
                related_assessment=related_assessment,
                item_id=item_id
            )
            context['reverification_link'] = reverification_link

        if verification_status:
            status_template = self.TEMPLATE_FOR_STATUS.get(verification_status)
            if status_template is None:
                log.error(
                    (
                        u"Unexpected status %s returned from the verification service "
                        u"for course %s at checkpoint %s and location %s for user %s"
                    ),
                    verification_status, course_id, related_assessment, item_id, user_id
                )
                status_template = self.TEMPLATE_FOR_STATUS["error"]

            html = self._render_template(status_template, context)
            fragment.add_content(html)

        else:
            html = self._render_template("static/html/reverification.html", context)
            fragment.add_content(html)

        # Add JS and CSS resources
        fragment.add_javascript(self._resource("static/js/reverification.js"))
        fragment.initialize_js('Reverification')
        fragment.add_css(self._resource(self.student_view_css_path()))

        return fragment

    def student_view_css_path(self):
        """Retrieve the CSS path for the student view based on the language text-direction. """
        i18n_service = self.runtime.service(self, 'i18n')
        if hasattr(i18n_service, 'get_language_bidi') and i18n_service.get_language_bidi():
            return "static/reverification-rtl.min.css"
        else:
            return "static/reverification-ltr.min.css"

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        try:
            cls = type(self)

            def none_to_empty(data):
                """
                Return empty string if data is None else return data.
                """
                return data if data is not None else ''

            edit_fields = (
                (field, none_to_empty(getattr(self, field.name)), validator)
                for field, validator in (
                    (cls.related_assessment, 'string'),
                    (cls.attempts, 'number'))
            )

            context = {
                'fields': edit_fields
            }
            fragment = Fragment()
            fragment.add_content(
                self._render_template(
                    'static/html/checkpoint_edit.html',
                    context
                )
            )
            fragment.add_javascript(self._resource("static/js/checkpoint_edit.js"))
            fragment.initialize_js('CheckpointEditBlock')
            return fragment
        except:  # pragma: NO COVER
            log.error("Error creating fragment for studio edit view", exc_info=True)
            raise

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        related_assessment = data.get('related_assessment')
        attempts = data.get('attempts')

        # Paranoid checks of the parameters we receive
        # None of these conditions should occur, because the front-end
        # validation should catch it.
        if related_assessment is None:
            log.error("related_assessment field not found in request")
        elif not isinstance(related_assessment, basestring):
            log.error("related_assessment has type %s, but we expected a string", type(data['related_assessment']))
        elif len(related_assessment) == 0:
            log.error("related_assessment cannot be an empty string")
        elif attempts is None:
            log.error("attempts field not found in request")
        elif not isinstance(attempts, int):
            log.error("attempts field was %s, but we expected an integer", data['attempts'])
        elif attempts < 0:
            log.error("attempts field cannot be negative")
        else:
            self.related_assessment = data.get('related_assessment')
            self.attempts = data.get('attempts')
            self.is_configured = True

            return {'result': 'success'}

        # If we got to this point, an error must have occurred
        return {'result': 'error'}

    @staticmethod
    def workbench_scenarios():
        return [
            (
                "Reverification Block",
                ReverificationBlock._resource("static/xml/reverification_block_example.xml")
            ),
        ]

    @XBlock.json_handler
    def skip_verification(self, data, suffix=''):
        """
        Called when submitting the form for skipping verification.
        """
        self.runtime.service(self, "reverification").skip_verification(
            self.related_assessment,
            self.scope_ids.user_id,
            self.course_id,
        )
        return {'success': True}

    def get_studio_preview(self):
        """ Return rendered studio view """
        context = {
            "view_container_link": "/container/" + unicode(self.scope_ids.usage_id)
        }

        fragment = Fragment()
        fragment.add_content(
            self._render_template(
                'static/html/studio_preview.html',
                context
            )
        )

        return fragment

    @staticmethod
    def _resource(path):
        """
        Handy helper for getting resources from our kit.
        """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @staticmethod
    def _render_template(template_path, context):
        """
        Evaluate a template by resource path, applying the provided context.
        """
        template_str = ReverificationBlock._resource(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    @property
    def _(self):
        i18nService = self.runtime.service(self, 'i18n')
        return i18nService.ugettext

    def validate(self):
        """
        Basic validation for this XBlock.
        """
        reverification_block_validation = super(ReverificationBlock, self).validate()

        if not self.is_configured:
            reverification_block_validation.add(
                ValidationMessage(
                    ValidationMessage.WARNING,
                    self._(
                        u"This checkpoint is not associated with an assessment yet. "
                        u"Please select an Assessment."
                    )
                )
            )
        return reverification_block_validation

    def remaining_attempts(self, user_attempts):
        """
        Get the number of remaining attempts against a user for a
        Reverification XBlock.

        Args:
            user_attempts(int): Number of re-verification attempts made by user

        Returns:
            Integer: Number of attempts against a user for a Reverification
            XBlock
        """
        # check if the 'attempts' field is not set i.e, 0 then user will get
        # one attempt
        if self.attempts == 0 and user_attempts == 0:
            return 1

        # check if 'attempts' field is set for Reverification XBlock and the
        # number of re-verification attempts made by the user exceeds that
        # number then user has no remaining attempts
        if self.attempts > 0 and (user_attempts >= self.attempts):
            return 0

        return self.attempts - user_attempts

    def is_course_credit_requirement(self):
        """ It tells that the xblock is a credit course requirement """
        return True

    def get_credit_requirement_namespace(self):
        """ Returns the namespace used for this credit requirements """
        return CREDIT_REQUIREMENT_NAMESPACE

    def get_credit_requirement_name(self):
        """ Returns the names used for this credit requirements """
        return unicode(self.scope_ids.usage_id)
