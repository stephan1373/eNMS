/*
global
JSONEditor: false
*/

import { call, configureNamespace, openPanel } from "../base.js";
import { tables } from "../table.js";

tables.json = class extends tables.data {
  rowButtons(row) {
    return `
      <li>
        <button type="button" class="btn btn-sm btn-info"
          onclick="eNMS.datastore.showJSONValue('${row.id}')"
          data-tooltip="View JSON Value"
        >
          <span class="glyphicon glyphicon-list-alt"></span>
        </button>
      </li>
      ${super.rowButtons(row)}
    `;
  }
};

function showJSONValue(id) {
  openPanel({
    name: "view_json_value",
    content: `<div id="content-${id}" style="height:100%"></div>`,
    title: "View JSON Value",
    id: id,
    callback: function() {
      call({
        url: `/get/json/${id}`,
        callback: (result) => {
          new JSONEditor(
            document.getElementById(`content-${id}`),
            {
              mode: "view",
              modes: ["code", "view"],
            },
            result.value
          );
        },
      });
    },
  });
}

tables.json.prototype.type = "json";

configureNamespace("datastore", [showJSONValue]);
