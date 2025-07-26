from django.contrib import admin
from .models import UserProfile, Vehicle, Ride, Booking

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Vehicle)
admin.site.register(Ride)
admin.site.register(Booking)