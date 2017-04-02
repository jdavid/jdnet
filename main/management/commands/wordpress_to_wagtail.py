"""
Forked from https://github.com/thelabnyc/wagtail_blog
"""

# Standard Library
from calendar import month_name
import html
import os
from urllib.parse import urlsplit
import urllib.request

from bs4 import BeautifulSoup

# Django
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth import get_user_model
from django.utils.html import linebreaks

# Wagtail
from wagtail.wagtailcore.models import Site
from wagtail.wagtailimages.models import Image

# Project
from main.models import Index, Page
from .wp_xml_parser import XML_parser


def get_child_or_add(parent, model, slug, **kw):
    qs = model.objects.child_of(parent).filter(slug=slug)
    if qs.exists():
        child = qs.get()
        for key, value in kw.items():
            setattr(child, key, value)
        child.save()
        return child

    child = model(slug=slug, **kw)
    return parent.add_child(instance=child)


class Command(BaseCommand):
    """
    This is a management command to migrate a Wordpress site to Wagtail.
    Two arguments should be used - the site to be migrated and the site it is
    being migrated to.

    Users will first need to make sure the WP REST API(WP API) plugin is
    installed on the self-hosted Wordpress site to migrate.
    Next users will need to create a BlogIndex object in this GUI.
    This will be used as a parent object for the child blog page objects.
    """

    def add_arguments(self, parser):
        """have to add this to use args in django 1.8"""
        parser.add_argument('xml', help="XML file to import from")
        parser.add_argument('--url',
                            default=False,
                            help="Base url of wordpress instance")

    def handle(self, *args, **options):
        """gets data from WordPress site"""
        self.xml_path = options['xml']
        self.url = options.get('url')

        self.xml_parser = XML_parser(self.xml_path)
        posts = self.xml_parser.get_posts_data()
        site = Site.objects.get(is_default_site=True)
        self.create_blog_pages(posts, site)

    def prepare_url(self, url):
        if url.startswith('//'):
            url = 'http:{}'.format(url)
        if url.startswith('/'):
            prefix_url = self.url
            if prefix_url and prefix_url.endswith('/'):
                prefix_url = prefix_url[:-1]
            url = '{}{}'.format(prefix_url or "", url)
        return url

    def convert_html_entities(self, text, *args, **options):
        """converts html symbols so they show up correctly in wagtail"""
        return html.unescape(text)

    def create_images_from_urls_in_content(self, body):
        """create Image objects and transfer image files to media root"""
        soup = BeautifulSoup(body, "html5lib")
        for img in soup.findAll('img'):
            old_url = img['src']
            if 'width' in img:
                width = img['width']
            if 'height' in img:
                height = img['height']
            else:
                width = 100
                height = 100
            path, file_ = os.path.split(img['src'])
            if not img['src']:
                continue  # Blank image
            if img['src'].startswith('data:'):
                continue # Embedded image
            try:
                remote_image = urllib.request.urlretrieve(
                    self.prepare_url(img['src']))
            except (urllib.error.HTTPError,
                    urllib.error.URLError,
                    UnicodeEncodeError,
                    ValueError):
                print("Unable to import " + img['src'])
                continue
            image = Image(title=file_, width=width, height=height)
            try:
                image.file.save(file_, File(open(remote_image[0], 'rb')))
                image.save()
                new_url = image.file.url
                body = body.replace(old_url, new_url)
                body = self.convert_html_entities(body)
            except TypeError:
                print("Unable to import image {}".format(remote_image[0]))
        return body

    def create_blog_pages(self, posts, site):
        """create Blog post entries from wordpress data"""

        root = site.root_page
        for post in posts:
            link = post['link']
            status = post['{wp}status']

            # Skip draft
            if status != 'publish':
                print('SKIP (status={}) {}'.format(status, link))
                continue

            # Path
            *path, slug = urlsplit(link)[2][1:].split('/')
            if path:
                year, month = path
                title = 'Year: {}'.format(year)
                parent = get_child_or_add(root, Index, year, title=title)
                title = 'Month: {} {}'.format(month_name[int(month)], year)
                parent = get_child_or_add(parent, Index, month, title=title)
            else:
                parent = root

            # Page
            slug = slug.split('.')[0] # Remove .html
            page = get_child_or_add(parent, Page, slug,
                title=post['title'],
                body=post['{content}encoded'],
            )

#           # get image info from content and create image objects
#           body = self.create_images_from_urls_in_content(body)

#           # format the date
#           date = post.get('date')[:10]
#           try:
#               new_entry = Page.objects.get(slug=slug)
#               new_entry.title = title
#               new_entry.body = body
#               new_entry.owner = user
#               new_entry.save()
#           except Page.DoesNotExist:
#               new_entry = blog_index.add_child(instance=Page(
#                   title=title, slug=slug, search_description="description",
#                   date=date, body=body, owner=user))
#           featured_image = post.get('featured_image')
#           if featured_image is not None:
#               title = post['featured_image']['title']
#               source = post['featured_image']['source']
#               path, file_ = os.path.split(source)
#               source = source.replace('stage.swoon', 'swoon')
#               try:
#                   remote_image = urllib.request.urlretrieve(
#                       self.prepare_url(source))
#                   width = 640
#                   height = 290
#                   header_image = Image(title=title, width=width, height=height)
#                   header_image.file.save(
#                       file_, File(open(remote_image[0], 'rb')))
#                   header_image.save()
#               except UnicodeEncodeError:
#                   header_image = None
#                   print('unable to set header image {}'.format(source))
#           else:
#               header_image = None
#           new_entry.header_image = header_image
#           new_entry.save()
