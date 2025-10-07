from django.contrib import admin
from .models import Post, PostFileContent
# Register your models here.

class PostFileContentInline(admin.TabularInline):
    model = PostFileContent
    extra = 0
    readonly_fields = ('creation_date', 'update_date')
    max_num = 10
    can_delete = True

class PostAdmin(admin.ModelAdmin):
    list_display = ('user_account', 'caption', 'is_open_to_comment', 'plan', 'creation_date')
    list_filter = ('creation_date', 'is_open_to_comment')
    search_fields = ('user_account__username', 'user_account__email', 'caption')
    ordering = ('-creation_date',)
    inlines = [PostFileContentInline]


admin.site.register(Post, PostAdmin)
