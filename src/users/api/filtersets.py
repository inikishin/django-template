from app.api.filtersets import SearchFilterSet
from users.models import User


class UserFilterSet(SearchFilterSet):
    search_fields = ["username", "email", "first_name", "last_name"]

    class Meta:
        model = User
        fields = ["is_active", "is_superuser"]
