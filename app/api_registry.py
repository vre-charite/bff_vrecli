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

from fastapi import FastAPI
from .routers import api_root
from .routers.v1 import api_file, api_project, api_manifest, api_validation, \
                        api_lineage, api_forward_entity_info, api_dataset, \
                            api_hpc, api_kg


def api_registry(app: FastAPI):
    prefix = "/v1"
    app.include_router(api_root.router)
    app.include_router(api_project.router, prefix=prefix)
    app.include_router(api_manifest.router, prefix=prefix)
    app.include_router(api_validation.router, prefix=prefix)
    app.include_router(api_lineage.router, prefix=prefix)
    app.include_router(api_forward_entity_info.router, prefix=prefix)
    app.include_router(api_file.router, prefix=prefix)
    app.include_router(api_dataset.router, prefix=prefix)
    app.include_router(api_hpc.router, prefix=prefix)
    app.include_router(api_kg.router, prefix=prefix)
