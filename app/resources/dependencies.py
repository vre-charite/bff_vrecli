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

from .helpers import *
from fastapi import Request
import time
import json
import jwt as pyjwt
from ..config import ConfigClass
import httpx
from ..models.base_models import APIResponse, EAPIResponseCode

api_response = APIResponse()

def get_project_role(user_id, project_code):
    query_payload = {"code": project_code}
    project = get_node(query_payload, 'Container')
    if not project:
        error_msg = customized_error_template(
            ECustomizedError.PROJECT_NOT_FOUND)
        code = EAPIResponseCode.not_found
        return error_msg, code
    project_id = project.get("id")
    role_check_result = get_user_role(user_id, project_id)
    if role_check_result:
        role = role_check_result.get("r").get('type')
        code = EAPIResponseCode.success
        return role, code
    else:
        error_msg = customized_error_template(
            ECustomizedError.USER_NOT_IN_PROJECT)
        code = EAPIResponseCode.forbidden
        return error_msg, code


async def jwt_required(request: Request):
    token = request.headers.get('Authorization')
    if token:
        token = token.replace("Bearer ", "")
    else:
        api_response.code = EAPIResponseCode.unauthorized
        api_response.error_msg = "Token required"
        return api_response.json_response()
    payload = pyjwt.decode(token, verify=False)
    username: str = payload.get("preferred_username")
    exp = payload.get('exp')
    if time.time() - exp > 0:
        api_response.code = EAPIResponseCode.unauthorized
        api_response.error_msg = "Token expired"
        return api_response.json_response()
    # check if user is existed in neo4j
    url = ConfigClass.NEO4J_SERVICE + "/v1/neo4j/nodes/User/query"
    with httpx.Client() as client:
        res = client.post(
            url=url,
            json={"name": username}
        )
    if res.status_code != 200:
        api_response.code = EAPIResponseCode.forbidden
        api_response.error_msg = "Neo4j service: " + json.loads(res.text)
        return api_response.json_response()
    users = res.json()
    if not users:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = f"Neo4j service: User {username} does not exist."
        return api_response.json_response()
    user_id = users[0]['id']
    role = users[0]['role']
    if username is None:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = "User not found"
        return api_response.json_response()
    return {"code": 200, "user_id": user_id, "username": username, "role": role, "token": token}


def check_permission(event: dict):
    """
    event = {'user_id': user_id,
             'username': username,
             'role': role,
             'project_code': project_code,
             'zone': zone}
    """
    user_id = event.get('user_id')
    username = event.get('username')
    role = event.get('role')
    project_code = event.get('project_code')
    zone = event.get('zone')
    project_role, code = get_project_role(user_id, project_code)
    user_info = get_node({'name': username}, 'User')
    user_status = user_info.get('status')
    if user_status != 'active':
        permission = {'error_msg': customized_error_template(ECustomizedError.PERMISSION_DENIED),
                      'code': code,
                      'result': f"User status: {user_status}"}
    elif role == "admin" and code != EAPIResponseCode.not_found:
        project_role = 'admin'
        permission = {'project_role': project_role}
    elif project_role == 'User not in the project':
        permission = {'error_msg': customized_error_template(ECustomizedError.PERMISSION_DENIED),
                      'code': code,
                      'result': project_role}
        return permission
    elif code == EAPIResponseCode.not_found:
        permission = {'error_msg': customized_error_template(ECustomizedError.PROJECT_NOT_FOUND),
                      'code': code,
                      'result': {}}
        return permission
    else:
        permission = {'project_role': project_role}
    if project_role != 'admin' and zone.lower() == ConfigClass.GREEN_ZONE_LABEL.lower():
        permission['project_code'] = project_code
        permission['uploader'] = username
    elif project_role != 'contributor' and zone.lower() == ConfigClass.CORE_ZONE_LABEL.lower():
        permission['project_code'] = project_code
    elif project_role == 'admin':
        permission['project_code'] = project_code
    else:
        permission = {'error_msg': customized_error_template(ECustomizedError.PERMISSION_DENIED),
                      'code': EAPIResponseCode.forbidden,
                      'result': {}}
        return permission
    return permission


def void_check_file_in_zone(data, file, project_code):
    payload = {"type": data.type,
               "zone": data.zone,
               "file_relative_path": file.get('resumable_relative_path') + '/' +
                                     file.get('resumable_filename'),
               "project_code": project_code
               }
    try:
        with httpx.Client() as client:
            result = client.get(ConfigClass.FILEINFO_HOST + f'/v1/project/{project_code}/file/exist/', params=payload)
        result = result.json()
    except Exception as e:
        api_response.error_msg = f"EntityInfo service  error: {e}"
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
    if result['code'] in [404, 200]:
        api_response.error_msg = "debug finding file"
        api_response.code = EAPIResponseCode.bad_request
        api_response.result = result
        return api_response.json_response()
    else:
        api_response.error_msg = "File with that name already exists"
        api_response.code = EAPIResponseCode.conflict
        api_response.result = data
        return api_response.json_response()


def select_url_by_zone(zone):
    if zone == ConfigClass.CORE_ZONE_LABEL.lower():
        url = ConfigClass.DATA_UPLOAD_SERVICE_CORE + "/v1/files/jobs"
    else:
        url = ConfigClass.DATA_UPLOAD_SERVICE_GREENROOM + "/v1/files/jobs"
    return url


def validate_upload_event(zone, data_type=None):
    if zone not in [ConfigClass.CORE_ZONE_LABEL.lower(), ConfigClass.GREEN_ZONE_LABEL.lower()]:
        error_msg = "Invalid Zone"
        return error_msg
    if data_type and data_type not in ["raw", "processed"]:
        error_msg = "Invalid Type"
        return error_msg


def transfer_to_pre(data, project_code, session_id):
    try:
        payload = {
            "current_folder_node": data.current_folder_node,
            "project_code": project_code,
            "operator": data.operator,
            "upload_message": data.upload_message,
            "data": data.data,
            "job_type": data.job_type
        }
        headers = {
            "Session-ID": session_id
        }
        url = select_url_by_zone(data.zone)
        with httpx.Client() as client:
            result = client.post(url, headers=headers, json=payload)
        return result
    except Exception as e:
        api_response.error_msg = f"Upload service  error: {e}"
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
