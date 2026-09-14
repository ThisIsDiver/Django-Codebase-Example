from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Article


# Create your views here.
class ArticleListView(ListView):
    queryset = Article.objects.filter(pub_date__isnull=False).order_by("-pub_date").all()
    context_object_name = "articles"
    template_name = "blogapp/article-list.html"

    def get_queryset(self):
        articles = Article.objects.select_related("author", "category").prefetch_related("tags").defer("pub_date")
        return articles

class ArticleDetailView(DetailView):
    model = Article
    template_name = "blogapp/article-details.html"
    context_object_name = "article"

class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes or additions blog articles"
    link = reverse_lazy("blogapp:article-list")

    def items(self):
        return Article.objects.filter(pub_date__isnull=False).order_by("-pub_date")[:5]

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item:Article):
        return item.content[:200]

    
