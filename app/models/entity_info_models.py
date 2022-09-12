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

from pydantic import BaseModel, Field
from .base_models import APIResponse


class CheckFileResponse(APIResponse):
    result: dict = Field({}, example={
        "id": 2077,
        "labels": [
            "File",
            "Greenroom"
            "Raw"
        ],
        "global_entity_id": "file_data-2a7ea1d8-7dea-11eb-8428-be498ca98c54-1614973025",
        "operator": "",
        "file_size": 1048576,
        "tags": [],
        "archived": "false",
        "path": "/data/core-storage/project/raw",
        "time_lastmodified": "2021-03-05T19:37:06",
        "uploader": "admin",
        "process_pipeline": "",
        "name": "Testdateiäöüßs4",
        "time_created": "2021-03-05T19:37:06",
        "guid": "f91b258d-2f1d-409a-9551-91af8057e70e",
        "full_path": "/data/core-storage/project/raw/Testdateiäöüßs4",
        "dcm_id": "undefined"
    }
    )
