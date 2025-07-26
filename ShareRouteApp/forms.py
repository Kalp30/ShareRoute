from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import DateTimeInput

from .models import UserProfile, Vehicle, Ride, Booking


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)
    is_driver = forms.BooleanField(required=False, label="Register as Driver")

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'phone_number', 'profile_picture', 'is_driver'
        ]

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                profile_picture=self.cleaned_data.get('profile_picture'),
                is_driver=self.cleaned_data['is_driver']
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture', 'is_driver']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['is_driver'].widget.attrs.update({'class': 'form-check-input'})



class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_name', 'license_plate', 'is_electric', 'vehicle_image', 'vehicle_document']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            'vehicle', 'origin_address', 'destination_address',
            'departure_time', 'available_seats', 'distance_km', 'rate'
        ]
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'rate': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': 'Enter rate per seat'
            }),
            'distance_km': forms.NumberInput(attrs={
                'step': '0.1',
                'class': 'form-control',
                'placeholder': 'Enter estimated distance in km'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seats_booked']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['seats_booked'].widget.attrs.update({'class': 'form-control', 'min': 1})