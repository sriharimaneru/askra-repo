import datetime
from haystack.indexes import *
from haystack import site
from models import UserProfile, StudentSection


class NoteIndex(SearchIndex):
    text = CharField(document=True)
    name = CharField(indexed=True)
    course = CharField(indexed=False)
    branch = CharField(indexed=False, faceted=True)
    year_of_passing = IntegerField(indexed=False, faceted=True) 
    city = CharField(indexed=False, faceted=True)

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return UserProfile.objects.all()

    def prepare(self, obj):
        prepared_data = super(NoteIndex, self).prepare(obj)
        
        first_name = obj.first_name
        last_name = obj.last_name
        
        searchable_text = []
        searchable_text.extend([first_name, last_name])        
        
        prepared_data['name'] = first_name + " " + last_name
        
        sc_list = StudentSection.objects.filter(userprofile = obj)
        
        if sc_list.count():
            sc = sc_list[0]        
            if sc.branch:
                prepared_data['course'] = sc.branch.course
                prepared_data['branch'] = sc.branch.branch
                searchable_text.extend([sc.branch.course, sc.branch.branch,])        
            prepared_data['year_of_passing'] = sc.year_of_graduation    
            searchable_text.extend([str(sc.year_of_graduation)])
        else:
            prepared_data['course'] = ""
            prepared_data['branch'] = ""
            prepared_data['year_of_passing'] = 0  
            
        if obj.city and obj.city.city:
            prepared_data['city'] = obj.city.city
        else:
            prepared_data['city'] = ""
            
        prepared_data['text'] = "".join(searchable_text)
        return prepared_data            
            

site.register(UserProfile, NoteIndex)
