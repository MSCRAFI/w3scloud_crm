from django.urls import path
from . import views

urlpatterns = [
    path("zoho/login/", views.zoho_login, name="zoho_login"),
    path("zoho/callback/", views.zoho_callback, name="zoho_callback"),
    path("zoho/leads/", views.list_leads, name="zoho_leads"),
    path("zoho/leads/create/", views.create_lead, name="zoho_create"),
    path("zoho/leads/<str:record_id>/", views.get_lead, name="zoho_get"),
]