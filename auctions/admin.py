from django.contrib import admin

from .models import Category, NewListing

# Register your models here.
admin.site.register(Category)
admin.site.register(NewListing)