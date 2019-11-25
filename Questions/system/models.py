from django.db import models
from uuid import uuid4, UUID
from django.core.exceptions import ValidationError
import datetime
# Create your models here.
class Question(models.Model):
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    title = models.CharField(max_length=100, unique=False)
    text = models.TextField()
    user = models.CharField(max_length=30, unique=False)
    date = models.DateTimeField(default=datetime.datetime.now)

    def from_dict(self, d):
        try:
            self.title = d['title']
            self.text = d['text']
            self.user = d['user']
        except KeyError as exp:
            raise KeyError("json don't containing field " + str(exp))

    def brief_to_dict(self):
        Tags = TagsForQuestions.objects.filter(question=self.uuid)
        tags_list = []
        for t in Tags:
            tags_list.append(t.tag.tag)
        return {"uuid": self.uuid,
                "title": self.title,
                "user": self.user,
                "tags": tags_list,
                }

    def detail_to_dict(self):
        files_list = []
        qfiles = FilesForQuestion.objects.filter(question=self.uuid)
        for f in qfiles:
            files_list.append(f.file_uuid)

        tags_list = []
        qtags = TagsForQuestions.objects.filter(question=self.uuid)
        for t in qtags:
            tags_list.append(t.tag.tag)

        return { "uuid": str(self.uuid),
                 "date": str(self.date),
                 "title": self.title,
                "text": self.text,
                "user": self.user,
                "files": files_list,
                "tags": tags_list,
                 }



class FilesForQuestion(models.Model):
    class Meta:
        unique_together = (('question', 'file_uuid'),)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    file_uuid = models.UUIDField(default=uuid4, editable=True)




class Tag(models.Model):
    tag = models.CharField(max_length=30, primary_key=True)

class TagsForQuestions(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)