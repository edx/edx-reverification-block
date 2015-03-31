"""An XBlock for in-course reverification. """

import pkg_resources
from xblock.core import XBlock
from xblock.fragment import Fragment


def load(path):
    """Load a resource from the package. """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


class ReverificationBlock(XBlock):
    """An XBlock for in-course reverification. """

    @property
    def course_id(self):
        return unicode(self.xmodule_runtime.course_id)  # pylint:disable=E1101

    def student_view(self, context=None):
        """Student view to render the re-verification link
            This will render the url to display in lms.
        """
        # TODO: Need to change the hard coded url

        anchor_str = "<a href='/verify_student/reverify/{course_id}/midterm/'>Reverify</a>"
        return Fragment(unicode(anchor_str).format(self=self, course_id=self.get_course_id()))

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
