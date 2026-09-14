from django.urls import path

from .views import ArticleListView, ArticleDetailView, LatestArticlesFeed

app_name = "blogapp"

urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article-details"),
    path("feed/", LatestArticlesFeed(), name="article-feed")
]