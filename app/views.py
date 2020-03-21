from django.shortcuts import render

from app.helpers import random_illustration


def show_home(request):
    if request.method == 'GET':
        illustration = random_illustration()
        print(illustration)
        return render(request, 'frontend/home.html', {'illustration': illustration})
