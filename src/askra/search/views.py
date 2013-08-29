import json
import collections
from pysolr import Solr

from django.http import HttpResponse, Http404
from django.views.generic.base import TemplateView, View
from haystack.query import SearchQuerySet, EmptySearchQuerySet
from haystack.views import SearchView
from django.conf import settings

from .forms import ProfileSearchBasicForm, CustomSearchForm
from django.core.paginator import Paginator, InvalidPage

# Number of results loaded on search page initially. Same number of results are loaded further
# with each AJAX call after that.

INITIAL_RESULTS_COUNT = 40


class FacetDetails():

    """
    used to pass on the facet details from View to Template
    """
    facet_id = ""
    name = ""
    options_selected = ""
    facet_options = []

    def __init__(self, facet_id="", name="", options_selected=[], facet_options=[]):
        self.facet_id = facet_id
        self.name = name
        self.options_selected = options_selected
        self.facet_options = facet_options


def load_facet_detail_map():
    retVal = collections.OrderedDict()
    retVal["branch"] = FacetDetails("branch", "Branch")
    retVal["year_of_graduation"] = FacetDetails("year_of_graduation", "Year Of Graduation")
    retVal["city"] = FacetDetails("city", "City")
    retVal["state"] = FacetDetails("state", "State")
    retVal["country"] = FacetDetails("country", "Country")
    retVal["higher_education_degree"] = FacetDetails(
        "higher_education_degree",
        "Higher Education Degree")
    retVal["higher_education_college"] = FacetDetails(
        "higher_education_college",
        "Higher Education College")
    retVal["company"] = FacetDetails("company", "Company")

    return retVal


class ProfileSearchView(SearchView):

    def __init__(self, *args, **kwargs):
        super(ProfileSearchView, self).__init__(*args, **kwargs)
        self.facet_detail_map = load_facet_detail_map()
        self.resultcount = 0

    def extra_context(self):
        extra = super(ProfileSearchView, self).extra_context()
        extra['results'] = self.results
        extra['resultcount'] = self.resultcount
        extra['facet_detail_map'] = self.facet_detail_map
        extra['request'] = self.request

        print "****************"
        for fd in self.facet_detail_map.values():
            print fd.facet_options
        print "****************"

        return extra

    def __call__(self, request):
        """
        Generates the actual response to the search.
        Relies on internal, overridable methods to construct the response.
        """
        self.facet_detail_map = load_facet_detail_map()
        self.request = request
        self.form = self.build_form()
        self.query = self.get_query()
        self.update_selected_facets()
        self.results = self.get_results()

        return self.create_response()

    def update_selected_facets(self):
        for facet_id in self.facet_detail_map.keys():
            facet_options_selected = self.request.GET.get(facet_id, '')
            print "-----------" + facet_options_selected
            if facet_options_selected:
                self.facet_detail_map[facet_id].options_selected = " OR ".join(facet_options_selected.split(","))

    def build_args(self):
        """Build the args in solr query - facets applied, counts
        Uses tagging and filtering to correct the facet counts.
        """
        retval = {"fq": [],
                  "facet": "on",
                  "facet.field": [],
                  "rows": 100,
                  }
        for facet_detail in self.facet_detail_map.values():
            retval["facet.field"].append("{!ex=%s}%s" %
                                         (facet_detail.facet_id, facet_detail.facet_id))
            if facet_detail.options_selected:
                retval["fq"].append("{!tag=%s}%s:%s" %
                                    (facet_detail.facet_id, facet_detail.facet_id,
                                     facet_detail.options_selected))
        print retval
        return retval

    def update_facet_counts(self, facet_counts_map):

        """
        output of pysolr.Solr.search() which is input for this function is
        'facet_fields': {'branch': ['Chemical', 1, 'ECE', 1]}

        We need it as
        'branch': ['Chemical', 1, 'ECE', 1]}
        """
        for facet_id in facet_counts_map:
            l = facet_counts_map[facet_id]
            self.facet_detail_map[facet_id].facet_options = \
                [l[i:i+2] for i in range(0, len(l), 2)]

    def get_results(self):
        """
        Applies all the selected facets on the form_results.
        """
        query = self.query if self.query else "*"
        complete_results = Solr(settings.HAYSTACK_CONNECTIONS['default']['URL']). \
                                    search(query, **self.build_args())
        self.update_facet_counts(complete_results.facets["facet_fields"])
        self.resultcount = complete_results.hits
        return complete_results.docs


def getsearchresults(request):
    name = request.GET.get("name", '')
    branch = request.GET.get("branch", '')
    year = request.GET.get("year_of_passing", '')
    offset = request.GET.get("offset", '0')
    branch_facet = request.GET.get("branch_facet", '')
    year_facet = request.GET.get("year_of_passing_facet", '')

    offsetvalue = int(offset)

    sqs = SearchQuerySet().facet('branch')
    sqs = sqs.facet('year_of_passing')

    if name or branch or year:
        sqs = sqs.auto_query(name + branch + year)

    results = sqs.auto_query(
        branch_facet +
        year_facet).order_by(
        'name')[
        offsetvalue:offsetvalue +
        20]

    return results


class BaseSearchView():

    def get_results(self, name, branch, year, offset, branch_facet, year_facet, city_facet):
        if year_facet:
            year_facet = [int(x) for x in year_facet.split(",")]

        sqs = SearchQuerySet().facet('branch')
        sqs = sqs.facet('year_of_passing')
        sqs = sqs.facet('city')

        if name:
            sqs = sqs.auto_query(name)
        if branch:
            sqs = sqs.filter(branch_exact=branch)
        if year:
            sqs = sqs.filter(year_of_passing_exact=year)
        if branch_facet:
            sqs = sqs.filter(branch_exact=branch_facet)
        if year_facet:
            sqs = sqs.filter(year_of_passing_exact__in=year_facet)
        if city_facet:
            sqs = sqs.filter(city_exact=city_facet)

        offsetvalue = int(offset)
        results = sqs.order_by('name')[offsetvalue:offsetvalue + INITIAL_RESULTS_COUNT]
        resultcount = len(results)

        return results, resultcount


class SearchView(BaseSearchView, TemplateView):
    template_name = "search/search.html"

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['request'] = self.request

        name = self.request.GET.get("name", '')
        branch = self.request.GET.get("branch", '')
        year = self.request.GET.get("year_of_passing", '')

        branch_facet = self.request.GET.get("branch_facet", '')
        year_facet = self.request.GET.get("year_of_passing_facet", '')

#        results = self.get_results(name, branch, year, offset, branch_facet, year_facet)
        if year_facet:
            year_facet = [int(x) for x in year_facet.split(",")]
        city_facet = self.request.GET.get("city_facet", "")

        sqs = SearchQuerySet().facet('branch')
        sqs = sqs.facet('year_of_passing')
        sqs = sqs.facet('city')

        if name or branch or year:
            context['form'] = ProfileSearchBasicForm(self.request.GET)
            if name:
                sqs = sqs.auto_query(name)
                context['name_selected'] = name
            if branch:
                sqs = sqs.filter(branch_exact=branch)
                context['branch_selected'] = branch
            if year:
                sqs = sqs.filter(year_of_passing_exact=year)
                context['year_selected'] = year
        else:
            context['form'] = ProfileSearchBasicForm()

        context['facets'] = sqs.facet_counts()

        # Horrible hardcoding - need to tweak it - By Srihari
        # To compute the facet counts
        if branch_facet:
            temp = sqs.filter(branch_exact=branch_facet)
            context['facets']['fields']['year_of_passing'] = temp.filter(city_exact=city_facet).facet_counts()[
                'fields']['year_of_passing'] if city_facet else temp.facet_counts()['fields']['year_of_passing']
        elif city_facet:
            context['facets']['fields']['year_of_passing'] = sqs.filter(
                city_exact=city_facet).facet_counts()['fields']['year_of_passing']

        if year_facet:
            temp = sqs.filter(year_of_passing_exact__in=year_facet)
            context['facets']['fields']['branch'] = temp.filter(city_exact=city_facet).facet_counts()[
                'fields']['branch'] if city_facet else temp.facet_counts()['fields']['branch']
        elif city_facet:
            context['facets']['fields']['branch'] = sqs.filter(
                city_exact=city_facet).facet_counts()['fields']['branch']

        if year_facet:
            temp = sqs.filter(year_of_passing_exact__in=year_facet)
            context['facets']['fields']['city'] = temp.filter(branch_exact=branch_facet).facet_counts()[
                'fields']['city'] if branch_facet else temp.facet_counts()['fields']['city']
        elif branch_facet:
            context['facets']['fields']['city'] = sqs.filter(
                branch_exact=branch_facet).facet_counts()['fields']['city']

        if branch_facet:
            sqs = sqs.filter(branch_exact=branch_facet)
            context['branch_facet_selected'] = branch_facet
        else:
            context['branch_facet_selected'] = ''

        if year_facet:
            sqs = sqs.filter(year_of_passing_exact__in=year_facet)
            year_facet_string = None
            for year in year_facet:
                if not year_facet_string:
                    year_facet_string = str(year)
                else:
                    year_facet_string = year_facet_string + "," + str(year)
            context['year_facets_selected'] = year_facet_string
        else:
            context['year_facets_selected'] = ''

        if city_facet:
            sqs = sqs.filter(city_exact=city_facet)
            context['city_facet_selected'] = city_facet
        else:
            context['city_facet_selected'] = ''

        context['facets']['fields']['year_of_passing'] = self.facet_sorting(
            context['facets']['fields']['year_of_passing'])
        context['facets']['fields']['city'] = self.facet_sorting(
            context['facets']['fields']['city'])
        context['facets']['fields']['branch'] = self.facet_sorting(
            context['facets']['fields']['branch'])

        results = sqs.order_by('name')[0:INITIAL_RESULTS_COUNT]
        resultcount = sqs.count()
        context['resultcount'] = resultcount
        context['initialoffset'] = INITIAL_RESULTS_COUNT
        context['results'] = results

        return context

    # Sort with in available options and then with in greyed out options
    def facet_sorting(self, facets):
        return (
            sorted([x for x in facets if x[1]], key=lambda x: x[0]) +
            sorted([x for x in facets if not x[1]], key=lambda x: x[0])
        )


class SearchAjaxView(BaseSearchView, View):

    def dispatch(self, request):
        response = {}
        if request.method == 'GET':
            offset = int(request.GET.get('offset', 0))
            results, resultcount = self.get_results(
                request.GET.get('name', ''), request.GET.get(
                    'branch', ''), request.GET.get('year', ''), offset,
                request.GET.get('branch_facet', ''), request.GET.get('year_facet', ''), request.GET.get('city_facet', ''))
            response['success'] = 'true'
            resultdata = []
            if results:
                for result in results:
                    resultobj = {}
                    resultobj['profile_id'] = result.profile_id
                    resultobj['name'] = result.name
                    resultobj['branch'] = result.branch
                    resultobj['year_of_passing'] = result.year_of_passing
                    resultobj['city'] = result.city
                    resultdata.append(resultobj)

            response['data'] = resultdata
            response['latestoffset'] = offset + resultcount

        return HttpResponse(json.dumps(response))


def ajaxresponse(request):
    print "Incoming query to ajax = [" + request.get_full_path() + "]"
    #results = getsearchresults(request)

    context = {}
    context['request'] = request

    name = request.GET.get("name", '')
    branch = request.GET.get("branch", '')
    year = request.GET.get("year_of_passing", '')
    offset = request.GET.get("offset", '0')

    branch_facet = request.GET.get("branch_facet", '')
    year_facet = request.GET.get("year_of_passing_facet", '')

    sqs = SearchQuerySet().facet('branch')
    sqs = sqs.facet('year_of_passing')

    if name or branch or year:
        context['form'] = ProfileSearchBasicForm(request.GET)
        sqs = sqs.auto_query(name + branch + year)
    else:
        context['form'] = ProfileSearchBasicForm()

    context['facets'] = sqs.facet_counts()

    if branch_facet:
        context['facets']['fields']['year_of_passing'] = sqs.auto_query(
            branch_facet).facet_counts()['fields']['year_of_passing']
        context['branch_facet_selected'] = branch_facet
    else:
        context['branch_facet_selected'] = ''

    if year_facet:
        context['facets']['fields']['branch'] = sqs.auto_query(
            year_facet).facet_counts()['fields']['branch']
        context['year_facet_selected'] = year_facet
    else:
        context['year_facet_selected'] = ''

    offsetvalue = 0
    if(offset != ''):
        offsetvalue = int(offset)
    results = sqs.auto_query(branch_facet + year_facet).order_by('name')
    context['resultcount'] = results.count()
    results = results[offsetvalue:offsetvalue + 20]

    querystring = ""
    if(name != ''):
        querystring += ('&name=' + name)
    if(branch != ''):
        querystring += ('&branch=' + branch)
    if(year != ''):
        querystring += ('&year_of_passing=' + year)

    # querystring+=('&offset='+str(offsetvalue+20))

    if(branch_facet != ''):
        querystring += ('&branch_facet=' + branch_facet)
    if(year_facet != ''):
        querystring += ('&year_facet=' + year_facet)

    print "Outgoing query string from ajax = [" + querystring + "]"
    context['querystring'] = querystring

    html = ""
    if not results:
        html += "<p>Sorry, no results found.</p>\n"
    else:
        for result in results:
            html += "<div class=\"result_div\">\n"
            html += "<h2 class=\"name section-subtitle\">" + result.name + "</h2>\n"
            if(result.branch):
                html += "<p class=\"branch\">" + result.branch + "</p>\n"
            if(result.year_of_passing):
                html += "<p class=\"year_of_passing\">" + str(result.year_of_passing) + "</p>\n"
            if(result.branch):
                html += "<p class=\"city\">" + result.branch + "</p>\n"
            html += "</div>\n"
    # print html
    return HttpResponse(html)
