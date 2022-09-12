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
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from ...models.lineage_models import *
from logger import LoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import jwt_required
from ...config import ConfigClass
import httpx

router = APIRouter()


@cbv(router)
class APILineage:
    _API_TAG = 'V1 Lineage'
    _API_NAMESPACE = "api_lineage"

    def __init__(self):
        self._logger = LoggerFactory(self._API_NAMESPACE).get_logger()

    @router.post("/lineage", tags=[_API_TAG],
                 response_model=LineageCreatePost,
                 summary="[PENDING] Create lineage for given geid")
    @catch_internal(_API_NAMESPACE)
    async def create_lineage(self, request_payload: LineageCreatePost,
                             current_identity: dict = Depends(jwt_required)):
        self._logger.info("API Lineage".center(80, '-'))
        proxy_payload = request_payload.__dict__
        url = ConfigClass.PROVENANCE_SERVICE + "/v1/lineage"
        self._logger.info(f"url: {url}")
        self._logger.info(f"payload: {proxy_payload}")
        with httpx.Client() as client:
            fw_response = client.post(url, json=proxy_payload, timeout=100, follow_redirects=True)
        return JSONResponse(content=fw_response.json(), status_code=fw_response.status_code)
