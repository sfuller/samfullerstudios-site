from django import template

from sfs_site.models import File


register = template.Library()


@register.simple_tag
def file(name):
    file = File.objects.get(name=str(name))

    filename = '/media/'
    if file:
        filename += file.file.name
    else:
        filename += 'NOTFOUND_' + name

    return filename
