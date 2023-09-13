from django import forms
from tinymce.widgets import TinyMCE

from .models import Post


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Post
        fields = '__all__'
