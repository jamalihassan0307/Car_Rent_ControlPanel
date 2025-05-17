from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = (
        (1, 'User'),
        (2, 'Admin'),
        (3, 'Resource Manager'),
        (4, 'Entry Operator'),
    )
    
    role = models.IntegerField(choices=ROLE_CHOICES, default=1)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Car(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance'),
    )
    
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    image = models.ImageField(upload_to='car_images/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.brand} {self.model}"

class RentDetail(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    )
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='rentals')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_get = models.DateField()
    date_return = models.DateField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.car.brand} {self.car.model} ({self.status})"
        
    @property
    def duration(self):
        """Calculate the number of days between pickup and return dates."""
        delta = self.date_return - self.date_get
        return delta.days + 1  
        
    @property
    def total_cost(self):
        """Calculate the total cost of the rental."""
        return self.duration * self.car.rate

class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.subject} - {self.user.username}"
