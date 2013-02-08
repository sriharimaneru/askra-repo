from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from calendar import calendar
import csv
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from xlrd import open_workbook
from django.db.models import Q
import logging
from utils import *

log = logging.getLogger('GROUPIFY')

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

IGNORE = 0
SAVE = 1
DO_NOTHING = 2
ACTION_CHOICES = ((IGNORE, "Ignore"),
               (SAVE, "Save"),
               (DO_NOTHING, "Do nothing"),)
            

class City(models.Model):
    city = models.CharField(max_length=150,null=True, blank=True, unique=True)
    state = models.CharField(max_length=150,null=True, blank=True)
    country = models.CharField(max_length=150,null=True, blank=True)
    
    def __unicode__(self):
        if(self.city):
            return self.city
        elif(self.state):
            return self.state
        else:
            return self.country
    
    class Meta:
        verbose_name_plural = "Cities"

class CitySynonym(models.Model):
    city = models.ForeignKey(City)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    role = models.IntegerField("User Role", choices=USER_ROLES, help_text="Choose the appropriate userRole")
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=75)
    gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=35, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    photo = models.ImageField("Profile picture", upload_to="profile_pictures/", null=True, blank=True, default='{{STATIC_URL}}default_male_profile_picture.jpg')
    city = models.ForeignKey(City, null=True, blank=True)
    twitter_url = models.URLField(max_length=100, null=True, blank=True)
    facebook_url = models.URLField(max_length=100, null=True, blank=True)
    linked_url = models.URLField(max_length=100, null=True, blank=True)
    website_url = models.URLField(max_length=100, null=True, blank=True)
    profile_status = models.IntegerField(choices = PROFILE_STATUS, null=True, blank=True, default=UNLINKED)
    about = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def set_gender(self, value):
        if(value):
            gender_dict=dict(GENDER_CHOICES)
            self.gender = [key for key,val in gender_dict.items() if val==value ][0]
        return self

    def set_role(self, value):
        if(value):
            role_dict=dict(USER_ROLES)
            self.role = [key for key,val in role_dict.items() if val==value ][0]
        return self

    def set_city(self, value):
        value=value.strip()
        if(value):
            if('/' in value): #Multiple cities separated by '/'. We take the first one.
                value = value.split('/')[0].strip()
            cities=City.objects.filter(Q(city__iexact=value) | Q(state__iexact=value) | Q(country__iexact=value))
            if(cities):
                self.city = cities[0]
            else:
                synonyms=CitySynonym.objects.filter(name__iexact=value)
                if(synonyms):
                    self.city = synonyms[0].city
                else:
                    log.debug("IMPORTANT: City not added: [" + value + "]")

        return self

    def get_branch(self):
        if(StudentSection.objects.filter(userprofile=self)):
            if(StudentSection.objects.filter(userprofile=self)[0].branch):
                return StudentSection.objects.filter(userprofile=self)[0].branch.branch
        else:
            return ""

    get_branch.short_description = "Branch"

    def get_year_of_graduation(self):
        if(StudentSection.objects.filter(userprofile=self)):
            return StudentSection.objects.filter(userprofile=self)[0].year_of_graduation
        else:
            return ""

    get_year_of_graduation.short_description = "Graudation Year"

    
class Branch(models.Model):
    branch = models.CharField(max_length=200, null=True, blank=True)
    course = models.CharField(max_length=200, null=True, blank=True)
    
    def get_full_name(self):
        return self.course + ", " + self.branch

    def __unicode__(self):
        return self.get_full_name()

    class Meta:
        verbose_name_plural = "Branches"

class BranchSynonym(models.Model):
    branch = models.ForeignKey(Branch)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class StudentSection(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    roll_num = models.CharField(max_length=20, null=True, blank=True)
    year_of_graduation = models.IntegerField(null=True, blank=True, help_text="Year of passing out")
    branch = models.ForeignKey(Branch, null=True, blank=True)

    def get_full_qualification(self):
        return self.branch.get_full_name() + " " + str(self.year_of_graduation)

    def set_branch(self, value):
        value=value.strip()
        if(value):
            branches=Branch.objects.filter(branch__iexact=value)
            if(branches):
                self.branch=branches[0]
            else:
                synonyms=BranchSynonym.objects.filter(name__iexact=value)
                if(synonyms):
                    self.branch=synonyms[0].branch
                else:
                    log.debug("Could not find branch [" + value + "]. Therefore not setting the value")
        return self

    
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
        if(self.date_of_joining is None or self.date_of_leaving is None or self.date_of_joining=="" or self.date_of_leaving==""):
            return ""
        else:
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
    
class CsvUpload(models.Model):
    uploaded_file = models.FileField(upload_to="data/upload_files/", blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    
    def save(self,**kwargs):
        log.debug(self.description)
        reader = csv.DictReader(self.uploaded_file)
        for row in reader:
            first_name = row['First Name']
            last_name = row['Last Name']
            phone_number = row['Phone Number']
            emailErrorRow = isValidEmailId(row['Email'])
            if(emailErrorRow is True):
                email = row['Email']
            else:
                email=''
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

            log.debug(text)
            user_profile.set_gender(gender)
            user_profile.set_role(role)
            user_profile.set_city(city)
            user_profile.save()
                
        log.debug("Bulk upload successful")
        super(CsvUpload, self).save(**kwargs)
        if(emailErrorRow is not True):
            errorRow.csv_file=self;
            errorRow.save()
    
    
class ErrorRow(models.Model):
    csv_file = models.ForeignKey(CsvUpload)
    name = models.CharField(max_length=20)
    reason = models.TextField()
    action = models.IntegerField(choices = ACTION_CHOICES, default = DO_NOTHING)

    def save(self,**kwargs):
        #if action is ignore, do nothing 
        
        #if action is save, delete it and create correspoinding user profile
        
        #if action is ignore, just delete it
        
        
        super(ErrorRow, self).save(**kwargs)

class XlsUpload(models.Model):
    uploaded_file = models.FileField(upload_to="data/upload_files/", blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    
    def save(self,**kwargs):
        wb = open_workbook(file_contents=self.uploaded_file.read())
        log.debug("Opening workbook ["+self.uploaded_file.url+"] to bulk upload profiles")
        for s in wb.sheets():
            log.debug("Sheet: ["+s.name+"], Num Rows: ["+str(s.nrows)+"], Num Cols: ["+str(s.ncols)+"]")
            colIndex = {}
            for row in range(s.nrows):
                if(row==0): #Header
                    for col in range(s.ncols):
                        header = (str(s.cell(row,col).value)).lower()
                        colIndex[header] = col
                    #log.debug("Resulting colIndex Map index : "+str(colIndex))
                else: #Data
                    name, mobile, email, branch, city, address, yog, rollno = '','','','','','',0,0
                    first_name, last_name = '',''

                    #Part 1: Extract all necessary values from the row.
                    #Add all fields here.
                    if(colIndex.get('email') is not None):
                        email = str(s.cell(row,colIndex['email']).value)
                        if(email!='' and (isValidEmailId(email) is False)):
                            log.debug("The email ID [" + email + "] is invalid. Ignoring it.")
                            email='' #For invalid email ID treat it as if the email ID is not present
                    else:
                        log.debug("Email does not exist in the excel sheet")

                    if(colIndex.get('name') is not None):
                        name = str(s.cell(row,colIndex['name']).value)
                        if(name):
                            try:
                                (first_name, last_name) = name.split(' ',1)
                            except ValueError:
                                first_name = name
                        
                    if(colIndex.get('mobile') is not None):
                        mobile = str(s.cell(row,colIndex['mobile']).value)

                    if(colIndex.get('branch') is not None):
                        branch = str(s.cell(row,colIndex['branch']).value)

                    if(colIndex.get('city') is not None):
                        city = str(s.cell(row,colIndex['city']).value)

                    if(colIndex.get('address') is not None):
                        address = (str(s.cell(row,colIndex['address']).value))
                    
                    if(colIndex.get('rollno') is not None):
                        rollnostr = s.cell(row,colIndex['rollno']).value
                        if(rollnostr==''):
                            rollno=0
                        elif(isValidRollNo(rollnostr) is False):
                            log.debug("The roll no [" +rollnostr+ "] is invalid. Ignoring it.")
                            rollno=0
                        else:
                            rollno = int(rollnostr)

                    if(colIndex.get('yog') is not None):
                        yogstr = s.cell(row,colIndex['yog']).value
                        if(yogstr==''):
                            yog=0
                        elif(isValidYOG(yogstr) is False):
                            log.debug("The YOG [" +yogstr+ "] is invalid. Ignoring it.")
                            yog=0
                        else:
                            yog = int(yogstr)

                    if(email=='' and name==''): #Currently email and name are being used as keys to check duplicates, so do not accept profile with blank email ID and name
                        log.debug("Email ID and name are empty, so profile is being ignored")
                        continue

                    log.debug("Details - First Name: ["+first_name+"], Last Name: ["+last_name+"], Email: ["+email+"], Branch: ["+branch+"]")
                    #log.debug("Mobile: ["+mobile+"], City: ["+city+"], Address: ["+address+"], YOG: ["+ str(yog) +"], RollNo: ["+ str(rollno) + "]")

                    #Part 2: Set the values of UserProfile fields.
                    try:
                        if(email): #Email is first key, name is second key when email is empty
                            user_profile=UserProfile.objects.get(email=email)
                            text = "A profile with email ID [" + email + "] already exists. Updated the other fields."
                        elif(name):
                            user_profile=UserProfile.objects.get(first_name=first_name, last_name=last_name, studentsection__year_of_graduation=yog)
                            text = "A profile with name [" + name + "] already exists. Updated the other fields."

                            if first_name: 
                                user_profile.first_name = first_name
                            if last_name:
                                user_profile.last_name = last_name
                            if mobile:
                                user_profile.phone_number = mobile
                            if address:
                                user_profile.address = address
                    except ObjectDoesNotExist:
                        user_profile = UserProfile(first_name=first_name, 
                                                   last_name=last_name,
                                                   email=email,
                                                   phone_number=mobile,
                                                   address=address,
                                                   role=ALUMNI)
                        text = "Added new profile with email ID [" + email + "] and name [" + name + "]"

                    except MultipleObjectsReturned:
                        text = "Seems like multiple profiles exist for [" +name+ "], email [" +email+ "]. Ignoring this row."

                    #Part 3: Set the foreign key fields
                    if(user_profile):
                        #log.debug("Setting city for ["+user_profile.first_name+"] to ["+city+"]")
                        user_profile.set_city(city)

                    user_profile.save()
                    log.debug(text)

                    #Part 4: Set other objects that have a relation to UserProfile
                    try:
                        student_section = StudentSection.objects.get(userprofile=user_profile)
                        if(rollno):
                            student_section.roll_num=rollno;
                        if(yog):
                            student_section.year_of_graduation=yog;
                        log.debug("Student Section already exists. Updating values for [" + name + "]")
                    except ObjectDoesNotExist:
                        student_section = StudentSection(userprofile=user_profile,
                                                         roll_num=rollno,
                                                         year_of_graduation=yog)
                        log.debug("Creating new student section for ["+ user_profile.first_name + "]")
                    
                    student_section.set_branch(branch)
                    student_section.save()

        log.debug("Bulk upload completed")
        super(XlsUpload, self).save(**kwargs)