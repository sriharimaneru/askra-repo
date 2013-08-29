from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from userprofile.models import UserProfile, Country, State, City, Course, Branch, \
                               StudentSection, Employer, JobDesignation, JobDomain, EmploymentDetail, \
                               College, Degree, HigherEducationDetail, Department, \
                               FacultyDesignation, FacultySection, UserTag, HigherEducationBranch, \
                               XlsUpload, ProfileJunkData, Synonym
from tag.models import Tag

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')

class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_country')
    list_filter = ('name', 'slug', 'country__name')
    search_fields = ('name', 'slug')

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_state', 'get_country')
    list_filter = ('name','slug', 'state__name', 'state__country__name')
    search_fields = ('name', 'slug')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')
    
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_course')
    list_filter = ('name', 'slug', 'course__name')
    search_fields = ('name', 'slug')

class EmployerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('id', 'name', 'slug')

class SynonymAdmin(admin.ModelAdmin):
    list_display = ('value', 'get_parent_name', 'get_resourcetype_name', 'get_aliastype_name')
    list_filter = ('value', )
    search_fields = ('value', )
    
class StudentSectionInline(admin.TabularInline):
    model = StudentSection
    extra=1
    
class EmploymentDetailInline(admin.TabularInline):
    model = EmploymentDetail
    extra=1        

class HigherEducationDetailInline(admin.TabularInline):
    model = HigherEducationDetail
    extra=1 
    
class FacultySectionInline(admin.TabularInline):
    model = FacultySection
    extra=1   

class UserTagInline(admin.TabularInline):
    model = UserTag
    extra=1

class TagInline(admin.TabularInline):
    model = Tag
    extra=1

class ProfileJunkDataInline(admin.TabularInline):
    model = ProfileJunkData
    extra=0   

              
class YOGListFilter(admin.SimpleListFilter):
    title = "Year of Graduation"
    parameter_name='yog'
    all_param_value='any'

    def lookups(self, request, model_admin):
        retval = ()
        for year_of_graduation in StudentSection.objects.values('year_of_graduation').distinct():
            retval += ((str(year_of_graduation["year_of_graduation"]), str(year_of_graduation["year_of_graduation"])),)

        return retval

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == self.all_param_value:
                return queryset
            else:
                return queryset.filter(studentsection__year_of_graduation=int(self.value()))
        else:
            return queryset

class BranchListFilter(admin.SimpleListFilter):
    title = 'Branch'
    parameter_name='branch'

    def lookups(self, request, model_admin):
        retval = ()
        for branch in Branch.objects.all():
            retval += ((branch.get_name(), branch.get_name()),)
        return retval

    def queryset(self, request, queryset):
        if self.value():
            try:
                selectedBranches=Branch.objects.filter(name__iexact=self.value())
                return queryset.filter(studentsection__branch__in=selectedBranches)
            except ObjectDoesNotExist:
                return queryset
        else:
            return queryset

#TODO: Create a place filter and add to UserProfileAdmin

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [("Basic Details", {"fields" : (('user', 'role', 'profile_status'), ('first_name','last_name', 'gender', 'slug'), 
                                                ('email', 'phone_number','date_of_birth', ), ('photo', 'address',), ('about',),)}),
                 ("Website Urls", {"fields" : (('linked_url', 'facebook_url',), ('website_url', 'twitter_url'))}),
                 ("Tags", {"fields": ('tags',)})]
    raw_id_fields = ('user',)
    list_display = ('id', 'first_name', 'last_name', 'slug', 'get_roll_num', 'get_course', 'get_branch', 'get_year_of_graduation', 'email', 'phone_number', 'get_place', 'role', 'profile_status', )
    list_filter = ('role', 'profile_status', YOGListFilter, BranchListFilter)
    search_fields = ('first_name', 'last_name', 'email',)
    inlines = (StudentSectionInline, EmploymentDetailInline, HigherEducationDetailInline, FacultySectionInline,
               ProfileJunkDataInline,)

    change_list_template = "admin/change_list_filter_sidebar.html"


class XlsUploadAdmin(admin.ModelAdmin):
    list_display = ('uploaded_file','description')

admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)    
admin.site.register(Country, CountryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(JobDesignation)
admin.site.register(JobDomain)
admin.site.register(College)
admin.site.register(Degree)
admin.site.register(Department)
admin.site.register(FacultyDesignation)
admin.site.register(HigherEducationBranch)
admin.site.register(XlsUpload, XlsUploadAdmin)
admin.site.register(Synonym, SynonymAdmin)