from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship
from wtforms.widgets import TextArea

from eNMS.database import db, vs
from eNMS.forms import DeviceForm
from eNMS.fields import (
    HiddenField,
    MultipleInstanceField,
    SelectField,
    StringField,
)
from eNMS.models.inventory import Device


class Network(Device):
    __tablename__ = class_type = "network"
    __mapper_args__ = {"polymorphic_identity": "network"}
    pretty_name = "Network"
    parent_type = "device"
    category = db.Column(db.SmallString)
    icon = db.Column(db.TinyString, default="network")
    id = db.Column(Integer, ForeignKey(Device.id), primary_key=True)
    path = db.Column(db.TinyString)
    labels = db.Column(db.Dict, info={"log_change": False})
    devices = relationship(
        "Device", secondary=db.device_network_table, back_populates="networks"
    )
    links = relationship(
        "Link", secondary=db.link_network_table, back_populates="networks"
    )
    logs = relationship("Changelog", back_populates="network")
    device_changelogs = relationship(
        "Changelog",
        secondary=db.changelog_network_table,
        back_populates="networks",
        info={"log_change": False},
    )

    def duplicate(self, clone=None):
        for property in ("labels", "devices", "links"):
            setattr(clone, property, getattr(self, property))
        for device in self.devices:
            device.positions[clone.name] = device.positions.get(self.name, (0, 0))
        db.session.commit()
        return clone

    def post_update(self):
        if len(self.networks) == 1:
            self.path = f"{self.networks[0].path}>{self.id}"
        else:
            self.path = str(self.id)
        return self.to_dict(include_relations=["networks", "devices"])

    def update(self, **kwargs):
        old_name = self.name
        super().update(**kwargs)
        if self.name == old_name:
            return
        for device in self.devices:
            if old_name not in device.positions:
                continue
            device.positions[self.name] = device.positions[old_name]


class NetworkForm(DeviceForm):
    form_type = HiddenField(default="network")
    category = SelectField("Category")
    networks = MultipleInstanceField("Networks", model="network")
    properties = ["category", "networks"]
