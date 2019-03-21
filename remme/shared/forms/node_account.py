from wtforms import fields, validators

from .base import ProtoForm


class NodeAccountInternalTransferPayloadForm(ProtoForm):
    value = fields.IntegerField(validators=[
        validators.DataRequired(message='Could not transfer with zero amount.')
    ])


class NodeAccountGenesisForm(ProtoForm):
    value = fields.IntegerField()


class CloseMasternodePayloadForm(ProtoForm):
    pass

