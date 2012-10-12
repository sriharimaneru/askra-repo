from django.db import models
from django import forms
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User
from tag.models import Tag
from calendar import calendar

ALUMNI = 0
STUDENT = 1
FACULTY = 2
ALUMNI_FACULTY = 3
USER_ROLES = ((ALUMNI, "Alumni"),
              (STUDENT, "Student"),
              (FACULTY, "Faculty"),
              (ALUMNI_FACULTY, "Alumni and Faculty"))

MALE = 0
FEMALE = 1
GENDER_CHOICES = ((MALE, "Male"),
               (FEMALE, "Female"),)

UNLINKED = 0
LINKED = 1
APPROVED = 2
PROFILE_STATUS = ((UNLINKED, "Unlinked"),
                  (LINKED, "Linked"),
                  (APPROVED, "Approved"),) 


TAG_APPROVED = 0
TAG_PENDING = 1
TAG_REJECTED = 2
USERTAG_STATUS_OPTIONS = ((TAG_APPROVED, "Approved"),
                          (TAG_PENDING, "Pending"),
                          (TAG_REJECTED, "Rejected"),)

class City(models.Model):
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    
    def __unicode__(self):
        return self.city
    
    class Meta:
        verbose_name_plural = "Cities"


class UserProfile(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    role = models.IntegerField("User Role", choices=USER_ROLES, help_text="Choose the appropriate userRole")
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=75)
    gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    photo = models.ImageField("Profile picture", upload_to="profile_pictures/", null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True)
    twitter_url = models.URLField(max_length=100, null=True, blank=True)
    facebook_url = models.URLField(max_length=100, null=True, blank=True)
    linked_url = models.URLField(max_length=100, null=True, blank=True)
    website_url = models.URLField(max_length=100, null=True, blank=True)
    profile_status = models.IntegerField(choices = PROFILE_STATUS, null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name
    
    
class Branch(models.Model):
    branch = models.CharField(max_length=200, null=True, blank=True)
    course = models.CharField(max_length=200, null=True, blank=True)
    
    def get_full_name(self):
        return self.course + ", " + self.branch

    def __unicode__(self):
        return self.get_full_name()

    class Meta:
        verbose_name_plural = "Branches"

class StudentSection(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    roll_num = models.CharField(max_length=20, null=True, blank=True)
    year_of_graduation = models.IntegerField(null=True, blank=True, help_text="Year of passing out")
    branch = models.ForeignKey(Branch, null=True, blank=True)

    def get_full_qualification(self):
        return self.branch.get_full_name() + " " + str(self.year_of_graduation)
  
    
class Employer(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name    

class JobDesignation(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name     
    
class JobDomain(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name     
    
                
class EmployementDetail(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    employer = models.ForeignKey(Employer)
    designation = models.ForeignKey(JobDesignation)
    domain = models.ForeignKey(JobDomain)
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)

    def get_employment_period(self):
        return str(self.date_of_joining.strftime("%b")) + ", " + str(self.date_of_joining.year)+ " - " + str(self.date_of_leaving.strftime("%b")) + ", " + str(self.date_of_leaving.year)

class College(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name     
    
        
class Degree(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name     

class HigherEducationBranch(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name     
        
class HigherEducationDetail(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    college = models.ForeignKey(College)
    degree = models.ForeignKey(Degree)
    branch = models.ForeignKey(HigherEducationBranch)
    year_of_graduation = models.IntegerField(null=True, blank=True, help_text="Year of passing out")


class Department(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name     
    
        
class FacultyDesignation(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name     
    
        
class FacultySection(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    deparment = models.ForeignKey(Department)
    designation = models.ForeignKey(FacultyDesignation)
    
class UserTag(models.Model):  
    userprofile = models.ForeignKey(UserProfile)
    tag = models.ForeignKey(Tag)
    status = models.IntegerField("Tag Category", choices=USERTAG_STATUS_OPTIONS,)

class EditProfileBasicForm(forms.Form):
    name = forms.CharField(max_length=100)
    course = forms.ChoiceField(choices=[ (branch.id, branch.course) for branch in Branch.objects.all() ])
    branch = forms.ChoiceField(choices=[ (branch.id, branch.branch) for branch in Branch.objects.all() ])
    year_of_graduation = forms.IntegerField(min_value=1900)
    city = forms.CharField(max_length=50)
    about = forms.CharField()

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