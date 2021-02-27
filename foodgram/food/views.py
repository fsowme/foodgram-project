from django.shortcuts import HttpResponse, render

from .models import Tag


def main(request):
    # if request.user.is_authenticated:
    return render(request, "index.html")


def testpage(request):
    print(request.user)
    return render(request, "base.html")
