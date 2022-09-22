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

from pydantic import Field, BaseModel
from .base_models import APIResponse


class KGImportPost(BaseModel):
    data: dict = Field({}, example={
                'dataset_code': [], 
                'data': {
                    'kg_cli_test1_1634922993.json': {
                        '@id': '1634922993', 
                        '@type': 'unit test', 
                        'key_value_pairs': {
                            'definition_file': True, 
                            'file_type': 'KG unit test', 
                            'existing_duplicate': False
                            }
                            }
                        }
                    }
    )


class KGResponseModel(APIResponse):
    """
    KG Resource Response Class
    """
    result: dict = Field({}, example={
        'code': 200, 
        'error_msg': '', 
        'result': {
            'processing': {}, 
            'ignored': {
                'kg_cli_test1_1634922993.json': {
                    '@id': '1634922993', 
                    '@type': 'unit test', 
                    'key_value_pairs': {
                        'definition_file': True, 
                        'file_type': 'KG unit test', 
                        'existing_duplicate': False
                        }, 
                    '@context': 'https://context.org', 
                    'feedback': 'Resource http://sample-url/kg/v1/resources/pilot/CORE_Datasets/_/1634922993 already exists in project pilot/CORE_Datasets'
                    }
                    }
                }
            }
    )
