from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from userprofile.models import UserProfile, City, Branch, StudentSection, \
                               Employer, JobDesignation, JobDomain, EmployementDetail, \
                               College, Degree, HigherEducationDetail, Department, \
                               FacultyDesignation, FacultySection, UserTag, HigherEducationBranch, CsvUpload, ErrorRow, \
                               XlsUpload, CitySynonym, BranchSynonym, ProfileJunkData
from tag.models import Tag

class CityAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country')
    list_filter = ('state','country')
    search_fields = ('city', 'state', 'country')
    
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch', 'course', 'specialisation')
    list_filter = ('branch', 'course', 'specialisation')
    search_fields = ('branch', 'course', 'specialisation')
    
class StudentSectionInline(admin.TabularInline):
    model = StudentSection
    extra=1
    
class EmployementDetailInline(admin.TabularInline):
    model = EmployementDetail
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
            retval += ((branch.get_full_name(), branch.get_full_name()),)
        return retval

    def queryset(self, request, queryset):
        print self.value()
        if self.value():
            try:
                if ',' in self.value():
                    (course, branch) = self.value().split(',', 1)
                    selectedBranch=Branch.objects.get(course__iexact=course.strip(), branch__iexact=branch.strip())
                else:
                    selectedBranch=Branch.objects.get(Q(course__iexact=self.value()) | Q(branch__iexact=self.value()))
                return queryset.filter(studentsection__branch=selectedBranch)
            except ObjectDoesNotExist:
                return queryset
        else:
            return queryset

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [("Basic Details", {"fields" : (('user', 'role', 'profile_status'), ('first_name','last_name', 'gender',), 
                                                ('email', 'phone_number','date_of_birth', ), ('photo', 'address', 'city',), ('about',),)}),
                 ("Website Urls", {"fields" : (('linked_url', 'facebook_url',), ('website_url', 'twitter_url'))}),
                 ("Tags", {"fields": ('tags',)})]
    raw_id_fields = ('user',)
    list_display = ('id', 'first_name', 'last_name', 'get_roll_num', 'get_course', 'get_branch', 'get_year_of_graduation', 'email', 'phone_number', 'city', 'role', 'profile_status', )
    list_filter = ('role', 'profile_status', 'city', )
    search_fields = ('first_name', 'last_name', 'email',)
    inlines = (StudentSectionInline, EmployementDetailInline, HigherEducationDetailInline, FacultySectionInline,
               ProfileJunkDataInline,)

    change_list_template = "admin/change_list_filter_sidebar.html"

class ErrorRowInline(admin.TabularInline):
    model = ErrorRow
       
class CsvUploadAdmin(admin.ModelAdmin):
    inlines = (ErrorRowInline, )
    list_display = ('uploaded_file','description')

class XlsUploadAdmin(admin.ModelAdmin):
    list_display = ('uploaded_file','description')
    
admin.site.register(City, CityAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Employer)
admin.site.register(JobDesignation)
admin.site.register(JobDomain)
admin.site.register(College)
admin.site.register(Degree)
admin.site.register(Department)
admin.site.register(FacultyDesignation)
admin.site.register(HigherEducationBranch)
admin.site.register(CsvUpload, CsvUploadAdmin)
admin.site.register(XlsUpload, XlsUploadAdmin)
admin.site.register(CitySynonym)
admin.site.register(BranchSynonym)