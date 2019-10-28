from django.db import models
import uuid
import datetime

# Create your models here.
class Permission(models.Model):
    '''Права пользователей'''
    id = models.AutoField(primary_key=True)
    name = models.TextField()
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
    """class Meta:
        unique_together = (("group", "permission", "object"),)"""

class User(models.Model):
    '''Таблица пользователей'''
    login = models.CharField(max_length= 30, null=False, primary_key=True, unique=True)
    password = models.TextField(null=False)
    fname = models.CharField(max_length = 30, null=True)
    lname = models.CharField(max_length=30, null=True)
    patronymic = models.CharField(max_length=30, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    birthday = models.DateField(null=True)
    date_registration = models.DateField(auto_now_add=True)
    date_visit = models.DateField()
    uuid_avatar = models.UUIDField(default=uuid.uuid4, editable=True, unique=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def from_dict(self, data, in_group = 'user'):
        '''
        {
            'login': <login>, - required
            'pass': <password>, - required
            'fname': <first_name>,
            'lname': <last_name>,
            'patronimyc': <patronimyc>,
            'birth': '<day>.<month>.<year>',
            'avatar': <uuid avatar from file service>
        }
        '''
        self.date_registration = datetime.datetime.now()
        self.login = data['login']
        self.password = data['pass']
        if 'fname' in data:
            self.fname = data['fname']
        if 'lname' in data:
            self.lname = data['lname']
        if 'patronymic' in data:
            self.patronymic = data['patronymic']
        if ('birth' in data):
            date = data['birth'].split('.')
            self.birthday = datetime.date(int(date[2]), int(date[1]), int(date[0]))
        if 'avatar' in data:
            self.uuid_avatar = data['avatar']
        self.date_visit = datetime.datetime.now()
        self.group = Group.objects.filter(name=in_group)[0]
    def to_dict(self):
        return {'login': self.login, 'fname': self.fname, 'lname': self.lname, 'patronymic': self.patronymic,
                'group': self.group.name, 'birth': self.birthday, 'date_reg': self.date_registration.strftime("%Y-%m-%d %H:%M:%S") ,
                'date_visit': self.date_visit.strftime("%Y-%m-%d %H:%M:%S"), 'uuid_avatar': str(self.uuid_avatar),'uuid': str(self.uuid)}
    def check_permission(self,uuid_service, uuid_object, need_permission):
        #проверим права супер-администратора
        admin_service = Service.objects.filter(name = '*')
        if len(admin_service) == 1:
            admin_object = ServiceObject.objects.filter(service = admin_service, object_type = '*')
            perm = UserPermission.objects.filter(user = self.login)
            print(perm)
            if len(perm) > 0:
                return True
        #сначало проверяем личные права пользователя затем права по группе
        serv_db = Service.objects.get(uuid = uuid_service)
        obj_db = ServiceObject.objects.get(service = serv_db, uuid = uuid_object)
        res_perm = UserPermission.objects.filter(user = self, object =  obj_db, permission = need_permission)
        if len(res_perm) == 1:
            return True
        #Проверяем права по группе
        res_perm = GroupPermission.objects.filter(user=self, object=obj_db, permission=need_permission)
        if len(res_perm) == 1:
            return True
        else:
            return False
class UserPermission(models.Model):
    '''Таблица содержащая права отдельных пользователей'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    object = models.ForeignKey(ServiceObject, on_delete=models.CASCADE)
    """class Meta:
        unique_together = (("group", "permission", "object"),)"""

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField(unique= True, null=False)
    #user_agent = models.TextField()

    '''Перед каждым обращением к ресурсу, гейт получает uuid ресурса, а замтем проверяет права пользователя'''


