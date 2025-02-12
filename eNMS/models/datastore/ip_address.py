from sqlalchemy import ForeignKey, Integer

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField, SelectField, StringField
from eNMS.models.administration import Data


class IPAddress(Data):
    __tablename__ = "ip_address"
    pretty_name = "IP Address"
    __mapper_args__ = {"polymorphic_identity": "ip_address"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)
    address = db.Column(db.TinyString)
    role = db.Column(db.TinyString)
    vrf_instance = db.Column(db.SmallString)


class IPAdressForm(DataForm):
    form_type = HiddenField(default="ip_address")
    address = StringField()
    role = SelectField(
        "Role",
        choices=(
            ("loopback", "Loopback"),
            ("secondary", "Secondary"),
            ("anycast", "Anycast"),
        ),
    )
    vrf_instance = StringField()
