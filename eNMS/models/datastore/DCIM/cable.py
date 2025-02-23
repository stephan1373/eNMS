from sqlalchemy import Boolean, Float, ForeignKey, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import (
    BooleanField,
    FloatField,
    HiddenField,
    InstanceField,
    SelectField,
    StringField,
)
from eNMS.models.administration import Data


class Cable(Data):
    __tablename__ = "cable"
    pretty_name = "Cable"
    __mapper_args__ = {"polymorphic_identity": "cable"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)
    source_port_id = db.Column(Integer, ForeignKey("port.id"))
    source_port = relationship("Port", foreign_keys=[source_port_id])
    source_port_name = association_proxy("source_port", "name")
    destination_port_id = db.Column(Integer, ForeignKey("port.id"))
    destination_port = relationship(
        "Port", foreign_keys=[destination_port_id]
    )
    destination_port_name = association_proxy("destination_port", "name")
    label = db.Column(db.SmallString)
    color = db.Column(db.SmallString)
    length = db.Column(Float, default=0)


class CableForm(DataForm):
    form_type = HiddenField(default="cable")
    store = InstanceField("Store", model="store", constraints={"data_type": "cable"})
    source_port = InstanceField("Port", model="port")
    destination_port = InstanceField("Port", model="port")
    label = StringField()
    color = StringField()
    length = FloatField(default=0.0)
    properties = ["source_port"]
