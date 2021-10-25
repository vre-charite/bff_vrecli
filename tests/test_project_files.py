import unittest
from fastapi.testclient import TestClient
from app.main import create_app    
from app.config import ConfigClass
from .prepare_test import SetupTest
from .logger import Logger
import requests
# import requests_mock
# from unittest import mock

app = create_app()


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == ConfigClass.DATA_UPLOAD_SERVICE_VRE + '/v1/files/jobs':
        return MockResponse({"key1": "value1"}, 200)
    elif args[0] == ConfigClass.DATA_UPLOAD_SERVICE_GREENROOM + '/v1/files/jobs':
        return MockResponse({"key2": "value2"}, 200)
    return requests.post(*args, **kwargs)


class TestFiles(unittest.TestCase):
    client = TestClient(app)
    log = Logger(name='test_lineage_operation.log')
    test = SetupTest(log)
    project = {}
    user = {}

    @classmethod
    def setUpClass(cls):
        cls.client.headers["Authorization"] = cls.test.auth()
        cls.client.headers["Session-ID"] = "gregtesting"
        cls.user = cls.test.get_user()
        cls.project = cls.test.create_project("testproject")
        cls.test.add_user_to_project(cls.user["id"], cls.project["id"], "admin")

    @classmethod
    def tearDownClass(cls):
        cls.test.delete_project(cls.project["id"])

    def test_01_post_files_greenroom_processed(self):
        project_code = self.project["code"]
        payload = {
            "operator": "jzhang10",
            "upload_message": "Greg Testing",
            "type": "processed",
            "zone": "greenroom",
            "filename": "fake.png",
            "job_type": "AS_FILE",
            "generate_id": "undefined",
            "current_folder_node": "",
            "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
        }
        response = self.client.post(f"/v1/project/{project_code}/files", json=payload)
        self.log.info(response.text)
        self.assertEqual(response.status_code, 500)

    def test_02_post_files_vrecore_processed(self):
        project_code = self.project["code"]
        payload = {
            "operator": "jzhang10",
            "upload_message": "Greg Testing",
            "type": "processed",
            "zone": "vrecore",
            "filename": "fake.png",
            "job_type": "AS_FILE",
            "generate_id": "undefined",
            "current_folder_node": "",
            "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
        }
        response = self.client.post(f"/v1/project/{project_code}/files", json=payload)
        print(response.text)
        self.assertEqual(response.status_code, 500)

    def test_03_post_files_greenroom_raw(self):
        project_code = self.project["code"]
        payload = {
            "operator": "jzhang10",
            "upload_message": "Greg Testing",
            "type": "raw",
            "zone": "greenroom",
            "filename": "fake.png",
            "job_type": "AS_FILE",
            "generate_id": "undefined",
            "current_folder_node": "",
            "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
        }
        response = self.client.post(f"/v1/project/{project_code}/files", json=payload)
        self.assertEqual(response.status_code, 500)

    def test_04_post_files_wrong_zone(self):
        project_code = self.project["code"]
        payload = {
            "operator": "jzhang10",
            "upload_message": "Greg Testing",
            "type": "raw",
            "zone": "wrong",
            "filename": "fake.png",
            "job_type": "AS_FILE",
            "generate_id": "undefined",
            "current_folder_node": "",
            "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
        }
        response = self.client.post(f"/v1/project/{project_code}/files", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_msg"], "Invalid Zone")

    def test_05_post_files_wrong_type(self):
        project_code = self.project["code"]
        payload = {
            "operator": "jzhang10",
            "upload_message": "Greg Testing",
            "type": "wrong",
            "zone": "vrecore",
            "filename": "fake.png",
            "job_type": "AS_FILE",
            "generate_id": "undefined",
            "current_folder_node": "",
            "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
        }
        response = self.client.post(f"/v1/project/{project_code}/files", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error_msg"], "Invalid Type")

    def test_06_post_files_permissions(self):
        self.test.remove_user_from_project(self.user["id"], self.project["id"])
        project_code = self.project["code"]
        payload = {
            "operator": "jzhang10",
            "upload_message": "Greg Testing",
            "type": "raw",
            "zone": "vrecore",
            "filename": "fake.png",
            "job_type": "AS_FILE",
            "generate_id": "undefined",
            "current_folder_node": "",
            "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
        }
        self.log.info(project_code)
        self.log.info(self.user['id'])
        response = self.client.post(f"/v1/project/{project_code}/files", json=payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["result"], "User not in the project")
        self.assertEqual(response.json()["error_msg"], "Permission Denied")


