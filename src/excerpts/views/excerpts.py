# from django.shortcuts import render

from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.urls import reverse
from django.template import loader
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from ..models import \
        Excerpt,\
        ExcerptVersion,\
        ExcerptSimilarity,\
        Tag,\
        TagType,\
        Entity


def index(request):
    return search(request)

def search(request):
    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 50)

    # Extract search field and filters
    search = request.GET.get("search", "")

    # Search for excerpts without parents
    excerpts = Excerpt.objects.filter(
        content__icontains=search,
        parents__isnull=True
    ).order_by("-id")

    # excerpts = Excerpt.objects.order_by("-id")

    paginator = Paginator(excerpts, page_size)
    page_obj = paginator.get_page(page_num)

    # Build previous and next page links
    prev_page_url = None
    next_page_url = None

    if page_obj.has_previous():
        prev_page_url = reverse("search") + \
                f"?page={page_obj.previous_page_number()}"

        if search:
            prev_page_url += f"&search={search}"

    if page_obj.has_next():
        next_page_url = reverse("search") + \
                f"?page={page_obj.next_page_number()}"

        if search:
            next_page_url += f"&search={search}"

    # Render list
    context = {
        # "excerpts": excerpts,
        "page_obj": page_obj,
        "prev_page_url": prev_page_url,
        "next_page_url": next_page_url,
        "page_sizes": [10, 25, 50, 100],
        "page_size": page_size,
        "search": search,
    }

    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/excerpts/_excerpt_list.html", context)

    # If browser request
    else:
        return render(request, "excerpts/excerpts/excerpt_search.html", context)

def excerpt(request, excerpt_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return excerpt_htmx(request, excerpt_id)
    # If not HTMX request
    else:
        return excerpt_html(request, excerpt_id)

def excerpt_html(request, excerpt_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)

    # If GET request
    if request.method == "GET":
        return render(request, "excerpts/excerpts/excerpt_page.html", {
            "excerpt": excerpt,
        })

    # If DELETE request
    elif request.method == "DELETE":
        # excerpt.delete()
        return HttpResponse(status=204)

def excerpt_htmx(request, excerpt_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)

    match request.method:
        # If GET request
        case "GET":
            context = { "excerpt": excerpt }
            return render(request, "excerpts/excerpts/_excerpt_editor.html", context)

        # If PUT request
        case "PUT":
            # Parse HTMX PUT request
            request_data = QueryDict(request.body)

            # Extract excerpt text
            excerpt_text = request_data.get("excerpt_content")

            # Update excerpt text
            excerpt.content = excerpt_text
            excerpt.save()

            # Create new version
            ExcerptVersion.objects.create(excerpt=excerpt, content=excerpt_text)

            # Render excerpt
            context = { "excerpt": excerpt }
            return render(request, "excerpts/excerpts/_excerpt.html", context)

        case "DELETE":
            excerpt = Excerpt.objects.get(id=excerpt_id)

            # Mark excerpt as deleted
            #@TODO-3: maintenance op to actually delete excerpts marked as deleted
            excerpt.soft_delete()

            # Return 204 success with no content
            return HttpResponse(status=204)

        case _:
            return HttpResponse(status=405)

def create_excerpt(request):
    if request.method == "POST":
        # Parse POST request
        request_data = QueryDict(request.body)

        # Extract excerpt text
        excerpt_text = request_data.get("excerpt_content")

        # Create new excerpt
        excerpt = Excerpt.objects.create(content=excerpt_text)

        # If HTMX request
        if request.headers.get("HX-Request") == "true":
            # Reuse search view to get updated list
            request.GET = request.GET.copy()

            # Force page 1 to show the new excerpt
            request.GET['page'] = 1
            return search(request)
        # If browser request
        else:
            return redirect("excerpt", excerpt_id=excerpt.id)

def add_tag(request, excerpt_id, tag_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    tag = Tag.objects.get(id=tag_id)

    excerpt.tags.add(tag)

    return render(request, "excerpts/excerpts/_excerpt_tags.html", { "excerpt": excerpt })

def add_autotag(request, excerpt_id, tag_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    tag = Tag.objects.get(id=tag_id)

    # Add tag to excerpt with is_autotag=True
    excerpt.tags.add(tag, through_defaults={ "is_autotag": True })

    return render(request,
                  "excerpts/excerpts/_excerpt_tags.html",
                  {
                      "excerpt": excerpt,
                      "show_unused": False
                  })

def remove_tag(request, excerpt_id, tag_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    tag = Tag.objects.get(id=tag_id)

    excerpt.tags.remove(tag)

    show_unused = request.POST.get("show_unused") == "true"

    return render(request,
                  "excerpts/excerpts/_excerpt_tags.html",
                  { "excerpt": excerpt, "show_unused": show_unused })
