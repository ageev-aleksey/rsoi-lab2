from django.db import models
import datetime

# Create your models here.
class Answer(models.Model):
    uuid = models.UUIDField(primary_key= True)
    question_uuid = models.UUIDField(null = False, unique=False)
    text = models.TextField()
    author = models.CharField(max_length=50, unique=False)
    date = models.DateField(default=datetime.datetime.now)
    def to_dict(self):
        return {
            'uuid': self.uuid,
            'question': self.question_uuid,
            'text': self.text,
            'author': self.author,
        }
    def from_dict(self, data):
        try:
            self.text = data['text']
            self.author = data['user']
            self.question_uuid = data['question']
        except KeyError as exp:
            raise KeyError("json don't containing field " + str(exp))


class FilesForAnswer(models.Model):
    class Meta:
        unique_together = (('answer', 'file_uuid'),)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    file_uuid = models.UUIDField(null=False, editable=True)