import datetime

import html5lib
import xml.etree.ElementTree as et

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context
from django.urls import reverse
from django.views import View

from pagebuilder import select
from . import models
import json
import queue
import django.template.loader
import django.contrib.staticfiles.finders

from .templatetags.sfs import file


class PageData(object):
    def __init__(self, **kwargs):
        self.content = kwargs.get('content')
        self.title = kwargs.get('title')
        self.status = kwargs.get('status')
        self.name = kwargs.get('name')
        self.parent_name = kwargs.get('parent_name')


class PageNode(object):
    def __init__(self, page):
        self.page = page
        self.children = []


class PageView(View):
    template_name = 'base.html'
    not_found_template_name = '404.html'

    def get_title_text(self, page_title):
        return ' '.join([page_title, '-', 'Sam Fuller'])

    def get(self, request, **kwargs):
        name = kwargs.get('name')
        try:
            page = models.Page.objects.get(name=name)
        except models.Page.DoesNotExist:
            page = None

        status = None
        content = None
        title = None
        name = None
        parent_name = None
        if page is None:
            status = 404
            title = 'Page Not Found'
            template = django.template.loader.get_template(PageView.not_found_template_name)
            content = template.render()
        else:
            status = 200
            content = self.render_content(page.content)
            title = self.get_title_text(page.title)
            name = page.name
            if page.parent is not None:
                parent_name = page.parent.name

        data = PageData(
            status=status,
            content=content,
            title=title,
            name=name,
            parent_name=parent_name
        )

        if request.GET.get('fragment', False):
            return self.render_fragment(request, data)

        return self.render_full_page(request, data)

    def render_content(self, content_text: str) -> str:
        document: et.Element = html5lib.parse(content_text)
        body = select('body', document).get(0)

        # Process src attributes
        for element in select('*[data-sfs-src]', body):
            src = element.get_attr('src')
            mode = element.get_attr('data-sfs-src')

            if mode == 'static':
                element.set_attr('src', static(src))
            elif mode == 'file':
                element.set_attr('src', file(src))

            element.del_attr('data-sfs-src')

        # Process anchor hrefs
        for a in select('a[data-sfs-href]', body):
            name = a.get_attr('href')
            a.set_attr('href', reverse('page', kwargs={'name': name}))
            a.del_attr('data-sfs-href')

        return html5lib.serialize(body)

    def get_common_context(self, data):
        return {
            'content': data.content,
            'title': data.title
        }

    def render_full_page(self, request, data):
        root_node = PageNode(None)
        nodes = queue.Queue()
        nodes.put(root_node)
        while not nodes.empty():
            node = nodes.get()
            children = models.Page.objects.filter(active=True, parent=node.page).order_by('order')
            for child in children:
                child_node = PageNode(child)
                node.children.append(child_node)
                nodes.put(child_node)

        context = self.get_common_context(data)
        context.update({
            'active_page_name': data.name,
            'active_page_parent_name': data.parent_name,
            'pages': root_node,
            'time': datetime.datetime.utcnow()
        })
        return render(request, PageView.template_name, context, status=data.status)

    def render_fragment(self, request, data):
        context = self.get_common_context(data)
        json_content = json.dumps(context)
        return HttpResponse(
            json_content,
            content_type='application/json',
            status=data.status
        )


class HomeView(PageView):
    def get_title_text(self, page_title):
        return 'Sam Fuller'
