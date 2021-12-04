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

def recordsPageView(request):
    contact_list = Prescriber.objects.all()
    # To return a new list, use the sorted() built-in function...
    newlist = sorted(contact_list, key=lambda x: (x.lname + x.fname), reverse=False)   
    paginator = Paginator(newlist, 15) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myDrugs/records.html', {'page_obj': page_obj})


def showSingleRecordPageView(request, pres_id):
    data = Prescriber.objects.get(npi = pres_id)
    state = State.objects.all()
    context = {
        "record": data,
        "state": state,
    }
    return render(request, 'myDrugs/editRecord.html', context)

def deletePrescriberPageView(request, pres_id):
    data = Prescriber.objects.get(npi = pres_id)
    data.delete()
    return recordsPageView(request)

def updatePrescribersPageView(request):
    if request.method == "POST":
        pres_id = request.POST['pres_id']

        prescriber = Prescriber.objects.get(npi = pres_id)

        prescriber.fname = request.POST['fname']
        prescriber.lname = request.POST['lname']
        prescriber.gender = request.POST['gender']
        prescriber.state = State.objects.get(statename = request.POST['state'])
        prescriber.specialty = request.POST['specialty']
        prescriber.isopioidprescriber = request.POST['isopioidprescriber']
        prescriber.totalprescriptions = request.POST['totalprescriptions']

        prescriber.save()
    return recordsPageView(request)
    

def addPrescriberPageView(request):
    if request.method == "POST":

        prescriber = Prescriber()

        prescriber.npi = request.POST['npi']
        prescriber.fname = request.POST['fname']
        prescriber.lname = request.POST['lname']
        prescriber.gender = request.POST['gender']
        prescriber.state = State.objects.get(statename = request.POST['state'])
        prescriber.specialty = request.POST['specialty']
        prescriber.isopioidprescriber = request.POST['isopioidprescriber']
        prescriber.totalprescriptions = request.POST['totalprescriptions']
        prescriber.save()
        return recordsPageView(request)
    else:
        return render(request, 'myDrugs/addPrescriber.html')

def showStateDropDownListView(request):
    state = State.objects.all()
    context = {
        "state": state,
    }
    return render(request, 'myDrugs/addPrescriber.html', context)
