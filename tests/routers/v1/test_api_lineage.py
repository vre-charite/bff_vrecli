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
from pytest_httpx import HTTPXMock

test_lineage_api = "/v1/lineage"


@pytest.mark.asyncio
async def test_create_lineage_should_return_200(test_async_client_auth, httpx_mock: HTTPXMock):
    payload = {
        "project_code": "test_project",
        "input_geid": "fake_input_geid",
        "output_geid": "fake_output_geid",
        "pipeline_name": "pipeline_name",
        "description": "Test lineage"
    }
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://provenance_service/v1/lineage',
        json={"mutatedEntities": {
            "UPDATE": [
                {
                    "typeName": "file_data",
                    "guid": "input_guid"
                },
                {
                    "typeName": "file_data",
                    "guid": "output_guid"
                }
            ],
            "CREATE": [
                {
                    "typeName": "Process",
                    "guid": "pipeline_guid"
                }
            ]
        },
        "guidAssignments": {
            "-18306307111308515": "pipeline_guid"
        }},
        status_code=200,
    )
    res = await test_async_client_auth.post(test_lineage_api, headers=header, json=payload)
    res_json = res.json()
    print(res_json.get('result'))
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_create_lineage_with_internal_error_should_return_500(test_async_client_auth, httpx_mock: HTTPXMock):
    payload = {
        "project_code": "test_project",
        "input_geid": "fake_input_geid",
        "output_geid": "fake_output_geid",
        "pipeline_name": "pipeline_name",
        "description": "Test lineage"
    }
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://provenance_service/v1/lineage',
        json={},
        status_code=500,
    )
    res = await test_async_client_auth.post(test_lineage_api, headers=header, json=payload)
    res_json = res.json()
    print(res_json.get('result'))
    assert res.status_code == 500

