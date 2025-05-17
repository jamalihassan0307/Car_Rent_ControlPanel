from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Car, RentDetail, ContactMessage


admin.site.site_header = 'Car Rental System Admin'
admin.site.site_title = 'Car Rental Admin Portal'
admin.site.index_title = 'Welcome to Car Rental Admin Portal'


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'profile_image')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'profile_image')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'status', 'rate')
    list_filter = ('brand', 'status')
    search_fields = ('brand', 'model', 'description')

class RentDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'car', 'status', 'date_get', 'date_return', 'date_created')
    list_filter = ('status', 'date_get', 'date_return')
    search_fields = ('user__username', 'car__brand', 'car__model')
    date_hierarchy = 'date_created'

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'date_sent', 'is_read')
    list_filter = ('is_read', 'date_sent')
    search_fields = ('subject', 'message', 'user__username')
    readonly_fields = ('date_sent',)
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    actions = ['mark_as_read']


admin.site.register(User, UserAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(RentDetail, RentDetailAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
