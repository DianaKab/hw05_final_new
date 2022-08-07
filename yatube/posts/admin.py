from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title', 'slug', 'description')
    list_filter = ('title', 'slug', 'description')
    empty_value_display = '-пусто-'


admin.site.register(Group)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'author', 'text', 'created')
    search_fields = ('pk', 'post', 'author', 'text', 'created')
    list_filter = ('post', 'author', 'text', 'created')
    empty_value_display = '-пусто-'


admin.site.register(Comment)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('pk', 'user', 'author')
    list_filter = ('pk', 'user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(Follow)
