from django.contrib.sitemaps import Sitemap

from .models import Article

class BlogSiteMap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Article.objects.filter(pub_date__isnull=False).order_by("-pub_date")

    def lastmode(self, obj: Article):
        return obj.pub_date

