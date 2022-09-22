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

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.kg_models import KGImportPost, KGResponseModel
from logger import LoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import jwt_required
from ...config import ConfigClass
import httpx
from fastapi.security import HTTPBasicCredentials, HTTPBearer

router = APIRouter()
_API_TAG = 'V1 KG'
_API_NAMESPACE = "api_kg"


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)
    security = HTTPBearer()
    
    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.post("/kg/resources", tags=[_API_TAG],
                response_model=KGResponseModel,
                summary="Import kg_resources")
    @catch_internal(_API_NAMESPACE)
    async def kg_import(self, request_payload: KGImportPost, credentials: HTTPBasicCredentials = Depends(security)):
        '''
        Import kg_resource
        '''
        self._logger.info("API KG IMPORT".center(80, '-'))
        url = ConfigClass.KG_SERVICE + "/v1/resources"
        self._logger.info(f'Requesting url: {url}')
        payload = {
                "data": request_payload.data
            }
        token = credentials.credentials
        headers = {"Authorization": "Bearer " + token}
        self._logger.info(f'Request payload: {payload}')
        self._logger.info(f'Request headers: {headers}')
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers)
        self._logger.info(f'Response: {response.text}')
        content=response.json()
        self._logger.info(f'Response content: {content}')
        return content
