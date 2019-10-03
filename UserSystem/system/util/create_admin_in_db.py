from UserSystem.system import models
import hashlib
models.Group(name = 'super-admin').save()
models.Permission(name = '*').save()
models.Service(name = '*').save()
models.ServiceObject(service = models.Service.objects.filter(name = '*')[0], object_type = '*').save()
models.GroupPermission(group = models.Group.objects.filter(name = 'super-admin')[0],
                       permission = models.Permission.objects.filter(name = '*')[0],
                       object = models.ServiceObject.objects.filter(object_type = '*'))
models.User(nick = 'super-admin', password = hashlib.sha256(b'123'),
            group = models.Group.objects.filter(name = 'super-admin'))