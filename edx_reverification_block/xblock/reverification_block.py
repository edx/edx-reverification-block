"""An XBlock for in-course reverification. """

import pkg_resources
from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

CHECKPOINT_NAME = "Final Exam"


def load(path):
    """Load a resource from the package. """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


@XBlock.wants("reverification")
class ReverificationBlock(XBlock):
    """An XBlock for in-course reverification. """

    # Fields
    checkpoint_name = String(
        scope=Scope.content,
        default=CHECKPOINT_NAME,
        help="Checkpoint Name"
    )

    @property
    def course_id(self):
        return unicode(self.xmodule_runtime.course_id)  # pylint:disable=E1101

    def student_view(self, context=None):
        """Student view to render the re-verification link

        This will render the url to display in lms along with marketing text.

        """
        course_id = self.get_course_id()
        item_id = unicode(self.scope_ids.usage_id)
        checkpoint_name = CHECKPOINT_NAME
        user_id = unicode(self.scope_ids.user_id)
        if not self.runtime.service(self, "reverification"):
            return Fragment(unicode("No service defined"))
        is_published = self.runtime.service(self, "reverification").is_published(self)
        verification_status = self.runtime.service(self, "reverification").get_status(
            user_id=user_id,
            course_id=course_id,
            checkpoint_name=checkpoint_name
        )
        if verification_status:
            # TODO: What message will be displayed to user if it is already has any status?
            frag = Fragment(unicode(verification_status))
            return frag
        reverification_link = self.runtime.service(self, "reverification").start_verification(
            course_id=course_id,
            checkpoint_name=checkpoint_name,
            item_id=item_id
        )
        org = self.get_org()
        html_str = pkg_resources.resource_string(__name__, "static/html/reverification.html")
        frag = Fragment(unicode(html_str).format(
            reverification_link=reverification_link,
            org=org,
            is_published=is_published
        ))
        return frag

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """

        html_str = pkg_resources.resource_string(__name__, "static/html/checkpoint_edit.html")
        frag = Fragment(unicode(html_str).format(
            checkpoint_name=self.checkpoint_name
        ))
        js_str = pkg_resources.resource_string(__name__, "static/js/checkpoint_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('CheckpointEditBlock')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.checkpoint_name = data.get('checkpoint_name')

        return {'result': 'success'}

    @staticmethod
    def workbench_scenarios():
        return [
            (
                "Reverification Block",
                load("static/xml/reverification_block_example.xml")
            ),
        ]

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
