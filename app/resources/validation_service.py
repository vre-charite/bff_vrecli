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

from ..resources. error_handler import customized_error_template, ECustomizedError
from ..models.error_model import InvalidEncryptionError
from .database_service import RDConnection
from .helpers import *
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
from logger import LoggerFactory


_logger = LoggerFactory("validation_service").get_logger()

def decryption(encrypted_message, secret):
    """
    decrypt byte that encrypted by encryption function
    encrypted_message: the string that need to decrypt to string
    secret: the string type secret key used to encrypt message
    return: string of the message
    """
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=base64.b64decode(secret),
            iterations=100000,
            backend=default_backend()
        )
        # use the key from current device information
        key = base64.urlsafe_b64encode(kdf.derive('SECRETKEYPASSWORD'.encode()))
        f = Fernet(key)
        decrypted = f.decrypt(base64.b64decode(encrypted_message))
        return decrypted.decode()
    except Exception as e:
        raise InvalidEncryptionError("Invalid encryption, could not decrypt message")

class ManifestValidator:

    def __init__(self):
        self.db = RDConnection()

    @staticmethod
    def validate_has_non_optional_attribute_field(input_attributes, compare_attr):
        if not compare_attr.get('optional') and not compare_attr.get('name') in input_attributes:
            return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES)

    @staticmethod
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

    @staticmethod
    def validate_attribute_name(input_attributes, exist_attributes):
        _logger.info("validate attribute name")
        valid_attributes = [attr.get('name') for attr in exist_attributes]
        for key, value in input_attributes.items():
            if key not in valid_attributes:
                return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % key

    def has_valid_attributes(self, event):
        _logger.info(f"received event: {event}")
        attributes = event.get('attributes')
        manifest = event.get('manifest')
        exist_manifest = self.db.get_attributes_in_manifest_in_db(manifest)
        _logger.info(f"existing manifest: {exist_manifest}")
        exist_attributes = exist_manifest[0].get('attributes')
        _name_error = self.validate_attribute_name(attributes, exist_attributes)
        _logger.info(f"validation name error: {_name_error}")
        if _name_error:
            return _name_error
        for attr in exist_attributes:
            required_attr = attr.get('name')
            if not attr.get('optional') and required_attr not in attributes:
                return customized_error_template(ECustomizedError.MISSING_REQUIRED_ATTRIBUTES) % required_attr
            elif attr not in exist_attributes:
                return customized_error_template(ECustomizedError.INVALID_ATTRIBUTE) % attr
            else:
                _optional_error = self.validate_has_non_optional_attribute_field(attributes, attr)
                if _optional_error:
                    return _optional_error
                _value_error = self.validate_attribute_field_by_value(attributes, attr)
                if _value_error:
                    return _value_error