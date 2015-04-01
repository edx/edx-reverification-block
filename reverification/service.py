"""Service for photo verification. """
from xblock.reference.plugins import Service


class VerificationService(Service):
    """TODO """

    def __init__(self, *args, **kwargs):
        """TODO """
        super(VerificationService, self).__init__(*args, **kwargs)
        try:
            from verify_student import api as verify_api
            self.api  = verify_api
        except ImportError:
            self.api = None

    def get_status(self, course_id, checkpoint_name):
        """TODO """
        if self.api is not None:
            return self.api.get_status(course_id, checkpoint_name)

    def start_verification(self, course_id, checkpoint_name):
        """TODO """
        if self.api is not None:
            return self.api.start_verification(course_id, checkpoint_name)
