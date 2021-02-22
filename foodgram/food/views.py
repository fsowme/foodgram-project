from django.shortcuts import HttpResponse, render


# Create your views here.
def testpage(request):
    # return render(request, "test.html")
    return render(request, "indexNotAuth.html")
    return HttpResponse("Ok")
