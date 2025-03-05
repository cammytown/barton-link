from django.http import HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse

from ...models import Excerpt
from ...services import AutotagService

autotag = AutotagService()

def autotag_excerpts(request):
    """
    Autotag excerpts.

    Present user with confirmation page before proceeding.
    """
    page_num = request.GET.get("page", 1)
    
    # Get autotag service status
    status = autotag.get_status()

    # Get excerpts with autotags
    excerpts = Excerpt.objects.filter(autotags__isnull=False).distinct()

    # Paginate excerpts
    paginator = Paginator(excerpts, 10)
    page_obj = paginator.get_page(page_num)

    prev_page_url = None
    next_page_url = None

    if page_obj.has_previous():
        prev_page_url = reverse("autotag") + \
                f"?page={page_obj.previous_page_number()}"

    if page_obj.has_next():
        next_page_url = reverse("autotag") + \
                f"?page={page_obj.next_page_number()}"

    context = {
        "status": status,
        "page_obj": page_obj,
        "prev_page_url": prev_page_url,
        "next_page_url": next_page_url,
    }

    return render(request, "excerpts/tools/autotag.html", context)

def start_autotag(request):
    """
    Start autotagging process.
    """
    autotag.start()
    return get_autotag_progress(request)

def stop_autotag(request):
    """
    Stop autotagging process.
    """
    autotag.stop()
    return HttpResponse("Autotag stopped.")

def get_autotag_progress(request):
    """
    Get autotagging progress.
    """
    status = autotag.get_status()
    return render(request, "excerpts/tools/_autotag_progress.html", { "status": status }) 