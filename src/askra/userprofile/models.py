from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from calendar import calendar
import csv
from django.core.exceptions import ObjectDoesNotExist
import re
from xlrd import open_workbook

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
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150,null=True, blank=True)
    country = models.CharField(max_length=150,null=True, blank=True)
    
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
        if(value):
            cities=City.objects.filter(city=value)
            if(cities):
                self.city = cities[0]
            else:
                city = City(city=value)
                city.save()
                print "Created a new city: [" + city.city + "]"
                self.city = city

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

class StudentSection(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    roll_num = models.CharField(max_length=20, null=True, blank=True)
    year_of_graduation = models.IntegerField(null=True, blank=True, help_text="Year of passing out")
    branch = models.ForeignKey(Branch, null=True, blank=True)

    def get_full_qualification(self):
        return self.branch.get_full_name() + " " + str(self.year_of_graduation)

    def set_branch(self, value):
        if(value):
            branches=Branch.objects.filter(branch__icontains=value)
            if(branches):
                self.branch=branches[0]
            else:
                print "Could not find branch [" + value + "]. Therefore not setting the value"

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
        print self.description
        reader = csv.DictReader(self.uploaded_file)
        for row in reader:
            first_name = row['First Name']
            last_name = row['Last Name']
            phone_number = row['Phone Number']
            emailErrorRow = self.validEmailId(row['Email'])
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

            print text
            user_profile.set_gender(gender)
            user_profile.set_role(role)
            user_profile.set_city(city)
            user_profile.save()
                
        print "Bulk upload successful"
        super(CsvUpload, self).save(**kwargs)
        if(emailErrorRow is not True):
            errorRow.csv_file=self;
            errorRow.save()


    def validEmailId(self,email):
        if(re.match('[^@]+@[^@]+\.[^@]+',email) is None):
            print "Email ID "+email+" is invalid! Creating an error row"
            errorRow = ErrorRow(csv_file=self,name='Invalid Email',reason='Email ID '+email+' is invalid')
            return errorRow
        else:
            print "Email ID "+email+" is valid!"
            return True
    
    
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
        print "Opening workbook ["+self.uploaded_file.url+"] to bulk upload profiles"
        for s in wb.sheets():
            print "Sheet: ["+s.name+"], Num Rows: ["+str(s.nrows)+"], Num Cols: ["+str(s.ncols)+"]"
            colIndex = {}
            for row in range(s.nrows):
                if(row==0): #Header
                    for col in range(s.ncols):
                        header = (str(s.cell(row,col).value)).lower()
                        colIndex[header] = col
                    print "Resulting colIndex Map index : "+str(colIndex)
                else: #Data
                    name, mobile, email, branch, city, address, yog, rollno = '','','','','','',0,0
                    first_name, last_name = '',''

                    #Part 1: Extract all necessary values from the row.
                    #Add all fields here.
                    if(colIndex.get('email') is not None):
                        email = str(s.cell(row,colIndex['email']).value)
                    else:
                        print "Email does not exist in the excel sheet"

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
                        rollno = int(s.cell(row,colIndex['rollno']).value)

                    if(colIndex.get('yog') is not None):
                        if(s.cell(row,colIndex['yog']).value != ''):
                            yog = int(s.cell(row,colIndex['yog']).value)

                    if(email=='' and name==''): #Currently email and name are being used as keys to check duplicates, so do not accept profile with blank email ID and name
                        print "Email ID and name are empty, so profile is being ignored"
                        continue 

                    #print "First Name: ["+first_name+"], Last Name: ["+last_name+"], Mobile: ["+mobile+"], Email: ["+email+"], Branch: ["+branch+"]"
                    #print "City: ["+city+"], Address: ["+address+"], YOG: ["+ str(yog) +"], RollNo: ["+ str(rollno) + "]"

                    #Part 2: Set the values of UserProfile fields.
                    try:
                        if(email): #Email is first key, name is second key when email is empty
                            user_profile=UserProfile.objects.get(email=email)
                            text = "A profile with email ID [" + email + "] already exists. Updated the other fields."
                        elif(name):
                            user_profile=UserProfile.objects.get(first_name=first_name, last_name=last_name)
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

                    #Part 3: Set the foreign key fields
                    if(user_profile):
                        print "Setting city for ["+user_profile.first_name+"] to ["+city+"]"
                        user_profile.set_city(city)

                    user_profile.save()
                    print text

                    #Part 4: Set other objects that have a relation to UserProfile
                    try:
                        student_section = StudentSection.objects.get(userprofile=user_profile)
                        if(rollno):
                            student_section.roll_num=rollno;
                        if(yog):
                            student_section.year_of_graduation=yog;
                        print "Student Section already exists. Updating values for [" + user_profile.first_name + "]"
                    except ObjectDoesNotExist:
                        student_section = StudentSection(userprofile=user_profile,
                                                         roll_num=rollno,
                                                         year_of_graduation=yog)
                        print "Creating new student section for ["+ user_profile.first_name + "]"
                    
                    student_section.set_branch(branch)
                    student_section.save()

        print "Bulk upload completed"
        super(XlsUpload, self).save(**kwargs)