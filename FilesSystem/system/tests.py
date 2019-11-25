from django.test import TestCase
from django.test import Client
from django.core.files import File
import json
from . import models
import uuid



class view_test(TestCase):
    def setUp(self) -> None:
        self.f = open('test.test', 'wb')
        self.f.write(b"test")
        self.f.close()
        self.f = File(open('test.test', 'rb'))
        self.cont = models.FileContainer(file=self.f, name="a")
    def tearDown(self) -> None:
        self.f.close()

    def test_file_info(self):
        self.cont.save()
        file_info = models.FileInfo(file=self.cont, file_name='test_name')
        file_info.save()
        c = Client()
        response = c.get(f"/api/v1/files/{str(file_info.uuid)}/info/")
        self.assertEquals(response.status_code, 200)
        ''' self.assertEquals(json.loads(response.content), {'data': str(file_info.date),
                                                         'uuid': str(file_info.uuid),
                                                         'file_name': 'test_name',
                                                         'file_size': 4})'''
    def test_all_fiels(self):
        self.cont.save()
        c = Client()
        response = c.get('/api/v1/files/all/')
        self.assertEquals(response.status_code, 200)
        '''self.assertEquals(json.loads(response.content),
                          {"type": "files_list",
                           "files": finfo_list,
                           "page": 1, "pages": 1})'''

    def test_delete(self):
        self.cont.save()
        file_info = models.FileInfo(file=self.cont, file_name='test_name')
        file_info.save()
        c = Client()
        resposnse = c.delete(f"/api/v1/files/{file_info.uuid}/")
        self.assertEquals(resposnse.status_code, 200)

    def test_get_file_info_list(self):
        self.cont.save()
        file_info = models.FileInfo(file=self.cont, file_name='test_name', uuid = uuid.uuid4())
        file_info.save()
        c = Client()
        print('-----')
        print(str(file_info.uuid))
        resposne = c.post("/api/v1/files/list/", data=json.dumps({'uuid': [str(file_info.uuid)]}),
                          content_type='application/json')
        print(resposne.content)
        self.assertEquals(resposne.status_code, 400)
