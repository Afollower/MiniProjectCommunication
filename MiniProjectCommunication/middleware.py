from django.shortcuts import HttpResponseRedirect
from django.shortcuts import render, redirect

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class SimpleMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path != '/user/login/' and request.path != '/user/register/':
            if request.session.get('is_login', None):
                pass
            else:
                return redirect('/user/login/')
