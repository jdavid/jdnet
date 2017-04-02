# Wagtail
from wagtail.wagtailcore import models
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class Index(models.Page):
    def get_pages(self):
        return Page.objects.live().descendant_of(self)


class Page(models.Page):
    body = RichTextField(blank=True)

    content_panels = models.Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]
