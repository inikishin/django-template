from django.contrib import admin

from posts.models import Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "language", "title", "author", "is_draft", "created_at", "updated_at"]
    list_filter = ["language", "author", "is_draft", "updated_at", "tags"]
    search_fields = ["title", "description"]
