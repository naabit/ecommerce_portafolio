from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views import View


class UserLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Has iniciado sesión correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)


class UserLogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect("core:home")


def register(request):
    return render(request, "users/register.html")