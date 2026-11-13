from django.urls import path
from . import views_public

app_name = 'public'

urlpatterns = [
    path('', views_public.home_view, name='home'),
    path('about/', views_public.about_view, name='about'),
    path('qualifications/', views_public.qualifications_view, name='qualifications'),
    path('services/', views_public.services_list_view, name='services'),
    path('services/<slug:slug>/', views_public.service_detail_view, name='service_detail'),
    path('expertise/', views_public.expertise_view, name='expertise'),
    path('education/', views_public.education_list_view, name='education'),
    path('education/<slug:slug>/', views_public.series_detail_view, name='series_detail'),
    path('blog/', views_public.blog_list_view, name='blog'),
    path('blog/<slug:slug>/', views_public.article_detail_view, name='article_detail'),
    path('booking/', views_public.booking_view, name='booking'),
    path('booking/success/<str:booking_ref>/', views_public.booking_success_view, name='booking_success'),
    path('booking/status/', views_public.booking_status_view, name='booking_status'),
    path('api/slots/', views_public.api_available_slots, name='api_available_slots'),
    path('contact/', views_public.contact_view, name='contact'),
]

