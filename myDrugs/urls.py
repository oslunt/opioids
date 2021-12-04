from django.urls import path
from .views import indexPageView, searchPageView, detailsPageView, recordsPageView, analysisPageView, showSingleRecordPageView, updatePrescribersPageView, prescriberSearchPageView, drugSearchPageView, detailsDrugPageView

urlpatterns = [
    path("search/prescriber/<int:prescriber>", detailsPageView, name="detailsPrescriber"),
    path("search/prescriber/", prescriberSearchPageView, name="prescriber"),
    path("search/drug/<int:drug>", detailsDrugPageView, name="detailsDrug"),
    path("search/drug/", drugSearchPageView, name="drug"),
    path("search/", searchPageView, name="search"),
    path("details/", detailsPageView, name="details"),
    path("analysis/", analysisPageView, name="analysis"),
    path("records/", recordsPageView, name="records"),
    path("showSingleRecord/<int:pres_id>", showSingleRecordPageView, name="showSingleRecord"),
    path("updatePrescribers/", updatePrescribersPageView, name="updatePres"),
    path("", indexPageView, name="index"),
] 