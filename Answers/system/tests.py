from django.test import TestCase

# Create your tests here.

class view_test(TestCase):
    maxDiff = None
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
