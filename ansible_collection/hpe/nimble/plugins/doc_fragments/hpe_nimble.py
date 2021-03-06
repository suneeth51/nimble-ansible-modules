# Copyright 2020 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

# author alok ranjan (alok.ranjan2@hpe.com)

class ModuleDocFragment(object):

    # HPE Nimble doc fragment
    DOCUMENTATION = '''
options:
  hostname:
    description:
    - The storage system IP address.
    required: True
    type: str
  password:
    description:
    - The storage system password.
    required: True
    type: str
  username:
    description:
    - The storage system user name.
    required: True
    type: str
requirements:
  - Ansible 2.9 or later
  - Nimble OS 5.1.4 or later
  - HPE Nimble Storage SDK for Python 1.0.0 or later (nimble-sdk Python module)

notes:
  -  check_mode not supported
    '''
