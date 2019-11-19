from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import datetime
import uuid as UUID
def create_file_path(instance, file_name):
    return "users_files/" + hashlib.md5(file_name.encode("utf-8")+instance.uuid).hexdigest()


# Create your models here.
class FileContainer (models.Model):
    name = models.CharField(max_length=32, primary_key=True)
    file = models.FileField(upload_to="users_files/")


def file_hash(file):
    md5_hash = hashlib.md5()
    for chunk in file.chunks():
        md5_hash.update(chunk)
    return md5_hash.hexdigest()

class FileInfo(models.Model):
    file_name = models.CharField(max_length=50)
    date = models.DateField(default=datetime.datetime.now)
    uuid = models.UUIDField(default=UUID.uuid4, unique=True, editable=True, primary_key=True)
    file = models.ForeignKey(FileContainer, unique=False, null=False, on_delete=models.CASCADE)

    def from_data(self, data, file):
        self.file_name = data['file_name']
        file.name = file_hash(file)
        try:
            new_file = FileContainer.objects.get(name=file.name)
        except ObjectDoesNotExist:
            new_file = FileContainer(name=file.name, file=file)
            new_file.save()
        self.file = new_file

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "file_name": self.file_name,
            "file_size": self.file.file.size,
            "date": self.date,
        }
