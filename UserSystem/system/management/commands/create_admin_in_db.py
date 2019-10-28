from system import models
import hashlib
import datetime


from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        import this

models.Group(name = 'super-admin').save()
all_permissions  = models.Permission(name = '*')
all_permissions.save()
models.Service(name = '*').save()
all_objects = models.ServiceObject(service = models.Service.objects.filter(name = '*')[0], object_type = '*')
all_objects.save()
models.GroupPermission(group = models.Group.objects.filter(name = 'super-admin')[0],
                       permission = models.Permission.objects.filter(name = '*')[0],
                       object = models.ServiceObject.objects.filter(object_type = '*')[0])
admin = models.User(login = 'super-admin', password = hashlib.sha256(b'123').hexdigest(),
            group = models.Group.objects.filter(name = 'super-admin')[0], date_registration = datetime.date(2019, 10, 16),
            date_visit = datetime.date(2019, 10, 16))
admin.save()

models.UserPermission(user = admin, object = all_objects, permission = all_permissions ).save()