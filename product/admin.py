from django.contrib import admin
from .models import *


class ProductAdmin(admin.ModelAdmin):
    """ """
    list_display = ('id', 'vcode', 'name', 'brand', 'price', 'latest_updated')
    readonly_fields = ('latest_updated',)
    search_fields = ('vcode', 'name', 'old_name')
    list_filter = ('brand',)


admin.site.register(ProductModel, ProductAdmin)