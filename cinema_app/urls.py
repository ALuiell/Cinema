"""
URL configuration for cinema_app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from cinema_app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('home/', views.HomePageView.as_view(), name='home'),
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('movies/genre/<str:genre_name>/', views.MovieGenreListView.as_view(), name='movie_genre_list'),

    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/<slug:slug>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('movies/<slug:slug>/sessions/', views.MovieSessionsView.as_view(), name='movie_sessions'),
    path('purchase/<slug:session_slug>/', views.purchase_ticket, name='purchase_ticket'),
    path('purchase_success/<int:seat_number>/<int:price>/<int:session_id>/', views.purchase_success,
         name='success_purchase_url'),
    path('session/<slug:session_slug>/available_seats/', views.get_available_seats, name='available_seats'),
    path('accounts/register/', views.UserRegisterView.as_view(), name='register'),
    path('accounts/login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/tickets/', views.UserTicketListView.as_view(), name='user_tickets'),
    path('profile/settings/', views.UserProfileSettingsView.as_view(), name='profile_settings'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
