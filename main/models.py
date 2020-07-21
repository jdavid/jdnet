# Wagtail
from wagtail.core import models
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel


class Index(models.Page):
    def get_pages(self):
        return Page.objects.live().descendant_of(self)


class Page(models.Page):
    body = RichTextField(blank=True)

    content_panels = models.Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]
