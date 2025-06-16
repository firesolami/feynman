from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("generate-summary/", views.generate_summary, name="generate_summary"),
    path("save-summary/", views.save_summary, name="save_summary"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("logout/", views.user_logout, name="logout"),
    path("summary-list/", views.summary_list, name="summary-list"),
    path("summary-details/<int:pk>", views.summary_details, name="summary-details"),
    path("delete-summary/<int:pk>", views.delete_summary, name="delete-summary"),
    path("ping/", views.ping, name="ping"),
]
