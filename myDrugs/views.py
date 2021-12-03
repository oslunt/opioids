from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def indexPageView(request):
    return render(request, "myDrugs/index.html")

def searchPageView(request):
    return render(request, "myDrugs/search.html")

def detailsPageView(request):
    return render(request, "myDrugs/details.html")

def recordsPageView(request):
    return render(request, "myDrugs/records.html")

def analysisPageView(request):
    return render(request, "myDrugs/analysis.html")