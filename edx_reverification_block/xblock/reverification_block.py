"""An XBlock for in-course reverification. """

import logging

from django.template import Context, Template

import pkg_resources
from xblock.core import XBlock
from xblock.fields import Scope, String, Boolean, Integer
from xblock.fragment import Fragment


log = logging.getLogger(__name__)
CHECKPOINT_NAME = "Assessment 1"


def load(path):
    """Load a resource from the package. """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


@XBlock.wants("reverification")
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

    @property
    def course_id(self):
        return unicode(self.xmodule_runtime.course_id)  # pylint:disable=E1101

    @property
    def in_studio_preview(self):
        """
        Check whether we are in Studio preview mode.

        Returns:
            bool

        """
        # When we're running in Studio Preview mode, the XBlock won't provide us with a user ID.
        # (Note that `self.xmodule_runtime` will still provide an anonymous
        # student ID, so we can't rely on that)
        return self.scope_ids.user_id is None

    @property
    def is_released(self):
        """
        Check if a xblock has been released.

        Returns:
            bool
        """
        # By default, assume that we're published, in case the runtime doesn't support publish date.
        return self.runtime.modulestore.has_published_version(self) if hasattr(self.runtime, 'modulestore') else True

    def student_view(self, context=None):
        """Student view to render the re-verification link

        This will render the url to display in lms along with marketing text.

        """

        # Assume that if service is not available then it is
        # in studio_preview because service are defined in LMS
        if not self.runtime.service(self, "reverification"):
            return self.get_studio_preview()
        course_id = self.get_course_id()
        item_id = unicode(self.scope_ids.usage_id)
        related_assessment = self.related_assessment
        user_id = unicode(self.scope_ids.user_id)

        if not self.runtime.service(self, "reverification"):
            return Fragment(unicode("No service defined in this runtime"))
        verification_status = self.runtime.service(self, "reverification").get_status(
            user_id=user_id,
            course_id=course_id,
            related_assessment=related_assessment
        )
        if verification_status:
            # TODO: What message will be displayed to user if it is already has any status?
            frag = Fragment(unicode(verification_status))
            return frag
        reverification_link = self.runtime.service(self, "reverification").start_verification(
            course_id=course_id,
            related_assessment=related_assessment,
            item_id=item_id
        )
        org = self.get_org()
        html_str = pkg_resources.resource_string(__name__, "static/html/reverification.html")
        frag = Fragment(unicode(html_str).format(
            reverification_link=reverification_link,
            checkpoint=self.related_assessment,
            course_id=unicode(course_id),
            user_id=user_id
        ))

        frag.add_javascript(_resource("static/js/skip_reverification.js"))
        frag.initialize_js('SkipReverifcation')
        return frag

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
                render_template(
                    'static/html/checkpoint_edit.html',
                    context
                )
            )
            fragment.add_javascript(_resource("static/js/checkpoint_edit.js"))
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
        self.related_assessment = data.get('related_assessment')
        self.attempts = data.get('attempts')
        self.is_configured = True

        return {'result': 'success'}

    @staticmethod
    def workbench_scenarios():
        return [
            (
                "Reverification Block",
                load("static/xml/reverification_block_example.xml")
            ),
        ]

    @XBlock.json_handler
    def skip_verification(self, data, suffix=''):
        """
        Called when submitting the form in Studio for skipping verification.
        """
        checkpoint = data.get("checkpoint")
        user_id = data.get("user_id")
        course_id = data.get("course_id")
        self.runtime.service(self, "reverification").skip_verification(
            checkpoint,
            user_id,
            course_id
        )

        return {'result': 'success'}

    def get_course_id(self):
        """ Return the course_id
        """
        # This is not the real way course_ids should work, but this is a
        # temporary expediency for LMS integration
        return self.course_id if hasattr(self, "xmodule_runtime") else "edX/Enchantment_101/April_1"

    def get_org(self):
        """ Return the org

        """
        # This is not the real way getting the org should work, but this is a
        # temporary expediency for LMS integration
        return self.xmodule_runtime.course_id.org if hasattr(self, "xmodule_runtime") else "edX ORG"

    def get_studio_preview(self):
        """ Return rendered studio view """
        context = {
            "is_configured": self.is_configured,
            "view_container_link": "/container/" + unicode(self.scope_ids.usage_id)
        }

        fragment = Fragment()
        fragment.add_content(
            render_template(
                'static/html/studio_preview.html',
                context
            )
        )

        return fragment


def _resource(path):  # pragma: NO COVER
    """
    Handy helper for getting resources from our kit.
    """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


def load_resource(resource_path):  # pragma: NO COVER
    """
    Gets the content of a resource
    """
    resource_content = pkg_resources.resource_string(__name__, resource_path)
    return unicode(resource_content)


def render_template(template_path, context=None):  # pragma: NO COVER
    """
    Evaluate a template by resource path, applying the provided context.
    """
    if context is None:
        context = {}

    template_str = load_resource(template_path)
    template = Template(template_str)
    return template.render(Context(context))
