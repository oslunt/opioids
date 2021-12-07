from django.db.models.query_utils import PathInfo
from django.shortcuts import redirect, render
from .models import Drug, Prescriber, State
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.db import connection
import requests
import json
import math

# Pagination specifications
class ContactListView(ListView):
    paginate_by = 2
    model = Prescriber

# Create your views here.

def indexPageView(request):
    return render(request, "myDrugs/index.html")

def searchPageView(request):   
    if request.method == "POST":
        database = request.POST['database']
        if database == 'Prescriber':
            return redirect('prescriber/')
        else:
            return redirect('drug/')
    return render(request, "search.html")

# Function uses pagination to display and pulls from database
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

# function is used to filter data for querying
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

# functions is used to connect to database, use pagination, and query the needed data
def detailsPageView(request, prescriber):
    presciber_obj = Prescriber.objects.get(npi = prescriber)
    cursor2 = connection.cursor()
    query2 = "SELECT pd.*, d.drugname, (SELECT ROUND(AVG(pd1.quantity),2) as average FROM prescriberdrug pd1 WHERE pd1.drugid = pd.drugid) FROM prescriberdrug pd JOIN drug d on pd.drugid= d.drugid WHERE npi = %s"
    cursor2.execute(query2, [prescriber])
    columns2 = [col[0] for col in cursor2.description]
    drug_obj = [dict(zip(columns2, row)) for row in cursor2.fetchall()]
    cursor = connection.cursor()
    query = "SELECT drugid, isopioid FROM drug"
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    drugs = [dict(zip(columns, row)) for row in cursor.fetchall()]
    paginator = Paginator(drug_obj, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    recommendation = prescriberRecommender(presciber_obj, drug_obj, drugs)
    print(recommendation)
    data = {
        'prescriber_obj': presciber_obj,
        'page_obj': page_obj,
        'recommendation': recommendation,
    }
    return render(request, "myDrugs/detailsPrescriber.html", data)


# function is used to connect to database and get requested info and query data

def prescriberRecommender(prescriber_obj, drug_obj, drugs):
    url = "http://9483b05f-0af0-4516-a794-db3c24e3b4b5.eastus2.azurecontainer.io/score"

    pd_list = []
    for row in drug_obj:
        pd_list.append({'npi': row['npi'], 'drugname': row['drugname'], 'quantity': row['quantity']})
    payload = json.dumps({
    "Inputs": {
        "WebServiceInput3": [
        {
            "npi": prescriber_obj.npi,
            "gender": prescriber_obj.gender,
            "state": prescriber_obj.state.state,
            "specialty": prescriber_obj.specialty,
            "isopioidprescriber": prescriber_obj.isopioidprescriber,
            "totalprescriptions": prescriber_obj.totalprescriptions,
            "credential": prescriber_obj.credential
        }
        ],
        "WebServiceInput1": pd_list,
        "WebServiceInput2": drugs
    },
    "GlobalParameters": {}
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer nvp29jiW4YEYAQF3PzWaCkLh04n3uI8f'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    json_data = json.loads(response.text)
    retval = ''
    for iCount in range(1, 6):
        if iCount != 5:
            retval = retval + json_data['Results']['WebServiceOutput0'][0]['Recommended Item ' + str(iCount)] + ", "
        else:
            retval = retval + json_data['Results']['WebServiceOutput0'][0]['Recommended Item ' + str(iCount)]
    return retval


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

# function is used to filter data for querying
def getDrugFilter(searchtype, keyword):
    if searchtype == 'drugname':
        return Drug.objects.filter(drugname__icontains=keyword)
    else:
        return Drug.objects.filter(isopioid__icontains=keyword)

# details view for drug search. Querys from database and displays to the page
def detailsDrugPageView(request, drug):
    drug_obj = Drug.objects.get(drugid = drug)
    cursor2 = connection.cursor()
    query2 = "SELECT p.fname, p.lname, pd.quantity FROM prescriberdrug pd JOIN prescriber p ON pd.npi = p.npi WHERE pd.drugid = %s ORDER BY pd.quantity DESC LIMIT 10"
    cursor2.execute(query2, [drug])
    columns2 = [col[0] for col in cursor2.description]
    page_obj = [dict(zip(columns2, row)) for row in cursor2.fetchall()]
    cursor = connection.cursor()
    query = "SELECT npi, gender, state, specialty, isopioidprescriber, totalprescriptions, credential from prescriber"
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    prescriber = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor3 = connection.cursor()
    query3 = "SELECT pd.drugid, p.fname || ' ' || p.lname as fullname, pd.quantity from prescriber p inner join prescriberdrug pd on p.npi = pd.npi"
    cursor3.execute(query3)
    columns3 = [col[0] for col in cursor3.description]
    prescriberdrug = [dict(zip(columns3, row)) for row in cursor3.fetchall()]
    #recommendation = drugRecommender(drug_obj, prescriber, prescriberdrug)
    data = {
        'drug_obj': drug_obj,
        'page_obj': page_obj,
        #'recommendation': recommendation
    }
    return render(request, "myDrugs/detailsDrug.html", data)

def drugRecommender(drug_obj, prescriber, prescriberdrug):
    url = "http://9c830994-51e0-47a0-9611-741637712e12.eastus2.azurecontainer.io/score"
    tempPrescriber =[]
    for row in prescriber:
        print(row)
        break
    for row in prescriber:
        tempPrescriber.append({
            'fullName': row['npi'],
            'gender': row['gender'],
            'state': row['state'],
            'specialty': row['specialty'],
            'isopioidprescriber': row['isopioidprescriber'],
            'totalprescriptions': row['totalprescriptions'],
            'credential': row['credential']
        })
    tempPrescriberDrug = []
    for row in prescriberdrug:
        tempPrescriberDrug.append({
            'drugid': row['drugid'],
            'fullName': row['fullname'],
            'quantity': row['quantity']
        })
    payload = json.dumps({
    "Inputs": {
        "WebServiceInput3": prescriber,
        "WebServiceInput1": prescriberdrug,
        "WebServiceInput0": [
        {
            "drugid": drug_obj.drugid,
            "isopioid": drug_obj.isopioid
        }
        ]
    },
    "GlobalParameters": {}
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer vO7LRHSFfZ19D4P5if2XTcUJk7BGgDv0'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    json_data = json.loads(response.text)
    retval = ''
    print(json_data)
    for iCount in range(1, 6):
        if iCount != 5:
            retval = retval + json_data['Results']['WebServiceOutput0'][0]['Recommended Item ' + str(iCount)] + ', '
        else :
            retval = retval + json_data['Results']['WebServiceOutput0'][0]['Recommended Item ' + str(iCount)]
    return retval

def recordsPageView(request):
    contact_list = Prescriber.objects.all()
    # To return a new list, use the sorted() built-in function...
    newlist = sorted(contact_list, key=lambda x: (x.lname + x.fname), reverse=False)   
    paginator = Paginator(newlist, 15) # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myDrugs/records.html', {'page_obj': page_obj})

# used for updating data in the crud system
def showSingleRecordPageView(request, pres_id):
    data = Prescriber.objects.get(npi = pres_id)
    state = State.objects.all()
    context = {
        "record": data,
        "state": state,
    }
    return render(request, 'myDrugs/editRecord.html', context)

# prescriber is removed from database
def deletePrescriberPageView(request, pres_id):
    data = Prescriber.objects.get(npi = pres_id)
    data.delete()
    return recordsPageView(request)

# prescriber is updated in database in this func
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
    
# in this view user can add a prescriber to the database
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

# function is used to show state dropdown list
def showStateDropDownListView(request):
    state = State.objects.all()
    context = {
        "state": state,
    }
    return render(request, 'myDrugs/addPrescriber.html', context)

# function is used to search data in the crud system
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

# function is used to query data fro the analysis page view
def analysisPageView(request):
    if request.method =="GET" and "analysischoice" in request.GET:
        type = request.GET['analysischoice']
    else:
        type = ''
    cursor2 = connection.cursor()
    query2 = "select fname, lname, gender, credential, s.statename, specialty from prescriber p left join(select pd.npi, d.drugid, d.drugname from drug d inner join prescriberdrug pd on d.drugid = pd.drugid where d.isopioid = False) temps on p.npi = temps.npi inner join state s on p.state = s.state where temps.npi is null"
    cursor2.execute(query2)
    columns2 = [col[0] for col in cursor2.description]
    page_obj = [dict(zip(columns2, row)) for row in cursor2.fetchall()]
    data = {
        'page_obj': page_obj,
        'type': type,
    }
    return render(request, "myDrugs/analysis.html", data)

def predictionPageView(request):
    if request.method == "POST":
        prediction = request.POST['prediction']
        if prediction == 'prescriber':
            return redirect('prescriber/')
        else:
            return redirect('drug/')
    return render(request, "predictor.html")

def calculatorPrescriberPageView(request):
    if request.method == "GET" and "gender" in request.GET and "specialty" in request.GET and "totalprescriptions" in request.GET:
        page_obj = calculatorClassificationAPI(request.GET['gender'], request.GET['specialty'], request.GET['totalprescriptions'])
        searchresults = {
            'gender': request.GET['gender'],
            'specialty': request.GET['specialty'],
            'totalprescriptions': request.GET['totalprescriptions'],
            }
    else:
        page_obj = ''
        searchresults = ''

    data = {
        'page_obj': page_obj,
        'searchresults': searchresults
    }

    return render(request, "myDrugs/calculatorPrescriber.html", data)

def calculatorClassificationAPI(gender, specialty, totalprescriptions):
    url = "http://0bc87be1-4e61-43bd-a748-68a5703ed377.eastus2.azurecontainer.io/score"
    payload = json.dumps({
    "Inputs": {
        "WebServiceInput0": [
        {
            "gender": gender,
            "specialty": specialty,
            "totalprescriptions": totalprescriptions
        }
        ]
    },
    "GlobalParameters": {}
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer nj0N2ZMAebtfB50teywADjJ1yUSwt4VM'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    json_string = response.text
    json_parsed = json.loads(json_string)
    json_dic = json_parsed['Results']['WebServiceOutput0']

    for key in range(0, len(json_dic)) :
        thing = json_dic[key]
    retval = ''
    for key1 in thing :
        retval = thing[key1]
    print(retval)
    return retval

def calculatorDrugPageView(request):
    if request.method == "GET" and "gender" in request.GET and "specialty" in request.GET and "isopioidprescriber" in request.GET:
        page_obj = calculatorRegressionAPI(request.GET['gender'], request.GET['specialty'], request.GET['isopioidprescriber'])
        searchresults = {
            'gender': request.GET['gender'],
            'specialty': request.GET['specialty'],
            'isopioidprescriber': request.GET['isopioidprescriber'],
            }
    else:
        page_obj = ''
        searchresults = ''

    data = {
        'page_obj': page_obj,
        'searchresults': searchresults
    }

    return render(request, "myDrugs/calculatorDrug.html", data)

def calculatorRegressionAPI(gender, specialty, isopioidprescriber):
    url = "http://6bc6e29e-0375-4330-b408-5f7bff5d0c88.eastus2.azurecontainer.io/score"

    payload = json.dumps({
    "Inputs": {
        "WebServiceInput0": [
        {
            "gender": gender,
            "specialty": specialty,
            "isopioidprescriber": isopioidprescriber
        }
        ]
    },
    "GlobalParameters": {}
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ggui3aj9ZHMSDvR6RPPqMg0byPOnPx5h'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    json_string = response.text
    json_parsed = json.loads(json_string)
    json_dic = json_parsed['Results']['WebServiceOutput0']

    for key in range(0, len(json_dic)) :
        thing = json_dic[key]
    retval = ''
    for key1 in thing :
        retval = str(round(math.exp(thing[key1]), 2))
    return retval
