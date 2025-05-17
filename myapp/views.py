from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.urls import reverse

from .models import User, UserProfile, Car, RentDetail, ContactMessage
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CarForm, BookingForm, ContactForm, UserForm

# Helper functions for permission checks
def is_admin(user):
    return user.is_authenticated and user.role == 2

def is_resource_manager(user):
    return user.is_authenticated and user.role == 3

def is_entry_operator(user):
    return user.is_authenticated and user.role == 4

def is_normal_user(user):
    return user.is_authenticated and user.role == 1

# Public Pages
def home(request):
    # Get featured cars (available ones)
    featured_cars = Car.objects.filter(status='available').order_by('-id')[:4]
    return render(request, 'myapp/home.html', {'featured_cars': featured_cars})

def about(request):
    return render(request, 'myapp/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # If user is authenticated, associate message with user
            if request.user.is_authenticated:
                message = form.save(commit=False)
                message.user = request.user
                message.save()
            else:
                # For anonymous users, we could either redirect to login or handle differently
                messages.info(request, "Please login to send a message")
                return redirect('login')
                
            messages.success(request, "Your message has been sent successfully!")
            return redirect('home')
    else:
        form = ContactForm()
    
    return render(request, 'myapp/contact.html', {'form': form})

def car_list(request):
    # Filter by brand or status if provided
    brand = request.GET.get('brand', None)
    status = request.GET.get('status', None)
    
    cars = Car.objects.all()
    
    if brand:
        cars = cars.filter(brand__icontains=brand)
    if status:
        cars = cars.filter(status=status)
    
    # Get distinct brands for filter dropdown
    brands = Car.objects.values_list('brand', flat=True).distinct()
    
    return render(request, 'myapp/car_list.html', {
        'cars': cars,
        'brands': brands,
    })

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 1  # Default role is normal user
            user.save()
            
            # Update profile
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.save()
            
            # Auto-login after registration
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            
            messages.success(request, "Registration successful! Welcome to Car Rental System.")
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'myapp/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Redirect based on role
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = UserLoginForm()
    
    return render(request, 'myapp/login.html', {'form': form})

# Dashboard Views
@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    # Common data for all roles
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(status='available').count()
    
    context.update({
        'total_cars': total_cars,
        'available_cars': available_cars,
    })
    
    # Normal user dashboard
    if is_normal_user(user):
        user_bookings = RentDetail.objects.filter(user=user).order_by('-date_created')
        pending_bookings = user_bookings.filter(status='pending').count()
        approved_bookings = user_bookings.filter(status='approved').count()
        
        context.update({
            'recent_bookings': user_bookings[:5],
            'pending_bookings': pending_bookings,
            'approved_bookings': approved_bookings,
        })
    
    # Admin dashboard
    elif is_admin(user):
        total_users = User.objects.count()
        total_bookings = RentDetail.objects.count()
        pending_approvals = RentDetail.objects.filter(status='pending').count()
        recent_messages = ContactMessage.objects.filter(is_read=False).order_by('-date_sent')[:5]
        
        context.update({
            'total_users': total_users,
            'total_bookings': total_bookings,
            'pending_approvals': pending_approvals,
            'recent_messages': recent_messages,
        })
    
    # Resource Manager dashboard
    elif is_resource_manager(user):
        total_users = User.objects.count()
        cars_by_status = Car.objects.values('status').annotate(count=Count('status'))
        
        context.update({
            'total_users': total_users,
            'cars_by_status': cars_by_status,
        })
    
    # Entry Operator dashboard
    elif is_entry_operator(user):
        recent_bookings = RentDetail.objects.all().order_by('-date_created')[:10]
        pending_approvals = RentDetail.objects.filter(status='pending').count()
        
        context.update({
            'recent_bookings': recent_bookings,
            'pending_approvals': pending_approvals,
        })
    
    return render(request, 'myapp/dashboard.html', context)

# Profile Management
@login_required
def profile(request):
    user = request.user
    return render(request, 'myapp/profile.html', {'user': user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'myapp/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# Car Management
@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'myapp/car_detail.html', {'car': car})

@login_required
def add_car(request):
    # Only admin and resource manager can add cars
    if not (is_admin(request.user) or is_resource_manager(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Car added successfully!")
            return redirect('car_list')
    else:
        form = CarForm()
    
    return render(request, 'myapp/add_car.html', {'form': form})

@login_required
def edit_car(request, car_id):
    # Only admin and resource manager can edit cars
    if not (is_admin(request.user) or is_resource_manager(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, "Car updated successfully!")
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarForm(instance=car)
    
    return render(request, 'myapp/edit_car.html', {'form': form, 'car': car})

@login_required
def delete_car(request, car_id):
    # Only admin and resource manager can delete cars
    if not (is_admin(request.user) or is_resource_manager(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        car.delete()
        messages.success(request, "Car deleted successfully!")
        return redirect('car_list')
    
    return render(request, 'myapp/delete_car.html', {'car': car})

# Booking Management
@login_required
def my_bookings(request):
    # For normal users - show their bookings
    bookings = RentDetail.objects.filter(user=request.user).order_by('-date_created')
    
    # Filter by status if provided
    status = request.GET.get('status', None)
    if status:
        bookings = bookings.filter(status=status)
    
    return render(request, 'myapp/my_bookings.html', {'bookings': bookings})

@login_required
def add_booking(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    # Check if car is available
    if car.status != 'available':
        messages.error(request, "Sorry, this car is not available for booking.")
        return redirect('car_detail', car_id=car.id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car
            booking.status = 'pending'
            booking.save()
            
            # Mark car as rented if admin or entry operator makes booking
            if is_admin(request.user) or is_entry_operator(request.user):
                booking.status = 'approved'
                booking.save()
                car.status = 'rented'
                car.save()
                messages.success(request, "Booking confirmed successfully!")
            else:
                messages.success(request, "Booking request submitted! Awaiting approval.")
            
            return redirect('my_bookings')
    else:
        form = BookingForm()
    
    return render(request, 'myapp/add_booking.html', {'form': form, 'car': car})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(RentDetail, id=booking_id)
    
    # Only allow cancellation of own bookings or by admin/entry operator
    if booking.user != request.user and not (is_admin(request.user) or is_entry_operator(request.user)):
        return HttpResponseForbidden("You don't have permission to cancel this booking.")
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        
        # If the booking was approved, make the car available again
        if booking.status == 'approved':
            car = booking.car
            car.status = 'available'
            car.save()
        
        messages.success(request, "Booking cancelled successfully!")
        
        if is_admin(request.user) or is_entry_operator(request.user):
            return redirect('manage_bookings')
        else:
            return redirect('my_bookings')
    
    return render(request, 'myapp/cancel_booking.html', {'booking': booking})

@login_required
def manage_bookings(request):
    # Only admin and entry operator can manage all bookings
    if not (is_admin(request.user) or is_entry_operator(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    bookings = RentDetail.objects.all().order_by('-date_created')
    
    # Filter by status if provided
    status = request.GET.get('status', None)
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by user if provided
    username = request.GET.get('username', None)
    if username:
        bookings = bookings.filter(user__username__icontains=username)
    
    return render(request, 'myapp/manage_bookings.html', {'bookings': bookings})

@login_required
def approve_booking(request, booking_id):
    # Only admin and entry operator can approve bookings
    if not (is_admin(request.user) or is_entry_operator(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    booking = get_object_or_404(RentDetail, id=booking_id)
    
    if booking.status != 'pending':
        messages.error(request, "This booking is not in pending status.")
        return redirect('manage_bookings')
    
    if request.method == 'POST':
        booking.status = 'approved'
        booking.save()
        
        # Update car status
        car = booking.car
        car.status = 'rented'
        car.save()
        
        messages.success(request, "Booking approved successfully!")
        return redirect('manage_bookings')
    
    return render(request, 'myapp/approve_booking.html', {'booking': booking})

@login_required
def return_car(request, booking_id):
    # Only admin and entry operator can process returns
    if not (is_admin(request.user) or is_entry_operator(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    booking = get_object_or_404(RentDetail, id=booking_id)
    
    if booking.status != 'approved':
        messages.error(request, "This booking is not in approved status.")
        return redirect('manage_bookings')
    
    if request.method == 'POST':
        booking.status = 'returned'
        booking.save()
        
        # Update car status
        car = booking.car
        car.status = 'available'
        car.save()
        
        messages.success(request, "Car return processed successfully!")
        return redirect('manage_bookings')
    
    return render(request, 'myapp/return_car.html', {'booking': booking})

# User Management
@login_required
def user_list(request):
    # Only admin and resource manager can view user list
    if not (is_admin(request.user) or is_resource_manager(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role if provided
    role = request.GET.get('role', None)
    if role and role.isdigit():
        users = users.filter(role=int(role))
    
    # Filter by username/email if provided
    search = request.GET.get('search', None)
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    return render(request, 'myapp/user_list.html', {'users': users})

@login_required
def add_user(request):
    # Only admin and resource manager can add users
    if not (is_admin(request.user) or is_resource_manager(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Set role from form data
            user.save()
            
            # Update profile
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.save()
            
            messages.success(request, "User added successfully!")
            return redirect('user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'myapp/add_user.html', {'form': form})

@login_required
def edit_user(request, user_id):
    # Only admin and resource manager can edit users
    if not (is_admin(request.user) or is_resource_manager(request.user)):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=user_to_edit)
        profile_form = UserProfileForm(request.POST, instance=user_to_edit.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "User updated successfully!")
            return redirect('user_list')
    else:
        user_form = UserForm(instance=user_to_edit)
        profile_form = UserProfileForm(instance=user_to_edit.profile)
    
    return render(request, 'myapp/edit_user.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_to_edit': user_to_edit
    })

# Contact Message Management
@login_required
def message_list(request):
    # Only admin can view messages
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    messages_list = ContactMessage.objects.all().order_by('-date_sent')
    
    # Filter by read status if provided
    is_read = request.GET.get('is_read', None)
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        messages_list = messages_list.filter(is_read=is_read_bool)
    
    return render(request, 'myapp/message_list.html', {'messages_list': messages_list})

@login_required
def message_detail(request, message_id):
    # Only admin can view message details
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    message = get_object_or_404(ContactMessage, id=message_id)
    
    # Mark as read when viewing
    if not message.is_read:
        message.is_read = True
        message.save()
    
    return render(request, 'myapp/message_detail.html', {'message': message})

@login_required
def mark_message_read(request, message_id):
    # Only admin can mark messages as read
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    
    messages.success(request, "Message marked as read!")
    return redirect('message_list')

@login_required
def mark_all_messages_read(request):
    # Only admin can mark all messages as read
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    # Update all unread messages
    ContactMessage.objects.filter(is_read=False).update(is_read=True)
    
    messages.success(request, "All messages marked as read!")
    return redirect('message_list')

@login_required
def delete_message(request, message_id):
    # Only admin can delete messages
    if not is_admin(request.user):
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    message = get_object_or_404(ContactMessage, id=message_id)
    message.delete()
    
    messages.success(request, "Message deleted successfully!")
    return redirect('message_list')
