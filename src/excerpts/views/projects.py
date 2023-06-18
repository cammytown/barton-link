from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render
from django.core.paginator import Paginator

from ..models import Project

def projects(request):
    # Get all projects alphabetically
    projects = Project.objects.order_by("name")

    # Paginate projects
    #@TODO

    context = { "projects": projects }

    return render(request, "excerpts/projects_index.html", context)

def project(request, project_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return project_htmx(request, project_id)
    else:
        return project_html(request, project_id)

def project_html(request, project_id):
    project = Project.objects.get(id=project_id)

    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 50)

    # Get excerpts with project
    excerpts = project.excerpts.all()

    # Paginate excerpts
    paginator = Paginator(excerpts, page_size)
    page_obj = paginator.get_page(page_num)

    context = { "project": project, "page_obj": page_obj }

    return render(request, "excerpts/project_page.html", context)

def project_htmx(request, project_id):
    project = Project.objects.get(id=project_id)

    match request.method:
        case "GET":
            return render(request,
                          "excerpts/project_editor.html",
                          { "project": project })
