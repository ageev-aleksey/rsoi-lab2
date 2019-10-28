from django.test import TestCase
from django.test import Client
import json


# Create your tests here.


class view_test(TestCase):
    maxDiff = None

    def setUp(self):
        import system.util.create_default_data
        import system.util.create_admin_in_db
        self.users_list = ({"type": "users_list", "users": [
            {
                "login": "super-admin",
                "fname": None,
                "lname": None,
                "patronymic": None,
                "group": "super-admin",
                "birth": None,
                "date_reg": "2019-10-16 00:00:00",
                "date_visit": "2019-10-16 00:00:00"
                #  "uuid_avatar": "66d8fabd-fdf7-48be-ab96-7101379af759",
                # "uuid": "4dcd8ae7-f7ad-448c-b50d-2797bd545d45"

            }
        ]})

    def test_users_list(self):
        c = Client()
        r = json.loads(c.get("/api/v1/users/").content)
        r['users'][0].pop("uuid_avatar")
        r['users'][0].pop("uuid")
        r = json.dumps(r).encode("utf8")
        print("\n====\n")
        print(r)
        print(json.dumps(self.users_list).encode('utf8'))
        print("\n====\n")
        self.assertEquals(r, json.dumps(self.users_list).encode('utf8'))

    def tets_registration_ne_user(self):
        c = Client()
        data = {
                "login": "NewUser",
                "pass": 5515,
                "fname": "Алексей",
                "lname": "Агеев",
                "patronymic": "Владимирович",
                "birth": "21.08.1997",
                "avatar": "47a666d1-f503-4c13-bd13-689f06dd83a5"
                }
        response = c.post('/api/v1/sigup/', data)
        self.users_list['users'].append(data)
        self.assertEquals(response.content, b'{"type": "ok", "data": "user add in db"}')




'''
  'login': <login>, - required
            'pass': <password>, - required
            'fname': <first_name>,
            'lname': <last_name>,
            'patronimyc': <patronimyc>,
            'birth': '<day>.<month>.<year>',
            'avatar': <uuid avatar from file service>'''
