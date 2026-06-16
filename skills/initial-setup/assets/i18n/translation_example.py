from modeltranslation.translator import TranslationOptions, register

from posts.models import Post


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ("title", "description")
