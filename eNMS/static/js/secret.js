import { Table, tables } from "./table.js";

tables.secret = class SecretTable extends Table {
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
          onclick="eNMS.base.showInstancePanel('secret', '${
            row.id
          }')" data-tooltip="Edit"
            ><span class="glyphicon glyphicon-edit"></span
          ></button>
        </li>
        ${this.deleteInstanceButton(row)}
      </ul>`,
    ];
  }
};

tables.secret.prototype.type = "secret";
