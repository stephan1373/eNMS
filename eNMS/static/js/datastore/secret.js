import { tables } from "../table.js";

tables.secret = class SecretTable extends tables.data {};

tables.secret.prototype.type = "secret";
