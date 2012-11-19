def logged_in(request):
    return 'access' in request.session
