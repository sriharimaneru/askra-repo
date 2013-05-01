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
from models import *
from forms import *
from haystack.forms import SearchForm
from django.http import HttpResponse
import json
from django.forms.models import modelformset_factory

def show_profile(request, profile_id):
    if not profile_id:
        return render_to_response("error.html", RequestContext(request, {}))

    user_profile = get_object_or_404(UserProfile, id=profile_id)
    student_section = StudentSection.objects.filter(userprofile = user_profile)[0]
    education_details = HigherEducationDetail.objects.filter(userprofile = user_profile)
    employment_details = EmployementDetail.objects.filter(userprofile = user_profile)
    other_profiles = StudentSection.objects.exclude(id=student_section.id)[:5] #Change logic to show relevant profiles
    tags = user_profile.tags.all()
    return render_to_response("view_profile.html", RequestContext(request, {'user_profile': user_profile,
    				 'student_section': student_section, 'education_details':education_details,
    				 'employment_details': employment_details, 'other_profiles':other_profiles, 'tags': tags,}))

def edit_profile(request, profile_id):
    if not profile_id:
        return render_to_response("error.html", RequestContext(request, {}))
    
    try:
        user_profile=UserProfile.objects.get(id=profile_id)
    except ObjectDoesNotExist:
        return render_to_response("error.html", RequestContext(request, {}))
    
    StudentFormSet = modelformset_factory(StudentSection, exclude=('userprofile'), extra=0, can_delete=True)
    
    if request.method == 'POST':
        userprofileform = EditUserProfileForm(request.POST, instance=user_profile)
        studentformset = StudentFormSet(request.POST, queryset=StudentSection.objects.filter(userprofile=user_profile))

        if userprofileform.is_valid() and studentformset.is_valid():
            userprofileform.save()
            studentsections = studentformset.save(commit=False)
            for studentsection in studentsections:
                studentsection.userprofile = user_profile
                studentsection.save()
            
            return HttpResponseRedirect('/profile/view/'+profile_id)
        else:
            print studentformset.errors
            print userprofileform.errors
            return render_to_response("edit_profile.html", RequestContext(request, 
                                {'userprofileform': userprofileform,  
                                 'studentformset': studentformset,
                                 'profile_id': profile_id, }))
    else:
        userprofileform = EditUserProfileForm(instance=user_profile)
        studentformset = StudentFormSet(queryset=StudentSection.objects.filter(userprofile=user_profile))
    
    return render_to_response("edit_profile.html", RequestContext(request, 
                                {'userprofileform': userprofileform,  
                                 'studentformset': studentformset, 
                                 'profile_id': profile_id, }))

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
        if form.is_valid():
            user_profile.first_name = form.cleaned_data['name'].split()[0]
            user_profile.last_name = form.cleaned_data['name'].split()[1]
            print form.cleaned_data['course']
            student_section.branch_id = form.cleaned_data['course']
            student_section.year_of_graduation = form.cleaned_data['year_of_graduation']
            if form.cleaned_data['city'] != '':
                user_profile.city = City.objects.get(city=form.cleaned_data['city'])
            user_profile.about = form.cleaned_data['about']
            
            user_profile.tags.clear()
            for tagstr in form.cleaned_data['tagList'].split(','):
                if tagstr == '':
                    continue
                try:
                    tag = Tag.objects.get(name=tagstr)
                except ObjectDoesNotExist:
                    tag= Tag(name=tagstr, category=GENERIC)
                    tag.save()

                user_profile.tags.add(tag)

            user_profile.save()
            student_section.save()

            return HttpResponseRedirect('/profile/view/'+profile_id)
    else:
        branchid = None
        if student_section.branch:
            branchid = student_section.branch.id
        
        alltags = [tag.name for tag in Tag.objects.all()] 
        taglist = ",".join([tag.name for tag in user_profile.tags.all()]) 
            
        form = EditProfileBasicForm({'name':user_profile.get_full_name(), 'course':branchid ,'year_of_graduation':student_section.year_of_graduation,
         'city':user_profile.city, 'about':user_profile.about, 'branch':branchid, 'tagList': taglist,}, {'picture': ''})

    return render(request, "edit_profile_basic.html", {'form': form, 'profile_id': profile_id,'tags': json.dumps(alltags), })

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

#Sort with in available options and then with in greyed out options
def facet_sorting(facets):
    return sorted([x for x in facets if x[1]], key=lambda x: x[0]) + sorted([x for x in facets if not x[1]], key=lambda x: x[0]) 

def search(request):
    context = {}   
    context['request'] = request
        
    name = request.GET.get("name", '')
    branch = request.GET.get("branch", '')
    year = request.GET.get("year_of_passing", '')
    offset = request.GET.get("offset", '0')
    
    branch_facet = request.GET.get("branch_facet", '') 
    year_facet = request.GET.get("year_of_passing_facet", '') 
    city_facet = request.GET.get("city_facet", "")   
           
    sqs = SearchQuerySet().facet('branch')
    sqs = sqs.facet('year_of_passing')
    sqs = sqs.facet('city')
    
            
    if name or branch or year:
        context['form'] = ProfileSearchBasicForm(request.GET)
        if name:
            sqs = sqs.auto_query(name)
        if branch:
            sqs = sqs.filter(branch_exact = branch)
        if year:
            sqs = sqs.filter(year_of_passing_exact = year)
    else:
        context['form'] = ProfileSearchBasicForm()
    
    context['facets'] = sqs.facet_counts()
    
        
    ##Horrible hardcoding - need to tweak it - By Srihari
    #To compute the facet counts
    
    if branch_facet:
        temp = sqs.filter(branch_exact = branch_facet)
        context['facets']['fields']['year_of_passing'] = temp.filter(city_exact = city_facet).facet_counts()['fields']['year_of_passing'] if city_facet else temp.facet_counts()['fields']['year_of_passing'] 
    elif city_facet:
        context['facets']['fields']['year_of_passing'] = sqs.filter(city_exact = city_facet).facet_counts()['fields']['year_of_passing']
            
    if year_facet:
        temp = sqs.filter(year_of_passing_exact = year_facet)        
        context['facets']['fields']['branch'] = temp.filter(city_exact = city_facet).facet_counts()['fields']['branch'] if city_facet else temp.facet_counts()['fields']['branch'] 
    elif city_facet:
        context['facets']['fields']['branch'] = sqs.filter(city_exact = city_facet).facet_counts()['fields']['branch']
        
    if year_facet:
        temp = sqs.filter(year_of_passing_exact = year_facet)        
        context['facets']['fields']['city'] = temp.filter(branch_exact = branch_facet).facet_counts()['fields']['city'] if branch_facet else temp.facet_counts()['fields']['city'] 
    elif branch_facet:
        context['facets']['fields']['city'] = sqs.filter(branch_exact = branch_facet).facet_counts()['fields']['city']
           
    if branch_facet:
        sqs = sqs.filter(branch_exact = branch_facet)
        context['branch_facet_selected'] = branch_facet
    else:
        context['branch_facet_selected'] = ''
            
    if year_facet:
        sqs = sqs.filter(year_of_passing_exact = year_facet)
        context['year_facet_selected'] = year_facet
    else:
        context['year_facet_selected'] = ''
        
    if city_facet:
        sqs = sqs.filter(city_exact = city_facet)
        context['city_facet_selected'] = city_facet
    else:
        context['city_facet_selected'] = '' 

        
        
    context['facets']['fields']['year_of_passing'] = facet_sorting(context['facets']['fields']['year_of_passing'])
    context['facets']['fields']['city'] = facet_sorting(context['facets']['fields']['city'])
    context['facets']['fields']['branch'] = facet_sorting(context['facets']['fields']['branch'])
           

    offsetvalue = int(offset)
    results = sqs.order_by('name')
    context['resultcount'] = results.count()
    #results = results[offsetvalue:offsetvalue+20]
    context['results'] = results[:1000]

    #querystring = request.get_full_path()
    #if('?' not in querystring):
    #    querystring=''
    #else:
    #    querystring=querystring.split('?')[1]

    '''
    querystring=""
    if(name!=''):
        querystring+=('&name='+name)
    if(branch!=''):
        querystring+=('&branch='+branch)
    if(year!=''):
        querystring+=('&year_of_passing='+year)
    
    #querystring+='&offset='
    
    if(branch_facet!=''):
        querystring+=('&branch_facet='+branch_facet)
    if(year_facet!=''):
        querystring+=('&year_facet='+year_facet)

    print "Outgoing query string from search = [" +querystring+ "]"
    context['querystring'] = querystring
    '''
    
    return render(request, "search/search.html", context)

def getsearchresults(request):
    name = request.GET.get("name", '')
    branch = request.GET.get("branch", '')
    year = request.GET.get("year_of_passing", '')
    offset = request.GET.get("offset", '0')
    branch_facet = request.GET.get("branch_facet", '') 
    year_facet = request.GET.get("year_of_passing_facet", '')    

    offsetvalue = int(offset)
           
    sqs = SearchQuerySet().facet('branch')
    sqs = sqs.facet('year_of_passing')
        
    if name or branch or year:
        sqs = sqs.auto_query(name + branch + year)

    results = sqs.auto_query(branch_facet + year_facet).order_by('name')[offsetvalue:offsetvalue+20]
    print len(results)

    return results

def ajaxresponse(request):
    print "Incoming query to ajax = [" +request.get_full_path()+ "]"
    #results = getsearchresults(request)

    context = {}   
    context['request'] = request
        
    name = request.GET.get("name", '')
    branch = request.GET.get("branch", '')
    year = request.GET.get("year_of_passing", '')
    offset = request.GET.get("offset", '0')
    
    branch_facet = request.GET.get("branch_facet", '') 
    year_facet = request.GET.get("year_of_passing_facet", '')    
           
    sqs = SearchQuerySet().facet('branch')
    sqs = sqs.facet('year_of_passing')
        
    if name or branch or year:
        context['form'] = ProfileSearchBasicForm(request.GET)
        sqs = sqs.auto_query(name + branch + year)
    else:
        context['form'] = ProfileSearchBasicForm()
    
    context['facets'] = sqs.facet_counts()
        
    if branch_facet:
        context['facets']['fields']['year_of_passing'] = sqs.auto_query(branch_facet).facet_counts()['fields']['year_of_passing']
        context['branch_facet_selected'] = branch_facet
    else:
        context['branch_facet_selected'] = ''
            
    if year_facet:
        context['facets']['fields']['branch'] = sqs.auto_query(year_facet).facet_counts()['fields']['branch']
        context['year_facet_selected'] = year_facet
    else:
        context['year_facet_selected'] = ''

    offsetvalue=0
    if(offset!=''):
        offsetvalue = int(offset)
    results = sqs.auto_query(branch_facet + year_facet).order_by('name')
    context['resultcount'] = results.count()
    results = results[offsetvalue:offsetvalue+20]

    querystring=""
    if(name!=''):
        querystring+=('&name='+name)
    if(branch!=''):
        querystring+=('&branch='+branch)
    if(year!=''):
        querystring+=('&year_of_passing='+year)

    #querystring+=('&offset='+str(offsetvalue+20))
    
    if(branch_facet!=''):
        querystring+=('&branch_facet='+branch_facet)
    if(year_facet!=''):
        querystring+=('&year_facet='+year_facet)

    print "Outgoing query string from ajax = [" +querystring+ "]"
    context['querystring'] = querystring

    html=""
    if not results:
        html+="<p>Sorry, no results found.</p>\n"
    else:
        for result in results:
            html+="<div class=\"result_div\">\n"
            html+="<h2 class=\"name section-subtitle\">" +result.name+ "</h2>\n"
            if(result.branch):
                html+="<p class=\"branch\">" +result.branch+ "</p>\n"
            if(result.year_of_passing):
                html+="<p class=\"year_of_passing\">" +str(result.year_of_passing)+ "</p>\n"
            if(result.branch):
                html+="<p class=\"city\">" +result.branch+ "</p>\n"
            html+="</div>\n"
    #print html
    return HttpResponse(html)
