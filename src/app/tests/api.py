import json

from rest_framework.test import APIClient as DRFAPIClient

from users.models import User


class ApiClient(DRFAPIClient):
    """
    Test API client.

    - When `user` is passed, the client is immediately authenticated as that user.
    - The get/post/patch/put/delete methods check the response status (the expected
      one can be overridden via `expected_status`) and return already parsed JSON.
    - Pass `as_response=True` to get the raw Response object.
    """

    def __init__(self, user: User | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if user is not None:
            self.user = user
            self.force_authenticate(user=user)

    def get(self, *args, **kwargs):
        return self._request("get", kwargs.pop("expected_status", 200), *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request("post", kwargs.pop("expected_status", 201), *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request("patch", kwargs.pop("expected_status", 200), *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request("put", kwargs.pop("expected_status", 200), *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request("delete", kwargs.pop("expected_status", 204), *args, **kwargs)

    def _request(self, method_name, expected, *args, **kwargs):
        kwargs["format"] = kwargs.get("format", "json")
        as_response = kwargs.pop("as_response", False)
        method = getattr(super(), method_name)

        response = method(*args, **kwargs)
        if as_response:
            return response

        content = self._decode(response)
        assert response.status_code == expected, content
        return content

    def _decode(self, response):
        content = response.content.decode("utf-8", errors="ignore")
        if self._is_json(response):
            return json.loads(content) if content else None
        return content

    @staticmethod
    def _is_json(response) -> bool:
        return response.has_header("content-type") and "json" in response["content-type"]
