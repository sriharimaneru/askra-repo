from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from xlrd import open_workbook, xldate_as_tuple, XL_CELL_TEXT
from django.db.models import Q
import logging
from userprofile.utils import getYOGFromRoll, isValidEmailId, isValidRollNo, \
    isValidYOG, slugify
from datetime import datetime
from django.db import IntegrityError


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

SYNONYM = 0
GROUP = 1
ALIAS_TYPES = ((SYNONYM, 'Synonym'),
               (GROUP, 'Group'))

CITY=0
STATE=1
COUNTRY=2
PLACE_TYPES = ((CITY, 'City'),
               (STATE, 'State'),
               (COUNTRY, 'Country'))

RT_COUNTRY=0
RT_STATE=1
RT_CITY=2
RT_COURSE=3
RT_BRANCH=4
RT_EMPLOYER=5
RT_JOBDESIGNATION=6
RT_JOBDOMAIN=7
RT_COLLEGE=8
RT_DEGREE=9
RT_HEBRANCH=10
RT_DEPARTMENT=11
RT_FACDESIGNATION=12
RT_TAG=13

RESOURCE_TYPES = ((RT_COUNTRY, 'Country'),
                  (RT_STATE, 'State'),
                  (RT_CITY, 'City'),
                  (RT_COURSE, 'Course'),
                  (RT_BRANCH, 'Branch'),
                  (RT_EMPLOYER, 'Employer'),
                  (RT_JOBDESIGNATION, 'Job Designation'),
                  (RT_JOBDOMAIN, 'Job Domain'),
                  (RT_COLLEGE, 'College'),
                  (RT_DEGREE, 'Degree'),
                  (RT_HEBRANCH, 'HigherEducationBranch'),
                  (RT_DEPARTMENT, 'Department'),
                  (RT_FACDESIGNATION, 'Designation'),
                  (RT_TAG, 'Tag'))


def get_resource_model_from_value(value):
    if value == RT_COUNTRY:
        return Country
    elif value == RT_STATE:
        return State
    elif value == RT_CITY:
        return City
    elif value == RT_COURSE:
        return Course
    elif value == RT_BRANCH:
        return Branch
    elif value == RT_EMPLOYER:
        return Employer
    elif value == RT_JOBDESIGNATION:
        return JobDesignation
    elif value == RT_JOBDOMAIN:
        return JobDomain
    elif value == RT_COLLEGE:
        return College
    elif value == RT_DEGREE:
        return Degree
    elif value == RT_HEBRANCH:
        return HigherEducationBranch
    elif value == RT_DEPARTMENT:
        return Department
    elif value == RT_FACDESIGNATION:
        return FacultyDesignation
    elif value == RT_TAG:
        return Tag
  
#Resources
class Country(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(Country, self).save(**kwargs)
        
    class Meta:
        verbose_name_plural = "Countries"    
    

class State(models.Model):    
    name = models.CharField(max_length=255)    
    slug = models.CharField(max_length=255, blank=True, unique=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    def get_country(self):
        if self.country is None:
            return ''
        else:
            return self.country.name
    get_country.short_description="country"
    
    def save(self,**kwargs):
        self.slug = slugify(self.name + " " + self.get_country())
        super(State, self).save(**kwargs)

class City(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    state = models.ForeignKey(State, null=True, blank=True)

    def __unicode__(self):
        return self.name
    
    def get_state(self):
        if self.state is None:
            return ''
        else:
            return self.state.name
    get_state.short_description = 'state'
        
    def get_country(self):
        if self.state is None:
            return ''
        elif self.state.country is None:
            return ''
        else:
            return self.state.country.name
    get_country.short_description = 'country'
    
    def save(self,**kwargs):
        self.slug = slugify(self.name + ' ' + self.get_state() + ' ' + self.get_country())
        isSaved = False
        ctr = 1
        
        while not isSaved:
            try:
                super(City, self).save(**kwargs)
                isSaved = True
            except IntegrityError: #Duplicate slug
                self.slug = self.slug + str(ctr)
                ctr = ctr + 1

    class Meta:
        verbose_name_plural = "Cities"    

class Course(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(Course, self).save(**kwargs)
        
    class Meta:
        verbose_name_plural = "Courses"

class Branch(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    course = models.ForeignKey(Course, null=True, blank=True)
    
    def __unicode__(self):
        return self.get_name()
    
    def get_name(self):
        if self.name:
            return self.name
        else:
            return ''
    
    def get_course(self):
        if self.course:
            return self.course.name
        else:
            return ''
    get_course.short_description='course'
    
    def get_full_qualification(self):
        if self.course:
            if self.get_name() != '':
                return self.course.name + ", " + self.get_name()
            else:
                return self.course.name
        else:
            return self.get_name()
    
    def save(self,**kwargs):
        self.slug = slugify(self.get_name() + ' ' + self.get_course())
        super(Branch, self).save(**kwargs)
        
    class Meta:
        verbose_name_plural = "Branches"

class Employer(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(Employer, self).save(**kwargs)

class JobDesignation(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(JobDesignation, self).save(**kwargs)
        
            
class JobDomain(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(JobDomain, self).save(**kwargs)

class College(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(College, self).save(**kwargs)     
    

class Degree(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(Degree, self).save(**kwargs)     

class HigherEducationBranch(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(HigherEducationBranch, self).save(**kwargs)

class Department(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(Department, self).save(**kwargs)     

class FacultyDesignation(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    
    def __unicode__(self):
        return self.name
    
    def save(self,**kwargs):
        self.slug = slugify(self.name)
        super(FacultyDesignation, self).save(**kwargs)

class UserProfile(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    role = models.IntegerField("User Role", choices=USER_ROLES, help_text="Choose the appropriate userRole")
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.CharField(max_length=255, blank=True, unique=True)
    email = models.EmailField(max_length=75)
    gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    photo = models.ImageField("Profile picture", upload_to="profile_pictures/", null=True, blank=True,)
    place_id = models.IntegerField(null=True, blank=True) #Should contain the city id, state id or country id
    place_type = models.IntegerField(choices=PLACE_TYPES, null=True, blank=True)
    twitter_url = models.URLField(max_length=100, null=True, blank=True)
    facebook_url = models.URLField(max_length=100, null=True, blank=True)
    linked_url = models.URLField(max_length=100, null=True, blank=True)
    website_url = models.URLField(max_length=100, null=True, blank=True)
    profile_status = models.IntegerField(choices = PROFILE_STATUS, null=True, blank=True, default=UNLINKED)
    about = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)

    def __unicode__(self):
        return self.get_full_name()
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return ""
    
    def get_short_name(self):
        if self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return ""
    
    def get_place(self):
        if self.place_id is None or self.place_type is None:
            return ''
        else:
            if self.place_type == CITY:
                try:
                    city = City.objects.get(id=self.place_id)
                    return city.name
                except ObjectDoesNotExist:
                    return ''
            elif self.place_type == STATE:
                try:
                    state = State.objects.get(id=self.place_id)
                    return state.name
                except ObjectDoesNotExist:
                    return ''
            elif self.place_type == COUNTRY:
                try:
                    country = Country.objects.get(id=self.place_id)
                    return country.name
                except ObjectDoesNotExist:
                    return ''
            else:
                return ''
    get_place.short_description = 'place'
    
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

    def set_place(self, value):
        value=value.strip()
        junkdata=''
        if(value):
            if('/' in value): #Multiple cities separated by '/'. We take the first one.
                (value, junkdata) = value.split('/',1)
                value=value.strip()
            
            cities = City.objects.filter(name__iexact=value)
            if(cities):
                self.place_id = cities[0].id
                self.place_type = CITY
            else:
                states = State.objects.filter(name__iexact=value)
                if(states):
                    self.place_id = states[0].id
                    self.place_type = STATE
                else:
                    countries = Country.objects.filter(name__iexact=value)
                    if(countries):
                        self.place_id = countries[0].id
                        self.place_type = COUNTRY
                    else:
                        synonyms=Synonym.objects.filter(Q(value__iexact=value), Q(resourcetype=RT_CITY)| 
                                                        Q(resourcetype=RT_STATE)|Q(resourcetype=RT_COUNTRY), 
                                                        Q(aliastype=SYNONYM))
                        if(synonyms):
                            if(synonyms[0].resourcetype == RT_CITY):
                                self.place_type = CITY
                                self.place_id = synonyms[0].parent_id
                            elif(synonyms[0].resourcetype == RT_STATE):
                                self.place_type = STATE
                                self.place_id = synonyms[0].parent_id
                            elif(synonyms[0].resourcetype == RT_COUNTRY):
                                self.place_type = COUNTRY
                                self.place_id = synonyms[0].parent_id
                            else:
                                slug = slugify(value)
                                try:
                                    city = City.objects.get(slug=slug)
                                    self.place_type = CITY
                                    self.place_id = city.id
                                except ObjectDoesNotExist:
                                    #Creating a new city be default. Admins will then change this data.
                                    newcity = City(name=value)
                                    newcity.save()
                        else:
                            #Creating a new city be default. Admins will then change this data.
                            newcity = City(name=value)
                            newcity.save()
                            log.debug("IMPORTANT: New city added: [" + value + "]")

            if junkdata!='':
                junkdata = ProfileJunkData(userprofile=self, key='place', value=junkdata)
                junkdata.save()

        return self

    def get_branch(self):
        studentsections = StudentSection.objects.filter(userprofile=self)
        if studentsections:
            return studentsections[0].get_branch_name()
        else:
            return ''
    get_branch.short_description = "Branch"

    def get_course(self):
        studentsections = StudentSection.objects.filter(userprofile=self)
        if studentsections:
            return studentsections[0].get_course_name()
        else:
            return ''
    get_course.short_description = "Course"

    def get_year_of_graduation(self):
        studentsections = StudentSection.objects.filter(userprofile=self) 
        if(studentsections):
            return studentsections[0].year_of_graduation
        else:
            return ''
    get_year_of_graduation.short_description = "Graduation Year"
        
    def save(self,**kwargs):
        
        if self.place_type is None:
            if self.place_id != '' and self.place_id is not None:
                raise ValidationError(('Place ID cannot be saved without place type'), code='invalid')
            
        if self.place_id is None or self.place_id == '':
            if self.place_type is not None:
                raise ValidationError(('Place type cannot be saved without place id'), code='invalid')        
        
        fullname = self.get_full_name()
        if fullname == '':
            fullname = 'default'
        self.slug = slugify(fullname)
        isSaved = False
        ctr = 1
        while not isSaved:
            try:
                super(UserProfile, self).save(**kwargs)
                isSaved = True
            except IntegrityError: #Duplicate slug
                self.slug = self.slug + str(ctr)
                ctr = ctr + 1

    def get_unique_slug(self):
        name = self.get_full_name()
        if name == '':
            name = 'default'
        slug = slugify(name)
        ctr = 0

        while True:
            userprofiles = UserProfile.objects.filter(slug=slug)
            if not userprofiles:
                return slug
            else:
                if userprofiles[0] == self:
                    return slug
                ctr = ctr + 1
                slug = slug + '-' + str(ctr)

        return slug

            
    def get_roll_num(self):
        studentsections = StudentSection.objects.filter(userprofile=self) 
        if(studentsections):
            return studentsections[0].roll_num
        else:
            return ''
    get_roll_num.short_description = "Roll No"

class ProfileJunkData(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=500)

class StudentSection(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    roll_num = models.CharField(max_length=20, null=True, blank=True)
    year_of_graduation = models.IntegerField(null=True, blank=True, help_text="Year of passing out")
    branch = models.ForeignKey(Branch, null=True, blank=True)
    
    def get_branch_name(self):
        if self.branch:
            return self.branch.get_name()
        else:
            return ''
    
    def get_course_name(self):
        if self.branch:
            return self.branch.get_course()
        else:
            return ''

    def get_full_qualification(self):
        if self.branch and self.year_of_graduation:
            return self.branch.get_full_qualification() + " " + str(self.year_of_graduation)
        elif self.branch:
            return self.branch.get_full_qualification()
        elif self.year_of_graduation:
            return str(self.year_of_graduation)
        else:
            return ""

    def set_branch(self, branch, course, specialisation):
        if course != '' and course != None:
            course = course.strip()
            try:
                courseData = Course.objects.get(name__iexact=course)
            except ObjectDoesNotExist:
                courseDataSynonyms = Synonym.objects.filter(value__iexact=course, resourcetype=RT_COURSE, aliastype=SYNONYM)
                if courseDataSynonyms:
                    courseData = courseDataSynonyms[0]
                else:
                    courseData = Course(name=course)
                    courseData.save()
        else:
            return #No course. Not saving any data.

        if specialisation != '' and specialisation != None:
            branch = specialisation #If specialisation is specified, that is the branch
                    
        if branch != '' and branch != None:
            branch = branch.strip()
            branchData = Branch.objects.filter(name__iexact=branch)
            if not branchData:
                branchSynonyms = Synonym.objects.filter(value__iexact=branch, resourcetype=RT_BRANCH, aliastype=SYNONYM)
                if branchSynonyms:
                    branchData = branchSynonyms[0]
                else:
                    branchObj = Branch(name=branch, course=courseData)
                    branchObj.save()
                    self.branch = branchObj
                    return
                    
            for branchObj in branchData:
                if branchObj.course == courseData: #Course matches
                    self.branch = branchObj
                    return
            
            branchObj = Branch(name=branch, course=courseData)
            branchObj.save()
            self.branch = branchObj
                    
    
    def save(self, **kwargs):
        #Add any validation here
        super(StudentSection, self).save(**kwargs)

class EmploymentDetail(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    employer = models.ForeignKey(Employer)
    designation = models.ForeignKey(JobDesignation)
    domain = models.ForeignKey(JobDomain)
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)

    def get_employment_period(self):
        if((self.date_of_joining is None and self.date_of_leaving is None) or (self.date_of_joining=="" and self.date_of_leaving=="")):
            return ""
        elif(self.date_of_leaving is None):
            return str(self.date_of_joining.strftime("%b %Y")) + " - Current"
        elif(self.date_of_joining is None):
            return " - " + str(self.date_of_leaving.strftime("%b %Y"))
        else:
            return str(self.date_of_joining.strftime("%b %Y")) + " - " + str(self.date_of_joining.year)+ " - " + str(self.date_of_leaving.strftime("%b")) + ", " + str(self.date_of_leaving.year)

        
class HigherEducationDetail(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    college = models.ForeignKey(College)
    degree = models.ForeignKey(Degree)
    branch = models.ForeignKey(HigherEducationBranch)
    year_of_graduation = models.IntegerField(null=True, blank=True, help_text="Year of passing out")
        
class FacultySection(models.Model):
    userprofile = models.ForeignKey(UserProfile)
    deparment = models.ForeignKey(Department)
    designation = models.ForeignKey(FacultyDesignation)
    
class UserTag(models.Model):  
    userprofile = models.ForeignKey(UserProfile)
    tag = models.ForeignKey(Tag)
    status = models.IntegerField("Tag Category", choices=USERTAG_STATUS_OPTIONS,)

class Synonym(models.Model):
    value = models.CharField(max_length=255)
    parent_id = models.IntegerField()
    resourcetype = models.IntegerField(choices=RESOURCE_TYPES)
    aliastype = models.IntegerField(choices=ALIAS_TYPES, default=SYNONYM)
    
    def __unicode__(self):
        return self.value
    
    def get_parent_name(self):
        resource = get_resource_model_from_value(self.resourcetype)
        try:
            obj = resource.objects.get(id=self.parent_id)
            return obj.name
        except ObjectDoesNotExist:
            return ''
    get_parent_name.short_description = 'Parent Value'
    
    def get_resourcetype_name(self):
        return dict(RESOURCE_TYPES)[self.resourcetype]
    get_resourcetype_name.short_description = 'Resource'
    
    def get_aliastype_name(self):
        return dict(ALIAS_TYPES)[self.aliastype]
    get_aliastype_name.short_description = 'Alias Type'
    

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
                        header = (unicode(s.cell(row,col).value)).lower()
                        colIndex[header] = col
                    log.debug("Resulting colIndex Map index : "+str(colIndex))
                else: #Data
                    name, mobile, email, branch, city, address, yog, rollno = '','','','','','',0,0
                    first_name, last_name = '',''
                    dob, specialisation, course, phone, offphone=None,'','','',''
                    junk = {}

                    #Part 1: Extract all necessary values from the row.
                    #Add all fields here.
                    if(colIndex.get('email') is not None):
                        email = unicode(s.cell(row,colIndex['email']).value).strip()
                        if('/' in email): #Multiple email IDs separated by '/'
                            (email, junk['email']) = email.split('/',1)
                        if(',' in email): #Multiple email IDs separated by '/'
                            (email, junk['email']) = email.split(',',1)
                        if(email!='' and (isValidEmailId(email) is False)):
                            log.debug("The email ID [" + email + "] is invalid. Putting it in junk.")
                            junk['email'] = email
                            email='' #For invalid email ID treat it as if the email ID is not present
                    else:
                        log.debug("Email does not exist in the excel sheet")

                    if(colIndex.get('name') is not None):
                        name = unicode(s.cell(row,colIndex['name']).value).strip()
                        if(name):
                            try:
                                (first_name, last_name) = name.split(' ',1)
                            except ValueError:
                                first_name = name
                        
                    if(colIndex.get('mobile') is not None):
                        mobilestr = s.cell(row,colIndex['mobile']).value
                        if type(mobilestr) is float: #to remove a trailing .0 for float numbers
                            mobile=unicode(int(mobilestr)).strip()
                        else:
                            mobile = unicode(mobilestr).strip()
                    
                    if(colIndex.get('phone') is not None):
                        phonestr = s.cell(row,colIndex['phone']).value
                        if type(phonestr) is float: #to remove a trailing .0 for float numbers
                            phone=unicode(int(phonestr)).strip()
                        else:
                            phone=unicode(phonestr).strip()

                    if phone!='':
                        if mobile!='':
                            mobile+=","+phone
                        else:
                            mobile=phone

                    if(colIndex.get('office phone') is not None):
                        offphonestr = s.cell(row,colIndex['office phone']).value
                        if type(offphonestr) is float: #to remove a trailing .0 for float numbers
                            offphone=unicode(int(offphonestr)).strip()
                        else:
                            offphone=unicode(offphonestr).strip()

                    if offphone!='':
                        if mobile!='':
                            mobile+=","+offphone
                        else:
                            mobile=offphone
                    
                    log.debug("Mobile number is ["+mobile+ "]")

                    if(colIndex.get('branch') is not None):
                        branch = unicode(s.cell(row,colIndex['branch']).value).strip()

                    if(colIndex.get('city') is not None):
                        city = unicode(s.cell(row,colIndex['city']).value).strip()

                    if(colIndex.get('address') is not None):
                        address = (unicode(s.cell(row,colIndex['address']).value)).strip()
                    
                    if(colIndex.get('rollno') is not None):
                        rollnostr = s.cell(row,colIndex['rollno']).value
                        if type(rollnostr) is str:
                            if(rollnostr==''):
                                rollno=0
                            elif(isValidRollNo(rollnostr) is False):
                                log.debug("The roll no [" +rollnostr+ "] is invalid. Ignoring it.")
                                junk['rollno'] = rollnostr
                                rollno=0
                            else:
                                rollno = int(rollnostr)
                        elif type(rollnostr) is float:
                            rollno=int(rollnostr)
                        else:
                            rollno=rollnostr

                    if(colIndex.get('yog') is not None):
                        yogstr = s.cell(row,colIndex['yog']).value
                        if type(yogstr) is str:
                            if(yogstr==''):
                                yog=0
                            elif(isValidYOG(yogstr) is False):
                                log.debug("The YOG [" +yogstr+ "] is invalid. Ignoring it.")
                                junk['yog'] = yogstr
                                yog=0
                            else:
                                yog = int(yogstr)
                        else:
                            yog=yogstr
                        
                    if yog==0:
                        if(getYOGFromRoll(str(rollno))):
                            yog = getYOGFromRoll(str(rollno))
                            
                    if(colIndex.get('dob') is not None):
                        dobtype = s.cell(row, colIndex['dob']).ctype
                        if dobtype == XL_CELL_TEXT:
                            dob = None
                        else:
                            dobnum = s.cell(row, colIndex['dob']).value
                            if dobnum!='':
                                dob = datetime(*xldate_as_tuple(dobnum, wb.datemode))
                            
                    if(colIndex.get('course') is not None):
                        course = unicode(s.cell(row,colIndex['course']).value).strip()
                    
                    if(colIndex.get('specialisation') is not None):
                        specialisation = unicode(s.cell(row,colIndex['specialisation']).value).strip()

                    if(email=='' and name==''): #Currently email and name are being used as keys to check duplicates, so do not accept profile with blank email ID and name
                        log.debug("Email ID and name are empty, so profile is being ignored")
                        continue

                    log.debug("Details - First Name: ["+first_name+"], Last Name: ["+last_name+"], Email: ["+email+"], Branch: ["+branch+"]")
#                    log.debug("Mobile: ["+mobile+"], City: ["+city+"], Address: ["+address+"], YOG: ["+ unicode(yog) +"], RollNo: ["+ unicode(rollno) + "]")

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
                            if dob:
                                user_profile.date_of_birth = dob
                    except ObjectDoesNotExist:
                        user_profile = UserProfile(first_name=first_name, 
                                                   last_name=last_name,
                                                   email=email,
                                                   phone_number=mobile,
                                                   address=address,
                                                   role=ALUMNI,
                                                   date_of_birth=dob)
                        text = "Added new profile with email ID [" + email + "] and name [" + name + "]"

                    except MultipleObjectsReturned:
                        text = "Seems like multiple profiles exist for [" +name+ "], email [" +email+ "]. Ignoring this row."
                    
                    log.debug(text)
                    user_profile.save()
                    
                    #Part 3: Set the foreign key fields
                    if(user_profile):
                        #log.debug("Setting city for ["+user_profile.first_name+"] to ["+city+"]")
                        user_profile.set_place(city)
                        user_profile.save()
                    
                    if junk:
                        for key, value in junk.items():
                            junkdata = ProfileJunkData(userprofile=user_profile, key=key, value=value)
                            junkdata.save()

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
                    
                    setbranchsuccess = student_section.set_branch(branch, course, specialisation)
                    if not setbranchsuccess:
                        junkdata = ProfileJunkData(userprofile=user_profile, key='branch', value=branch+","+course+","+specialisation)
                        junkdata.save()
                    
                    student_section.save()

        log.debug("Bulk upload completed")
        super(XlsUpload, self).save(**kwargs)
        
#class CsvUpload(models.Model):
#    uploaded_file = models.FileField(upload_to="data/upload_files/", blank=False, null=False)
#    description = models.TextField(blank=True, null=True)
#    
#    def save(self,**kwargs):
#        log.debug(self.description)
#        reader = csv.DictReader(self.uploaded_file)
#        for row in reader:
#            first_name = row['First Name']
#            last_name = row['Last Name']
#            phone_number = row['Phone Number']
#            emailErrorRow = isValidEmailId(row['Email'])
#            if(emailErrorRow is True):
#                email = row['Email']
#            else:
#                email=''
#            gender = row['Gender']
#            role = row['User Role']
#            city = row['City']
#
#            try:
#                user_profile=UserProfile.objects.get(email=email)
#                text = "A profile with email ID [" + email + "] already exists. Updated the other fields."
#                user_profile.first_name = first_name
#                user_profile.last_name = last_name
#                user_profile.phone_number = phone_number
#                user_profile.email = email
#            except ObjectDoesNotExist:
#                user_profile = UserProfile(first_name=first_name, 
#                                           last_name=first_name,
#                                           email=email,
#                                           phone_number=phone_number)
#                text = "Added new profile with email ID [" + email + "]"
#
#            log.debug(text)
#            user_profile.set_gender(gender)
#            user_profile.set_role(role)
#            user_profile.set_city(city)
#            user_profile.save()
#                
#        log.debug("Bulk upload successful")
#        super(CsvUpload, self).save(**kwargs)
#        if(emailErrorRow is not True):
#            emailErrorRow.csv_file=self;
#            emailErrorRow.save()

#class ErrorRow(models.Model):
#    csv_file = models.ForeignKey(CsvUpload)
#    name = models.CharField(max_length=20)
#    reason = models.TextField()
#    action = models.IntegerField(choices = ACTION_CHOICES, default = DO_NOTHING)
#
#    def save(self,**kwargs):
#        #if action is ignore, do nothing 
#        
#        #if action is save, delete it and create correspoinding user profile
#        
#        #if action is ignore, just delete it
#        
#        
#        super(ErrorRow, self).save(**kwargs)