import { currentStore, displayStorePath } from "../administration.js";
import { Table, tables } from "../table.js";

tables.store = class StoreTable extends Table {
  addRow(kwargs) {
    let row = super.addRow(kwargs);
    row.scoped_name = `<a href="#" onclick="eNMS.administration.enterStore
        ({ id: ${row.id}})">
          <span class="glyphicon glyphicon-book" style="margin-left: 8px"></span>
          <b style="margin-left: 6px">${row.scoped_name}</b>
        </a>`;
    return row;
  }

  get controls() {
    const status = currentStore ? "" : "disabled";
    return [
      this.columnDisplay(),
      this.displayChangelogButton(),
      this.refreshTableButton(),
      this.clearSearchButton(),
      `
      <a
        id="upward-store-btn"
        class="btn btn-info ${status}"
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
          onclick="eNMS.base.showInstancePanel('store', '${
            row.id
          }')" data-tooltip="Edit"
            ><span class="glyphicon glyphicon-edit"></span
          ></button>
        </li>
        ${this.deleteInstanceButton(row)}
      </ul>`,
    ];
  }

  get filteringConstraints() {
    return currentStore ? {} : { store_filter: "empty" };
  }

  postProcessing(...args) {
    super.postProcessing(...args);
    displayStorePath();
  }
};

tables.store.prototype.type = "store";
