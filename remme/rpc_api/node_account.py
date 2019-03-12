# Copyright 2018 REMME
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------
import json
import logging

from google.protobuf.json_format import MessageToJson

from remme.clients.basic import BasicClient
from remme.protos.node_account_pb2 import NodeAccount
from remme.rpc_api.utils import validate_params
from remme.shared.forms import get_address_form

__all__ = (
    'get_node_account',
)

logger = logging.getLogger(__name__)


@validate_params(get_address_form('node_account_address'))
async def get_node_account(request):
    """
    Get node account.

    Returns:
        Node account data (balance, reputation, node_state) in json.
    """
    client = BasicClient()

    node_address = request.params['node_account_address']
    raw_account = await client.get_value(node_address)

    node_account = NodeAccount()
    node_account.ParseFromString(raw_account)

    data = MessageToJson(message=node_account, preserving_proto_field_name=True, including_default_value_fields=True)
    return json.loads(data)
