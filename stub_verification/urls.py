"""URLs for the stub reverification flow.

This is a fake implementation of the reverification flow
in edx-platform's verify_student app.  Unlike in the actual
flow, we don't submit photos to an external service.

"""
from django.conf.urls import patterns, url


COURSE_ID_PATTERN = r'(?P<course_id>[^/+]+(/|\+)[^/+]+(/|\+)[^/]+)'
CHECKPOINT_PATTERN = r'(?P<checkpoint_name>[^/]+)'
USAGE_ID_PATTERN = r'(?P<usage_id>(?:i4x://?[^/]+/[^/]+/[^/]+/[^@]+(?:@[^/]+)?)|(?:[^/]+))'


urlpatterns = patterns(
    'stub_verification.views',
    url(
        r'^reverify_flow/{course_id}/{usage_id}/(?P<checkpoint_name>[^/]+)/(?P<user_id>[^/]+)/$'.format(
            course_id=COURSE_ID_PATTERN,
            usage_id=USAGE_ID_PATTERN
        ),
        'stub_reverify_flow',
        name='stub_reverify_flow',
    ),

    url(
        r'^submit_reverification_photos$',
        'stub_submit_reverification_photos',
        name='stub_submit_reverification_photos'
    )
)
