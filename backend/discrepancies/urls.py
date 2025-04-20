from django.urls import path
from .views import (DiscrepancyListCreateView,
                    DiscrepancyDetectView,
                    DiscrepancySaveView,
                    DiscrepancyUpdateView,
                    ExampleAnnotationsView)

urlpatterns = [
    path("projects/<int:project_id>/discrepancies", DiscrepancyListCreateView.as_view(), name="discrepancy-list"),
    path("projects/<int:project_id>/discrepancies/detect", DiscrepancyDetectView.as_view(), name="discrepancy-detect"),
    path("projects/<int:project_id>/examples/<int:example_id>/discrepancies/save", DiscrepancySaveView.as_view(), name="discrepancy-save"),
    path("discrepancies/<int:pk>/", DiscrepancyUpdateView.as_view(), name="discrepancy-update"),
    path("projects/<int:project_id>/examples/<int:example_id>/annotations", ExampleAnnotationsView.as_view(), name="example-annotations"),
]
