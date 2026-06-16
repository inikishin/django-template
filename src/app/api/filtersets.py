import operator
from functools import reduce

from django.db.models import Q, QuerySet
from django.db.models.constants import LOOKUP_SEP
from django_filters import rest_framework as filters


class SearchFilterSet(filters.FilterSet):
    """
    Adds full-text search over a list of fields via the `search` query parameter.

    Usage:

        class MyFilterSet(SearchFilterSet):
            search_fields = ["name", "related__name"]

            class Meta:
                model = MyModel
                fields = ["status"]

    Search terms are separated by spaces and/or commas. Each term is searched
    across all fields (OR), while between terms AND applies.
    """

    search_fields: list[str] = []

    search = filters.CharFilter(method="filter_search")

    @staticmethod
    def get_search_terms(search_value: str) -> list[str]:
        """Split the search value into terms by spaces and commas."""
        params = search_value.replace("\x00", "").replace(",", " ")
        return params.split()

    def _get_search_query(self, filter_value: str) -> Q:
        search_terms = self.get_search_terms(filter_value)
        if not search_terms:
            return Q()

        orm_lookups = [LOOKUP_SEP.join([field, "icontains"]) for field in self.search_fields]

        conditions = []
        for term in search_terms:
            queries = [Q(**{lookup: term}) for lookup in orm_lookups]
            conditions.append(reduce(operator.or_, queries))

        return reduce(operator.and_, conditions)

    def filter_search(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        search_query = self._get_search_query(value)
        if not self.search_fields or not search_query:
            return queryset
        return queryset.filter(search_query)
