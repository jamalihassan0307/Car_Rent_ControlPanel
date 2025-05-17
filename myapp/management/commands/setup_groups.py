from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from myapp.models import Car, User, RentDetail, ContactMessage

class Command(BaseCommand):
    help = 'Creates default groups and assigns permissions'

    def handle(self, *args, **options):
        
        admin_group, created = Group.objects.get_or_create(name='Admin')
        resource_manager_group, created = Group.objects.get_or_create(name='Resource Manager')
        entry_operator_group, created = Group.objects.get_or_create(name='Entry Operator')
        user_group, created = Group.objects.get_or_create(name='User')
        
        
        car_ct = ContentType.objects.get_for_model(Car)
        user_ct = ContentType.objects.get_for_model(User)
        rent_detail_ct = ContentType.objects.get_for_model(RentDetail)
        contact_message_ct = ContentType.objects.get_for_model(ContactMessage)
        
        
        admin_group.permissions.clear()
        resource_manager_group.permissions.clear()
        entry_operator_group.permissions.clear()
        user_group.permissions.clear()
        
        
        all_permissions = Permission.objects.filter(
            content_type__in=[car_ct, user_ct, rent_detail_ct, contact_message_ct]
        )
        admin_group.permissions.add(*all_permissions)
        
        
        
        car_perms = Permission.objects.filter(content_type=car_ct)
        user_perms = Permission.objects.filter(content_type=user_ct)
        resource_manager_group.permissions.add(*car_perms)
        resource_manager_group.permissions.add(*user_perms)
        
        
        
        entry_operator_group.permissions.add(
            *Permission.objects.filter(content_type=rent_detail_ct),
            Permission.objects.get(content_type=car_ct, codename='view_car')
        )
        
        
        
        user_group.permissions.add(
            Permission.objects.get(content_type=car_ct, codename='view_car'),
            Permission.objects.get(content_type=rent_detail_ct, codename='add_rentdetail'),
            Permission.objects.get(content_type=rent_detail_ct, codename='view_rentdetail'),
            Permission.objects.get(content_type=contact_message_ct, codename='add_contactmessage')
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created groups and assigned permissions')) 