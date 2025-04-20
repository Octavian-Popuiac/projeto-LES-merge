from django.urls import path
from .views import (
    GroupListCreateView, 
    GroupDetailView, 
    GroupPermissionList,
    GroupMembersView,
    GroupPermissionsView,
    UserPermissionView,
    UserPermissionsView,
    GroupDebugView,
    CheckGroupName
)

urlpatterns = [
    path("groups/", GroupListCreateView.as_view(), name="group-list-create"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group-detail"),
    path("groups/with-permissions/", GroupPermissionList.as_view(), name="group-with-permissions"),
    path("groups/<int:pk>/users/", GroupMembersView.as_view(), name="group-users"),
    path("groups/all_permissions/", GroupPermissionList.as_view(), name="all-permissions"),
    path("groups/<int:pk>/group_permissions/", GroupPermissionsView.as_view(), name="group-permissions-list"),
    path('groups/check-name/', CheckGroupName.as_view(), name='check-group-name'),
    path("groups/<int:pk>/permissions/", GroupPermissionsView.as_view(), name="group-permissions-update"),


    path("groups/debug/", GroupDebugView.as_view(), name="group-debug"),
]