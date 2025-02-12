import { currentStore, displayStorePath } from "../administration.js";
import { tables } from "../table.js";

tables.store = class extends tables.data {
  addRow(kwargs) {
    let row = super.addRow(kwargs);
    row.scoped_name = `<a href="#" onclick="eNMS.administration.enterStore
        ({ id: ${row.id}})">
          <span class="glyphicon glyphicon-book" style="margin-left: 8px"></span>
          <b style="margin-left: 6px">${row.scoped_name}</b>
        </a>`;
    return row;
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
