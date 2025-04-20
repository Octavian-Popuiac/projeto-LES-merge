from django.urls import path
from .views import PerspectiveCreateView
from .views import LabelsWithPerspectiveAnswersView
from .views import PerspectiveByProjectView
from .views import PerspectiveAnswerSubmitView
from .views import ProjectPerspectiveMemberDataView
from .views import DeleteProjectPerspectiveView
from .views import DeleteUserPerspectiveAnswersView


urlpatterns = [
    path("perspectives/create/", PerspectiveCreateView.as_view(), name="create-perspective"),
    path("projects/<int:project_id>/examples/<int:example_id>/labels-perspective/", LabelsWithPerspectiveAnswersView.as_view(), name="labels-with-perspective",),
    path("perspectives/projects/<int:project_id>/", PerspectiveByProjectView.as_view(), name="perspective-by-project"),
    path("perspectives/answers/submit/", PerspectiveAnswerSubmitView.as_view(), name="submit-perspective-answers"),
    path("perspectives/projects/<int:project_id>/member-data/", ProjectPerspectiveMemberDataView.as_view(), name="perspective-member-data"),
    path("perspectives/projects/<int:project_id>/delete/", DeleteProjectPerspectiveView.as_view(), name="delete-project-perspective"),
    path("perspectives/projects/<int:project_id>/users/<int:user_id>/delete/", DeleteUserPerspectiveAnswersView.as_view(), name="delete-user-perspective"),
]
