import { currentStore } from "../administration.js";
import { call, configureNamespace, notify } from "../base.js";
import { tables } from "../table.js";

tables.vlan = class extends tables.data {};

function getNextVlanId() {
    call({
      url: "/filtering/vlan",
      data: {constraints: {store: [currentStore.name] }, bulk: "vlan_id"},
      callback: (vlanIds) => {
        notify(`Next Vlan ID: ${Math.max(...vlanIds) + 1}`, "success", 5);
      },
    });
  }
  
  tables.vlan.prototype.type = "vlan";
  
  configureNamespace("datastore", [getNextVlanId]);
  