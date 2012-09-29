# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from userprofile.models import *

def show_profile(request, profile_id):
    if not profile_id:
        return render_to_response("error.html")

    user_profile = UserProfile.objects.get(id=1)
    student_section = StudentSection.objects.filter(userprofile = user_profile)[0]
    education_details = HigherEducationDetail.objects.filter(userprofile = user_profile)
    employment_details = EmployementDetail.objects.filter(userprofile = user_profile)
    return render_to_response("view_profile.html", RequestContext(request, {'user_profile': user_profile,
    				 'student_section': student_section, 'education_details':education_details,
    				 'employment_details': employment_details}))
