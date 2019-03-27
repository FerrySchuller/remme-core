"""
Provide tests for obligatory payment
"""
import time

import pytest

from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import (
    Transaction,
    TransactionHeader,
)

from remme.protos.node_account_pb2 import (
    NodeAccount,
)
from remme.protos.obligatory_payment_pb2 import (
    ObligatoryPaymentPayload,
    ObligatoryPaymentMethod,
)
from remme.protos.transaction_pb2 import TransactionPayload
from remme.shared.utils import hash512
from remme.tp.node_account import NodeAccountHandler
from remme.tp.obligatory_payment import ObligatoryPaymentHandler
from testing.conftest import create_signer
from testing.utils.client import proto_error_msg

from .shared import (
    COMMITTEE_SIZE,
    OBLIGATORY_PAYMENT,
    BLOCK_WINNER_PUBLIC_KEY,
    BLOCK_WINNER_ADDRESS,
    BLOCK_WINNER_PRIVATE_KEY,
    COMMITTEE_ADDRESSES,
    INPUTS,
    OUTPUTS,
    TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS,
    create_context
)


def test_pay_obligatory_payment_from_operational():
    """
    Case: pay obligatory payment from operational balances.
    Expect: block winner takes all obligatory payment.
    """
    operational_balance = 10000
    frozen_balance = 10000
    unfrozen_balance = 10000

    obligatory_payment_payload = ObligatoryPaymentPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT
    transaction_payload.data = obligatory_payment_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BLOCK_WINNER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=BLOCK_WINNER_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BLOCK_WINNER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(operational_balance, frozen_balance, unfrozen_balance)

    ObligatoryPaymentHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=COMMITTEE_ADDRESSES)

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    node_account = state_as_dict.get(BLOCK_WINNER_ADDRESS, NodeAccount())
    obligatory_reward = (COMMITTEE_SIZE-1)*OBLIGATORY_PAYMENT
    assert node_account.reputation.unfrozen == unfrozen_balance + obligatory_reward

    for address in COMMITTEE_ADDRESSES:
        if address == BLOCK_WINNER_ADDRESS:
            continue
        node_account = state_as_dict.get(address, NodeAccount())
        assert node_account.balance == operational_balance - OBLIGATORY_PAYMENT


def test_pay_obligatory_payment_from_unfrozen():
    """
    Case: pay obligatory payment from unfrozen balances.
    Expect: block winner takes all obligatory payment.
    """
    operational_balance = 0
    frozen_balance = 10000
    unfrozen_balance = 10000

    obligatory_payment_payload = ObligatoryPaymentPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT
    transaction_payload.data = obligatory_payment_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BLOCK_WINNER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=BLOCK_WINNER_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BLOCK_WINNER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(operational_balance, frozen_balance, unfrozen_balance)

    ObligatoryPaymentHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=COMMITTEE_ADDRESSES)

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    node_account = state_as_dict.get(BLOCK_WINNER_ADDRESS, NodeAccount())
    obligatory_reward = (COMMITTEE_SIZE-1)*OBLIGATORY_PAYMENT
    assert node_account.reputation.unfrozen == unfrozen_balance + obligatory_reward

    for address in COMMITTEE_ADDRESSES:
        if address == BLOCK_WINNER_ADDRESS:
            continue
        node_account = state_as_dict.get(address, NodeAccount())
        assert node_account.reputation.unfrozen == unfrozen_balance - OBLIGATORY_PAYMENT


def test_pay_obligatory_payment_from_frozen():
    """
    Case: pay obligatory payment from frozen balances.
    Expect: block winner takes all obligatory payment.
    """
    operational_balance = 0
    frozen_balance = 10000
    unfrozen_balance = 0

    obligatory_payment_payload = ObligatoryPaymentPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT
    transaction_payload.data = obligatory_payment_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BLOCK_WINNER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=BLOCK_WINNER_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BLOCK_WINNER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(operational_balance, frozen_balance, unfrozen_balance)

    ObligatoryPaymentHandler().apply(transaction=transaction_request, context=mock_context)

    state_as_list = mock_context.get_state(addresses=COMMITTEE_ADDRESSES)

    state_as_dict = {}
    for entry in state_as_list:
        acc = NodeAccount()
        acc.ParseFromString(entry.data)
        state_as_dict[entry.address] = acc

    node_account = state_as_dict.get(BLOCK_WINNER_ADDRESS, NodeAccount())
    obligatory_reward = (COMMITTEE_SIZE-1)*OBLIGATORY_PAYMENT
    assert node_account.reputation.unfrozen == unfrozen_balance + obligatory_reward

    for address in COMMITTEE_ADDRESSES:
        if address == BLOCK_WINNER_ADDRESS:
            continue
        node_account = state_as_dict.get(address, NodeAccount())
        assert node_account.reputation.frozen == frozen_balance - OBLIGATORY_PAYMENT


def test_pay_obligatory_payment_no_funds():
    """
    Case: not enough balance for obligatory payment.
    Expect: exception with malformed committee message is raised.
    """
    operational_balance = 0
    frozen_balance = 0
    unfrozen_balance = 0

    obligatory_payment_payload = ObligatoryPaymentPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT
    transaction_payload.data = obligatory_payment_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BLOCK_WINNER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=BLOCK_WINNER_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BLOCK_WINNER_PRIVATE_KEY).sign(serialized_header),
    )

    mock_context = create_context(operational_balance, frozen_balance, unfrozen_balance)

    with pytest.raises(InvalidTransaction) as error:
        ObligatoryPaymentHandler().apply(transaction=transaction_request, context=mock_context)

    assert "Malformed committee. A node doesn't have enough tokens to pay obligatory payment." == str(error.value)


def test_pay_obligatory_payment_malformed_committee():
    """
    Case: not enough public keys in committee.
    Expect: exception with malformed committee message is raised.
    """
    operational_balance = 100000
    frozen_balance = 0
    unfrozen_balance = 0

    obligatory_payment_payload = ObligatoryPaymentPayload()

    transaction_payload = TransactionPayload()
    transaction_payload.method = ObligatoryPaymentMethod.PAY_OBLIGATORY_PAYMENT
    transaction_payload.data = obligatory_payment_payload.SerializeToString()

    serialized_transaction_payload = transaction_payload.SerializeToString()

    transaction_header = TransactionHeader(
        signer_public_key=BLOCK_WINNER_PUBLIC_KEY,
        family_name=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_name'),
        family_version=TRANSACTION_REQUEST_ACCOUNT_HANDLER_PARAMS.get('family_version'),
        inputs=INPUTS,
        outputs=OUTPUTS,
        dependencies=[],
        payload_sha512=hash512(data=serialized_transaction_payload),
        batcher_public_key=BLOCK_WINNER_PUBLIC_KEY,
        nonce=time.time().hex().encode(),
    )

    serialized_header = transaction_header.SerializeToString()

    transaction_request = TpProcessRequest(
        header=transaction_header,
        payload=serialized_transaction_payload,
        signature=create_signer(private_key=BLOCK_WINNER_PRIVATE_KEY).sign(serialized_header),
    )
    allowed_validators = '0'
    for i in range(0, COMMITTEE_SIZE-2):
        allowed_validators += ';' + str(i)

    mock_context = create_context(
        operational_balance,
        frozen_balance,
        unfrozen_balance,
        allowed_validators=allowed_validators
    )

    with pytest.raises(InvalidTransaction) as error:
        ObligatoryPaymentHandler().apply(transaction=transaction_request, context=mock_context)

    assert "Malformed committee." == str(error.value)
