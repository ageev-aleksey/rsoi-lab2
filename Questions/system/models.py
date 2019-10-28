from django.db import models
from uuid import uuid4

# Create your models here.
class Question(models.Model):
    uuid = models.UUIDField(default=uuid4, primary_key=True)
    title = models.CharField(max_length=50)
    brief = models.TextField()
    text = models.TextField()
    user_uuid = models.UUIDField(default=uuid4, unique=True,  editable=True)
    rating = models.IntegerField(default=0)

    def from_dict(self, d):
        self.title = d['title']
        self.brief = d['brief']
        self.text = d['text']
        self.user_uuid = d['user_uuids']
        return self.uuid
    def brief_to_dict(self):
        answers = Answer.objects.filter(uuid = self.uuid)
        isCorrect = False
        for answer in answers:
            if answer.isCorrect():
                isCorrect = True
                break
        return {"title": self.title,
                "brief": self.brief,
                "author": self.user_uuid,
                "answers": isCorrect}

    def detail_to_dict(self):
        answers = Answer.objects.filter(uuid = self.uuid)
        answers_list = []
        for el in answers:
            answer_dict = el.to_dict()
            afiles = FilesForAnswer.objects.filter(answer=self.uuid)
            file_list = []
            for f in afiles:
                file_list.append(f.file_uuid)
            answer_dict['files'] = file_list
            answers_list.append(answer_dict)

        return {"title": self.title,
                "text": self.text,
                "author": self.user_uuid,
                "answers": answers_list}

class Answer(models.Model):
    uuid = models.UUIDField(default=uuid4, primary_key= True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    user_uuid = models.UUIDField(default=uuid4, unique=True, editable=True)

    def to_dict(self):
        return {
            'text': self.text,
            'author': self.user_uuid,
        }

class FilesForQuestion(models.Model):
    class Meta:
        unique_together = (('question', 'file_uuid'),)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    file_uuid = models.UUIDField(default=uuid4, editable=True)


class FilesForAnswer(models.Model):
    class Meta:
        unique_together = (('answer', 'file_uuid'),)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    file_uuid = models.UUIDField(default=uuid4, editable=True)
