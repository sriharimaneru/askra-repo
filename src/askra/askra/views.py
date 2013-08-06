# Create your views here.
from userprofile.models import StudentSection, UserProfile
from django.views.generic.base import TemplateView

class AboutView(TemplateView):
    template_name="about.html"
    
    
    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
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
        
        context['columnchartdata'] = chart_data
        context['totalalumdata'] = totalalumcollected
        context['remainingalumdata'] = remainingalumdata
        context['percentalumdatacollected'] = percentalumdatacollected
        context['percentalumdataremaining'] = percentalumdataremaining
        
        return context
