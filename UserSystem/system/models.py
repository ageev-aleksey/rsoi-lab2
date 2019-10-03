from django.db import models
import uuid

# Create your models here.
class Permission(models.Model):
    '''Права пользователей'''
    id = models.AutoField(primary_key=True)
    permission = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class Group(models.Model):
    '''Группы пользователей'''
    name = models.TextField(primary_key=True)

class Service(models.Model):
    '''Сервисы, которые зарегистрированы в системе авторизации'''
    name = models.TextField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class ServiceObject(models.Model):
    '''Объекты сервиса, к которому можно организовать контроль доступа'''
    service = models.ForeignKey(Service, primary_key=True, on_delete=models.CASCADE)
    object_type = models.CharField(max_length=50)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    class Meta:
        unique_together = (("service", "object_type"),)

class GroupPermission(models.Model):
    '''Таблица содержащая права каждой группы пользователей'''
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    object = models.ForeignKey(ServiceObject, on_delete=models.CASCADE)
    class Meta:
        unique_together = (("group", "permission", "object"),)

class User(models.Model):
    '''Таблица пользователей'''
    nick = models.CharField(max_length= 30, null=False, primary_key=True)
    password = models.TextField(null=False)
    fname = models.CharField(max_length = 30)
    lname = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    birthday = models.DateField()
    date_registration = models.DateField()
    data_visit = models.DateField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length = 50, unique=True, null=False)
    #user_agent = models.TextField()

    '''Перед каждым обращением к ресурсу, гейт получает uuid ресурса, а замтем проверяет права пользователя'''


