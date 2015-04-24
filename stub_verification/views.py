"""Views for the fake reverification flow. """
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import VerificationStatus


@require_GET
def stub_reverify_flow(request, course_id, checkpoint_name, usage_id, user_id):
    """Display a page that allows users to (fake) submit photos. """
    context = RequestContext(request, {
        'user_id': user_id,
        'course_id': course_id,
        'checkpoint_name': checkpoint_name
    })
    return render_to_response("stub_verification/reverify.html", context)


@require_POST
def stub_submit_reverification_photos(request):
    """Simulate that the user has submitted photos. """
    params = {
        'course_id': request.POST.get('course_id'),
        'checkpoint_name': request.POST.get('checkpoint_name'),
        'user_id': request.POST.get('user_id')
    }

    status, _ = VerificationStatus.objects.get_or_create(**params)
    status.status = "submitted"
    status.save()

    context = {
        'admin_url': reverse(
            'admin:stub_verification_verificationstatus_change',
            args=(status.id,)
        ),
    }
    context.update(**params)
    return render_to_response("stub_verification/submitted.html", context)
