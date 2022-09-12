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

test_dataset_api = "/v1/datasets"
dataset_code = "testdataset"
test_dataset_detailed_api = "/v1/dataset/testdataset"

@pytest.mark.asyncio
async def test_list_dataset_without_token(test_async_client):
    res = await test_async_client.get(test_dataset_api)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"

@pytest.mark.asyncio
async def test_list_dataset_should_successed(test_async_client_auth, mocker):
    mocker.patch('app.routers.v1.api_dataset.query_node_has_relation_for_user',\
         return_value=[{"end_node" :{"code": "testdataset"}}])
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_dataset_api, headers=header)
    print(f"RESPONSE: {res.json()}")
    res_json = res.json()
    assert res_json.get('code') == 200
    datasets = []
    for d in res_json.get('result'):
        datasets.append(d.get('code'))
    assert dataset_code in datasets

@pytest.mark.asyncio
async def test_list_empty_dataset(test_async_client_auth,mocker):
    mocker.patch('app.routers.v1.api_dataset.query_node_has_relation_for_user',\
         return_value=[])
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_dataset_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert res_json.get('result') == []

@pytest.mark.asyncio
async def test_get_dataset_detail_without_token(test_async_client):
    res = await test_async_client.get(test_dataset_detailed_api)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required" 

@pytest.mark.asyncio
async def test_get_dataset_detail_should_successed(test_async_client_auth, mocker):
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_dataset.get_node',\
        return_value = {
            "labels": ["Dataset"],
            "global_entity_id": "fake_geid",
            "creator": "testuser",
            "modality": [],
            "code": "test0111"
            }
        )
    mocker.patch('app.routers.v1.api_dataset.RDConnection.get_dataset_versions',\
        mock_get_dataset_versions)
    res = await test_async_client_auth.get(test_dataset_detailed_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 200
    result = res_json.get('result')
    _dataset_info = result.get('general_info')
    assert _dataset_info["creator"] == "testuser"
    _version_info = result.get('version_detail')
    assert _version_info[0]["dataset_code"] == dataset_code
    _version_no = result.get("version_no")
    assert _version_no == 1

@pytest.mark.asyncio
async def test_get_dataset_detail_no_access(test_async_client_auth, mocker):
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_dataset.get_node',\
        return_value = {
            "labels": ["Dataset"],
            "global_entity_id": "fake_geid",
            "creator": "fakeuser",
            "modality": [],
            "code": "test0111"
            }
        )
    res = await test_async_client_auth.get(test_dataset_detailed_api, headers=header)    
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg') == "Permission Denied"

@pytest.mark.asyncio
async def test_get_dataset_detail_not_exist(test_async_client_auth, mocker):
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_dataset.get_node',\
        return_value = {
            "labels": ["None"],
            "global_entity_id": "fake_geid",
            "creator": "testuser",
            "modality": [],
            "code": "test0111"
            }
        )
    res = await test_async_client_auth.get(test_dataset_detailed_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 404
    assert res_json.get('error_msg') == "Cannot found given dataset code"


def mock_get_dataset_versions(arg1, arg2):
    mock_dataset_version = [
        {
            "dataset_code": dataset_code
        }
    ]
    return mock_dataset_version

