from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField, SelectField
from eNMS.models.administration import Data
from eNMS.variables import vs

class Store(Data):
    __tablename__ = "store"
    pretty_name = "Store"
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)
    data_type = db.Column(db.SmallString, default="store")
    data = relationship(
        "Data",
        back_populates="store",
        foreign_keys="Data.store_id",
    )
    __mapper_args__ = {
        "polymorphic_identity": "store",
        "inherit_condition": id == Data.id,
    }

    def post_update(self, migration_import=False):
        old_name = self.name
        super().post_update()
        if migration_import or old_name != self.name:
            for datum in self.data:
                datum.post_update()
        return self.get_properties()

class StoreForm(DataForm):
    template = "object"
    form_type = HiddenField(default="store")
    id = HiddenField()
    data_type = SelectField("Data Type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type.choices = sorted(vs.subtypes["data"].items(), key=lambda x: x[0] != "store")

    def validate(self, **_):
        valid_form = super().validate()
        current_store = db.fetch("store", id=self.id.data, allow_none=True)
        invalid_data_type_change = current_store and current_store.data and self.data_type.data != current_store.data_type
        if invalid_data_type_change:
            self.data_type.errors.append("The Data Type of a store can only be modified if the store is empty.")
        return valid_form and not invalid_data_type_change
