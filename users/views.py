from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views import View
from .forms import UserRegisterForm


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
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user)  # login automático
            messages.success(request, "Cuenta creada correctamente.")

            return redirect("core:home")
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})