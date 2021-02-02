from django.db import models


class Page(models.Model):
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    icon = models.CharField(max_length=64, blank=True)
    order = models.IntegerField(default=0)
    content = models.TextField()
    parent = models.ForeignKey('Page', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=128)
    file = models.FileField(upload_to='files')

    def __str__(self):
        return self.name
