from django.urls import path
from .views import indexPageView, searchPageView, detailsPageView, recordsPageView, analysisPageView

urlpatterns = [
    path("search/", searchPageView, name="search"),
    path("details/", detailsPageView, name="details"),
    path("records/", recordsPageView, name="records"),
    path("analysis/", analysisPageView, name="analysis"),
    path("", indexPageView, name="index"),
]