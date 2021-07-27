import json
import requests
from ..config import ConfigClass
from ..resources. error_handler import customized_error_template, ECustomizedError
from ..models.base_models import APIResponse, EAPIResponseCode
from ..commons.data_providers.data_models import DataManifestModel, DataAttributeModel
from ..commons.data_providers.database import SessionLocal
from ..service_logger.logger_factory_service import SrvLoggerFactory

_logger = SrvLoggerFactory("Helpers").get_logger()


def get_zone(namespace):
    return {"greenroom": "Greenroom",
            "vrecore": "VRECore"}.get(namespace.lower(), 'greenroom')


def get_path_by_zone(namespace, project_code):
    return {"greenroom": f"/data/vre-storage/{project_code}/",
            "vrecore": f"/vre-data/{project_code}/"
            }.get(namespace.lower(), 'greenroom')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DBConnection(metaclass=Singleton):

    def __init__(self):
        self.session = SessionLocal()

    def get_db(self):
        db = self.session
        try:
            yield db
        finally:
            db.close()


def get_manifest_name_from_project_in_db(event):
    project_code = event.get('project_code')
    manifest_name = event.get('manifest_name', None)
    db_session = event.get('session')
    if manifest_name:
        m = db_session.query(DataManifestModel.name,
                             DataManifestModel.id)\
            .filter_by(project_code=project_code, name=manifest_name)\
            .first()
        if not m:
            return None
        else:
            manifest = {'name': m[0], 'id': m[1]}
            return manifest
    else:
        manifests = db_session.query(DataManifestModel.name,
                                     DataManifestModel.id)\
            .filter_by(project_code=project_code)\
            .all()
        manifest_in_project = []
        for m in manifests:
            manifest = {'name': m[0], 'id': m[1]}
            manifest_in_project.append(manifest)
        return manifest_in_project


def get_attributes_in_manifest_in_db(event):
    manifest = event.get('manifest')
    db_session = event.get('session')
    attr_list = []
    attributes = db_session.query(DataAttributeModel.name,
                                  DataAttributeModel.type,
                                  DataAttributeModel.optional,
                                  DataAttributeModel.value). \
        filter_by(manifest_id=manifest.get('id')). \
        order_by(DataAttributeModel.id.asc()).all()
    if not attributes:
        return None
    for attr in attributes:
        result = {"name": attr[0],
                  "type": attr[1],
                  "optional": attr[2],
                  "value": attr[3]}
        attr_list.append(result)
    return attr_list


def get_user_role(user_id, project_id):
    url = ConfigClass.NEO4J_SERVICE + "/relations"
    try:
        res = requests.get(
            url=url,
            params={"start_id": user_id,
                    "end_id": project_id})
        _res = json.loads(res.text)[0]
        return _res
    except Exception:
        return None


def query__node_has_relation_with_admin():
    url = ConfigClass.NEO4J_SERVICE + "nodes/Container/query"
    data = {'is_all': 'true'}
    try:
        res = requests.post(url=url, json=data)
        project = res.json()
        return project
    except Exception:
        return None


def query_node_has_relation_for_user(username):
    url = ConfigClass.NEO4J_SERVICE + "relations/query"
    data = {'start_params': {'name': username}}
    try:
        res = requests.post(url=url, json=data)
        res = res.json()
        project = []
        for i in res:
            project.append(i['end_node'])
        return project
    except Exception:
        return None


def query_file_in_project(project_code, filename, zone='Greenroom'):
    _logger.info("query_file_in_project".center(80, '-'))
    url = ConfigClass.NEO4J_SERVICE_v2 + "nodes/query"
    path = get_path_by_zone(zone, project_code) + filename
    data = {"query": {
        "name": filename.split('/')[-1],
        "full_path": path,
        "archived": False,
        "project_code": project_code,
        "labels": ["File", zone]}}
    _logger.info(f"Query url: {url}")
    try:
        _logger.info(f"Get file info payload: {data}")
        res = requests.post(url=url, json=data)
        _logger.info(f"Query file response: {res.text}")
        file_res = res.json()
        _logger.info(f"file response: {file_res}")
        if file_res.get('code') == 200 and file_res.get('result'):
            return file_res
        else:
            _logger.info("Get name as folder")
            _logger.info(filename.split('/'))
            if len(filename.split('/')) < 2:
                relative_path = ''
            else:
                relative_path = '/'.join(filename.split('/')[0: -1])
            _logger.info(f'relative_path: {relative_path}')
            folder = {"query": {
                "name": filename.split('/')[-1],
                "folder_relative_path": relative_path,
                "archived": False,
                "project_code": project_code,
                "labels": ["Folder", zone]}}
            _logger.info(f"Query folder payload: {folder}")
            _res = requests.post(url=url, json=folder)
            _logger.info(f"Query folder response: {_res.text}")
            _res = _res.json()
            if _res.get('code') == 200 and _res.get('result'):
                return _res
            else:
                return []
    except Exception as e:
        _logger.error(str(e))
        return []


def get_file_entity_id(project_code, file_name, zone='Greenroom'):
    res = query_file_in_project(project_code, file_name, zone)
    res = res.get('result')
    if not res:
        return None
    else:
        global_entity_id = res[0].get('global_entity_id')
        return global_entity_id


def get_file_by_id(file_id):
    post_data = {"global_entity_id": file_id}
    try:
        response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/File/query", json=post_data)
        if not response.json():
            return None
        return response.json()[0]
    except Exception:
        return None


def get_dataset_node(project_code):
    post_data = {"code": project_code}
    try:
        response = requests.post(ConfigClass.NEO4J_SERVICE + f"nodes/Container/query", json=post_data)
        if not response.json():
            return None
        return response.json()[0]
    except Exception:
        return None


def has_permission(event):
    user_role = event.get('user_role')
    username = event.get('username')
    project_code = event.get('project_code')
    _projects = get_user_projects(user_role, username)
    _projects = [p.get('code') for p in _projects]
    if project_code not in _projects:
        result = customized_error_template(ECustomizedError.PERMISSION_DENIED)
        code = EAPIResponseCode.forbidden
    else:
        result = 'permit'
        code = EAPIResponseCode.success
    return code, result


def get_user_projects(user_role, username):
    _logger.info("get_user_projects".center(80, '-'))
    projects_list = []
    if user_role == "admin":
        project_candidate = query__node_has_relation_with_admin()
    else:
        project_candidate = query_node_has_relation_for_user(username)
    _logger.info(f"Number of candidates: {len(project_candidate)}")
    for p in project_candidate:
        if 'Container' in p['labels']:
            res_projects = {'name': p.get('name'),
                            'code': p.get('code'),
                            'id': p.get('id'),
                            'geid': p.get('global_entity_id')}
            projects_list.append(res_projects)
        else:
            _logger.info(f'Non-candidate: {p}')
    _logger.info(f"Number of projects found: {len(projects_list)}")
    return projects_list


def attach_manifest_to_file(event):
    project_code = event.get('project_code')
    global_entity_id = event.get('global_entity_id')
    manifest_id = event.get('manifest_id')
    attributes = event.get('attributes')
    username = event.get('username')
    project_role = event.get('project_role')
    _logger.info("attach_manifest_to_file".center(80, '-'))
    url = ConfigClass.FILEINFO_HOST + "/v1/file/attributes/attach"
    payload = {"project_code": project_code,
               "manifest_id": manifest_id,
               "global_entity_id": [global_entity_id],
               "attributes": attributes,
               "inherit": True,
               "project_role": project_role,
               "username": username}
    _logger.info(f"POSTING: {url}")
    _logger.info(f"PAYLOAD: {payload}")
    response = requests.post(url=url, json=payload)
    _logger.info(f"RESPONSE: {response.text}")
    if not response.json():
        return None
    return response.json()


def validate_has_non_optional_attribute_field(input_attributes, compare_attr):
    if not compare_attr.get('optional') and not compare_attr.get('name') in input_attributes:
        return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES)


def validate_attribute_field_by_value(input_attributes, compare_attr):
    attr_name = compare_attr.get('name')
    value = input_attributes.get(attr_name)
    if value and compare_attr.get('type') == "text":
        if len(value) > 100:
            return customized_error_template(ECustomizedError.TEXT_TOO_LONG) % attr_name
    elif value and compare_attr.get('type') == 'multiple_choice':
        if value not in compare_attr.get('value').split(","):
            return customized_error_template(ECustomizedError.INVALID_CHOICE) % attr_name
    else:
        if not compare_attr.get('optional'):
            return customized_error_template(ECustomizedError.FIELD_REQUIRED) % attr_name


def validate_attribute_name(input_attributes, exist_attributes):
    valid_attributes = [attr.get('name') for attr in exist_attributes]
    for key, value in input_attributes.items():
        if key not in valid_attributes:
            return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % key


def has_valid_attributes(event):
    attributes = event.get('attributes')
    exist_attributes = get_attributes_in_manifest_in_db(event)
    _name_error = validate_attribute_name(attributes, exist_attributes)
    if _name_error:
        return _name_error
    for attr in exist_attributes:
        required_attr = attr.get('name')
        if not attr.get('optional') and required_attr not in attributes:
            return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES) % required_attr
        elif attr not in exist_attributes:
            return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % attr
        else:
            _optional_error = validate_has_non_optional_attribute_field(attributes, attr)
            if _optional_error:
                return _optional_error
            _value_error = validate_attribute_field_by_value(attributes, attr)
            if _value_error:
                return _value_error


def http_query_node_zone(folder_event):
    namespace = folder_event.get('namespace')
    project_code = folder_event.get('project_code')
    folder_name = folder_event.get('folder_name')
    display_path = folder_event.get('display_path')
    folder_relative_path = folder_event.get('folder_relative_path')
    zone_label = get_zone(namespace)
    payload = {
        "query": {
            "folder_relative_path": folder_relative_path,
            "display_path": display_path,
            "name": folder_name,
            "project_code": project_code,
            "labels": ['Folder', zone_label]}
    }
    node_query_url = ConfigClass.NEO4J_SERVICE_v2 + "nodes/query"
    response = requests.post(node_query_url, json=payload)
    return response


def get_parent_label(source):
    return {
        'folder': 'Folder',
        'container': 'Container'
    }.get(source.lower(), None)


def separate_rel_path(folder_path):
    folder_layers = folder_path.strip('/').split('/')
    if len(folder_layers) > 1:
        rel_path = '/'.join(folder_layers[:-1])
        folder_name = folder_layers[-1]
    else:
        rel_path = ''
        folder_name = folder_path
    return rel_path, folder_name


def verify_list_event(source_type, folder):
    if source_type == 'Folder' and not folder:
        code = EAPIResponseCode.bad_request
        error_msg = 'missing folder name'
    elif source_type == 'Container' and folder:
        code = EAPIResponseCode.bad_request
        error_msg = 'Query project does not require folder name'
    else:
        code = EAPIResponseCode.success
        error_msg = ''
    return code, error_msg


def check_folder_exist(zone, project_code, folder):
    folder_check_event = {
        'namespace': zone,
        'project_code': project_code,
        'display_path': folder,
        'folder_name': folder.split('/')[-1],
        'folder_relative_path': '/'.join(folder.split('/')[0:-1])
    }
    folder_response = http_query_node_zone(folder_check_event)
    res = folder_response.json().get('result')
    if folder_response.status_code != 200:
        error_msg = folder_response.json()["error_msg"]
        code = EAPIResponseCode.internal_error
    elif res:
        error_msg = ''
        code = EAPIResponseCode.success
    else:
        error_msg = 'Folder not exist'
        code = EAPIResponseCode.not_found
    return code, error_msg
