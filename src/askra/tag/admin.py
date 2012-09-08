from django.contrib import admin
from tag.models import Tag

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(Tag, TagAdmin)