from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q
from django.db import models
from datetime import datetime
from django.core.paginator import Paginator
from .models import Ride, Vehicle, UserProfile, Booking
from django.contrib import messages
from .forms import UserRegistrationForm, VehicleForm, RideForm, BookingForm, ProfileUpdateForm


# Create your views here.
def index(request):
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    date = request.GET.get('date')
    ev_only = request.GET.get('ev_only')

    #  Determine if a search was performed
    search_performed = any([origin, destination, date, ev_only])

    rides = Ride.objects.filter(departure_time__gte=timezone.now())

    if origin:
        rides = rides.filter(origin_address__icontains=origin)
    if destination:
        rides = rides.filter(destination_address__icontains=destination)
    if date:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
            rides = rides.filter(departure_time__date=selected_date)
        except ValueError:
            pass
    if ev_only:
        rides = rides.filter(vehicle__is_electric=True)

    rides = rides.order_by('departure_time')

    paginator = Paginator(rides, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #  Recently Viewed (from session)
    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed_rides = list(
        Ride.objects.filter(id__in=recently_viewed_ids)
        .order_by(models.Case(*[models.When(pk=pk, then=pos) for pos, pk in enumerate(recently_viewed_ids)]))
    )

    context = {
        'rides': page_obj,
        'total_results': paginator.count,
        'page_obj': page_obj,
        'search_performed': search_performed,  # Pass flag to template
        'recently_viewed_rides': recently_viewed_rides,
        'last_search': {
            'origin': request.COOKIES.get('last_origin', ''),
            'destination': request.COOKIES.get('last_destination', ''),
            'date': request.COOKIES.get('last_date', ''),
            'ev_only': request.COOKIES.get('last_ev_only', ''),
        }
    }

    response = render(request, 'ShareRouteApp/index.html', context)

    # Save cookies only if the user performed a search
    if search_performed:
        response.set_cookie('last_origin', origin or '')
        response.set_cookie('last_destination', destination or '')
        response.set_cookie('last_date', date or '')
        response.set_cookie('last_ev_only', '1' if ev_only else '')

    return response


def about(request):
    return render(request, 'ShareRouteApp/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Send email
        send_mail(
            subject=f"Contact Form: {name}",
            message=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )

    return render(request, "ShareRouteApp/contact.html")


# ---------------- LOGIN ----------------
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'ShareRouteApp/login.html')



# ---------------- REGISTER ----------------
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'ShareRouteApp/register.html', {'form': form})


# ---------------- LOGOUT ----------------
def user_logout(request):
    logout(request)
    return redirect('index')



@login_required
def profile(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            request.user.email = form.cleaned_data.get('email')
            request.user.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(
            instance=user_profile,
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email
            }
        )

    last_visit_time = request.session.get('last_visit_time', None)

    return render(request, 'ShareRouteApp/profile.html', {
        'form': form,
        'last_visit_time': last_visit_time
    })




def is_driver_check(user):
    """Check if logged-in user is a driver."""
    try:
        return user.userprofile.is_driver
    except UserProfile.DoesNotExist:
        return False


@login_required
@user_passes_test(is_driver_check, login_url='/')
def driver_dashboard(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    vehicles = Vehicle.objects.filter(driver=user_profile)
    rides = Ride.objects.filter(driver=user_profile)

    return render(request, 'ShareRouteApp/driver_dashboard.html', {
        'vehicles': vehicles,
        'rides': rides,
        'now': timezone.now()  # Pass current time
    })


@login_required
@user_passes_test(is_driver_check, login_url='/')
def add_vehicle(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = user_profile
            vehicle.save()
            return redirect('driver_dashboard')
    else:
        form = VehicleForm()

    return render(request, 'ShareRouteApp/vehicle_form.html', {'form': form})


@login_required
@user_passes_test(is_driver_check, login_url='/')
def post_ride(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = RideForm(request.POST)
        form.fields['vehicle'].queryset = Vehicle.objects.filter(driver=user_profile)

        if form.is_valid():
            ride = form.save(commit=False)
            ride.driver = user_profile

            # CO2 saved per seat
            ride.co2_saved = ride.distance_km * 0.120

            ride.save()
            return redirect('driver_dashboard')
    else:
        form = RideForm()
        form.fields['vehicle'].queryset = Vehicle.objects.filter(driver=user_profile)

    return render(request, 'ShareRouteApp/ride_form.html', {'form': form})



def ride_detail(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)

    # Store recently viewed rides in session
    recently_viewed = request.session.get('recently_viewed', [])

    if ride_id in recently_viewed:
        recently_viewed.remove(ride_id)  # Avoid duplicates

    recently_viewed.insert(0, ride_id)  # Add at the beginning (most recent first)

    if len(recently_viewed) > 4:  # Keep only last 4 rides
        recently_viewed = recently_viewed[:4]

    request.session['recently_viewed'] = recently_viewed

    return render(request, 'ShareRouteApp/ride_detail.html', {'ride': ride})

@login_required
def driver_rides(request, driver_id):
    driver_profile = get_object_or_404(UserProfile, id=driver_id)
    rides = Ride.objects.filter(driver=driver_profile).order_by('-departure_time')

    return render(request, 'ShareRouteApp/driver_rides.html', {
        'driver': driver_profile,
        'rides': rides,
        'now': timezone.now(),
    })


@login_required
@user_passes_test(is_driver_check, login_url='/')
def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, driver__user=request.user)

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('driver_dashboard')
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'ShareRouteApp/vehicle_form.html', {'form': form})


@login_required
@user_passes_test(is_driver_check, login_url='/')
def edit_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, driver__user=request.user)

    if ride.departure_time <= timezone.now():
        return redirect('driver_dashboard')

    if request.method == 'POST':
        form = RideForm(request.POST, instance=ride)
        form.fields['vehicle'].queryset = Vehicle.objects.filter(driver=ride.driver)
        if form.is_valid():
            form.save()
            return redirect('driver_dashboard')
    else:
        form = RideForm(instance=ride)
        form.fields['vehicle'].queryset = Vehicle.objects.filter(driver=ride.driver)

    return render(request, 'ShareRouteApp/ride_form.html', {'form': form})


@login_required
@user_passes_test(is_driver_check, login_url='/')
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, driver__user=request.user)

    if Ride.objects.filter(vehicle=vehicle, departure_time__lte=timezone.now()).exists():
        return redirect('driver_dashboard')

    vehicle.delete()
    return redirect('driver_dashboard')


@login_required
@user_passes_test(is_driver_check, login_url='/')
def delete_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, driver__user=request.user)

    if ride.departure_time <= timezone.now():
        return redirect('driver_dashboard')

    Booking.objects.filter(ride=ride).delete()
    ride.delete()
    return redirect('driver_dashboard')



@login_required
def book_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data['seats_booked']
            if seats <= ride.available_seats:
                # Create booking
                booking = form.save(commit=False)
                booking.user = request.user
                booking.ride = ride
                booking.save()

                # Update available seats
                ride.available_seats -= seats
                ride.save()

                return redirect('ride_detail', ride_id=ride.id)
    else:
        form = BookingForm()

    return render(request, 'ShareRouteApp/book_ride.html', {'ride': ride, 'form': form})



@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    ride = booking.ride

    # Prevent cancellation after departure
    if ride.departure_time <= timezone.now():
        messages.error(request, "You cannot cancel a booking after the ride has departed.")
        return redirect('booking_history')

    # Restore seats
    ride.available_seats += booking.seats_booked
    ride.save()

    # Delete booking
    booking.delete()

    return redirect('booking_history')



@login_required
def booking_history(request):
    # Fetch all bookings for the logged-in user
    bookings = Booking.objects.filter(user=request.user).select_related('ride', 'ride__vehicle')


    response = render(request, 'ShareRouteApp/booking_history.html', {
        'bookings': bookings,
        'now': timezone.now()
    })
    response.set_cookie('last_history_visit', timezone.now().strftime('%Y-%m-%d %H:%M:%S'))

    return response


@login_required
@user_passes_test(is_driver_check, login_url='/')
def driver_bookings(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, driver__user=request.user)
    bookings = ride.booking_set.select_related('user__userprofile')

    # Annotate total cost for each booking
    for booking in bookings:
        booking.total_cost = booking.seats_booked * ride.rate

    return render(request, 'ShareRouteApp/driver_bookings.html', {
        'ride': ride,
        'bookings': bookings
    })