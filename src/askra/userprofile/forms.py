from django import forms
from django.forms.formsets import formset_factory
from userprofile.models import *

class EditProfileBasicForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    course = forms.ChoiceField(choices=[(branch.id, branch.course) for branch in Branch.objects.all()], required=False)    
    branch = forms.ChoiceField(choices=[(branch.id, branch.branch) for branch in Branch.objects.all()], required=False)
    year_of_graduation = forms.IntegerField(min_value=1900, required=False)
    city = forms.CharField(max_length=50, required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)
    picture = forms.ImageField(label="Profile picture", required=False)
    
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
    
class ProfileSearchBasicForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    branches_list = [(branch.branch, branch.branch) for branch in Branch.objects.all() if branch.branch]
    branches_list = [("", "All")] + sorted(branches_list, key=lambda x: x[1])
    branch = forms.ChoiceField(choices = branches_list, required=False)
    year_of_passing = forms.ChoiceField(choices = [("", "All")] + [(x,x) for x in range(1964, 2009)] + [("2011", "2011"), ("2013", "2013"), ("2014", "2014"), ("2015", "2015"), ("2016", "2016")], required=False)


