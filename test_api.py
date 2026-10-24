"""Offline tests: real Supabase SDK, mocked database HTTP, no real credentials."""
import json
import os
import unittest
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient
from supabase import create_client, ClientOptions
import main
from database import get_client


class StudentTests(unittest.TestCase):
    def setUp(self):
        self.responses = []
        self.requests = []
        def respond(request):
            self.requests.append(request)
            if not self.responses:
                raise AssertionError('Unexpected database request')
            status, body = self.responses.pop(0)
            return httpx.Response(status, json=body)
        self.http = httpx.Client(transport=httpx.MockTransport(respond))
        self.db = create_client('https://example.supabase.co','test-key',options=ClientOptions(
            httpx_client=self.http,auto_refresh_token=False,persist_session=False))
        main.app.dependency_overrides[get_client] = lambda: self.db
        self.client = TestClient(main.app)
        self.addCleanup(main.app.dependency_overrides.clear)
        self.addCleanup(self.http.close)
        self.addCleanup(self.client.close)
        self.data = {'name':'Asha','email':'asha@example.com','age':22,'course':'Python'}
        self.record = dict(self.data,id=7)

    def queue(self, body, status=200):
        self.responses.append((status,body))

    def test_create(self):
        self.queue([self.record],201)
        response=self.client.post('/students',json=dict(self.data,name=' Asha ',course=' Python '))
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json(),self.record)
        request=self.requests[-1]
        self.assertEqual(request.method,'POST')
        self.assertEqual(request.url.path,'/rest/v1/student')
        self.assertEqual(json.loads(request.content),self.data)

    def test_list_empty_and_populated(self):
        for records in [[],[self.record]]:
            self.queue(records)
            response=self.client.get('/students')
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json(),records)
        self.assertEqual(self.requests[-1].url.params['order'],'id.asc')

    def test_get_and_missing(self):
        self.queue([self.record])
        self.assertEqual(self.client.get('/students/7').json(),self.record)
        self.assertEqual(self.requests[-1].url.params['id'],'eq.7')
        self.queue([])
        response=self.client.get('/students/999')
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json(),{'detail':'Student 999 not found'})

    def test_update_and_repeat(self):
        updated=dict(self.data,course='FastAPI',age=23)
        for _ in range(2):
            self.queue([dict(updated,id=7)])
            response=self.client.put('/students/7',json=updated)
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json(),dict(updated,id=7))
            request=self.requests[-1]
            self.assertEqual(request.method,'PATCH')  # SDK database update; public route is PUT.
            self.assertEqual(request.url.params['id'],'eq.7')
            self.assertEqual(json.loads(request.content),updated)
            self.assertIn('return=representation',request.headers['prefer'])

    def test_update_missing_does_not_insert(self):
        self.queue([])
        response=self.client.put('/students/999',json=self.data)
        self.assertEqual(response.status_code,404)
        self.assertEqual(len(self.requests),1)
        self.assertEqual(self.requests[0].method,'PATCH')

    def test_delete_and_repeat_missing(self):
        self.queue([self.record])
        response=self.client.delete('/students/7')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json(),{'message':'Student deleted','student_id':7})
        self.assertEqual(self.requests[-1].method,'DELETE')
        self.assertEqual(self.requests[-1].url.params['id'],'eq.7')
        self.queue([])
        self.assertEqual(self.client.delete('/students/7').status_code,404)

    def test_invalid_fields(self):
        invalid=[{},dict(self.data,id=7)]
        for field in self.data:
            missing=dict(self.data);del missing[field];invalid.append(missing)
            invalid.append(dict(self.data,**{field:None}))
        for field,values in [('name',['','  ','ab','x'*51]),('email',['invalid','']),
                             ('age',[18,100,0,-1,22.5,'22',True]),('course',['',' ','x','x'*101])]:
            for value in values:invalid.append(dict(self.data,**{field:value}))
        for body in invalid:
            for method,path in [('POST','/students'),('PUT','/students/7')]:
                with self.subTest(method=method,body=body):
                    self.assertEqual(self.client.request(method,path,json=body).status_code,422)
        self.assertEqual(self.requests,[])

    def test_valid_boundaries(self):
        for name,age,course in [('Amy',19,'AI'),('x'*50,99,'y'*100)]:
            body=dict(self.data,name=name,age=age,course=course)
            self.queue([dict(body,id=7)])
            self.assertEqual(self.client.post('/students',json=body).status_code,201)

    def test_path_and_json_validation(self):
        for value in ['0','-1','abc','1.5']:
            for method in ['GET','PUT','DELETE']:
                args={'json':self.data} if method=='PUT' else {}
                self.assertEqual(self.client.request(method,f'/students/{value}',**args).status_code,422)
        for method,path in [('POST','/students'),('PUT','/students/7')]:
            self.assertEqual(self.client.request(method,path).status_code,422)
            self.assertEqual(self.client.request(method,path,content='{',headers={'Content-Type':'application/json'}).status_code,422)
        self.assertEqual(self.requests,[])

    def test_database_network_and_unexpected_failures(self):
        for code in ['PGRST205','42P01','42501']:
            self.queue({'code':code,'message':'private database detail','details':None,'hint':None},400)
            response=self.client.get('/students')
            self.assertEqual(response.status_code,503)
            self.assertNotIn('private database detail',response.text)
        for error,status in [(httpx.ConnectError('private'),503),(RuntimeError('private'),500)]:
            with patch.object(self.db,'table',side_effect=error):
                for method,path,body in [('GET','/students',None),('GET','/students/7',None),
                    ('POST','/students',self.data),('PUT','/students/7',self.data),('DELETE','/students/7',None)]:
                    response=self.client.request(method,path,**({'json':body} if body else {}))
                    self.assertEqual(response.status_code,status)
                    self.assertNotIn('private',response.text)

    def test_missing_configuration_and_swagger(self):
        main.app.dependency_overrides.clear()
        get_client.cache_clear()
        with patch.dict(os.environ,{'SUPABASE_URL':'','SUPABASE_KEY':''}):
            self.assertEqual(self.client.get('/students').status_code,503)
            self.assertEqual(self.client.get('/docs').status_code,200)
            paths=self.client.get('/openapi.json').json()['paths']
            self.assertEqual({p:set(m) for p,m in paths.items()},
                {'/students':{'get','post'},'/students/{student_id}':{'get','put','delete'}})
        get_client.cache_clear()


if __name__=='__main__':
    unittest.main()
