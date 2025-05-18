from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile, Car, RentDetail, ContactMessage

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)
    profile_image = forms.ImageField(required=False)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial=1)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'phone', 'profile_image', 'role', 'password1', 'password2']

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'profile_image']
        widgets = {
            'profile_image': forms.FileInput()
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'country', 'email_notifications', 'remember_devices']

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'image', 'status', 'rate', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'image': forms.FileInput()
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = RentDetail
        fields = ['date_get', 'date_return']
        widgets = {
            'date_get': forms.DateInput(attrs={'type': 'date'}),
            'date_return': forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        date_get = cleaned_data.get('date_get')
        date_return = cleaned_data.get('date_return')
        
        if date_get and date_return:
            if date_get > date_return:
                raise forms.ValidationError("Return date must be after pickup date.")
        
        return cleaned_data

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5})
        } 