from sqlalchemy import ForeignKey, Integer

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField, InstanceField, SelectField, StringField
from eNMS.models.administration import Data


class VLAN(Data):
    __tablename__ = "vlan"
    pretty_name = "VLAN"
    __mapper_args__ = {"polymorphic_identity": "vlan"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)
    vlan_id = db.Column(db.TinyString)
    role = db.Column(db.SmallString)
    group = db.Column(db.SmallString)


class VLANForm(DataForm):
    form_type = HiddenField(default="vlan")
    store = InstanceField("Store", model="store", constraints={"data_type": "vlan"})
    vlan_id = db.Column(db.TinyString)
    role = db.Column(db.SmallString)
    group = db.Column(db.SmallString)
    properties = ["vlan_id", "role", "group"]
