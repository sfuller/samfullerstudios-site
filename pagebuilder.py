import argparse
import os

# import settings
#
# settings.configure()
import sys
import xml.etree.ElementTree as et
from typing import List, Optional, Set

import cssselect2 as cssselect2
import html5lib
import tinycss2
from django.core import files
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
from sfs_site.models import Page, File

parser = argparse.ArgumentParser()


def error(message: str) -> None:
    sys.stderr.write(f'{message}\n')
    sys.stderr.flush()


def main() -> int:
    args = parser.parse_args()

    # Find sfsfile
    if not os.path.isfile('sfsfile'):
        error('Could not find sfsfile in current directory')
        return 1

    build_pages()
    build_files()


def build_pages():
    paths: List[str] = []

    for dirpath, dirnames, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext != '.html':
                continue
            paths.append(os.path.join(dirpath, filename))

    pages_being_processed = [os.path.splitext(os.path.split(path)[1])[0] for path in paths]

    # Ensure all pages exist in database first
    for page_name in pages_being_processed:
        try:
            Page.objects.get(name=page_name)
        except Page.DoesNotExist:
            page = Page(name=page_name)
            page.save()

    for path in paths:
        print(f'Building page {path}')
        build_page(path)


def build_files():
    paths: List[str] = []

    for dirpath, dirnames, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if name.startswith('.') or ext == '.html':
                continue
            paths.append(os.path.join(dirpath, filename))

    for path in paths:
        print(f'Building file {path}')

        filename = os.path.split(path)[1]
        handle, _ = os.path.splitext(filename)
        if handle.startswith('.'):
            continue

        try:
            file = File.objects.get(name=handle)
        except File.DoesNotExist:
            file = File(name=handle)

        with open(path, 'rb') as f:
            file.file.save(filename, files.File(f))

        file.save()


def build_page(filepath: str) -> None:
    with open(filepath, "rb") as f:
        document: et.Element = html5lib.parse(f)

    name, _ = os.path.splitext(os.path.split(filepath)[1])
    page = Page.objects.get(name=name)

    page.order = int(select('meta[name=sfs_order]', document).get_attr('content') or 0)
    page.active = parse_bool_attr_value(select('meta[name=sfs_active]', document).get_attr('content'))
    page.icon = select('meta[name=sfs_icon]', document).get_attr('content') or ''
    page.title = select('title', document).text

    parent_name = select('meta[name=sfs_parent]', document).get_attr('content')
    if parent_name:
        parent_page = Page.objects.get(name=parent_name)
        page.parent = parent_page

    body = select('body', document).get(0)
    page.content = html5lib.serialize(body)

    page.save()


def parse_bool_attr_value(value: Optional[str]) -> bool:
    if not value:
        return False
    lower = value.lower()
    return True if lower == 'yes' or lower == 'true' else False


def select(rule: str, element: et.Element) -> 'PQuery':
    rules = tinycss2.parse_stylesheet(rule + ' {}', skip_whitespace=True)
    matcher = cssselect2.Matcher()

    for rule in rules:
        selectors = cssselect2.compile_selector_list(rule.prelude)
        for selector in selectors:
            matcher.add_selector(selector, None)

    wrapper = cssselect2.ElementWrapper.from_html_root(element)

    matching_elements: List[et.Element] = []

    for element in wrapper.iter_subtree():
        matches = matcher.match(element)
        if matches:
            matching_elements.append(element.etree_element)

    return PQuery(matching_elements)


class PQueryIter(object):
    def __init__(self, elements: List[et.Element]):
        self.index = 0
        self.elements = elements

    def __next__(self):
        if self.index >= len(self.elements):
            raise StopIteration
        pq = PQuery([self.elements[self.index]])
        self.index += 1
        return pq


class PQuery(object):
    def __init__(self, elements: List[et.Element]) -> None:
        self.elements = elements

    def get(self, index: int) -> Optional[et.Element]:
        if index >= len(self.elements) or index < 0:
            return None
        return self.elements[index]

    def get_attr(self, name: str) -> Optional[str]:
        for element in self.elements:
            return element.attrib.get(name)
        return None

    def set_attr(self, name: str, value: str) -> 'PQuery':
        for element in self.elements:
            element.attrib[name] = value
        return self

    def del_attr(self, name: str) -> 'PQuery':
        for element in self.elements:
            del element.attrib[name]
        return self

    @property
    def text(self) -> str:
        for element in self.elements:
            return element.text
        return ''

    @text.setter
    def set_text(self, text: str) -> 'PQuery':
        for element in self.elements:
            element.text = text
        return self

    def __iter__(self):
        return PQueryIter(self.elements.copy())


if __name__ == '__main__':
    main()
