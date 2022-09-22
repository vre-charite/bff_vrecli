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

class HPCAuthPost(BaseModel):
    """
    Auth HPC post model
    """
    token_issuer: str
    username: str
    password: str

class HPCAuthResponse(APIResponse):
    """
    HPC Auth Response Class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": 
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                }
        }
    )

class HPCJobSubmitPost(BaseModel):
    """
    Submit HPC Job post model
    """
    host: str
    username: str
    token: str
    job_info: dict


class HPCJobResponse(APIResponse):
    """
    HPC Job Response Class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": {
                "job_id":15178
                }
        }
    )

class HPCJobInfoGet(BaseModel):
    """
    Get HPC Job info model
    """
    job_id: str
    host: str
    username: str
    token: str


class HPCJobInfoResponse(APIResponse):
    """
    HPC Job Info Response Class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": {
                "job_id":"12345",
                "job_state":"COMPLETED",
                "standard_error":"",
                "standard_input":"",
                "standard_output":""
                }
        }
    )

class HPCNodesResponse(APIResponse):
    """
    HPC Nodes Response Class
    """
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "result": [
            {
                "hostname": {
                    "cores": 42,
                    "cpu": 200,
                    "free_memory": 100000,
                    "gpus": 8,
                    "threads": 6,
                    "state": "idle"

                }

            },
            {
                "hostname": {
                    "cores": 20,
                    "cpu": 100,
                    "free_memory": 200000,
                    "gpus": 4,
                    "threads": 2,
                    "state": "down"

                }

            }
        ]
    }
                         )

class HPCNodeInfoResponse(APIResponse):
    """
    HPC Node Info Response Class
    """
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "result": [
            {
                "hostname": {
                    "cores": 42,
                    "cpu": 200,
                    "free_memory": 100000,
                    "gpus": 8,
                    "threads": 6,
                    "state": "idle"

                }

            }
        ]
    }
                         )

class HPCPartitonsResponse(APIResponse):
    """
    HPC Partitions Response Class
    """
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "result": [
            {
                "partition_name": {
                    "nodes": ["s-sc-gpu01, s-sc-gpu03"],
                    "tres": "cpu=1500,mem=20000M,node=2,billing=3000"

                }

            },
            {
                "partition_name": {
                    "nodes": ["s-sc-gpu02"],
                    "tres": "cpu=2500,mem=10000M,node=1,billing=2000"

                }

            }
        ]
    }
                         )

class HPCPartitionInfoResponse(APIResponse):
    """
    HPC Partition Info Response Class
    """
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "result": [
            {
                "partition_name": {
                    "nodes": ["s-sc-gpu01, s-sc-gpu03"],
                    "tres": "cpu=1500,mem=20000M,node=2,billing=3000"

                }

            }
        ]
    }
                         )

