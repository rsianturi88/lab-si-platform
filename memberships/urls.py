from django.urls import path
from . import views
urlpatterns=[
 path('', views.member_list, name='member_list'),
 path('create/', views.member_create, name='member_create'),
 path('<int:pk>/', views.member_detail, name='member_detail'),
 path('<int:pk>/edit/', views.member_edit, name='member_edit'),
 path('<int:pk>/delete/', views.member_delete, name='member_delete'),
 path('groups/', views.group_list, name='group_list'),
 path('groups/create/', views.group_create, name='group_create'),
 path('groups/<int:pk>/', views.group_detail, name='group_detail'),
 path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
 path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
]
