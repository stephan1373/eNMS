from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField
from eNMS.models.administration import Data


class Store(Data):
    __tablename__ = "store"
    __mapper_args__ = {
        "polymorphic_identity": "store",
        "inherit_condition": id == Data.id,
    }
    pretty_name = "Store"
    parent_type = "data"
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)
    data = relationship(
        "Data",
        back_populates="store",
        foreign_keys="Data.store_id",
        cascade="all, delete-orphan",
    )


class StoreForm(DataForm):
    form_type = HiddenField(default="store")
