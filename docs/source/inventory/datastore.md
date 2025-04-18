---
title: Data Store
---

# Data Store

## Overview

## Adding a new model to the Data Store

- In the `models / datastore` folder, add a new python file to define the database model and its associated form.

```
from eNMS.database import db
from eNMS.forms import DataForm
from eNMS.fields import HiddenField, InstanceField
from eNMS.models.administration import Data

class Example(Data):
    __tablename__ = "iso_address"
    pretty_name = "ISO Address"
    __mapper_args__ = {"polymorphic_identity": "iso_address"}
    id = db.Column(Integer, ForeignKey("data.id"), primary_key=True)


class ExampleForm(DataForm):
    form_type = HiddenField(default="iso_address")
    store = InstanceField(
        "Store", model="store", constraints={"data_type": "iso_address"}
    )
```

- In `static / js / datastore`, add a new JS file with the table code:

```
import { tables } from "../table.js";

tables.iso_address = class extends tables.data {};
tables.iso_address.prototype.type = "iso_address";
```