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


class Error(Exception):
    pass

class InvalidEncryptionError(Error):
    def __init__(self, message="Invalid encryption"):
        super().__init__(message)

class HPCError(Error):
    def __init__(self, code, message="HPC error"):
        self.code = code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
