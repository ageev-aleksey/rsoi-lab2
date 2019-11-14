from django.db import models
from uuid import uuid4, UUID
from django.core.exceptions import ValidationError
# Create your models here.
class Question(models.Model):
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    title = models.CharField(max_length=50, unique=False)
    text = models.TextField()
    user_uuid = models.UUIDField(default=uuid4, unique=False,  editable=True)
    rating = models.IntegerField(default=0)

    def from_dict(self, d):
        try:
            self.title = d['title']
            self.text = d['text']
            self.user_uuid = UUID(d['user'])
        except ValueError as exp:
            raise ValueError("incorrect user uuid")
        except KeyError as exp:
            raise KeyError("json don't containing field " + str(exp))

    def brief_to_dict(self):
        Tags = TagsForQuestions.objects.filter(question=self.uuid)
        tags_list = []
        for t in Tags:
            tags_list.append(t.tag.tag)
        return {"uuid": self.uuid,
                "title": self.title,
                "user": self.user_uuid,
                "tags": tags_list,
                }

    def detail_to_dict(self):
        answers = Answer.objects.filter(question=self.uuid)
        answers_list = []
        for el in answers:
            answer_dict = el.to_dict()
            afiles = FilesForAnswer.objects.filter(answer=answer_dict['uuid'])
            files_list = []
            for f in afiles:
                file_list.append(f.file_uuid)
                answer_dict['files'] = files_list
            answers_list.append(answer_dict)
        files_list = []
        qfiles = FilesForQuestion.objects.filter(question=self.uuid)
        for f in qfiles:
            files_list.append(f.file_uuid)

        tags_list = []
        qtags = TagsForQuestions.objects.filter(question=self.uuid)
        for t in qtags:
            tags_list.append(t.tag.tag)

        return { "uuid": self.uuid,
                 "title": self.title,
                "text": self.text,
                "user": self.user_uuid,
                "files": files_list,
                "tags": tags_list,
                "answers": answers_list}



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