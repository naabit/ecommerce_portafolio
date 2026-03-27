from django.http import HttpResponse


def user_login(request):
    return HttpResponse("Login en construcción")


def user_logout(request):
    return HttpResponse("Logout en construcción")


def register(request):
    return HttpResponse("Registro en construcción")