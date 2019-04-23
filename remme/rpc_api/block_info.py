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
import logging

from remme.clients.block_info import BlockInfoClient
from remme.rpc_api.utils import validate_params
from remme.shared.forms.identifier import BlockIdentifierForm
from remme.shared.forms.block_info import IntegerForm
from remme.shared.exceptions import (
    ClientException,
    CountInvalid,
    KeyNotFound,
)
from remme.shared.forms import (
    ProtoForm,
    ListInfoForm,
)

__all__ = (
    'get_block_number',
    'get_blocks',

    'list_blocks',
    'fetch_block',
)

logger = logging.getLogger(__name__)

block_info_client = BlockInfoClient()


@validate_params(ProtoForm)
async def get_block_number(request):
    try:
        block_config = await block_info_client.get_block_info_config()
        return block_config.latest_block + 1
    except KeyNotFound as e:
        return 0


@validate_params(IntegerForm)
async def get_blocks(request):
    start = request.params.get('start', 0)
    limit = request.params.get('limit', 0)

    try:
        return await block_info_client.get_blocks_info(start, limit)
    except KeyNotFound:
        raise KeyNotFound('Blocks not found.')


@validate_params(ListInfoForm)
async def list_blocks(request):
    ids = request.params.get('ids')
    start = request.params.get('start')
    limit = request.params.get('limit')
    head = request.params.get('head')
    reverse = request.params.get('reverse')

    try:
        return await block_info_client.list_blocks(ids, start, limit, head, reverse)
    except (KeyNotFound, ClientException):
        raise KeyNotFound('List of blocks not found.')
    except CountInvalid:
        raise CountInvalid('Invalid limit count.')


@validate_params(BlockIdentifierForm)
async def fetch_block(request):
    block_id = request.params['id']
    try:
        return await block_info_client.fetch_block(block_id)
    except KeyNotFound:
        raise KeyNotFound(f'Block with id `{block_id}` not found.')
