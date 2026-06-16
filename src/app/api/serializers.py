from rest_framework import serializers


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    """ModelSerializer whose fields are all marked read_only.

    Useful for serializers of nested objects and for list/retrieve,
    which should not accept data for writing.
    """

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields
