from django.contrib import admin
from userprofile.models import UserProfile, City, Branch, StudentSection, \
                               Employer, JobDesignation, JobDomain, EmployementDetail, \
                               College, Degree, HigherEducationDetail, Department, \
                               FacultyDesignation, FacultySection, UserTag

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
              
class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [("Basic Details", {"fields" : (('user', 'role', 'profile_status'), ('first_name','last_name', 'gender'), 
                                                ('email', 'phone_number',), ('photo', 'city',))}),
                 ("Website Urls", {"fields" : (('linked_url', 'facebook_url',), ('website_url', 'twitter_url'))}),]
    raw_id_fields = ('user',)
    list_display = ('id', 'first_name', 'last_name', 'role', 'profile_status',)
    list_filter = ('role', 'profile_status', 'city')
    search_fields = ('first_name', 'last_name', 'email',)
    inlines = (StudentSectionInline, EmployementDetailInline, HigherEducationDetailInline, FacultySectionInline,
               UserTagInline, )
    
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






