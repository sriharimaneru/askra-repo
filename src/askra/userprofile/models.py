from django.db import models
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