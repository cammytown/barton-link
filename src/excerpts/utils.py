from .models import Dataset

def get_active_dataset_info(request):
    """
    Get basic active dataset info from the session without database queries.
    
    Args:
        request: The HTTP request with session
        
    Returns:
        dict or None: Dictionary with 'id' and 'name' of active dataset, or None if not set
    """
    dataset_id = request.session.get('active_dataset_id')
    dataset_name = request.session.get('active_dataset_name')
    
    if dataset_id and dataset_name:
        return {'id': dataset_id, 'name': dataset_name}
    return None

def get_active_dataset(request, fetch_object=True):
    """
    Get the active dataset info or object from the session.
    
    Args:
        request: The HTTP request with session
        fetch_object: If True, queries database for Dataset object; if False, returns dict with id/name
        
    Returns:
        Dataset, dict, or None: Dataset object (if fetch_object=True) or dict with 'id' and 'name'
    """
    # Get basic info from session
    info = get_active_dataset_info(request)
    
    # If no active dataset or we don't need the object, return the info
    if not info or not fetch_object:
        return info
    
    # Query database for the actual object
    try:
        active_dataset = Dataset.objects.get(id=info['id'])
        # Update name in session if it changed
        if active_dataset.name != info['name']:
            request.session['active_dataset_name'] = active_dataset.name
        return active_dataset
    except Dataset.DoesNotExist:
        # If the dataset doesn't exist anymore, remove it from session
        if 'active_dataset_id' in request.session:
            del request.session['active_dataset_id']
        if 'active_dataset_name' in request.session:
            del request.session['active_dataset_name']
        return None 