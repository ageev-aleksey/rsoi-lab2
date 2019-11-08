from django.test import TestCase
from django.test import Client
import json
# Create your tests here.




# Create your tests here.


class view_test(TestCase):
    maxDiff = None
    def test_empty_list_question(self):
        c = Client()
        response = c.get("/api/v1/questions/1/")
        self.assertEquals(response.status_code, 203)
        self.assertEquals(json.loads(response.content), {"type": "error", "data": "result after apply this request does not containing data"})
    def test_add_and_read_questions_list(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
                                                "title": "Как делат тесты?",
                                                "text": "детальное описание вопроса",
                                                "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
                                                "tags": ["python", "django", "РСОИ"]
                                            }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        uuid1 = json.loads(response.content)['uuid']
        response = c.post("/api/v1/questions/add/", json.dumps({
                                                "title": "еще один вопрос",
                                                "text": "очередне описание вопроса",
                                                "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
                                                "tags": []
                                            }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        uuid2 = json.loads(response.content)['uuid']
        response = c.get("/api/v1/questions/1/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {
                                                "type": "questions_brief_paginate",
                                                "page": 1,
                                                "pages": 1,
                                                "questions": [
                                                                {
                                                                    "uuid": uuid1,
                                                                    "title": "Как делат тесты?",
                                                                    "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
                                                                    "tags": ["python", "django", "РСОИ"],
                                                                    "answers": 0,
                                                                },
                                                                {
                                                                    "uuid": uuid2,
                                                                    "title": "еще один вопрос",
                                                                    "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
                                                                    "tags": [],
                                                                    "answers": 0,
                                                                }
                                                            ]
                                            })
    def test_delete_question(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
            "title": "еще один вопрос",
            "text": "очередне описание вопроса",
            "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
            "tags": []
        }), content_type='application/json')
        uuid = json.loads(response.content)['uuid']
        response = c.delete(f"/api/v1/questions/{uuid}/")
        self.assertEquals(json.loads(response.content), {'type': 'ok'})
        response = c.get("/api/v1/questions/1/")
        self.assertEquals(json.loads(response.content), {"type": "error", "data": "result after apply this request does not containing data"})

    def test_get_question_detail(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
            "title": "Как делат тесты?",
            "text": "детальное описание вопроса",
            "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
            "tags": ["python", "django", "РСОИ"],
            "files": []
        }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        uuid = json.loads(response.content)["uuid"]
        response = c.get(f"/api/v1/questions/{uuid}/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {
            "uuid": uuid,
            "title": "Как делат тесты?",
            "text": "детальное описание вопроса",
            "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
            "tags": ["python", "django", "РСОИ"],
            "answers": [],
            "files": []
        })

    def test_add_get_answers(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
            "title": "Как делат тесты?",
            "text": "детальное описание вопроса",
            "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
            "tags": ["python", "django", "РСОИ"],
            "files": ["925e9ec7-1721-49f2-bd7e-043dab044f0e"]
        }), content_type='application/json')
        uuid = json.loads(response.content)['uuid']
        response = c.post(f"/api/v1/questions/{uuid}/answers/add/", json.dumps({
                "text": "Берешь и делаешь!",
                "user": "2c010530-bc3b-47de-bbd6-9bd4db726517",
                "files": ['0346039a-a667-44e1-a762-1a354156053d',
                          "35dae4ea-f684-498c-88f6-4bd382180bde"]
        }), content_type='application/json')
        print(response.content)
        self.assertEquals(response.status_code, 201)
        response = c.post(f"/api/v1/questions/{uuid}/answers/add/", json.dumps({
                "text": "Все просто. Зайди на следующий сайт, и ты там найдешь как делать. google.com",
                "user": "925e9ec7-1721-49f2-bd7e-043dab044f0e",
                "files": []
        }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        response = c.get(f"/api/v1/questions/{uuid}/")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content), {
            "uuid": uuid,
            "title": "Как делат тесты?",
            "text": "детальное описание вопроса",
            "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
            "tags": ["python", "django", "РСОИ"],
            "answers": [
                {
                    "text": "Берешь и делаешь!",
                    "user": "2c010530-bc3b-47de-bbd6-9bd4db726517",
                    "isCorrect": False,
                    "files": ['0346039a-a667-44e1-a762-1a354156053d', "0346039a-a667-44e1-a762-1a354156053d",
                                "35dae4ea-f684-498c-88f6-4bd382180bde"]
                },
                {
                    "text": "Все просто. Зайди на следующий сайт, и ты там найдешь как делать. google.com",
                    "user": "925e9ec7-1721-49f2-bd7e-043dab044f0e",
                    "isCorrect": False,
                    "files": []
                }
            ],
            "files": ["925e9ec7-1721-49f2-bd7e-043dab044f0e"]
        })

    def test_delete_answer_with_error_uuid_question(self):
        c = Client()
        response = c.post("/api/v1/questions/add/", json.dumps({
            "title": "Как делат тесты?",
            "text": "детальное описание вопроса",
            "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
            "tags": ["python", "django", "РСОИ"],
            "files": ["925e6ec7-1721-49f2-bd7e-043dab044f0e"]
        }), content_type='application/json')
        uuidq = json.loads(response.content)['uuid']
        response = c.post(f"/api/v1/questions/{uuidq}/answers/add", json.dumps({
            "text": "тут текст вопроса",
            "user": "94597947-78fc-4f33-a7f4-21c11e6630e6",
            "files": ["1fac3o6f-ba14-40bd-b2f3-6d45c9d54939"]
        }), content_type='application/json')
        print("++++++++++++++")
        print(response.content)
        print("++++++++++++++")
        uuida = json.loads(response.content)['uuid']
        response = c.delete(f"/api/v1/questions/{uuidq+'a'}/answers/{uuida}")
        self.assertEquals(json.loads(response), {"type": "ok"})

        def test_delete_answer(self):
            c = Client()
            response = c.post("/api/v1/questions/add/", json.dumps({
                "title": "Как делат тесты?",
                "text": "детальное описание вопроса",
                "user": "2c080530-bc3b-47de-bbd6-9bd4db726517",
                "tags": ["python", "django", "РСОИ"],
                "files": ["925e9ec7-1721-49f2-bd7e-043dab044f0e"]
            }), content_type='application/json')
            uuidq = json.loads(response.content)['uuid']
            response = c.post(f"/api/v1/questions/{uuidq}/answers/add", {
                "text": "тут текст вопроса",
                "user": "94597947-78fc-4f33-a7f4-21c11e6630e6",
                "files": ["1fac3e6f-ba14-40bd-b2f3-6d45c9d54939"]
            })
            uuida = json.loads(response.content)['uuid']
            response = c.delete(f"/api/v1/questions/{uuidq}/answers/{uuida}", json.dumps({
                "text": "тут текст вопроса",
                "user": "94597947-78fc-4f33-a7f4-21c11e6630e6",
                "files": ["1fac3e6f-ba14-40bd-b2f3-6d45c9d54939"]
            }))
            self.assertEquals(json.loads(response), {"type": "ok"})
#TODO добавить в ответ рэйтинг статьи.