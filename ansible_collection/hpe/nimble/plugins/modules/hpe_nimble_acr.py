#!/usr/bin/python

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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
author:
  - Alok Ranjan (@ranjanal)
description: On HPE Nimble Storage array - Create or delete access control record for volume.
module: hpe_nimble_acr
options:
  apply_to:
    required: False
    choices:
    - volume
    - snapshot
    - both
    - pe
    - vvol_volume
    - vvol_snapshot
    type: str
    default: both
    description:
    - Type of object this access control record applies to.
  chap_user:
    required: False
    type: str
    description:
    - Name for the CHAP user.
  initiator_group:
    required: False
    type: str
    description:
    - The Initiator group name.
  lun:
    required: False
    type: int
    description:
    - If this access control record applies to a regular volume, this attribute is the volume's LUN Logical Unit Number.
    - If the access protocol is iSCSI, the LUN will be 0. However, if the access protocol is fibre channel, the LUN will be in the range from 0 to 2047.
  pe_ids:
    required: False
    type: list
    description:
    - List of candidate protocol endpoints that may be used to access the Virtual volume. One of them will be selected for the access control record.
    - This field is required only when creating an access control record for a virtual volume.
  protocol_endpoint:
    required: False
    type: str
    description:
    - Name for the protocol endpoint this access control record applies to.
  snapshot:
    required: False
    type: str
    description:
    - Name of the snapshot this access control record applies to.
  state:
    required: True
    choices:
    - present
    - absent
    - create
    type: str
    description:
    - Choice for access control record operation.
  volume:
    required: False
    type: str
    description:
    - Name for the volume this access control record applies to.
extends_documentation_fragment: hpe_nimble
short_description: Manages a HPE Nimble Storage access control record.
version_added: 2.9
'''

EXAMPLES = r'''

# If state is "create", create access control record for given volume, fails if it exist.
# If state is "present", create access control record if not already present.
- name: Create access control record for volume
  hpe_nimble_acr:
    hostname: "{{ hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    volume: "{{ volume }}"
    initiator_group: "{{ initiator_group }}"
    state: "{{ state | default('present') }}" # fail if exist

# Delete the access control record for a given volume name
- name: Delete access control record for volume
  hpe_nimble_acr:
    hostname: "{{ hostname }}"
    username: "{{ username }}"
    password: "{{ password }}"
    volume: "{{ volume }}"
    state: "absent" # fail if volume does not exist

'''
RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from nimbleclient.v1 import client
except ImportError:
    client = None
import ansible_collections.hpe.nimble.plugins.module_utils.hpe_nimble as utils


def create_acr(
        client_obj,
        initiator_group,
        volume,
        state,
        **kwargs):

    if utils.is_null_or_empty(initiator_group):
        return (False, False, "Access control record creation failed. No initiator group provided.")
    if utils.is_null_or_empty(volume):
        return (False, False, "Access control record creation failed. No volume name provided.")

    try:
        # see if the igroup is already present
        ig_resp = client_obj.initiator_groups.get(id=None, name=initiator_group)
        if ig_resp is None:
            return (False, False, f"Initiator Group '{initiator_group}' is not present on array.")
        vol_resp = client_obj.volumes.get(id=None, name=volume)
        if vol_resp is None:
            return (False, False, f"Volume name '{volume}' is not present on array.")

        acr_resp = client_obj.access_control_records.get(id=None, vol_name=volume)
        if utils.is_null_or_empty(acr_resp) is False:
            changed_attrs_dict, params = utils.remove_unchanged_or_null_args(acr_resp, **kwargs)
        else:
            params = utils.remove_null_args(**kwargs)
        if acr_resp is None or acr_resp.attrs.get("initiator_group_id") != ig_resp.attrs.get("id"):
            acr_resp = client_obj.access_control_records.create(initiator_group_id=ig_resp.attrs.get("id"),
                                                                vol_id=vol_resp.attrs.get("id"),
                                                                **params)
            return (True, True, f"Successfully created access control record for volume '{volume}'.")
        else:
            # check the state. if it is set to present ,we pass else if it is 'create' then we will fail
            if state == "present":
                return (True, False, f"Access control record is already present for volume '{volume}'.")
        return (False, False, f"Access control record for volume '{volume}' cannot be created as it is already present.")
    except Exception as ex:
        return (False, False, f"Access control record creation failed | {ex}")


def delete_acr(
        client_obj,
        volume):

    if utils.is_null_or_empty(volume):
        return (False, False, "Access control record deletion failed. No volume name Provided.")

    try:
        vol_resp = client_obj.volumes.get(id=None, name=volume)
        if vol_resp is None:
            return (False, False, f"Volume name '{volume}' is not present on array.")

        acr_resp = client_obj.access_control_records.get(id=None, vol_name=volume)
        if acr_resp is not None:
            acr_resp = client_obj.access_control_records.delete(acr_resp.attrs.get("id"))
            return (True, True, f"Successfully deleted access control record for volume '{volume}'.")
        else:
            return (True, False, f"Access control record for volume '{volume}' Cannot be deleted as it is not present.")
    except Exception as ex:
        return (False, False, f"Access control record deletion failed | {ex}")


def main():

    fields = {
        "state": {
            "required": True,
            "choices": ['present', 'absent', 'create'],
            "type": "str"
        },
        "apply_to": {
            "required": False,
            "choices": ['volume', 'snapshot', 'both', 'pe', 'vvol_volume', 'vvol_snapshot'],
            "type": "str",
            "no_log": False,
            "default": "both"
        },
        "chap_user": {
            "required": False,
            "type": "str",
            "no_log": False
        },
        "lun": {
            "required": False,
            "type": "int",
            "no_log": False
        },
        "volume": {
            "required": False,
            "type": "str",
            "no_log": False
        },
        "pe_ids": {
            "required": False,
            "type": "list",
            "no_log": False
        },
        "protocol_endpoint": {
            "required": False,
            "type": "str",
            "no_log": False
        },
        "snapshot": {
            "required": False,
            "type": "str",
            "no_log": False
        },
        "initiator_group": {
            "required": False,
            "type": "str",
            "no_log": False
        }
    }
    default_fields = utils.basic_auth_arg_fields()
    fields.update(default_fields)
    module = AnsibleModule(argument_spec=fields)
    if client is None:
        module.fail_json(msg='the python nimble-sdk module is required.')

    hostname = module.params["hostname"]
    username = module.params["username"]
    password = module.params["password"]
    state = module.params["state"]
    apply_to = module.params["apply_to"]
    chap_user = module.params["chap_user"]
    lun = module.params["lun"]
    volume = module.params["volume"]
    pe_ids = module.params["pe_ids"]
    protocol_endpoint = module.params["protocol_endpoint"]
    snapshot = module.params["snapshot"]
    initiator_group = module.params["initiator_group"]

    if (username is None or password is None or hostname is None):
        module.fail_json(
            msg="Storage system IP or username or password is null.")

    client_obj = client.NimOSClient(
        hostname,
        username,
        password
    )

    # defaults
    return_status = changed = False
    msg = "No Task to run."

    # States
    if state == "create" or state == "present":
        return_status, changed, msg = create_acr(
            client_obj,
            initiator_group,
            volume,
            state,
            apply_to=apply_to,
            chap_user_id=utils.get_chap_user_id(client_obj, chap_user),
            lun=lun,
            pe_id=utils.get_pe_id(client_obj, protocol_endpoint),
            snap_id=utils.get_snapshot_id(client_obj, snapshot),
            pe_ids=pe_ids)

    elif state == "absent":
        return_status, changed, msg = delete_acr(client_obj, volume)

    if return_status:
        module.exit_json(return_status=return_status, changed=changed, msg=msg)
    else:
        module.fail_json(return_status=return_status, changed=changed, msg=msg)


if __name__ == '__main__':
    main()
