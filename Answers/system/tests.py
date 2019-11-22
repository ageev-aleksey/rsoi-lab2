from django.test import TestCase, Client
import json
from . import  models
import uuid
# Create your tests here.

class view_test(TestCase):
    maxDiff = None
    def setUp(self):
        self.answer = models.Answer(uuid=uuid.uuid4(), question_uuid=uuid.uuid4(), user="SuperUser",
                               text="Товарищи! постоянное информационно-пропагандистское обеспечение"
                                    " нашей деятельности позволяет выполнять важные "
                                    "задания по разработке модели развития.")
    def test_add_get_answers(self):
        c = Client()
        response = c.post("/api/v1/answers/add/", json.dumps({
            "text": "Берешь и делаешь!",
            "user": "2c010530-bc3b-47de-bbd6-9bd4db726517",
            "files": ['0346039a-a667-44e1-a762-1a354156053d',
                      "35dae4ea-f684-498c-88f6-4bd382180bde"],
            "question": "c8842e36-d98a-43a8-9268-c804ae0ad7fc",
        }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        response = c.post("/api/v1/answers/add/", json.dumps({
                    "text": "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
                    "user": "11111",
                    "question": "2fcc80f1-f579-4268-b6c5-43c27797eb03",
                    "files": ["2fcc80f1-f579-4268-b6c5-43c27797eb03"]
                    }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        uuid = json.loads(response.content)["uuid"]
        response = c.get(f"/api/v1/answers/{uuid}/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content),{
                                    "type": "answer",
                                    "answer": {
                                                "uuid": uuid,
                                                "text": "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
                                                "user": "11111",
                                                "files": ["2fcc80f1-f579-4268-b6c5-43c27797eb03"],
                                                "question": "2fcc80f1-f579-4268-b6c5-43c27797eb03",
                                            }
                                    })

    def test_get_answer(self):
        self.answer.save()
        c = Client()
        response = c.get(f"/api/v1/answers/{self.answer.uuid}/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {
            'type': "answer",
            "answer": self.answer.to_dict()
            })

    def test_add_answer(self):
        c = Client()
        response = c.post("/api/v1/answers/add/", data=json.dumps(self.answer.to_dict()),
                          content_type="application/json")
        self.assertEquals(response.status_code, 201)
        objects = models.Answer.objects.all()
        self.assertEquals(objects.count(), 1)
        a = objects[0]
        fcount = models.FilesForAnswer.objects.filter(answer=a).count()
        self.assertEquals(fcount, 0)
        self.assertEquals({"text": a.text,
                           "user": a.user,
                           "files": []},
                          {"text": self.answer.text,
                           "user": self.answer.user,
                           "files": []})
    def test_delete_answer(self):
        self.answer.save()
        c = Client()
        answ = models.Answer.objects.all()
        self.assertEquals(answ.count(), 1)
        c.delete(f"/api/v1/answers/{self.answer.uuid}/")
        answ = models.Answer.objects.all()
        self.assertEquals(answ.count(), 0)

    def test_answers_page(self):
        quuid = uuid.uuid4()
        self.answer.question_uuid = quuid
        self.answer.save()
        a2 = models.Answer(uuid=uuid.uuid4(), question_uuid=quuid , user="AnotherUser",
                               text="Что мне делать")
        a2.save()
        c = Client()
        response = c.get(f"/api/v1/answers/?page=1&question={str(quuid)}")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {
            "type": "answers_list_pagination",
            "page": 1,
            "pages": 1,
            "answers": [self.answer.to_dict(), a2.to_dict()]
        })

    def test_answers_page2(self):
        quuid = uuid.uuid4()
        answ = []
        describe = []
        for i in range(20):
            answ.append(models.Answer(uuid=uuid.uuid4(), question_uuid=quuid , user="AnotherUser",
                                      text="Что мне делать"))
            answ[-1].save()
            describe.append(answ[-1].to_dict())
        c = Client()
        response = c.get(f"/api/v1/answers/?page=1&question={str(quuid)}")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {
            "type": "answers_list_pagination",
            "page": 1,
            "pages": 7,
            "answers": describe[0:3]
        })
        response = c.get(f"/api/v1/answers/?page=2&question={str(quuid)}")
        self.assertEquals(json.loads(response.content), {
            "type": "answers_list_pagination",
            "page": 2,
            "pages": 7,
            "answers": describe[3:6]
        })
        response = c.get(f"/api/v1/answers/?page=7&question={str(quuid)}")
        self.assertEquals(json.loads(response.content), {
            "type": "answers_list_pagination",
            "page": 7,
            "pages": 7,
            "answers": describe[18:20]
        })
        response = c.get(f"/api/v1/answers/?page=8&question={str(quuid)}")
        self.assertEquals(json.loads(response.content), {"type": "error", "data": "this page for answer not exists"})

    def test_count_answers(self):
        self.answer.question_uuid = uuid.uuid4()
        self.answer.save()
        models.Answer(text="sdsdsdsd", user="User", question_uuid=self.answer.question_uuid).save()
        c = Client()
        response = c.get(f"/api/v1/answers/count/?question={str(self.answer.question_uuid)}")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content),
                          {"type": "ok",
                           "count": 2})

    def test_counts_answers(self):
        self.answer.question_uuid = uuid.uuid4()
        self.answer.save()
        models.Answer(text="sdsdsdsd", user="User", question_uuid=self.answer.question_uuid).save()
        c = Client()
        quuid = uuid.uuid4()
        models.Answer(text="sdsdsdsdsd", user="OtherUser", question_uuid=quuid).save()
        response = c.post("/api/v1/answers/counts/",
                          json.dumps({"questions": [str(self.answer.question_uuid), str(quuid)]}),
                          content_type="application/json")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content),{"type": "count_answers_list", "count": [2, 1]})

    def test_is_exist(self):
        c = Client()
        response = c.get(f"/api/v1/answers/{self.answer.uuid}/exist/")
        self.assertEquals(response.status_code, 404)
        self.answer.save()
        response = c.get(f"/api/v1/answers/{self.answer.uuid}/exist/")
        self.assertEquals(response.status_code, 200)

    def test_attach_file(self):
        self.answer.save()
        fuuid = uuid.uuid4()
        c = Client()
        response = c.post(f"/api/v1/answers/{str(self.answer.uuid)}/files/{str(fuuid)}/")
        self.assertEquals(response.status_code, 200)
        file = models.FilesForAnswer.objects.filter(file_uuid=fuuid)
        self.assertEquals(file.count(), 1)