import { tables } from "../table.js";

tables.json = class extends tables.data {
  rowButtons(row) {
    return `
      <li>
        <button type="button" class="btn btn-sm btn-info"
          onclick="showJSONValue('${row.id}')"
          data-tooltip="View JSON Value"
        >
          <span class="glyphicon glyphicon-list-alt"></span>
        </button>
      </li>
      ${super.rowButtons(row)}
    `;
  }
};

tables.json.prototype.type = "json";
