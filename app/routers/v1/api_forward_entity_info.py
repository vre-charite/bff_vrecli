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
from ...resources.error_handler import catch_internal
from ...resources.dependencies import jwt_required
from ...resources.helpers import *
from ...models.entity_info_models import CheckFileResponse
from logger import LoggerFactory
import httpx

router = APIRouter()


@cbv(router)
class APIEntityInfo:
    _API_TAG = 'Entity INFO'
    _API_NAMESPACE = "api_forward_entity_info"

    def __init__(self):
        self._logger = LoggerFactory(self._API_NAMESPACE).get_logger()

    @router.get("/project/{project_code}/file/exist", tags=[_API_TAG],
                response_model=CheckFileResponse,
                summary="Check source file")
    @catch_internal(_API_NAMESPACE)
    async def check_source_file(self, project_code, zone, file_relative_path,
                                current_identity: dict = Depends(jwt_required)):
        try:
            role = current_identity["role"]
        except (AttributeError, TypeError):
            return current_identity
        query = {
            "project_code": project_code,
            "zone": zone,
            "file_relative_path": file_relative_path
        }
        with httpx.Client() as client:
            fw_response = client.get(ConfigClass.FILEINFO_HOST + "/v1/project/{}/file/exist".format(project_code), params=query)
        return JSONResponse(content=fw_response.json(), status_code=fw_response.status_code)
