import { tables } from "../table.js";

tables.json = class extends tables.data {};
tables.json.prototype.type = "json";
