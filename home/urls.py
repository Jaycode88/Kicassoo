from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
     path('', views.index, name='home'),
     path('about/', views.about, name='about'),
     path('events/', views.events, name='events'),
     path('collections/all/', views.all_collections, name='all_collections'),

     path('collections/perfectmoments/',
         views.perfectmoments, name='perfectmoments'),

     path('collections/ropesofwisdom/',
         views.ropesofwisdom, name='ropesofwisdom'),

     path('collections/thekingdom/', views.thekingdom, name='thekingdom'),
     path('contact/', views.contact, name='contact'),
     path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
     path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
