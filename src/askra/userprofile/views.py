# Create your views here.
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.template import RequestContext
from userprofile.models import *
from userprofile.forms import *
from django.http import HttpResponseRedirect, Http404
import csv
from django.forms.util import ErrorList
from django.core.exceptions import ObjectDoesNotExist

def show_profile(request, profile_id):
    if not profile_id:
        return render_to_response("error.html", RequestContext(request, {}))

    user_profile = get_object_or_404(UserProfile, id=profile_id)
    student_section = StudentSection.objects.filter(userprofile = user_profile)[0]
    education_details = HigherEducationDetail.objects.filter(userprofile = user_profile)
    employment_details = EmployementDetail.objects.filter(userprofile = user_profile)
    other_profiles = StudentSection.objects.exclude(id=student_section.id)[:5] #Change logic to show relevant profiles
    return render_to_response("view_profile.html", RequestContext(request, {'user_profile': user_profile,
    				 'student_section': student_section, 'education_details':education_details,
    				 'employment_details': employment_details, 'other_profiles':other_profiles}))

def reg_step_2(request,x):
    user_profiles = UserProfile.objects.filter(role=ALUMNI)
    branches = Branch.objects.all()
    student_sections = list()
    for user_profile in user_profiles:
        student_section = StudentSection.objects.get(userprofile=user_profile)
        student_sections.append(student_section)

    return render_to_response("reg-step-2.html", RequestContext(request, {'student_sections':student_sections, 'branches':branches}))

def reg_step_3(request,x):
    return render_to_response("reg-step-3.html", RequestContext(request, {}))

def edit_profile_basic(request, profile_id):
    if not profile_id:
       return render_to_response("error.html", RequestContext(request, {}))

    user_profile=UserProfile.objects.get(id=profile_id)
    student_section=StudentSection.objects.filter(userprofile = user_profile)[0]

    if request.method=='POST':
    	form = EditProfileBasicForm(request.POST, request.FILES)
        print "indisde post"
    	if form.is_valid():
            user_profile.first_name = form.cleaned_data['name'].split()[0]
            user_profile.last_name = form.cleaned_data['name'].split()[1]
            print form.cleaned_data['course']
            student_section.branch_id = form.cleaned_data['course']
            student_section.year_of_graduation = form.cleaned_data['year_of_graduation']
            user_profile.city = City.objects.get(city=form.cleaned_data['city'])
            user_profile.about = form.cleaned_data['about']

            user_profile.save()
            student_section.save()

    	    return HttpResponseRedirect('/profile/view/'+profile_id)
    else:
        form = EditProfileBasicForm({'name':user_profile.get_full_name(), 'course':student_section.branch.id ,'year_of_graduation':student_section.year_of_graduation,
         'city':user_profile.city, 'about':user_profile.about, 'branch':student_section.branch.id}, {'picture': ''})

    return render(request, "edit_profile_basic.html", {'form': form, 'profile_id': profile_id,})

def edit_profile_weblinks(request, profile_id):
    if not profile_id:
       return render_to_response("error.html", RequestContext(request, {}))

    user_profile=UserProfile.objects.get(id=profile_id)

    if request.method=='POST':
        form = EditProfileWeblinksForm(request.POST)
        if form.is_valid():
            user_profile.facebook_url = form.cleaned_data['facebook_url']
            user_profile.twitter_url = form.cleaned_data['twitter_url']
            user_profile.linked_url = form.cleaned_data['linkedin_url']
            user_profile.save()
            return HttpResponseRedirect('/profile/view/'+profile_id)
    else:
        form = EditProfileWeblinksForm({'facebook_url':user_profile.facebook_url, 
            'twitter_url': user_profile.twitter_url, 'linkedin_url': user_profile.linked_url})

    return render(request, "edit_profile_weblinks.html", {'form': form, 'profile_id': profile_id,})


def edit_profile_education(request, profile_id):
    if not profile_id:
       return render_to_response("error.html", RequestContext(request, {}))

    user_profile=UserProfile.objects.get(id=profile_id)
    #student_section = StudentSection.objects.filter(userprofile = user_profile)[0]
    education_details = HigherEducationDetail.objects.filter(userprofile=user_profile)
    EditProfileEducationFormSet = formset_factory(EditProfileEducationForm, extra=0)

    if request.method == 'POST':
        formset = EditProfileEducationFormSet(request.POST,request.FILES)
        if formset.is_valid():
            for i in range(0,formset.total_form_count()):
                form = formset.forms[i]
                education_details[i].college = form.cleaned_data['college']
                education_details[i].degree = form.cleaned_data['degree']
                education_details[i].branch = form.cleaned_data['branch']
                education_details[i].year_of_graduation = form.cleaned_data['year_of_graduation']
                education_details[i].save()
            return HttpResponseRedirect('/profile/view/'+profile_id)
    else:
        formset = EditProfileEducationFormSet()
        for i in range(0,len(education_details)):
            form = EditProfileEducationForm({'year_of_graduation':education_details[i].year_of_graduation})
            formset.forms.append(form)

    return render(request, "edit_profile_education.html", {'formset':formset, 'profile_id':profile_id, })


def edit_profile_employment(request, profile_id):
    if not profile_id:
       return render_to_response("error.html", RequestContext(request, {}))

    user_profile=UserProfile.objects.get(id=profile_id)
    employment_details = EmployementDetail.objects.filter(userprofile = user_profile)
    EditProfileEmploymentFormSet = formset_factory(EditProfileEmploymentForm, extra=0)

    if request.method == 'POST':
        formset = EditProfileEmploymentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for i in range(0,formset.total_form_count()):
                form = formset.forms[i]
                employment_details[i].employer = form.cleaned_data['employer']
                employment_details[i].designation = form.cleaned_data['designation']
                employment_details[i].domain = form.cleaned_data['domain']
                employment_details[i].date_of_joining = form.cleaned_data['date_of_joining']
                employment_details[i].date_of_leaving = form.cleaned_data['date_of_leaving']
                employment_details[i].save()
            return HttpResponseRedirect('/profile/view/'+profile_id)
    else:
        formset = EditProfileEmploymentFormSet()
        for i in range(0,len(employment_details)):
            form = EditProfileEmploymentForm({'date_of_joining':employment_details[i].date_of_joining, 'date_of_leaving':employment_details[i].date_of_leaving})
            formset.forms.append(form)

    return render(request, "edit_profile_employment.html", {'formset':formset, 'profile_id':profile_id, })

def profile_bulk_upload(request,x):
    if request.method == 'POST':
        form = ProfileBulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            errors = form._errors.setdefault("uploaded_file", ErrorList())
            reader = csv.DictReader(request.FILES['uploaded_file'])
            for row in reader:
                first_name = row['First Name']
                last_name = row['Last Name']
                phone_number = row['Phone Number']
                email = row['Email']
                gender = row['Gender']
                role = row['User Role']
                city = row['City']

                try:
                    user_profile=UserProfile.objects.get(email=email)
                    text = "A profile with email ID [" + email + "] already exists. Updated the other fields."
                    user_profile.first_name = first_name
                    user_profile.last_name = last_name
                    user_profile.phone_number = phone_number
                    user_profile.email = email
                except ObjectDoesNotExist:
                    user_profile = UserProfile(first_name=first_name, 
                                               last_name=first_name,
                                               email=email,
                                               phone_number=phone_number)
                    text = "Added new profile with email ID [" + email + "]"

                errors.append(text)
                user_profile.set_gender(gender)
                user_profile.set_role(role)
                user_profile.set_city(city)
                user_profile.save()
                
            errors.append("Bulk upload successful")
    else:
        form = ProfileBulkUploadForm()
    return render(request, "profile_bulk_upload.html", {'form':form, })

def draw_charts(request, x):
    dict = {}
    for yog in StudentSection.objects.values('year_of_graduation').distinct():
        year = yog["year_of_graduation"]
        number = UserProfile.objects.filter(studentsection__year_of_graduation=year).count()
        dict[str(year)] = number
    
    return render_to_response("reports.html", RequestContext(request, {'data':dict,}))