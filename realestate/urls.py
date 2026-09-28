from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.properties, name='properties'),
    path('properties/<slug:slug>/', views.property_detail, name='property_detail'),
    path('properties/<slug:slug>/schedule-self-tour/', views.tour_request, name='tour_request'),
    path('properties/<slug:slug>/schedule-self-tour/success/<int:tour_id>/', views.tour_success, name='tour_success'),
]
