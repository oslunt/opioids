from django.urls import path
from .views import indexPageView, searchPageView, detailsPageView, recordsPageView, analysisPageView, showSingleRecordPageView, updatePrescribersPageView

urlpatterns = [
    path("search/", searchPageView, name="search"),
    path("details/", detailsPageView, name="details"),
    path("analysis/", analysisPageView, name="analysis"),
    path("records/", recordsPageView, name="records"),
    path("showSingleRecord/<int:pres_id>", showSingleRecordPageView, name="showSingleRecord"),
    path("updatePrescribers/", updatePrescribersPageView, name="updatePres"),
    path("", indexPageView, name="index"),
]