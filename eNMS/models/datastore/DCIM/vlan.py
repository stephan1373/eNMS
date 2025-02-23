from sqlalchemy import ForeignKey, Integer

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField, InstanceField, StringField
from eNMS.models.administration import Data


class Port(Data):
    __tablename__ = "port"
    pretty_name = "Port"
    __mapper_args__ = {"polymorphic_identity": "port"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)


class PortForm(DataForm):
    form_type = HiddenField(default="port")
    store = InstanceField("Store", model="store", constraints={"data_type": "port"})
    properties = ["port_id", "role", "group"]
