from ast import parse
from wtforms import (
    BooleanField,
    FloatField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
)
from wtforms.validators import InputRequired
from wtforms.widgets import TextArea

from eNMS import app
from eNMS.forms import BaseForm
from eNMS.forms.fields import (
    CodeField,
    DictField,
    DictSubstitutionField,
    MultipleInstanceField,
    NoValidationSelectField,
    PasswordSubstitutionField,
    PythonField,
    SubstitutionField,
)
from eNMS.forms.help import HelpLabel


class ServiceForm(BaseForm):
    template = "service"
    form_type = HiddenField(default="service")
    id = HiddenField()
    name = StringField("Name")
    type = StringField("Service Type")
    shared = BooleanField("Shared Service")
    scoped_name = StringField("Scoped Name", [InputRequired()])
    description = StringField("Description")
    device_query = PythonField("Device Query (define targets from a python query)")
    device_query_property = SelectField(
        "Query Property Type", choices=(("name", "Name"), ("ip_address", "IP address"))
    )
    devices = MultipleInstanceField(label=HelpLabel(
            text="Devices",
            field_id="devices",
            help_url="/static/help/service/common/devices.html"))
    pools = MultipleInstanceField("Pools")
    workflows = MultipleInstanceField("Workflows")
    waiting_time = IntegerField(
        "Time to Wait before next service is started (in seconds)", default=0
    )
    send_notification = BooleanField("Send a notification")
    send_notification_method = SelectField(
        "Notification Method",
        choices=(("mail", "Mail"), ("slack", "Slack"), ("mattermost", "Mattermost")),
    )
    notification_header = StringField(widget=TextArea(), render_kw={"rows": 5})
    include_device_results = BooleanField("Include Device Results")
    include_link_in_summary = BooleanField("Include Result Link in Summary")
    display_only_failed_nodes = BooleanField("Display only failed nodes")
    mail_recipient = StringField("Mail Recipients (separated by comma)")
    number_of_retries = IntegerField("Number of retries", default=0)
    time_between_retries = IntegerField("Time between retries (in seconds)", default=10)
    maximum_runs = IntegerField("Maximum number of runs", default=1)
    skip = BooleanField("Skip this Service Regardless")
    skip_query = PythonField(
        label=HelpLabel(
            text="Skip Service If True (Python)",
            field_id="skip_query",
            help_url="/static/help/service/common/skip_query.html")
    )
    skip_value = SelectField(
        label=HelpLabel(
            text="Skip Success Value",
            field_id="skip_value",
            help_url="/static/help/service/common/skip_value.html"),
        choices=(("True", "True"), ("False", "False"),),
    )
    vendor = StringField(label=HelpLabel(
        text="Operating System",
        field_id="vendor",
        help_url="/static/help/service/common/vendor.html"))
    operating_system = StringField(label=HelpLabel(
        text="Operating System",
        field_id="operating_system",
        help_url="/static/help/service/common/operating_system.html"))
    initial_payload = DictField(**{"label": HelpLabel(
        text="Initial Payload",
        field_id="initial_payload",
        help_url="/static/help/service/common/initial_payload.html")})
    iteration_values = PythonField(
        label=HelpLabel(
            text="Iteration values: run service for each value (python query)",
            field_id="operating_system",
            help_url="/static/help/service/common/iteration_values.html"))
    iteration_variable_name = StringField(
        default="iteration_value",
        label=HelpLabel(
            text="Iteration Variable Name",
            field_id="operating_system",
            help_url="/static/help/service/common/operating_system.html"))
    iteration_devices = PythonField("Iteration Devices")
    iteration_devices_property = SelectField(
        "Iteration Devices Property",
        choices=(("name", "Name"), ("ip_address", "IP address")),
    )
    result_postprocessing = CodeField(widget=TextArea(), render_kw={"rows": 8})
    log_level = NoValidationSelectField(
        "Log Level",
        choices=((0, "Disable logging"), *enumerate(app.log_levels, 1)),
        default=1,
    )
    multiprocessing = BooleanField("Multiprocessing")
    max_processes = IntegerField("Maximum number of processes", default=15)
    conversion_method = SelectField(
        "Conversion Method",
        choices=(
            ("none", "No conversion"),
            ("text", "Text"),
            ("json", "Json dictionary"),
            ("xml", "XML dictionary"),
        ),
    )
    validation_method = SelectField(
        "Validation Method",
        choices=(
            ("none", "No validation"),
            ("text", "Validation by text match"),
            ("dict_included", "Validation by dictionary inclusion"),
            ("dict_equal", "Validation by dictionary equality"),
        ),
    )
    content_match = SubstitutionField(
        "Content Match", widget=TextArea(), render_kw={"rows": 8}
    )
    content_match_regex = BooleanField("Match content with Regular Expression")
    dict_match = DictSubstitutionField("Dictionary Match")
    negative_logic = BooleanField("Negative Logic")
    delete_spaces_before_matching = BooleanField("Delete spaces before matching")
    run_method = SelectField(
        "Run Method",
        choices=(
            ("per_device", "Run the service once per device"),
            ("once", "Run the service once"),
        ),
    )
    query_fields = [
        "device_query",
        "skip_query",
        "iteration_values",
        "result_postprocessing",
    ]

    def validate(self):
        valid_form = super().validate()
        no_recipient_error = (
            self.send_notification.data
            and self.send_notification_method.data == "mail"
            and not self.mail_recipient.data
        )
        if no_recipient_error:
            self.mail_recipient.errors.append(
                "Please add at least one recipient for the mail notification."
            )
        bracket_error = False
        for query_field in self.query_fields:
            field = getattr(self, query_field)
            try:
                parse(field.data)
            except Exception as exc:
                bracket_error = True
                field.errors.append(f"Wrong python expression ({exc}).")
            if "{{" in field.data and "}}" in field.data:
                bracket_error = True
                field.errors.append(
                    "You cannot use variable substitution "
                    "in a field expecting a python expression."
                )
        conversion_validation_mismatch = (
            self.conversion_method.data == "text"
            and "dict" in self.validation_method.data
            or self.conversion_method.data in ("xml", "json")
            and "dict" not in self.validation_method.data
        )
        if conversion_validation_mismatch:
            self.conversion_method.errors.append(
                f"The conversion method is set to '{self.conversion_method.data}'"
                f" and the validation method to '{self.validation_method.data}' :"
                " these do not match."
            )
        return (
            valid_form
            and not no_recipient_error
            and not bracket_error
            and not conversion_validation_mismatch
        )


class ConnectionForm(ServiceForm):
    form_type = HiddenField(default="connection")
    abstract_service = True
    credentials = SelectField(
        choices=(
            ("device", "Device Credentials"),
            ("user", "User Credentials"),
            ("custom", "Custom Credentials"),
        ),
        label=HelpLabel(text="Credentials", field_id="credentials",
                        help_url="/static/help/service/connection/credentials.html")
    )
    custom_username = SubstitutionField(
        label=HelpLabel(text="Custom Username", field_id="custom_username",
                        help_url="/static/help/service/connection/custom_username.html"))
    custom_password = PasswordSubstitutionField(
        label=HelpLabel(text="Custom Password", field_id="custom_password",
                        help_url="/static/help/service/connection/custom_password.html"))
    start_new_connection = BooleanField(
        label=HelpLabel(text="Start New Connection", field_id="start_new_connection",
                        help_url="/static/help/service/connection/start_new_connection.html"))
    close_connection = BooleanField(
        label=HelpLabel(text="Close Connection", field_id="close_connection",
                        help_url="/static/help/service/connection/close_connection.html"))
    group = {
        "commands": [
            "credentials",
            "custom_username",
            "custom_password",
            "start_new_connection",
            "close_connection",
        ],
        "default": "expanded",
    }


class NetmikoForm(ConnectionForm):
    form_type = HiddenField(default="netmiko")
    abstract_service = True
    driver = SelectField(choices=app.NETMIKO_DRIVERS)
    use_device_driver = BooleanField(default=True)
    enable_mode = BooleanField(
        "Enable mode (run in enable mode or as root)", default=True
    )
    config_mode = BooleanField("Config mode", default=False)
    fast_cli = BooleanField()
    timeout = FloatField(default=10.0)
    delay_factor = FloatField(
        (
            "Delay Factor (Changing from default of 1"
            " will nullify Netmiko Timeout setting)"
        ),
        default=1.0,
    )
    global_delay_factor = FloatField(
        (
            "Global Delay Factor (Changing from default of 1"
            " will nullify Netmiko Timeout setting)"
        ),
        default=1.0,
    )
    groups = {
        "Netmiko Parameters": {
            "commands": [
                "driver",
                "use_device_driver",
                "enable_mode",
                "config_mode",
                "fast_cli",
                "timeout",
                "delay_factor",
                "global_delay_factor",
            ],
            "default": "expanded",
        },
        "Connection Parameters": ConnectionForm.group,
    }


class NapalmForm(ConnectionForm):
    form_type = HiddenField(default="napalm")
    abstract_service = True
    driver = SelectField(
        choices=app.NAPALM_DRIVERS,
        label=HelpLabel(text="Driver", field_id="driver",
                        help_url="/static/help/service/napalm/driver.html")
    )
    use_device_driver = BooleanField(default=True)
    timeout = IntegerField(default=10)
    optional_args = DictField(**{"label": HelpLabel(
        text="Initial Payload",
        field_id="optional_args",
        help_url="/static/help/service/napalm/optional_args.html")})
    groups = {
        "Napalm Parameters": {
            "commands": ["driver", "use_device_driver", "timeout", "optional_args"],
            "default": "expanded",
        },
        "Connection Parameters": ConnectionForm.group,
    }


class RunForm(BaseForm):
    template = "object"
    form_type = HiddenField(default="run")
    id = HiddenField()


class RestartWorkflowForm(BaseForm):
    action = "eNMS.workflow.restartWorkflow"
    form_type = HiddenField(default="restart_workflow")
    start_services = MultipleInstanceField("Services", model="service")
    restart_runtime = NoValidationSelectField("Restart Runtime", choices=())
    restart_from_top_level_workflow = BooleanField(default=True)


class LogsForm(BaseForm):
    template = "logs"
    form_type = HiddenField(default="logs")
    runtimes = NoValidationSelectField("Runtime", choices=())


class ResultForm(BaseForm):
    template = "result"
    form_type = HiddenField(default="result")


class ResultTableForm(BaseForm):
    template = "table"
    form_type = HiddenField(default="table")
    runtimes = NoValidationSelectField("Runtime", choices=())


class DisplayForm(BaseForm):
    template = "display"
    form_type = HiddenField(default="display")


class TreeForm(BaseForm):
    template = "tree"
    form_type = HiddenField(default="tree")
    runtimes = NoValidationSelectField("Runtime", choices=())


class CalendarForm(BaseForm):
    template = "calendar"
    form_type = HiddenField(default="calendar")


class CompareForm(DisplayForm):
    form_type = HiddenField(default="compare")


class DisplayConfigurationForm(DisplayForm):
    form_type = HiddenField(default="display_configuration")


class FileForm(DisplayForm):
    template = "file"
    form_type = HiddenField(default="file")
    file_content = StringField(widget=TextArea(), render_kw={"rows": 8})


class AddServiceForm(BaseForm):
    form_type = HiddenField(default="add_services")
    template = "add_services"
    mode = SelectField(
        "Mode",
        choices=(
            ("deep", "Deep Copy (creates a duplicate from the service)"),
            ("shallow", "Shallow Copy (creates a reference to the service)"),
        ),
    )


class WorkflowLabelForm(BaseForm):
    form_type = HiddenField(default="workflow_label")
    action = "eNMS.workflow.createLabel"
    text = StringField(widget=TextArea(), render_kw={"rows": 15})
    alignment = SelectField(
        "Text Alignment",
        choices=(("left", "Left"), ("center", "Center"), ("right", "Right")),
    )


class WorkflowEdgeForm(BaseForm):
    template = "object"
    form_type = HiddenField(default="workflow_edge")
    id = HiddenField()
    label = StringField()
