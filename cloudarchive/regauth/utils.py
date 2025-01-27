from django.http import HttpResponseRedirect
import jwt

def authorized_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_email'):
            return HttpResponseRedirect('/guest')
        response = func(request, *args, **kwargs)
        return response
    return wrapper


