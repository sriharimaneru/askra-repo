# Create your views here.
from django.shortcuts import render_to_response, render
from django.template import RequestContext, context
from userprofile.forms import *
from userprofile.models import StudentSection, UserProfile

def about(request):
    chart_data = {}
    for yog in StudentSection.objects.values('year_of_graduation').distinct():
        year = yog["year_of_graduation"]
        if year>0:
            number = UserProfile.objects.filter(studentsection__year_of_graduation=year).count()
            chart_data[str(year)] = number

    totalalumcollected = UserProfile.objects.filter(role=0).count()
    remainingalumdata = 40000 - totalalumcollected
    percentalumdatacollected = int(100*(totalalumcollected/40000.0))
    percentalumdataremaining = 100 - percentalumdatacollected
    
    context = {'columnchartdata':chart_data, 'totalalumdata': totalalumcollected, 
                              'remainingalumdata': remainingalumdata, 'percentalumdatacollected': percentalumdatacollected, 
                              'percentalumdataremaining': percentalumdataremaining,}
    
    return render(request, "search/search.html", context)