from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    is_driver = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



class Vehicle(models.Model):
    driver = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    vehicle_name = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20, unique=True, blank=True)
    is_electric = models.BooleanField(default=False)
    vehicle_document = models.FileField(upload_to='vehicle_docs/', blank=True, null=True)
    vehicle_image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle_name} ({self.license_plate})"


class Ride(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    origin_address = models.CharField(max_length=200, blank=True)
    destination_address = models.CharField(max_length=200, blank=True)
    departure_time = models.DateTimeField(default=timezone.now)
    available_seats = models.PositiveIntegerField()
    distance_km = models.FloatField(default=0.0)
    co2_saved = models.FloatField(default=0.0)
    rate = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.origin_address} → {self.destination_address}"



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    seats_booked = models.PositiveIntegerField(default=1)
    booking_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} booked {self.seats_booked} seat(s) on {self.ride}"