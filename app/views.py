from django.shortcuts import render


def show_home(request):
    if request.method == 'GET':
        return render(request, 'frontend/home.html', {})
