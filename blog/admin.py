from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from blog.models import Post


class PostAdmin(MPTTModelAdmin):
    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.select_related('author', 'parent')


admin.site.register(Post, PostAdmin)
