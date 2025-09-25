from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('build/', views.build_resume, name='build_resume'),
    path('download/<int:resume_id>/', views.download_resume, name='download_resume'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('track-download/<int:resume_id>/', views.track_download, name='track_download'),
    path('resumes/edit/<int:resume_id>/', views.edit_resume, name='edit_resume'),
    path('delete/<int:resume_id>/', views.delete_resume, name='delete_resume'),
]