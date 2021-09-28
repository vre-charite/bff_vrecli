from ..commons.data_providers.data_models import DataManifestModel, DataAttributeModel, DatasetVersionModel
from ..commons.data_providers.database import DBConnection
from ..service_logger.logger_factory_service import SrvLoggerFactory


class RDConnection:
    
    def __init__(self):
        self._logger = SrvLoggerFactory("Helpers").get_logger()
        db = DBConnection()
        self.db_session = db.session

    def get_manifest_name_from_project_in_db(self, event):
        project_code = event.get('project_code')
        manifest_name = event.get('manifest_name', None)
        if manifest_name:
            m = self.db_session.query(DataManifestModel.name,
                                DataManifestModel.id)\
                .filter_by(project_code=project_code, name=manifest_name)\
                .first()
            if not m:
                return None
            else:
                manifest = {'name': m[0], 'id': m[1]}
                return manifest
        else:
            manifests = self. db_session.query(DataManifestModel.name,
                                        DataManifestModel.id)\
                .filter_by(project_code=project_code)\
                .all()
            manifest_in_project = []
            for m in manifests:
                manifest = {'name': m[0], 'id': m[1]}
                manifest_in_project.append(manifest)
            return manifest_in_project


    def get_attributes_in_manifest_in_db(self, event):
        manifest = event.get('manifest')
        attr_list = []
        attributes = self.db_session.query(DataAttributeModel.name,
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


    def get_dataset_versions(self, event):
        self._logger.info("get_dataset_versions".center(80, '-'))
        self._logger.info(f'Query event: {event}')
        dataset_geid = event.get('dataset_geid')
        dataset_versions = []
        versions = self.db_session.query(DatasetVersionModel.dataset_code,
                                    DatasetVersionModel.dataset_geid,
                                    DatasetVersionModel.version,
                                    DatasetVersionModel.created_by,
                                    DatasetVersionModel.created_at,
                                    DatasetVersionModel.location,
                                    DatasetVersionModel.notes). \
            filter_by(dataset_geid=dataset_geid). \
            order_by(DatasetVersionModel.id.asc()).all()
        self._logger.info(f"Query result: {versions}")
        if not versions:
            return []
        for attr in versions:
            result = {"dataset_code": attr[0],
                    "dataset_geid": attr[1],
                    "version": attr[2],
                    "created_by": attr[3],
                    "created_at": str(attr[4]),
                    "location": attr[5],
                    "notes": attr[6]
                    }
            dataset_versions.append(result)
        return dataset_versions