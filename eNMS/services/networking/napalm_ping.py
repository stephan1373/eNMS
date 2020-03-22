from sqlalchemy import Boolean, ForeignKey, Integer
from wtforms import HiddenField, IntegerField, StringField

from eNMS.database.dialect import Column, MutableDict, SmallString
from eNMS.forms.fields import SubstitutionField
from eNMS.forms.automation import NapalmForm
from eNMS.models.automation import ConnectionService
from eNMS.forms.help import HelpLabel


class NapalmPingService(ConnectionService):

    __tablename__ = "napalm_ping_service"
    pretty_name = "NAPALM Ping"
    parent_type = "connection_service"
    id = Column(Integer, ForeignKey("connection_service.id"), primary_key=True)
    count = Column(Integer, default=0)
    driver = Column(SmallString)
    use_device_driver = Column(Boolean, default=True)
    timeout = Column(Integer, default=60)
    optional_args = Column(MutableDict)
    packet_size = Column(Integer, default=0)
    destination_ip = Column(SmallString)
    source_ip = Column(SmallString)
    timeout = Column(Integer, default=0)
    ttl = Column(Integer, default=0)
    vrf = Column(SmallString)

    __mapper_args__ = {"polymorphic_identity": "napalm_ping_service"}

    def job(self, run, payload, device):
        napalm_connection = run.napalm_connection(device)
        destination = run.sub(run.destination_ip, locals())
        source = run.sub(run.source_ip, locals())
        run.log("info", f"NAPALM PING : {source} -> {destination}", device)
        ping = napalm_connection.ping(
            destination=destination,
            source=source,
            vrf=run.vrf,
            ttl=run.ttl or 255,
            timeout=run.timeout or 2,
            size=run.packet_size or 100,
            count=run.count or 5,
        )
        return {"success": "success" in ping, "result": ping}


class NapalmPingForm(NapalmForm):
    form_type = HiddenField(default="napalm_ping_service")
    count = IntegerField(default=5, label=HelpLabel(text="Count", field_id="count", help_url="/static/help/service/napalm_ping/count.html"))
    packet_size = IntegerField(default=100, label=HelpLabel(text="Packet Size", field_id="packet_size", help_url="/static/help/service/napalm_ping/packet_size.html"))
    destination_ip = SubstitutionField(label=HelpLabel(text="Destination IP", field_id="destination_ip", help_url="/static/help/service/napalm_ping/destination_ip.html"))
    source_ip = SubstitutionField(label=HelpLabel(text="Source IP", field_id="source_ip", help_url="/static/help/service/napalm_ping/source_ip.html"))
    timeout = IntegerField(default=2, label=HelpLabel(text="Timeout", field_id="timeout", help_url="/static/help/service/napalm_ping/timeout.html"))
    ttl = IntegerField(default=255, label=HelpLabel(text="TTL", field_id="ttl", help_url="/static/help/service/napalm_ping/ttl.html"))
    vrf = StringField(label=HelpLabel(text="VRF", field_id="vrf", help_url="/static/help/service/napalm_ping/vrf.html"))
    groups = {
        "Ping Parameters": {
            "commands": [
                "count",
                "packet_size",
                "destination_ip",
                "source_ip",
                "timeout",
                "ttl",
                "vrf",
            ],
            "default": "expanded",
        },
        **NapalmForm.groups,
    }
