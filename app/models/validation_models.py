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


class ManifestValidatePost(BaseModel):
    """
    Validate Manifest post model
    """
    manifest_json: dict = Field({}, example={
                "manifest_name": "Manifest1",
                "project_code": "sampleproject",
                "attributes": {"attr1": "a1", "attr2": "test cli upload"},
                "file_path": "/data/core-storage/sampleproject/raw/testf1"
            }
    )


class ManifestValidateResponse(APIResponse):
    """
    Validate Manifest Response class
    """
    result: dict = Field({}, example={
                    "code": 200,
                    "error_msg": "",
                    "result": "Valid"
                }
            )


class ValidateDICOMIDPOST(BaseModel):
    """Validate DICOM ID Post model"""
    dcm_id: str


class ValidateDICOMIDResponse(APIResponse):
    """
    Validate DICOM ID response class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": "VALID"
        }
    )

class EnvValidatePost(BaseModel):
    """
    Validate Environment post model
    """
    action: str
    environ: str
    zone: str


class EnvValidateResponse(APIResponse):
    """
    Validate Manifest Response class
    """
    result: dict = Field({}, example={
        "code":200,
        "error_msg":"",
        "result":"valid"
        }
    )
