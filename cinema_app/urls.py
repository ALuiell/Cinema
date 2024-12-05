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
from django.urls import path, include
from cinema_app import custom_auth_views, views, user_profile_views, services
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Main views
    path('', views.redirect_to_home),
    path('home/', views.HomePageView.as_view(), name='home'),
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movies/<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),


    # Session-related views
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/<slug:slug>/', views.SessionListView.as_view(), name='movie_session_list'),

    path('session/<slug:slug>/', views.SessionDetailView.as_view(), name='session_detail'),

    # Ticket purchasing
    path('purchase/<slug:session_slug>/', views.purchase_ticket, name='purchase_ticket'),
    path('purchase_success/<int:order_id>/', views.purchase_success, name='success_purchase_url'),
    path('purchase_cancel/<int:order_id>/', views.purchase_cancel, name='cancel_purchase_url'),
    path('session/<slug:session_slug>/available_seats/', views.get_available_seats, name='available_seats'),
    # Payment
    path('retry_purchase/order/<int:pk>', views.retry_payment, name='retry_payment'),

    # Authentication paths
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('accounts/register/', custom_auth_views.UserRegisterView.as_view(), name='register'),
    path('accounts/login/', custom_auth_views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', custom_auth_views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # User profile views
    path('profile/', user_profile_views.UserProfileView.as_view(), name='profile'),
    path('profile/orders/', user_profile_views.UserOrderListView.as_view(), name='user_orders'),
    path('profile/settings/', user_profile_views.UserProfileSettingsView.as_view(), name='profile_settings'),
]

# Static files (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
