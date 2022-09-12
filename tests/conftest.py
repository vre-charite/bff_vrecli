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

from pydantic import BaseModel
import app.routers.v1.api_kg
import pytest

from fastapi.testclient import TestClient
from async_asgi_testclient import TestClient as TestAsyncClient
from fastapi import Request
from app.config import ConfigClass
from app.resources.dependencies import jwt_required
from run import app
from app.routers.v1.api_kg import APIProject

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_async_client():
    client = TestAsyncClient(app)
    app.dependency_overrides[jwt_required] = jwt_required
    return client

@pytest.fixture
def test_async_client_auth():
    '''
        Create client with mock auth token
    '''
    client = TestAsyncClient(app)
    app.dependency_overrides[jwt_required] = overide_jwt_required
    return client


@pytest.fixture
def test_async_client_kg_auth():
    '''
        Create client with mock auth token for kg api only
    '''
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = overide_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


@pytest.fixture
def test_async_client_project_member_auth():
    '''
        Create client with mock auth token for kg api only
    '''
    client = TestAsyncClient(app)
    security = HTTPAuthorizationCredentials
    app.dependency_overrides[jwt_required] = overide_member_jwt_required
    app.dependency_overrides[APIProject.security] = security
    return client


async def overide_jwt_required(request: Request):
    return {
        "code": 200, 
        "user_id": 1, 
        "username": "testuser", 
        "role": "admin", 
        "token": "fake token"
    }


async def overide_member_jwt_required(request: Request):
    return {
        "code": 200,
        "user_id": 1,
        "username": "testuser",
        "role": "contributor",
        "token": "fake token"
    }

class HTTPAuthorizationCredentials(BaseModel):
    credentials: str = 'fake_token'



@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr(ConfigClass, 'NEO4J_SERVICE', 'http://neo4j_service')
    monkeypatch.setattr(ConfigClass, 'FILEINFO_HOST', 'http://fileinfo_service')
    monkeypatch.setattr(ConfigClass, 'KG_SERVICE', 'http://kg_service')
    monkeypatch.setattr(ConfigClass, 'PROVENANCE_SERVICE',
                        'http://provenance_service')
    monkeypatch.setattr(ConfigClass, 'GREEN_ZONE_LABEL', 'gr')
    monkeypatch.setattr(ConfigClass, 'CORE_ZONE_LABEL', 'cr')
    monkeypatch.setattr(ConfigClass, 'DATA_UPLOAD_SERVICE_CORE',
                        'http://data_upload_cr')
    monkeypatch.setattr(
        ConfigClass, 'DATA_UPLOAD_SERVICE_GREENROOM', 'http://data_upload_gr')
    monkeypatch.setattr(
        ConfigClass, 'HPC_SERVICE', 'http://service_hpc')
