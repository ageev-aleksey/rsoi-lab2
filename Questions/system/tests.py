from django.test import TestCase
from django.test import Client
import json
from . import models
import uuid
# Create your tests here.




# Create your tests here.


class view_test(TestCase):
    maxDiff = None
    def setUp(self) -> None:
        self.question = models.Question(title = "Title", text="large text", user="king")
    def test_empty_list_question(self):
        c = Client()
        response = c.get("/api/v1/questions/?page=1")
        self.assertEquals(response.status_code, 203)
        self.assertEquals(json.loads(response.content), {"type": "error", "data": "result after apply this request does not containing data"})
    def test_add_and_read_questions_list(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
                                                "title": "Как делат тесты?",
                                                "text": "детальное описание вопроса",
                                                "user": "this user",
                                                "tags": ["python", "django", "РСОИ"]
                                            }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        uuid1 = json.loads(response.content)['uuid']
        response = c.post("/api/v1/questions/add/", json.dumps({
                                                "title": "еще один вопрос",
                                                "text": "очередне описание вопроса",
                                                "user": "this user",
                                                "tags": []
                                            }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        uuid2 = json.loads(response.content)['uuid']
        response = c.get("/api/v1/questions/?page=1")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {
                                                "type": "questions_brief_paginate",
                                                "page": 1,
                                                "pages": 1,
                                                "questions": [
                                                                {
                                                                    "uuid": uuid1,
                                                                    "title": "Как делат тесты?",
                                                                    "user": "this user",
                                                                    "tags": ["python", "django", "РСОИ"],

                                                                },
                                                                {
                                                                    "uuid": uuid2,
                                                                    "title": "еще один вопрос",
                                                                    "user": "this user",
                                                                    "tags": [],
                                                                }
                                                            ]
                                            })
    def test_delete_question(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
            "title": "еще один вопрос",
            "text": "очередне описание вопроса",
            "user": "andrey",
            "tags": ['tag']
        }), content_type='application/json')
        print(response.content)
        self.assertEquals(response.status_code, 201)
        uuid = json.loads(response.content)['uuid']
        response = c.delete(f"/api/v1/questions/{uuid}/")
        self.assertEquals(json.loads(response.content), {'type': 'ok'})
        response = c.get("/api/v1/questions/?page=1")
        self.assertEquals(json.loads(response.content), {"type": "error", "data": "result after apply this request does not containing data"})

    def test_error_questions_page(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
            "title": "еще один вопрос",
            "text": "очередне описание вопроса",
            "user": "this user",
            "tags": []
        }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        response = c.get("/api/v1/questions/?page=2")
        print(response.content)
        self.assertEquals(json.loads(response.content), {"type": "error", "data": "page number exceed existing number of pages"})


    def test_add_file(self):
        question = models.Question(title = "Title", text="large text", user="king")
        question.save()
        c = Client()
        fuuid = uuid.uuid4()
        response = c.post(f"/api/v1/questions/{str(question.uuid)}/files/{fuuid}/")
        self.assertEquals(response.status_code, 200)

    def test_is_exist(self):
        self.question.save()
        c = Client()
        response = c.get(f"/api/v1/questions/{str(self.question.uuid)}/exist/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {'type': "ok", "data": "Object exist"})

    def test_try_delete_not_exist_file(self):
        self.question.save()
        fuuid = uuid.uuid4()
        c = Client()
        response = c.delete(f"api/v1/files/{fuuid}/")
        self.assertEquals(response.status_code, 404)

    def test_try_delete_not_exist_file(self):
        self.question.save()
        file = models.FilesForQuestion(question=self.question)
        c = Client()
        response = c.delete(f"/api/v1/files/{str(file.file_uuid)}/")
        self.assertEquals(response.status_code, 404)

    def test_try_delete_file(self):
        self.question.save()
        file = models.FilesForQuestion(question=self.question)
        file.save()
        c = Client()
        response = c.delete(f"/api/v1/files/{str(file.file_uuid)}/")
        self.assertEquals(response.status_code, 200)

    def test_delete_and_return_files(self):
        self.question.save()
        file1 = models.FilesForQuestion(question=self.question)
        file1.save()
        file2 = models.FilesForQuestion(question=self.question)
        file2.save()
        c = Client()
        response = c.delete(f"/api/v1/questions/{self.question.uuid}/get_files/")
        self.assertEquals(response.status_code, 200)
        '''self.assertEquals(json.loads(response.content), {"type": "files_list",
                                                         "uuid": [str(file2.file_uuid), str(file1.file_uuid)]})'''

    def test_question_detail(self):
        c = Client()
        self.question.save()
        response = c.get(f"/api/v1/questions/{str(self.question.uuid)}/")
        self.assertEquals(response.status_code, 200)
        '''self.assertEquals(json.loads(response.content), { "uuid": str(self.question.uuid),
                 "date": str(self.question.date),
                 "title": self.question.title,
                "text": self.question.text,
                "user": self.question.user,
                "files": [],
                "tags": [],
                 })'''


