from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Overview
    path('', views.dashboard_index, name='index'),

    # Appointments
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/calendar/', views.appointments_calendar, name='appointments_calendar'),

    # Patients
    path('patients/', views.patients_list, name='patients_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),

    # Medical Services
    path('services/', views.services_list, name='services_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),

    # Education Series & Videos
    path('education/', views.education_series_list, name='education_series_list'),
    path('education/series/create/', views.series_create, name='series_create'),
    path('education/series/<int:pk>/edit/', views.series_edit, name='series_edit'),
    path('education/video/create/', views.video_create, name='video_create'),
    path('education/video/<int:pk>/edit/', views.video_edit, name='video_edit'),
    path('education/video/<int:pk>/delete/', views.video_delete, name='video_delete'),

    # Articles
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),

    # Doctor Profile
    path('doctor-profile/', views.doctor_profile_edit, name='doctor_profile'),

    # Settings & Logs
    path('settings/', views.site_settings_edit, name='site_settings'),
    path('messages/', views.contact_messages_list, name='contact_messages'),
    path('activity-logs/', views.activity_logs_list, name='activity_logs'),
]

