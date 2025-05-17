from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('cars/', views.car_list, name='car_list'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(template_name='myapp/login.html'), name='logout'),
    
    # Password management
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='myapp/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='myapp/password_change_done.html'), name='password_change_done'),
    
    # User dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Car management
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/add/', views.add_car, name='add_car'),
    path('car/edit/<int:car_id>/', views.edit_car, name='edit_car'),
    path('car/delete/<int:car_id>/', views.delete_car, name='delete_car'),
    
    # Booking management
    path('booking/', views.my_bookings, name='my_bookings'),
    path('booking/add/<int:car_id>/', views.add_booking, name='add_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/manage/', views.manage_bookings, name='manage_bookings'),
    path('booking/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('booking/return/<int:booking_id>/', views.return_car, name='return_car'),
    
    # User management (admin/resource manager)
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    
    # Contact messages (admin)
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('messages/mark-all-read/', views.mark_all_messages_read, name='mark_all_messages_read'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
]
