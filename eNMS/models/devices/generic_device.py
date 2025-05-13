from sqlalchemy import ForeignKey, Integer

from eNMS.database import db
from eNMS.forms import DeviceForm
from eNMS.fields import HiddenField, StringField
from eNMS.models.inventory import Device


class GenricDevice(Device):
    __tablename__ = "generic_device"
    __mapper_args__ = {"polymorphic_identity": "generic_device"}
    pretty_name = "Generic Device"
    id = db.Column(Integer, ForeignKey("device.id"), primary_key=True)
    serial_number = db.Column(db.SmallString)


class GenericDeviceForm(DeviceForm):
    form_type = HiddenField(default="generic_device")
    serial_number = StringField("Serial Number")
    properties = ["serial_number"]
