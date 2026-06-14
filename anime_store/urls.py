from django.urls import path
from django.contrib import admin
from store import views
from anime_store.authentication import login as auth_login_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='root'),
    path('admin/', admin.site.urls),

    # Login/Logout 
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    path('index/', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('catalog/', views.catalog, name='catalog'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path('support/', views.support, name='support'),
    path('about/', views.about, name='about'),
]