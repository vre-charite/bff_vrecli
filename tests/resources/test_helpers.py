# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

import pytest
import app.resources.helpers
from app.resources.helpers import *
from tests.helper import EAPIResponseCode
from requests.models import Response


def test_get_user_role_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/relations?start_id=1&end_id=1086',
        json=[{"node":"fake_node"}],
        status_code=200,
    )
    result = get_user_role(1, 1086)
    assert result["node"] == "fake_node"


def test_get_user_role_failed():
    result = get_user_role(1, 1086)
    assert result == None


def test_query__node_has_relation_with_admin_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{"node": "fake_node"}],
        status_code=200,
    )
    result = query__node_has_relation_with_admin()
    assert result[0]["node"] == "fake_node"


def test_query__node_has_relation_with_admin_failed(httpx_mock):
    result = query__node_has_relation_with_admin()
    assert result == []


def test_query_node_has_relation_for_user_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        json=[{"node": "fake_node"}],
        status_code=200,
    )
    result = query_node_has_relation_for_user("test_user", "Container")
    assert result[0]["node"] == "fake_node"


def test_query_node_has_relation_for_user_failed():
    result = query_node_has_relation_for_user("test_user", "Container")
    assert result == []


def test_get_node_by_geid_successed(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='http://neo4j_service/v1/neo4j/nodes/geid/fake_geid',
        json=[{"node": "fake_node"}],
        status_code=200,
    )
    result = get_node_by_geid("fake_geid")
    assert result[0]["node"] == "fake_node"


def test_get_node_by_geid_failed():
    result = get_node_by_geid("fake_geid")
    assert result == None


def test_batch_query_node_by_geid_successed(httpx_mock):
    geid_list = ["fake_geid"]
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={"result": [{"global_entity_id": "fake_geid"}]},
        status_code=200,
    )
    result_geid_list, query_node = batch_query_node_by_geid(geid_list)
    assert result_geid_list == geid_list
    assert query_node == {'fake_geid': {'global_entity_id': 'fake_geid'}}


def test_query_file_in_project_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={
            "code": 200,
            "result": {"global_entity_id": "fake_geid"}
            },
        status_code=200,
    )
    result = query_file_in_project("test_project", "testfolder/testfile")
    assert result['code'] == 200


def test_query_file_in_project_return_empty(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={
            "code": 200,
            "result": None
        },
        status_code=200,
    )
    result = query_file_in_project("test_project", "testfolder/testfile")
    assert result == []


def test_query_file_in_project_return_failed():
    result = query_file_in_project("test_project", "testfolder/testfile")
    assert result == []


def test_get_node_successed(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=[{
            "code": 200,
            "result": {}
        }],
        status_code=200,
    )
    result = get_node(123, "Container")
    assert result == {
        "code": 200,
        "result": {}
    }


def test_get_node_with_response_json_as_none(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Container/query',
        json=None,
        status_code=200,
    )
    result = get_node(123, "Container")
    assert result == None


def test_get_node_by_code_failed():
    result = get_node(123, "Container")
    assert result == None


def test_get_user_admin_projects_successed(mocker):
    mocker.patch.object(app.resources.helpers,
                        "query__node_has_relation_with_admin", mock_query__node_has_relation_with_admin)
    result = get_user_projects('admin', 'test_user')
    assert result[0]['name'] == 'test_user'
    assert result[0]['code'] == 123


def test_get_user_project_user_projects_successed(mocker):
    mocker.patch.object(app.resources.helpers,
                        "query_node_has_relation_for_user", mock_query_node_has_relation_for_user)
    result = get_user_projects('contributor', 'test_user')
    assert result[0]['name'] == 'test_user'
    assert result[0]['code'] == 123


def test_attach_manifest_to_file_successed(httpx_mock):
    event = {
        'project_code':'project_code',
        'global_entity_id': 'geid',
        'manifest_id': 'mani_id',
        'attributes': 'attr',
        'username': 'test_user',
        'project_role': 'admin',
    }
    httpx_mock.add_response(
        method='POST',
        url='http://fileinfo_service/v1/files/attributes/attach',
        json={"node": "fake_node"},
        status_code=200,
    )
    result = attach_manifest_to_file(event)
    assert result == {"node": "fake_node"}


def test_attach_manifest_to_file_failed(httpx_mock):
    event = {
        'project_code': 'project_code',
        'global_entity_id': 'geid',
        'manifest_id': 'mani_id',
        'attributes': 'attr',
        'username': 'test_user',
        'project_role': 'admin',
    }
    httpx_mock.add_response(
        method='POST',
        url='http://fileinfo_service/v1/files/attributes/attach',
        json={},
        status_code=400,
    )
    result = attach_manifest_to_file(event)
    assert result == None


def test_http_query_node_zone(httpx_mock):
    event = {
        'project_code': 'project_code',
        'namespace': 'gr',
        'folder_name': 'folder_name',
        'display_path': 'display_path',
        'folder_relative_path': 'folder_relative_path',
        'project_role': 'admin',
    }
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={"node": "fake_node"},
        status_code=200,
    )
    result = http_query_node_zone(event)
    assert result.json() == {"node": "fake_node"}


@pytest.mark.parametrize("test_source, expect_result", [("folder", "Folder"), ("container", "Container"), ("File", None)])
def test_get_parent_label(test_source, expect_result):
    result = get_parent_label(test_source)
    assert result == expect_result


def test_separate_rel_path_with_namefolder():
    rel_path, folder_name = separate_rel_path("test_user/folder")
    assert rel_path == "test_user"
    assert folder_name == "folder"


def test_separate_rel_path_without_namefolder():
    rel_path, folder_name = separate_rel_path("test_user")
    assert rel_path == ""
    assert folder_name == "test_user"


@pytest.mark.parametrize("test_source, test_folder, expect_result",\
                         [("Folder", None, 'missing folder name'), 
                          ("Container", "test_user", 'Query project does not require folder name'),
                          ("Container", None, '')])
def test_verify_list_event(test_source, test_folder, expect_result):
    code, error_msg = verify_list_event(test_source, test_folder)
    assert error_msg == expect_result


@pytest.mark.parametrize("test_zone, folder, expect_result",
                         [("gr", "test_user/folder", ''),
                          ("zone", "test_user/folder", 'mock_error'),
                          ("cr", "test_user/not_exist_folder", 'Folder not exist')])
def test_check_folder_exist(mocker, test_zone, folder, expect_result):
    mocker.patch.object(app.resources.helpers,
                        "http_query_node_zone", mock_http_query_node_zone)
    code, error_msg = check_folder_exist(test_zone, "test_project", folder)
    assert error_msg == expect_result


def mock_http_query_node_zone(arg1):
    mock_response = Response()
    if arg1['namespace'] == 'gr':
        mock_response.status_code = 200
        mock_response._content = b'{"result": "fake_node"}'
    elif arg1['folder_name'] == "not_exist_folder":
        mock_response.status_code = 200
        mock_response._content = b'{"result": []}'
    else:
        mock_response.status_code = 500
        mock_response._content = b'{ "error_msg" : "mock_error" }'
    return mock_response


def mock_query__node_has_relation_with_admin():
    return [{
        'name': 'test_user',
        'code':123,
        'id':'fake_id',
        'global_entity_id': 'geid'
    }]


def mock_query_node_has_relation_for_user(arg1):
    return [{'r': {'status':'active'}, 'end_node': {'name': 'test_user',
                                                       'code': 123,
                                                       'id': 'fake_id',
                                                       'global_entity_id': 'geid'}}]
