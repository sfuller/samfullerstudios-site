from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    pass
    # fields = ('name', 'title', 'content', 'parent')


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    pass
