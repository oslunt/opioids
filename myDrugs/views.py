from django.shortcuts import render
from .models import Prescriber, State
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.generic import ListView


class ContactListView(ListView):
    paginate_by = 2
    model = Prescriber

# Create your views here.

def indexPageView(request):
    return render(request, "myDrugs/index.html")

def searchPageView(request):
    return render(request, "myDrugs/search.html")

def detailsPageView(request):
    return render(request, "myDrugs/details.html")

def analysisPageView(request):
    return render(request, "myDrugs/analysis.html")
""""
def recordsPageView(request):
    data = Prescriber.objects.all()
    context = {
        "pres" : data
    }
    return render(request, "myDrugs/records.html", context)
"""
def recordsPageView(request):
    contact_list = Prescriber.objects.all()
    paginator = Paginator(contact_list, 15) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'myDrugs/records.html', {'page_obj': page_obj})


def showSingleRecordPageView(request, pres_id):
    data = Prescriber.objects.get(npi = pres_id)
    context = {
        "record": data,
    }

    return render(request, 'myDrugs/editRecord.html', context)


def updatePrescribersPageView(request):
    if request.method == "POST":
        pres_id = request.POST['pres_id']

        prescriber = Prescriber.objects.get(npi = pres_id)

        
        Prescriber.state = State.objects.get(statename = state.name)##fix this ish
        


        prescriber.fname = request.POST['fname']
        prescriber.lname = request.POST['lname']
        prescriber.gender = request.POST['gender']
        prescriber.state = request.POST['state']
        prescriber.specialty = request.POST['specialty']
        prescriber.isopioidprescriber = request.POST['isopioidprescriber']
        prescriber.totalprescriptions = request.POST['totalprescriptions']

        prescriber.save()
    return recordsPageView(request)

