import { tables } from "../table.js";

tables.ip_address = class SecretTable extends tables.data {};

tables.ip_address.prototype.type = "ip_address";
