from haystack.indexes import SearchIndex, Indexable
from userprofile.models import UserProfile, SYNONYM, Synonym, GROUP,\
    RT_COLLEGE
from haystack.fields import FacetMultiValueField, FacetCharField, \
    IntegerField, CharField

class UserProfileIndex(SearchIndex, Indexable):
    profile_id = IntegerField(indexed=False, model_attr="id")  # used for preparing url
    text = CharField(document=True)
    name = CharField(model_attr="get_full_name")
    course = FacetMultiValueField()
    branch = FacetMultiValueField()
    year_of_graduation = FacetMultiValueField()
    city = FacetCharField()
    state = FacetCharField()
    country = FacetCharField()
    higher_education_degree = FacetMultiValueField()
    higher_education_college = FacetMultiValueField()
    higher_education_college_synonyms = FacetMultiValueField()
    higher_education_college_groups = FacetMultiValueField()
    company = FacetMultiValueField()
    tags = FacetMultiValueField()

    def get_model(self):
        return UserProfile

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return UserProfile.objects.all()

    def prepare_course(self, object):
        return [sc.branch.course.name for sc in object.studentsection_set.all() if sc.branch]

    def prepare_branch(self, object):
        return [sc.branch.name for sc in object.studentsection_set.all() if sc.branch]

    def prepare_year_of_graduation(self, object):
        return [sc.year_of_graduation for sc in object.studentsection_set.all()]

    def prepare_higher_education_degree(self, object):
        return [he.degree.name for he in object.highereducationdetail_set.all() if he.degree]

    def prepare_higher_education_college_synonyms(self, object):
        retval = []
        for he in object.highereducationdetail_set.all():
            if he.college:
                retval.extend([hes.value for hes in Synonym.objects.filter(parent_id=he.college.id,
                                                                          resourcetype=RT_COLLEGE,
                                                                          aliastype=SYNONYM)])
        return retval

    def prepare_higher_education_college_groups(self, object):
        retval = []
        for he in object.highereducationdetail_set.all():
            if he.college:
                retval.extend([hes.value for hes in Synonym.objects.filter(parent_id=he.college.id,
                                                                          resourcetype=RT_COLLEGE,
                                                                          aliastype=GROUP)])
        return retval

    def prepare_higher_education_college(self, object):
        return [he.college.name for he in object.highereducationdetail_set.all() if he.college]

    def prepare_company(self, object):
        return [ed.employer.name for ed in object.employmentdetail_set.all() if ed.employer]

    def prepare_tags(self, object):
        return [tag.name for tag in object.tags.all()]

    def prepare(self, obj):
        prepared_data = super(UserProfileIndex, self).prepare(obj)

        searchable_text = []

        searchable_text.extend(
            [prepared_data['name'], prepared_data['city'], prepared_data['state'],
             prepared_data['country'], ])

        searchable_text.extend([" ".join(prepared_data['course'])])
        searchable_text.extend([" ".join(prepared_data['branch'])])
        searchable_text.extend([" ".join([str(x) for x in prepared_data['year_of_graduation']])])
        searchable_text.extend([" ".join(prepared_data['higher_education_degree'])])
        searchable_text.extend([" ".join(prepared_data['higher_education_college'])])
        searchable_text.extend([" ".join(prepared_data['higher_education_degree'])])
        searchable_text.extend([" ".join(prepared_data['higher_education_college_synonyms'])])
        searchable_text.extend([" ".join(prepared_data['higher_education_college_groups'])])
        searchable_text.extend([" ".join(prepared_data['higher_education_college'])])
        searchable_text.extend([" ".join(prepared_data['company'])])
        searchable_text.extend([" ".join(prepared_data['tags'])])

        prepared_data['text'] = "\n".join([x for x in searchable_text if x is not None])
        print obj.id

        return prepared_data
