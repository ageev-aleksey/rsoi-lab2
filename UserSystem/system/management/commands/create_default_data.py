from system import models
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        import this


user_group = models.Group(name = 'user')
user_group.save()
guest_group = models.Group(name = 'guest')
guest_group.save()

pread = models.Permission(name = 'read')
pread.save()
pcreate = models.Permission(name = 'create')
pcreate.save()
pedit = models.Permission(name = 'edit')
pedit.save()

service = models.Service(name = 'questions')
service.save()
question = models.ServiceObject(service = service, object_type = 'question')
question.save()
owner_question = models.ServiceObject(service = service, object_type = 'owner_question')
owner_question.save()
answer = models.ServiceObject(service = service, object_type = 'answer')
answer.save()
owner_answer = models.ServiceObject(service = service, object_type = 'owner_answer')
owner_answer.save()

models.GroupPermission(group = user_group, permission = pread, object = question).save()
models.GroupPermission(group = user_group, permission = pcreate, object = question).save()
models.GroupPermission(group = user_group, permission = pedit, object = owner_question).save()
models.GroupPermission(group = user_group, permission = pread, object = owner_question).save()
models.GroupPermission(group = user_group, permission = pread, object = answer).save()
models.GroupPermission(group = user_group, permission = pcreate, object = answer).save()
models.GroupPermission(group = user_group, permission = pread, object = owner_answer).save()
models.GroupPermission(group = user_group, permission = pedit, object = owner_answer).save()

models.GroupPermission(group = guest_group, permission = pread, object = question).save()
models.GroupPermission(group = guest_group, permission = pread, object = answer).save()

test_service = models.Service(name = 'Test')
test_service.save()
test_object = models.ServiceObject(service = test_service, object_type = "test_object")
test_object.save()