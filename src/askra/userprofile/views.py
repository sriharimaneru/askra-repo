from django.shortcuts import render_to_response, render
from django.template import RequestContext
from userprofile.models import UserProfile, Synonym, StudentSection, HigherEducationDetail, \
    EmploymentDetail, FacultySection, Employer, City , State, Country, HigherEducationBranch, \
    College, JobDesignation, JobDomain , RT_EMPLOYER, RT_CITY, \
    get_resource_model_from_value, get_resource_type_from_string
#from tag.models import Tag, GENERIC 
from userprofile.forms import EditUserProfileForm, ProfileSearchBasicForm
from django.http import HttpResponseRedirect, Http404
#from django.forms.util import ErrorList
from haystack.query import SearchQuerySet
from django.http import HttpResponse
import json
from django.forms.models import modelformset_factory
from django.views.generic.base import TemplateView, View
#from django.forms.formsets import formset_factory


class ShowProfileView(TemplateView):
    def get_template_names(self):
        profile_id = self.kwargs['profile_id']
        if not profile_id:
            return "error.html"
        else:
            return "view_profile.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        profile_id = self.kwargs['profile_id']
        
        if not profile_id:
            return context
    
        try:
            user_profile = UserProfile.objects.get(id=profile_id)
            context['user_profile'] = user_profile
        except UserProfile.DoesNotExist:
            return context
        
        student_sections = StudentSection.objects.filter(userprofile = user_profile)
        if student_sections:
            student_section = student_sections[0]
            context['student_section'] = student_section
            
            if student_section.branch:
                related_profiles = StudentSection.objects.filter(branch=student_section.branch, year_of_graduation=student_section.year_of_graduation).exclude(id=student_section.id)[:5]
            else:
                related_profiles = StudentSection.objects.filter(year_of_graduation=student_section.year_of_graduation).exclude(id=student_section.id)[:5]
            
            context['other_profiles'] = related_profiles 
            
        context['education_details'] = HigherEducationDetail.objects.filter(userprofile = user_profile)
        context['employment_details'] = EmploymentDetail.objects.filter(userprofile = user_profile)
        context['tags'] = user_profile.tags.all()
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if 'user_profile' in context:
            return TemplateView.render_to_response(self, context, **response_kwargs)
        else:
            raise Http404
    
class ErrorView(TemplateView):
    template_name="error.html"

class EditProfileView(TemplateView):
    
    StudentFormSet = modelformset_factory(StudentSection, exclude=('userprofile'), extra=0, can_delete=True)
    EmploymentFormSet = modelformset_factory(EmploymentDetail, exclude = ('userprofile'), extra=0, can_delete=True)
    HigherEducationFormSet = modelformset_factory(HigherEducationDetail, exclude = ('userprofile'), extra=0, can_delete=True)
    FacultyFormSet = modelformset_factory(FacultySection, exclude = ('userprofile'), extra=0, can_delete=True)
    
    def get_template_names(self):
        profile_id = self.kwargs['profile_id']
        if not profile_id:
            return "error.html"
        else:
            return "edit_profile.html"
    
    def get(self, request, *args, **kwargs):
        profile_id = self.kwargs['profile_id']
        
        try:
            user_profile=UserProfile.objects.get(id=profile_id)
        except UserProfile.DoesNotExist:
            raise Http404
        
        userprofileform = EditUserProfileForm(instance=user_profile)
        studentformset = self.StudentFormSet(queryset=StudentSection.objects.filter(userprofile=user_profile), prefix='student')
        employmentformset = self.EmploymentFormSet(queryset=EmploymentDetail.objects.filter(userprofile=user_profile), prefix='employment')
        highereducationformset = self.HigherEducationFormSet(queryset=HigherEducationDetail.objects.filter(userprofile=user_profile), prefix='highereducation')
        facultyformset = self.FacultyFormSet(queryset=FacultySection.objects.filter(userprofile=user_profile), prefix='faculty')
    
        return render_to_response("edit_profile.html", RequestContext(self.request, 
                                    {'userprofileform': userprofileform,  
                                     'studentformset': studentformset,
                                     'employmentformset': employmentformset,
                                     'higheredformset': highereducationformset,
                                     'facultyformset': facultyformset,
                                     'profile_id': profile_id, }))
    
    def post(self, request, *args, **kwargs):
        profile_id = self.kwargs['profile_id']
        try:
            user_profile=UserProfile.objects.get(id=profile_id)
        except UserProfile.DoesNotExist:
            raise Http404
        
        userprofileform = EditUserProfileForm(request.POST, request.FILES, instance=user_profile)
        studentformset = self.StudentFormSet(request.POST, queryset=StudentSection.objects.filter(userprofile=user_profile), prefix='student')
        employmentformset = self.EmploymentFormSet(request.POST, queryset=EmploymentDetail.objects.filter(userprofile=user_profile), prefix='employment')
        highereducationformset = self.HigherEducationFormSet(request.POST, queryset=HigherEducationDetail.objects.filter(userprofile=user_profile), prefix='highereducation')
        facultyformset = self.FacultyFormSet(request.POST, queryset=FacultySection.objects.filter(userprofile=user_profile), prefix='faculty')

        if userprofileform.is_valid() and studentformset.is_valid() and employmentformset.is_valid() and highereducationformset.is_valid() and facultyformset.is_valid():
            
            userprofileform.save()
            
            #Student Section
            for stform in studentformset:
                if stform not in studentformset.deleted_forms:
                    studentsection = stform.instance
                    if (studentsection.year_of_graduation is None or studentsection.year_of_graduation == '')\
                     and (studentsection.roll_num is None or studentsection.roll_num == '')\
                     and (studentsection.branch is None):
                        continue
                    studentsection.userprofile = user_profile
                    studentsection.save()
                
            for stform in studentformset.deleted_forms:
                studentsection = stform.instance
                if studentsection.pk:
                    studentsection.delete()
            
            #Employment Details
            for empform in employmentformset:
                if empform not in employmentformset.deleted_forms:
                    employment = empform.instance
                    if employment.pk:
                        employment.userprofile = user_profile
                        employment.save()
                
            for empform in employmentformset.deleted_forms:
                employment = empform.instance
                if employment.pk:
                    employment.delete()

            #Higher Education Details
            for edform in highereducationformset:
                if edform not in highereducationformset.deleted_forms:
                    highered = edform.instance
                    if highered.pk:
                        highered.userprofile = user_profile
                        highered.save()
                
            for edform in highereducationformset.deleted_forms:
                highered = edform.instance
                if highered.pk:
                    highered.delete()
            
            #Faculty Section
            for facultyform in facultyformset:
                if facultyform not in facultyformset.deleted_forms:
                    faculty = facultyform.instance
                    if faculty.pk:
                        faculty.userprofile = user_profile
                        faculty.save()
                
            for facultyform in facultyformset.deleted_forms:
                faculty = facultyform.instance
                if faculty.pk:
                    faculty.delete()            
            
            return HttpResponseRedirect('/profile/view/'+profile_id)
        else:
#            print studentformset.errors
#            print userprofileform.errors
            return render_to_response("edit_profile.html", RequestContext(self.request, 
                                {'userprofileform': userprofileform,  
                                 'studentformset': studentformset,
                                 'employmentformset': employmentformset,
                                 'higheredformset': highereducationformset,
                                 'facultyformset': facultyformset,
                                 'profile_id': profile_id, }))

def ajaxtest(request):

    return render_to_response('ajaxtest.html', {'dummy' : 123})


class ResourceListAjaxView(View):
    def get(self, request):
        results = self.get_resultset(request.GET['r'], request.GET['q'])
        return HttpResponse(json.dumps(results))
    
    def get_resultset(self, resource, query):
        resourcetype = get_resource_type_from_string(resource)
        if resourcetype is None:
            return []
        
        model = get_resource_model_from_value(resourcetype) 
        
        #1. Direct objects
        objects = model.objects.filter(name__icontains=query)
        results = [obj.name for obj in objects] 
        
        #2. Synonyms
        synonyms = Synonym.objects.filter(value__istartswith=query, resourcetype=resourcetype)
        parent_ids = [synonym.parent_id for synonym in synonyms]
        synonym_objects = model.objects.filter(id__in=parent_ids)
        results = results + [synonym.name for synonym in synonym_objects]
        results = list(set(results)) #To remove duplicates
        
        return results

        
#def show_profile(request, profile_id):
#    if not profile_id:
#        return render_to_response("error.html", RequestContext(request, {}))
#
#    user_profile = get_object_or_404(UserProfile, id=profile_id)
#    student_section = StudentSection.objects.filter(userprofile = user_profile)[0]
#    education_details = HigherEducationDetail.objects.filter(userprofile = user_profile)
#    employment_details = EmployementDetail.objects.filter(userprofile = user_profile)
#    other_profiles = StudentSection.objects.exclude(id=student_section.id)[:5] #Change logic to show relevant profiles
#    tags = user_profile.tags.all()
#    return render_to_response("view_profile.html", RequestContext(request, {'user_profile': user_profile,
#                     'student_section': student_section, 'education_details':education_details,
#                     'employment_details': employment_details, 'other_profiles':other_profiles, 'tags': tags,}))


#def edit_profile(request, profile_id):
#    if not profile_id:
#        return render_to_response("error.html", RequestContext(request, {}))
#    
#    try:
#        user_profile=UserProfile.objects.get(id=profile_id)
#    except ObjectDoesNotExist:
#        return render_to_response("error.html", RequestContext(request, {}))
#    
#    StudentFormSet = modelformset_factory(StudentSection, exclude=('userprofile'), extra=0, can_delete=True)
#    EmploymentFormSet = modelformset_factory(EmployementDetail, exclude = ('userprofile'), extra=0, can_delete=True)
#    HigherEducationFormSet = modelformset_factory(HigherEducationDetail, exclude = ('userprofile'), extra=0, can_delete=True)
#    FacultyFormSet = modelformset_factory(FacultySection, exclude = ('userprofile'), extra=0, can_delete=True)
#    
#    if request.method == 'POST':
#        userprofileform = EditUserProfileForm(request.POST, request.FILES, instance=user_profile)
#        studentformset = StudentFormSet(request.POST, queryset=StudentSection.objects.filter(userprofile=user_profile))
#        employmentformset = EmploymentFormSet(request.POST, queryset=EmployementDetail.objects.filter(userprofile=user_profile))
#        highereducationformset = HigherEducationFormSet(request.POST, queryset=HigherEducationDetail.objects.filter(userprofile=user_profile))
#        facultyformset = FacultyFormSet(request.POST, queryset=FacultySection.objects.filter(userprofile=user_profile))
#
#        if userprofileform.is_valid() and studentformset.is_valid() and employmentformset.is_valid() and highereducationformset.is_valid() and facultyformset.is_valid():
#            userprofileform.save()
#            
#            #Student Section
#            for stform in studentformset:
#                if stform not in studentformset.deleted_forms:
#                    studentsection = stform.instance
#                    if (studentsection.year_of_graduation is None or studentsection.year_of_graduation == '')\
#                     and (studentsection.roll_num is None or studentsection.roll_num == '')\
#                     and (studentsection.branch is None):
#                        continue
#                    studentsection.userprofile = user_profile
#                    studentsection.save()
#                
#            for stform in studentformset.deleted_forms:
#                studentsection = stform.instance
#                if studentsection.pk:
#                    studentsection.delete()
#            
#            #Employment Details
#            for empform in employmentformset:
#                if empform not in employmentformset.deleted_forms:
#                    employment = empform.instance
#                    employment.userprofile = user_profile
#                    employment.save()
#                
#            for empform in employmentformset.deleted_forms:
#                employment = empform.instance
#                if employment.pk:
#                    employment.delete()
#
#            #Higher Education Details
#            for edform in highereducationformset:
#                if edform not in highereducationformset.deleted_forms:
#                    highered = edform.instance
#                    highered.userprofile = user_profile
#                    highered.save()
#                
#            for edform in highereducationformset.deleted_forms:
#                highered = edform.instance
#                if highered.pk:
#                    highered.delete()
#            
#            #Faculty Section
#            for facultyform in facultyformset:
#                if facultyform not in facultyformset.deleted_forms:
#                    faculty = facultyform.instance
#                    faculty.userprofile = user_profile
#                    faculty.save()
#                
#            for facultyform in facultyformset.deleted_forms:
#                faculty = facultyform.instance
#                if faculty.pk:
#                    faculty.delete()            
#            
#            return HttpResponseRedirect('/profile/view/'+profile_id)
#        else:
##            print studentformset.errors
##            print userprofileform.errors
#            return render_to_response("edit_profile.html", RequestContext(request, 
#                                {'userprofileform': userprofileform,  
#                                 'studentformset': studentformset,
#                                 'employmentformset': employmentformset,
#                                 'higheredformset': highereducationformset,
#                                 'facultyformset': facultyformset,
#                                 'profile_id': profile_id, }))
#    else:
#        userprofileform = EditUserProfileForm(instance=user_profile)
#        studentformset = StudentFormSet(queryset=StudentSection.objects.filter(userprofile=user_profile))
#        employmentformset = EmploymentFormSet(queryset=EmployementDetail.objects.filter(userprofile=user_profile))
#        highereducationformset = HigherEducationFormSet(queryset=HigherEducationDetail.objects.filter(userprofile=user_profile))
#        facultyformset = FacultyFormSet(queryset=FacultySection.objects.filter(userprofile=user_profile))
#    
#    return render_to_response("edit_profile.html", RequestContext(request, 
#                                {'userprofileform': userprofileform,  
#                                 'studentformset': studentformset,
#                                 'employmentformset': employmentformset,
#                                 'higheredformset': highereducationformset,
#                                 'facultyformset': facultyformset,
#                                 'profile_id': profile_id, }))

#class ProfileBulkUploadView(TemplateView):
#    def get(self, request, *args, **kwargs):
#        form = ProfileBulkUploadForm()
#        return render(request, "profile_bulk_upload.html", {'form':form, })
#    
#    def post(self, request, *args, **kwargs):
#        form = ProfileBulkUploadForm(request.POST, request.FILES)
#        if form.is_valid():
#            errors = form._errors.setdefault("uploaded_file", ErrorList())
#            reader = csv.DictReader(request.FILES['uploaded_file'])
#            for row in reader:
#                first_name = row['First Name']
#                last_name = row['Last Name']
#                phone_number = row['Phone Number']
#                email = row['Email']
#                gender = row['Gender']
#                role = row['User Role']
#                city = row['City']
#
#                try:
#                    user_profile=UserProfile.objects.get(email=email)
#                    text = "A profile with email ID [" + email + "] already exists. Updated the other fields."
#                    user_profile.first_name = first_name
#                    user_profile.last_name = last_name
#                    user_profile.phone_number = phone_number
#                    user_profile.email = email
#                except ObjectDoesNotExist:
#                    user_profile = UserProfile(first_name=first_name, 
#                                               last_name=first_name,
#                                               email=email,
#                                               phone_number=phone_number)
#                    text = "Added new profile with email ID [" + email + "]"
#
#                errors.append(text)
#                user_profile.set_gender(gender)
#                user_profile.set_role(role)
#                user_profile.set_place(city)
#                user_profile.save()
#                
#            errors.append("Bulk upload successful")
#        return render(request, "profile_bulk_upload.html", {'form':form, })

#def edit_profile_basic(request, profile_id):
#    if not profile_id:
#        return render_to_response("error.html", RequestContext(request, {}))
#
#    user_profile=UserProfile.objects.get(id=profile_id)
#    student_section=StudentSection.objects.filter(userprofile = user_profile)[0]
#
#    if request.method=='POST':
#        form = EditProfileBasicForm(request.POST, request.FILES)
#        if form.is_valid():
#            user_profile.first_name = form.cleaned_data['name'].split()[0]
#            user_profile.last_name = form.cleaned_data['name'].split()[1]
#            print form.cleaned_data['course']
#            student_section.branch_id = form.cleaned_data['course']
#            student_section.year_of_graduation = form.cleaned_data['year_of_graduation']
#            if form.cleaned_data['city'] != '':
#                user_profile.city = City.objects.get(city=form.cleaned_data['city'])
#            user_profile.about = form.cleaned_data['about']
#            
#            user_profile.tags.clear()
#            for tagstr in form.cleaned_data['tagList'].split(','):
#                if tagstr == '':
#                    continue
#                try:
#                    tag = Tag.objects.get(name=tagstr)
#                except ObjectDoesNotExist:
#                    tag= Tag(name=tagstr, category=GENERIC)
#                    tag.save()
#
#                user_profile.tags.add(tag)
#
#            user_profile.save()
#            student_section.save()
#
#            return HttpResponseRedirect('/profile/view/'+profile_id)
#    else:
#        branchid = None
#        if student_section.branch:
#            branchid = student_section.branch.id
#        
#        alltags = [tag.name for tag in Tag.objects.all()] 
#        taglist = ",".join([tag.name for tag in user_profile.tags.all()]) 
#            
#        form = EditProfileBasicForm({'name':user_profile.get_full_name(), 'course':branchid ,'year_of_graduation':student_section.year_of_graduation,
#         'city':user_profile.city, 'about':user_profile.about, 'branch':branchid, 'tagList': taglist,}, {'picture': ''})
#
#    return render(request, "edit_profile_basic.html", {'form': form, 'profile_id': profile_id,'tags': json.dumps(alltags), })
#
#def edit_profile_weblinks(request, profile_id):
#    if not profile_id:
#        return render_to_response("error.html", RequestContext(request, {}))
#
#    user_profile=UserProfile.objects.get(id=profile_id)
#
#    if request.method=='POST':
#        form = EditProfileWeblinksForm(request.POST)
#        if form.is_valid():
#            user_profile.facebook_url = form.cleaned_data['facebook_url']
#            user_profile.twitter_url = form.cleaned_data['twitter_url']
#            user_profile.linked_url = form.cleaned_data['linkedin_url']
#            user_profile.save()
#            return HttpResponseRedirect('/profile/view/'+profile_id)
#    else:
#        form = EditProfileWeblinksForm({'facebook_url':user_profile.facebook_url, 
#            'twitter_url': user_profile.twitter_url, 'linkedin_url': user_profile.linked_url})
#
#    return render(request, "edit_profile_weblinks.html", {'form': form, 'profile_id': profile_id,})
#
#
#def edit_profile_education(request, profile_id):
#    if not profile_id:
#        return render_to_response("error.html", RequestContext(request, {}))
#
#    user_profile=UserProfile.objects.get(id=profile_id)
#    #student_section = StudentSection.objects.filter(userprofile = user_profile)[0]
#    education_details = HigherEducationDetail.objects.filter(userprofile=user_profile)
#    EditProfileEducationFormSet = formset_factory(EditProfileEducationForm, extra=0)
#
#    if request.method == 'POST':
#        formset = EditProfileEducationFormSet(request.POST,request.FILES)
#        if formset.is_valid():
#            for i in range(0,formset.total_form_count()):
#                form = formset.forms[i]
#                education_details[i].college = form.cleaned_data['college']
#                education_details[i].degree = form.cleaned_data['degree']
#                education_details[i].branch = form.cleaned_data['branch']
#                education_details[i].year_of_graduation = form.cleaned_data['year_of_graduation']
#                education_details[i].save()
#            return HttpResponseRedirect('/profile/view/'+profile_id)
#    else:
#        formset = EditProfileEducationFormSet()
#        for i in range(0,len(education_details)):
#            form = EditProfileEducationForm({'year_of_graduation':education_details[i].year_of_graduation})
#            formset.forms.append(form)
#
#    return render(request, "edit_profile_education.html", {'formset':formset, 'profile_id':profile_id, })
#
#
#def edit_profile_employment(request, profile_id):
#    if not profile_id:
#        return render_to_response("error.html", RequestContext(request, {}))
#
#    user_profile=UserProfile.objects.get(id=profile_id)
#    employment_details = EmployementDetail.objects.filter(userprofile = user_profile)
#    EditProfileEmploymentFormSet = formset_factory(EditProfileEmploymentForm, extra=0)
#
#    if request.method == 'POST':
#        formset = EditProfileEmploymentFormSet(request.POST, request.FILES)
#        if formset.is_valid():
#            for i in range(0,formset.total_form_count()):
#                form = formset.forms[i]
#                employment_details[i].employer = form.cleaned_data['employer']
#                employment_details[i].designation = form.cleaned_data['designation']
#                employment_details[i].domain = form.cleaned_data['domain']
#                employment_details[i].date_of_joining = form.cleaned_data['date_of_joining']
#                employment_details[i].date_of_leaving = form.cleaned_data['date_of_leaving']
#                employment_details[i].save()
#            return HttpResponseRedirect('/profile/view/'+profile_id)
#    else:
#        formset = EditProfileEmploymentFormSet()
#        for i in range(0,len(employment_details)):
#            form = EditProfileEmploymentForm({'date_of_joining':employment_details[i].date_of_joining, 'date_of_leaving':employment_details[i].date_of_leaving})
#            formset.forms.append(form)
#
#    return render(request, "edit_profile_employment.html", {'formset':formset, 'profile_id':profile_id, })



#def profile_bulk_upload(request,x):
#    if request.method == 'POST':
#        form = ProfileBulkUploadForm(request.POST, request.FILES)
#        if form.is_valid():
#            errors = form._errors.setdefault("uploaded_file", ErrorList())
#            reader = csv.DictReader(request.FILES['uploaded_file'])
#            for row in reader:
#                first_name = row['First Name']
#                last_name = row['Last Name']
#                phone_number = row['Phone Number']
#                email = row['Email']
#                gender = row['Gender']
#                role = row['User Role']
#                city = row['City']
#
#                try:
#                    user_profile=UserProfile.objects.get(email=email)
#                    text = "A profile with email ID [" + email + "] already exists. Updated the other fields."
#                    user_profile.first_name = first_name
#                    user_profile.last_name = last_name
#                    user_profile.phone_number = phone_number
#                    user_profile.email = email
#                except ObjectDoesNotExist:
#                    user_profile = UserProfile(first_name=first_name, 
#                                               last_name=first_name,
#                                               email=email,
#                                               phone_number=phone_number)
#                    text = "Added new profile with email ID [" + email + "]"
#
#                errors.append(text)
#                user_profile.set_gender(gender)
#                user_profile.set_role(role)
#                user_profile.set_city(city)
#                user_profile.save()
#                
#            errors.append("Bulk upload successful")
#    else:
#        form = ProfileBulkUploadForm()
#    return render(request, "profile_bulk_upload.html", {'form':form, })

##Sort with in available options and then with in greyed out options
#def facet_sorting(facets):
#    return sorted([x for x in facets if x[1]], key=lambda x: x[0]) + sorted([x for x in facets if not x[1]], key=lambda x: x[0]) 


#def search(request):
#    context = {}   
#    context['request'] = request
#        
#    name = request.GET.get("name", '')
#    branch = request.GET.get("branch", '')
#    year = request.GET.get("year_of_passing", '')
#    offset = request.GET.get("offset", '0')
#    
#    branch_facet = request.GET.get("branch_facet", '') 
#    year_facet = request.GET.get("year_of_passing_facet", '')
#    if year_facet:
#        year_facet = [int(x) for x in year_facet.split(",")] 
#    city_facet = request.GET.get("city_facet", "")   
#           
#    sqs = SearchQuerySet().facet('branch')
#    sqs = sqs.facet('year_of_passing')
#    sqs = sqs.facet('city')
#    
#            
#    if name or branch or year:
#        context['form'] = ProfileSearchBasicForm(request.GET)
#        if name:
#            sqs = sqs.auto_query(name)
#        if branch:
#            sqs = sqs.filter(branch_exact = branch)
#        if year:
#            sqs = sqs.filter(year_of_passing_exact = year)
#    else:
#        context['form'] = ProfileSearchBasicForm()
#    
#    context['facets'] = sqs.facet_counts()
#    
#        
#    ##Horrible hardcoding - need to tweak it - By Srihari
#    #To compute the facet counts
#    
#    if branch_facet:
#        temp = sqs.filter(branch_exact = branch_facet)
#        context['facets']['fields']['year_of_passing'] = temp.filter(city_exact = city_facet).facet_counts()['fields']['year_of_passing'] if city_facet else temp.facet_counts()['fields']['year_of_passing'] 
#    elif city_facet:
#        context['facets']['fields']['year_of_passing'] = sqs.filter(city_exact = city_facet).facet_counts()['fields']['year_of_passing']
#            
#    if year_facet:
#        temp = sqs.filter(year_of_passing_exact__in = year_facet)        
#        context['facets']['fields']['branch'] = temp.filter(city_exact = city_facet).facet_counts()['fields']['branch'] if city_facet else temp.facet_counts()['fields']['branch'] 
#    elif city_facet:
#        context['facets']['fields']['branch'] = sqs.filter(city_exact = city_facet).facet_counts()['fields']['branch']
#        
#    if year_facet:
#        temp = sqs.filter(year_of_passing_exact__in = year_facet)        
#        context['facets']['fields']['city'] = temp.filter(branch_exact = branch_facet).facet_counts()['fields']['city'] if branch_facet else temp.facet_counts()['fields']['city'] 
#    elif branch_facet:
#        context['facets']['fields']['city'] = sqs.filter(branch_exact = branch_facet).facet_counts()['fields']['city']
#           
#    if branch_facet:
#        sqs = sqs.filter(branch_exact = branch_facet)
#        context['branch_facet_selected'] = branch_facet
#    else:
#        context['branch_facet_selected'] = ''
#            
#    if year_facet:
#        sqs = sqs.filter(year_of_passing_exact__in = year_facet)
#        context['year_facets_selected'] = [str(x) for x in year_facet]
#    else:
#        context['year_facets_selected'] = ''
#        
#    if city_facet:
#        sqs = sqs.filter(city_exact = city_facet)
#        context['city_facet_selected'] = city_facet
#    else:
#        context['city_facet_selected'] = '' 
#
#        
#    print context['year_facets_selected']
#    
#    context['facets']['fields']['year_of_passing'] = facet_sorting(context['facets']['fields']['year_of_passing'])
#    context['facets']['fields']['city'] = facet_sorting(context['facets']['fields']['city'])
#    context['facets']['fields']['branch'] = facet_sorting(context['facets']['fields']['branch'])
#           
#
#    offsetvalue = int(offset)
#    results = sqs.order_by('name')
#    context['resultcount'] = results.count()
#    #results = results[offsetvalue:offsetvalue+20]
#    context['results'] = results[:1000]
#
#    #querystring = request.get_full_path()
#    #if('?' not in querystring):
#    #    querystring=''
#    #else:
#    #    querystring=querystring.split('?')[1]
#
#    '''
#    querystring=""
#    if(name!=''):
#        querystring+=('&name='+name)
#    if(branch!=''):
#        querystring+=('&branch='+branch)
#    if(year!=''):
#        querystring+=('&year_of_passing='+year)
#    
#    #querystring+='&offset='
#    
#    if(branch_facet!=''):
#        querystring+=('&branch_facet='+branch_facet)
#    if(year_facet!=''):
#        querystring+=('&year_facet='+year_facet)
#
#    print "Outgoing query string from search = [" +querystring+ "]"
#    context['querystring'] = querystring
#    '''
#    
#    return render(request, "search/search.html", context)


#def reg_step_2(request,x):
#    user_profiles = UserProfile.objects.filter(role=ALUMNI)
#    branches = Branch.objects.all()
#    student_sections = list()
#    for user_profile in user_profiles:
#        student_section = StudentSection.objects.get(userprofile=user_profile)
#        student_sections.append(student_section)
#
#    return render_to_response("reg-step-2.html", RequestContext(request, {'student_sections':student_sections, 'branches':branches}))
#
#def reg_step_3(request,x):
#    return render_to_response("reg-step-3.html", RequestContext(request, {}))
