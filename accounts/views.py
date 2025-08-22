from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
	return render(request, 'home.html')


def login_view(request):
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			user = form.get_user()
			auth_login(request, user)
			return redirect('home')
	else:
		form = AuthenticationForm(request)
	return render(request, 'login.html', {'form': form})


def register_view(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			authenticated_user = authenticate(request, username=username, password=password)
			if authenticated_user is not None:
				auth_login(request, authenticated_user)
				return redirect('home')
	else:
		form = UserCreationForm()
	return render(request, 'register.html', {'form': form})
