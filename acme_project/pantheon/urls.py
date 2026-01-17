# pantheon/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('figures/', views.figure_list, name='figure_list'),
    path('figures/create/', views.figure_create, name='figure_create'),
    path('figures/<int:pk>/', views.figure_detail, name='figure_detail'),
    path('figures/<int:pk>/edit/', views.figure_update, name='figure_update'),
    path('figures/<int:pk>/delete/', views.figure_delete, name='figure_delete'),
    path('statistics/', views.statistics_view, name='statistics'),
]
