'''
Created on 17-Aug-2013

@author: srihari
'''
from django import forms
from userprofile.models import Branch
from haystack.forms import SearchForm 

class ProfileSearchBasicForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    branches_list = [(branch.branch, branch.branch) for branch in Branch.objects.all() if branch.branch]
    branches_list = [("", "All")] + sorted(branches_list, key=lambda x: x[1])
    branch = forms.ChoiceField(choices = branches_list, required=False)
    year_of_passing = forms.ChoiceField(choices = [("", "All")] + [(x,x) for x in range(1964, 2009)] + [("2011", "2011"), ("2013", "2013"), ("2014", "2014"), ("2015", "2015"), ("2016", "2016")], required=False)


class CustomSearchForm(SearchForm):
    
    q = forms.CharField(required=False, label='Search', 
                        widget=forms.TextInput(attrs={'placeholder': 'Search across thousands of profiles'}))

    def no_query_found(self):
        return self.searchqueryset.all()
     