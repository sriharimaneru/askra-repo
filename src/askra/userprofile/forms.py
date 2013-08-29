from django import forms
from models import *
from django.forms import widgets
from django.template.loader import get_template
from django.template import Context

class EditUserProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(input_formats=['%d/%m/%Y',], required=False,
                                    widget = widgets.DateInput(format='%d/%m/%Y'))
    photo = forms.ImageField(widget = widgets.FileInput(), required=False)
 
    def clean(self):
        super(forms.ModelForm, self).clean()
        return self.cleaned_data
    
    class Meta:
        model = UserProfile
        exclude = ('user', 'role', 'profile_status', )


class EditStudentSectionForm(forms.ModelForm):
    class Meta:
        model = StudentSection
        exclude = ('userprofile')
    
    def as_custom(self):
        t = get_template('student_section_form.html')
        return t.render(Context({'stform': self},))
    
class EditProfileBasicForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    course = forms.ChoiceField(choices=[(branch.id, branch.course) for branch in Branch.objects.all()], required=False)    
    branch = forms.ChoiceField(choices=[(branch.id, branch.branch) for branch in Branch.objects.all()], required=False)
    year_of_graduation = forms.IntegerField(min_value=1900, required=False)
    city = forms.CharField(max_length=50, required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)
    picture = forms.ImageField(label="Profile picture", required=False)
    tagList = forms.CharField(max_length=400, required=False, widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(EditProfileBasicForm, self).__init__(*args, **kwargs)
        self.fields['course'].choices.insert(0, ('','None'))
        self.fields['branch'].choices.insert(0, ('','None'))

    #def __init__(self, curr_branch_course, *args, **kwargs):
    #    super(EditProfileBasicForm, self).__init__(*args, **kwargs)

        #courses = list()
        #branches = list()
        #branch_courses = Branch.objects.all()
        #for branch_course in branch_courses:
        #    courses.append(branch_course.course)
        #    if curr_branch_course.course == branch_course.course:
        #        branches.append(branch_course.branch)
        #courses = list(set(courses))
        #branches = list(set(branches))

        #self.fields['course'] = forms.ChoiceField(initial=courses.index(curr_branch_course.course),choices=[(courses.index(course), course) for course in courses])
        #self.fields['branch'] = forms.ChoiceField(initial=branches.index(curr_branch_course.branch),choices=[(branches.index(branch), branch) for branch in branches])

class EditProfileWeblinksForm(forms.Form):
    facebook_url = forms.URLField(max_length=100)
    twitter_url = forms.URLField(max_length=100)
    linkedin_url = forms.URLField(max_length=100)

class EditProfileEducationForm(forms.Form):
    college = forms.ChoiceField(choices=[(college.id, college.name) for college in College.objects.all()])
    degree = forms.ChoiceField(choices=[(degree.id, degree.name) for degree in Degree.objects.all()])
    branch = forms.ChoiceField(choices=[(branch.id, branch.name) for branch in HigherEducationBranch.objects.all()])
    year_of_graduation = forms.IntegerField(min_value=1900)

class EditProfileEmploymentForm(forms.Form):
    employer = forms.ChoiceField(choices=[(employer.id, employer.name) for employer in Employer.objects.all()])
    designation = forms.ChoiceField(choices=[(designation.id, designation.name) for designation in JobDesignation.objects.all()])
    domain = forms.ChoiceField(choices=[(domain.id, domain.name) for domain in JobDomain.objects.all()])
    date_of_joining = forms.DateField()
    date_of_leaving = forms.DateField()

class ProfileBulkUploadForm(forms.Form):
    uploaded_file = forms.FileField(label='Select a csv file', help_text='Maximum 1000 rows')
    


