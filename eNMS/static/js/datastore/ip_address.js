import { displayStorePath } from "../administration.js";
import { Table, tables } from "../table.js";

tables.ip_address = class SecretTable extends Table {
  get controls() {
    return [
      this.columnDisplay(),
      this.displayChangelogButton(),
      this.refreshTableButton(),
      this.clearSearchButton(),
      `
      <a
        id="upward-store-btn"
        class="btn btn-info"
        onclick="eNMS.administration.enterStore({parent: true})"
        type="button"
      >
        <span class="glyphicon glyphicon-chevron-up"></span>
      </a>`,
      this.createNewButton(),
      this.bulkEditButton(),
      this.exportTableButton(),
      this.bulkDeletionButton(),
      `<div id="current-store-path" style="margin-top: 9px; margin-left: 9px"></div>`,
    ];
  }

  buttons(row) {
    return [
      `
      <ul class="pagination pagination-lg" style="margin: 0px;">
        <li>
          <button type="button" class="btn btn-sm btn-primary"
          onclick="eNMS.base.showInstancePanel('ip_address', '${
            row.id
          }')" data-tooltip="Edit"
            ><span class="glyphicon glyphicon-edit"></span
          ></button>
        </li>
        ${this.deleteInstanceButton(row)}
      </ul>`,
    ];
  }

  postProcessing(...args) {
    super.postProcessing(...args);
    displayStorePath();
  }
};

tables.ip_address.prototype.type = "ip_address";
