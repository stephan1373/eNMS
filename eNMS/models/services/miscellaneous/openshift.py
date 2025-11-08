from requests.auth import HTTPBasicAuth
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship
from urllib.parse import urlparse, parse_qs

from eNMS.database import db
from eNMS.environment import env
from eNMS.fields import (
    HiddenField,
    InstanceField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
)
from eNMS.forms import ServiceForm
from eNMS.models.automation import Service


class OpenShiftService(Service):
    __tablename__ = "openshift_service"
    pretty_name = "OpenShift Authentication"
    id = db.Column(Integer, ForeignKey("service.id"), primary_key=True)
    auth_url = db.Column(db.LargeString)
    client_id = db.Column(db.SmallString, default="openshift-challenging-client")
    timeout = db.Column(Integer, default=15)
    credentials = db.Column(db.SmallString, default="custom")
    named_credential_id = db.Column(Integer, ForeignKey("credential.id"))
    named_credential = relationship("Credential")
    custom_username = db.Column(db.SmallString)
    custom_password = db.Column(db.SmallString)

    __mapper_args__ = {"polymorphic_identity": "openshift_service"}

    def job(self, run, device=None):
        local_variables = locals()
        auth_url = run.sub(run.auth_url, local_variables)
        log = f"Authenticating to OpenShift at {auth_url}"
        run.log("info", log, device, logger="security")        
        kwargs = {
            "params": {
                "client_id": run.sub(run.client_id, local_variables),
                "response_type": "token"
            },
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRF-Token": "1"
            },
            "timeout": run.timeout,
            "verify": True,
            "allow_redirects": False
        }
        if run.dry_run:
            return {"url": auth_url, "kwargs": kwargs}
        credentials = run.get_credentials(device, add_secret=False)
        if self.credentials != "custom" or credentials["username"]:
            kwargs["auth"] = HTTPBasicAuth(
                credentials["username"], credentials["password"]
            )
        response = env.request_session.get(auth_url, **kwargs)
        result = {
            "success": True,
            "result": response.text,
            "url": auth_url,
            "status_code": response.status_code,
            "headers": dict(response.headers),
        }
        result["location"] = response.headers.get("Location")
        query_params = parse_qs(urlparse(result["location"]).fragment)
        result["bearer_token"] = query_params["access_token"][0]
        return result


class OpenShiftForm(ServiceForm):
    form_type = HiddenField(default="openshift_service")
    auth_url = StringField("Auth URL", substitution=True)
    client_id = StringField("Client ID", default="openshift-challenging-client", substitution=True)
    timeout = IntegerField(default=15)
    credentials = SelectField(
        "Credentials",
        choices=(
            ("device", "Device Credentials"),
            ("object", "Named Credential"),
            ("custom", "Custom Credentials"),
        ),
    )
    named_credential = InstanceField("Named Credential", model="credential")
    custom_username = StringField("Custom Username", substitution=True)
    custom_password = PasswordField("Custom Password", substitution=True)

    def validate(self, **_):
        valid_form = super().validate()
        device_credentials_error = (
            self.credentials.data == "device" and self.run_method.data == "once"
        )
        if device_credentials_error:
            self.credentials.errors.append(
                "Device credentials cannot be selected because the service "
                "'Run Method' is not set to 'Run Once per Device'"
            )
        return valid_form and not device_credentials_error
