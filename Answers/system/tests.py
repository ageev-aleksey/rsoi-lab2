from django.test import TestCase, Client
import json
# Create your tests here.

class view_test(TestCase):
    maxDiff = None
    def test_add_get_answers(self):
        c = Client()
        response = c.post("/api/v1/answers/add/", json.dumps({
            "text": "Берешь и делаешь!",
            "author": "2c010530-bc3b-47de-bbd6-9bd4db726517",
            "files": ['0346039a-a667-44e1-a762-1a354156053d',
                      "35dae4ea-f684-498c-88f6-4bd382180bde"],
            "question": "c8842e36-d98a-43a8-9268-c804ae0ad7fc",
        }), content_type='application/json')
        self.assertEquals(response.status_code, 201)
        response = c.post("/api/v1/answers/add/", json.dumps({
                    "text": "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
                    "author": "11111",
                    "question": "2fcc80f1-f579-4268-b6c5-43c27797eb03",
                    "files": ["2fcc80f1-f579-4268-b6c5-43c27797eb03"]
                    }), content_type='application/json')
        print(response.content)
        self.assertEquals(response.status_code, 201)
        uuid = json.loads(response.content)["uuid"]
        response = c.get(f"/api/v1/answers/{uuid}/")
        print(response.content)
        self.assertEquals(response.status_code, 200)
        print(json.loads(response.content))
        self.assertEquals(json.loads(response.content),{
                                    "type": "answer",
                                    "answer": {
                                                "uuid": uuid,
                                                "text": "11111111111111111111111111111111111111111111111111111111111111111111111111111111",
                                                "author": "11111",
                                                "files": ["2fcc80f1-f579-4268-b6c5-43c27797eb03"],
                                                "question": "2fcc80f1-f579-4268-b6c5-43c27797eb03",
                                            }
                                    })
