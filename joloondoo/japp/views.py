from django.shortcuts import render

# Create your views here
def home(request):
    return render(request, 'home.html', {})


def login_page(request):
    return render(request, 'login_page.html', {})


def register_page(request):
    return render(request, 'register_page.html', {})

def practise(request):
    return render(request, 'practise.html', {})
