from django.db.models.aggregates import Avg
from django.db.models.query_utils import PathInfo
from django.shortcuts import redirect, render
from .models import Drug, Prescriber, Prescriberdrug, State
from django.core.paginator import Paginator
from django.http import HttpResponse, request
from django.views.generic import ListView
from django.db import connection

class ContactListView(ListView):
    paginate_by = 2
    model = Prescriber

# Create your views here.

def indexPageView(request):
    return render(request, "myDrugs/index.html")

def searchPageView(request):   
    data = {
        'page_obj': '',
        'type': ''
    }
    if request.method == "POST":
        database = request.POST['database']
        if database == 'Prescriber':
            return redirect('prescriber/')
        else:
            return redirect('drug/')
    return render(request, "search.html", data)

def prescriberSearchPageView(request):
    if request.method == "GET" and "search" in request.GET and "searchtype" in request.GET:
        keyword = request.GET['search']
        request.session['search'] = keyword
        searchtype = request.GET['searchtype']
        request.session['searchtype'] = searchtype
        contact_list = getFilter(searchtype, keyword)
    elif "search" in request.session and "searchtype" in request.session and "search" not in request.GET:
        keyword = request.session['search']
        searchtype = request.session['searchtype']
        contact_list = getFilter(searchtype, keyword)
    else:
        contact_list = Prescriber.objects.all()

    paginator = Paginator(contact_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data = {
        'page_obj': page_obj,
        'type': 'Prescriber',
    }

    return render(request, "myDrugs/prescriberSearch.html", data)

def getFilter(searchtype, keyword):
    if searchtype == 'fname':
        return Prescriber.objects.filter(fname__icontains=keyword)
    elif searchtype == 'lname':
        return Prescriber.objects.filter(lname__icontains=keyword)
    elif searchtype == 'gender':
        return Prescriber.objects.filter(gender__icontains=keyword)
    elif searchtype == 'credential':
        return Prescriber.objects.filter(credential__icontains=keyword)
    elif searchtype == 'state':
        state = State.objects.filter(statename__icontains=keyword)
        return Prescriber.objects.filter(state__in=state)
    else:
        return Prescriber.objects.filter(specialty__icontains=keyword)

def detailsPageView(request, prescriber):
    presciber_obj = Prescriber.objects.get(npi = prescriber)
    cursor2 = connection.cursor()
    query2 = "SELECT pd.*, d.drugname, (SELECT ROUND(AVG(pd1.quantity),2) as average FROM prescriberdrug pd1 WHERE pd1.drugid = pd.drugid) FROM prescriberdrug pd JOIN drug d on pd.drugid= d.drugid WHERE npi = %s"
    cursor2.execute(query2, [prescriber])
    columns2 = [col[0] for col in cursor2.description]
    drug_obj = [dict(zip(columns2, row)) for row in cursor2.fetchall()]
    paginator = Paginator(drug_obj, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data = {
        'prescriber_obj': presciber_obj,
        'page_obj': page_obj,
    }
    return render(request, "myDrugs/detailsPrescriber.html", data)

def drugSearchPageView(request):
    if request.method == "GET" and "drugsearch" in request.GET and "searchtypedrug" in request.GET:
        keyword = request.GET['drugsearch']
        request.session['drugsearch'] = keyword
        searchtype = request.GET['searchtypedrug']
        request.session['searchtypedrug'] = searchtype
        contact_list = getDrugFilter(searchtype, keyword)
    elif "drugsearch" in request.session and "searchtypedrug" in request.session and "drugsearch" not in request.GET:
        keyword = request.session['drugsearch']
        searchtype = request.session['searchtypedrug']
        contact_list = getDrugFilter(searchtype, keyword)
    else:
        contact_list = Drug.objects.all()

    paginator = Paginator(contact_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data = {
        'page_obj': page_obj,
        'type': 'Drug',
    }

    return render(request, "myDrugs/drugSearch.html", data)

def getDrugFilter(searchtype, keyword):
    if searchtype == 'drugname':
        return Drug.objects.filter(drugname__icontains=keyword)
    else:
        return Drug.objects.filter(isopioid__icontains=keyword)

def detailsDrugPageView(request, drug):
    drug_obj = Drug.objects.get(drugid = drug)
    cursor2 = connection.cursor()
    query2 = "SELECT p.fname, p.lname, pd.quantity FROM prescriberdrug pd JOIN prescriber p ON pd.npi = p.npi WHERE pd.drugid = %s ORDER BY pd.quantity DESC LIMIT 10"
    cursor2.execute(query2, [drug])
    columns2 = [col[0] for col in cursor2.description]
    page_obj = [dict(zip(columns2, row)) for row in cursor2.fetchall()]
    data = {
        'drug_obj': drug_obj,
        'page_obj': page_obj,
    }
    return render(request, "myDrugs/detailsDrug.html", data)


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


def searchRecordsPageView(request):
    if request.method == "POST":
        searched = request.POST.get('record-search')
        prescriber = (Prescriber.objects.filter(fname__icontains=searched)|Prescriber.objects.filter(lname__icontains=searched))
        
        
    # To return a new list, use the sorted() built-in function...
        newlist = sorted(prescriber, key=lambda x: (x.lname + x.fname), reverse=False)   
        paginator = Paginator(newlist, 15) # Show 25 contacts per page.
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'myDrugs/searchRecords.html',{'searched': searched, 'prescriber':prescriber, 'page_obj': page_obj} )
    else:
        return render(request, 'myDrugs/searchRecords.html',{} )


def analysisPageView(request):
    cursor2 = connection.cursor()
    query2 = "select fname, lname, gender, credential, s.statename, specialty from prescriber p left join(select pd.npi, d.drugid, d.drugname from drug d inner join prescriberdrug pd on d.drugid = pd.drugid where d.isopioid = False) temps on p.npi = temps.npi inner join state s on p.state = s.state where temps.npi is null"
    cursor2.execute(query2)
    columns2 = [col[0] for col in cursor2.description]
    page_obj = [dict(zip(columns2, row)) for row in cursor2.fetchall()]
    data = {
        'page_obj': page_obj,
    }
    return render(request, "myDrugs/analysis.html", data)

