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

from enum import Enum
from pydantic import BaseModel, Field
from .base_models import APIResponse


class LineageCreatePost(BaseModel):
    project_code: str
    input_geid: str
    output_geid: str
    pipeline_name: str
    description: str


class LineageCreateResponse(APIResponse):
    """
    Validate Manifest Response class
    """
    result: dict = Field({}, example={
        "message": "Succeed"
    }
    )
