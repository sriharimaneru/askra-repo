# Create your views here.
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.template import RequestContext
from userprofile.models import *
from userprofile.forms import *
from django.http import HttpResponseRedirect, Http404
import csv
from django.forms.util import ErrorList
from django.core.exceptions import ObjectDoesNotExist
from haystack.query import SearchQuerySet
from haystack.forms import SearchForm
from django.http import HttpResponse

def index(request):
    dict = {}
    for yog in StudentSection.objects.values('year_of_graduation').distinct():
        year = yog["year_of_graduation"]
        number = UserProfile.objects.filter(studentsection__year_of_graduation=year).count()
        dict[str(year)] = number

    totalalumcollected = UserProfile.objects.filter(role=0).count()
    remainingalumdata = 30000 - totalalumcollected
    percentalumdatacollected = 100*(totalalumcollected/30000.0)
    percentalumdataremaining = 100 - percentalumdatacollected
    
    return render_to_response("index.html", RequestContext(request, {'columnchartdata':dict, 'totalalumdata': totalalumcollected, 
                              'remainingalumdata': remainingalumdata, 'percentalumdatacollected': percentalumdatacollected, 
                              'percentalumdataremaining': percentalumdataremaining, }))