from django.contrib import admin
from .models import FollowingFollower, BlockList
# Register your models here.


class FollowingFollowerAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'is_accepted', 'creation_date', 'acception_date')
    list_filter = ('is_accepted', 'creation_date', 'acception_date')
    search_fields = ('follower__username', 'follower__email', 'following__username', 'following__email')
    ordering = ('-creation_date',)



class BlockListAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'creation_date')
    list_filter = ('creation_date',)
    search_fields = ('blocker__username', 'blocker__email', 'blocked__username', 'blocked__email')
    ordering = ('-creation_date',)



admin.site.register(FollowingFollower, FollowingFollowerAdmin)
admin.site.register(BlockList, BlockListAdmin)
