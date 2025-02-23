from sqlalchemy import Boolean, ForeignKey, Integer

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import BooleanField, HiddenField, InstanceField, SelectField, StringField
from eNMS.models.administration import Data


class Port(Data):
    __tablename__ = "port"
    pretty_name = "Port"
    __mapper_args__ = {"polymorphic_identity": "port"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)
    label = db.Column(db.SmallString)
    speed = db.Column(db.SmallString)
    connected = db.Column(Boolean, default=False)


class PortForm(DataForm):
    form_type = HiddenField(default="port")
    store = InstanceField("Store", model="store", constraints={"data_type": "port"})
    label = StringField()
    speed = SelectField(choices=("10BASE-T", "100BASE-T", "1000BASE-T", "10GBASE-T"))
    connected = BooleanField("Connected", default=False)
    properties = ["label", "speed", "connected"]
