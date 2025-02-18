/*
global
JSONEditor: false
*/

import { call, configureNamespace } from "../base.js";
import { tables } from "../table.js";

tables.json = class extends tables.data {
  rowButtons(row) {
    return `
      <li>
        <button type="button" class="btn btn-sm btn-info"
          onclick="eNMS.datastore.downloadJSONObject('${row.id}')"
          data-tooltip="View JSON Value"
        >
          <span class="glyphicon glyphicon-list-alt"></span>
        </button>
      </li>
      ${super.rowButtons(row)}
    `;
  }
};

function downloadJSONObject(id) {
  call({
    url: `/get/json/${id}`,
    callback: (result) => {
      console.log(result)
    },
  });
}

tables.json.prototype.type = "json";

configureNamespace("datastore", [downloadJSONObject]);
