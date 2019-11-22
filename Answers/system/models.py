from django.db import models
import datetime
import uuid as UUID

class AnswerController(models.Manager):
    def get_files(self, answer_uuid):
        answer = Answer.objects.get(uuid=answer_uuid)
        files = super().get_queryset().filter(answer=answer)
        fl = []
        for f in files:
            fl.append(f.file_uuid)
        return fl
    def check_answers_qestion_belong(self, uuid_answers, uuid_question):
        for uuid in uuid_answers:
            if Answer.objects.get(uuid=uuid).question_uuid != uuid_question:
                return False
        return True

class Answer(models.Model):
    uuid = models.UUIDField(default=UUID.uuid4, unique=True)
    question_uuid = models.UUIDField(null=False, unique=False)
    text = models.TextField()
    user = models.CharField(max_length=30, unique=False)
    date = models.DateField(default=datetime.datetime.now)

    objects = models.Manager()
    controller = AnswerController()
    def to_dict(self):
        files = FilesForAnswer.objects.filter(answer=self.id)
        flist = []
        for f in files:
            flist.append(str(f.file_uuid))
        return {
            'uuid': str(self.uuid),
            'question': str(self.question_uuid),
            'text': self.text,
            'user': self.user,
            'files': flist,
        }
    def from_dict(self, data):
        try:
            self.text = data['text']
            self.user = data['user']
            self.question_uuid = data['question']
        except KeyError as exp:
            raise KeyError("json don't containing field " + str(exp))


class FilesForAnswer(models.Model):
    class Meta:
        unique_together = (('answer', 'file_uuid'),)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    file_uuid = models.UUIDField(null=False, editable=True)

    objects = models.Manager()
    controller = AnswerController()