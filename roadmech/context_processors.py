# roadmech/context_processors.py

def user_type(request):
    """Adds user_type to context to check if user is a mechanic."""
    if request.user.is_authenticated:
        if hasattr(request.user, "mechanicprofile"):
            return {"user_type": "mechanic"}
        return {"user_type": "user"}
    return {}
