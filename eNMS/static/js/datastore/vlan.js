import { tables } from "../table.js";

tables.vlan = class extends tables.data {};
tables.vlan.prototype.type = "vlan";
