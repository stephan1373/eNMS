from sqlalchemy import ForeignKey, Integer
from wtforms.widgets import TextArea

from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField, PasswordField
from eNMS.models.administration import Data


class Secret(Data):
    __tablename__ = export_type = "secret"
    pretty_name = "Secret"
    __mapper_args__ = {"polymorphic_identity": "secret"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)
    secret_value = db.Column(db.LargeString)


class SecretForm(DataForm):
    form_type = HiddenField(default="secret")
    secret_value = PasswordField("Value", widget=TextArea(), render_kw={"rows": 6})
    properties = ["secret_value"]
