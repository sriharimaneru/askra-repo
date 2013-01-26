from django.contrib import admin
from userprofile.models import UserProfile, City, Branch, StudentSection, \
                               Employer, JobDesignation, JobDomain, EmployementDetail, \
                               College, Degree, HigherEducationDetail, Department, \
                               FacultyDesignation, FacultySection, UserTag, HigherEducationBranch, CsvUpload, ErrorRow, \
                               XlsUpload

class CityAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'country')
    list_filter = ('state','country')
    search_fields = ('city', 'state', 'country')
    
class BranchAdmin(admin.ModelAdmin):
    list_display = ('branch', 'course', )
    list_filter = ('course', )
    search_fields = ('branch', )    
    
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

              
class YOGListFilter(admin.SimpleListFilter):
    title = "Year of Graduation"
    parameter_name='yog'

    def lookups(self, request, model_admin):
        retval = ()
        for year_of_graduation in StudentSection.objects.values('year_of_graduation').distinct():
            retval += ((year_of_graduation["year_of_graduation"], str(year_of_graduation["year_of_graduation"])),)

        return retval


    def queryset(self, request, queryset):
        #return queryset.all()
        print self.value()
        if self.value():
            return queryset.filter(studentsection__year_of_graduation = self.value())
        else:
            return queryset.all()

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [("Basic Details", {"fields" : (('user', 'role', 'profile_status'), ('first_name','last_name', 'gender'), 
                                                ('email', 'phone_number',), ('photo', 'address', 'city',), ('about',),)}),
                 ("Website Urls", {"fields" : (('linked_url', 'facebook_url',), ('website_url', 'twitter_url'))}),]
    raw_id_fields = ('user',)
    list_display = ('id', 'first_name', 'last_name', 'get_branch', 'get_year_of_graduation', 'email', 'phone_number', 'city', 'role', 'profile_status', )
    list_filter = ('role', 'profile_status', 'city', YOGListFilter)
    search_fields = ('first_name', 'last_name', 'email',)
    inlines = (StudentSectionInline, EmployementDetailInline, HigherEducationDetailInline, FacultySectionInline,
               UserTagInline, )

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







