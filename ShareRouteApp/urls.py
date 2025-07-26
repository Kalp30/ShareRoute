from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Auth
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    path('profile/', views.profile, name='profile'),

    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('driver/post-ride/', views.post_ride, name='post_ride'),
    path('driver-bookings/<int:ride_id>/', views.driver_bookings, name='driver_bookings'),
    path('driver/edit-vehicle/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),
    path('driver/edit-ride/<int:ride_id>/', views.edit_ride, name='edit_ride'),
    path('driver/delete-vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('driver/delete-ride/<int:ride_id>/', views.delete_ride, name='delete_ride'),

    path('ride/<int:ride_id>/', views.ride_detail, name='ride_detail'),
    path('ride/<int:ride_id>/book/', views.book_ride, name='book_ride'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('driver/<int:driver_id>/rides/', views.driver_rides, name='driver_rides'),

    path('booking-history/', views.booking_history, name='booking_history'),
]