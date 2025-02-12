from sqlalchemy import ForeignKey, Integer

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField
from eNMS.models.administration import Data


class IPAddress(Data):
    __tablename__ = "ip_address"
    pretty_name = "IP Address"
    __mapper_args__ = {"polymorphic_identity": "ip_address"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)


class IPAdressForm(DataForm):
    form_type = HiddenField(default="ip_address")
