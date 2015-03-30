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

    def student_view(self, context=None):
        return Fragment(u"<h1>Hello World</h1>")

    @staticmethod
    def workbench_scenarios():
        return [
            (
                "Reverification Block",
                load("static/xml/reverification_block_example.xml")
            ),
        ]
