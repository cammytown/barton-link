from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.urls import reverse
from django.template import loader
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from ..models import Dataset, Excerpt
from ..utils import get_active_dataset, get_active_dataset_info

def index(request):
    """
    Display a list of all datasets.
    """
    datasets = Dataset.objects.all().order_by('name')
    
    # Get the current active dataset info from session - no database query needed
    active_dataset_info = get_active_dataset_info(request)
    
    context = {
        'datasets': datasets,
        'active_dataset_info': active_dataset_info,
    }
    
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/datasets/_dataset_list.html", context)
    # If browser request
    else:
        return render(request, 'excerpts/datasets/index.html', context)

def create(request):
    """
    Create a new dataset.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            dataset = Dataset.objects.create(
                name=name,
                description=description
            )
            
            # Set as active dataset
            request.session['active_dataset_id'] = dataset.id
            request.session['active_dataset_name'] = dataset.name
            
            # If HTMX request
            if request.headers.get("HX-Request") == "true":
                # Return to the dataset list with the new dataset
                return index(request)
            # If browser request
            else:
                return redirect('datasets')
    
    # If GET request or invalid form data
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/datasets/_dataset_form.html")
    # If browser request
    else:
        return render(request, 'excerpts/datasets/create.html')

def view(request, dataset_id):
    """
    View a specific dataset and its excerpts.
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        return HttpResponseNotFound("Dataset not found")
    
    # Set as active dataset
    request.session['active_dataset_id'] = dataset.id
    request.session['active_dataset_name'] = dataset.name
    
    # Get excerpts for this dataset
    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 50)
    
    # Extract search field
    search = request.GET.get("search", "")
    
    # Search for excerpts without parents in this dataset
    excerpts = Excerpt.objects.filter(
        content__icontains=search,
        parents__isnull=True,
        dataset=dataset
    ).order_by("-id")
    
    paginator = Paginator(excerpts, page_size)
    page_obj = paginator.get_page(page_num)
    
    # Build previous and next page links
    prev_page_url = None
    next_page_url = None
    
    if page_obj.has_previous():
        prev_page_url = reverse("dataset", args=[dataset_id]) + \
                f"?page={page_obj.previous_page_number()}"
        
        if search:
            prev_page_url += f"&search={search}"
    
    if page_obj.has_next():
        next_page_url = reverse("dataset", args=[dataset_id]) + \
                f"?page={page_obj.next_page_number()}"
        
        if search:
            next_page_url += f"&search={search}"
    
    context = {
        'dataset': dataset,
        'excerpts': page_obj,
        'search': search,
        'prev_page_url': prev_page_url,
        'next_page_url': next_page_url,
    }
    
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/datasets/_dataset_excerpts.html", context)
    # If browser request
    else:
        return render(request, 'excerpts/datasets/view.html', context)

def edit(request, dataset_id):
    """
    Edit a dataset.
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        return HttpResponseNotFound("Dataset not found")
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            dataset.name = name
            dataset.description = description
            dataset.save()
            
            # If HTMX request
            if request.headers.get("HX-Request") == "true":
                context = {'dataset': dataset}
                return render(request, "excerpts/datasets/_dataset_details.html", context)
            # If browser request
            else:
                return redirect('datasets')
    
    context = {
        'dataset': dataset,
    }
    
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/datasets/_dataset_edit_form.html", context)
    # If browser request
    else:
        return render(request, 'excerpts/datasets/edit.html', context)

def delete(request, dataset_id):
    """
    Delete a dataset.
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        return HttpResponseNotFound("Dataset not found")
    
    if request.method == 'POST':
        # Check if this is the active dataset
        if request.session.get('active_dataset_id') == dataset_id:
            del request.session['active_dataset_id']
            if 'active_dataset_name' in request.session:
                del request.session['active_dataset_name']
        
        # Soft delete the dataset
        dataset.soft_delete()
        
        # If HTMX request
        if request.headers.get("HX-Request") == "true":
            # Return updated dataset list
            return index(request)
        # If browser request
        else:
            return redirect('datasets')
    
    context = {
        'dataset': dataset,
    }
    
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/datasets/_dataset_delete_confirm.html", context)
    # If browser request
    else:
        return render(request, 'excerpts/datasets/delete.html', context)

def set_active(request, dataset_id):
    """
    Set a dataset as active.
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        return HttpResponseNotFound("Dataset not found")
    
    # Set as active dataset
    request.session['active_dataset_id'] = dataset.id
    request.session['active_dataset_name'] = dataset.name
    
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        # Return updated dataset list
        return index(request)
    
    # If browser request - redirect back to the referring page or datasets list
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('datasets') 