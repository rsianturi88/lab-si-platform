from django.urls import path
from . import views
urlpatterns=[
    path('', views.activity_list, name='activity_list'),
    path('create/', views.activity_create, name='activity_create'),
    path('<int:pk>/', views.activity_detail, name='activity_detail'),
    path('<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('<int:pk>/delete/', views.activity_delete, name='activity_delete'),
]
