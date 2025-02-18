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
          data-tooltip="Download JSON Object as File"
        >
          <span class="glyphicon glyphicon-download"></span>
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
