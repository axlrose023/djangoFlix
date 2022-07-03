from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import UserRegistrationForm, UserLogInForm


# Create your views here.


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                new_user = form.save(commit=False)
                new_user.set_password(form.cleaned_data['password2'])
                new_user.save()
                return redirect('login')
            except:
                form.add_error(None, 'Ошибка Регистрации пользователя')
        else:
            messages.error(request, 'Form is not valid')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


class LogInUser(LoginView):
    form = UserLogInForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('home')
