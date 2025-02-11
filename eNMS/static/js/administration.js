/*
global
CodeMirror: false
page: false
settings: true
Dropzone: false
rbac: false
user: false
*/

import {
  call,
  configureNamespace,
  displayDiff,
  downloadFile,
  editors,
  initCodeMirror,
  notify,
  openPanel,
  processInstance,
} from "./base.js";
import { clearSearch, refreshTable, tables } from "./table.js";

export let folderPath = localStorage.getItem("folderPath") || "";
export let currentStore;

function displayFiles() {
  if ($("#files").length || page == "file_table") {
    return notify("The files table is already displayed.", "error", 5);
  }
  openPanel({
    name: "files",
    size: "1000 600",
    content: `
      <form id="search-form-file" style="margin: 15px">
        <div id="tooltip-overlay" class="overlay"></div>
        <nav
          id="controls-file"
          class="navbar navbar-default nav-controls"
          role="navigation"
        ></nav>
        <table
          id="table-file"
          style="margin-top: 10px;"
          class="table table-striped table-bordered table-hover"
          cellspacing="0"
          width="100%"
        ></table>
      </form>`,
    tableId: "file",
    title: "Files",
    callback: function() {
      // eslint-disable-next-line new-cap
      new tables["file"]();
    },
  });
}

export function displayFolderPath() {
  let currentPath = "";
  let htmlPath = [];
  `/files${folderPath}`
    .split("/")
    .slice(1)
    .forEach((folder) => {
      currentPath += folder == "files" ? "" : `/${folder}`;
      htmlPath.push(`<b> / </b>
        <button type="button" class="btn btn-xs btn-primary"
        onclick="eNMS.administration.enterFolder({path: '${currentPath}'})">
          ${folder}
        </button>
      `);
    });
  $("#current-folder-path").html(`<b>Current Folder :</b>${htmlPath.join("")}`);
}

function enterFolder({ folder, path, parent }) {
  clearSearch("file");
  if (parent) {
    folderPath = folderPath
      .split("/")
      .slice(0, -1)
      .join("/");
  } else {
    folderPath = path || folder ? path || `${folderPath}/${folder}` : "";
  }
  localStorage.setItem("folderPath", folderPath);
  refreshTable("file", null, null, true);
  if (folder) {
    $("#upward-folder-btn").removeClass("disabled");
  } else if (!folderPath) {
    $("#upward-folder-btn").addClass("disabled");
  }
  displayFolderPath();
}

function enterStore(data) {
  call({
    url: "/get_store",
    data: {store: currentStore, ...data},
    callback: function(store) {
      currentStore = store;
      if (store) {
        $("#upward-store-btn").removeClass("disabled");
      } else {
        $("#upward-store-btn").addClass("disabled");
      }
      const tableId = store ? `${store.data_type}-${store.id}` : "store";
      $("#table-div").empty().html(`
        <form id="search-form-${tableId}"
          style="padding: 12px 17px; width: 100%">
          <div id="tooltip-overlay" class="overlay"></div>
          <nav
            id="controls-${tableId}"
            class="navbar navbar-default nav-controls"
            role="navigation"
          ></nav>
          <table
            id="table-${tableId}"
            style="margin-top: 10px"
            class="table table-striped table-bordered table-hover add-id"
            cellspacing="0"
            width="100%"
          ></table>
        </form>
      `);
      if (store) {
        new tables[store.data_type](store.id, {
          store_id: store.id,
          store_id_filter: "equality",
        });
      } else {
        new tables["store"];
      }
    },
  });
}

export function displayStorePath() {
  let currentPath = "";
  let htmlPath = [];
  currentStore.path
    .split("/")
    .slice(1)
    .forEach((store) => {
      currentPath += `/${store}`;
      htmlPath.push(`<b> / </b>
        <button type="button" class="btn btn-xs btn-primary"
        onclick="eNMS.administration.enterStore({path: '${currentPath}'})">
          ${store}
        </button>
      `);
    });
  $("#current-store-path").html(`<b>Current Store :</b>${htmlPath.join("")}`);
}

function downloadProfilingData() {
  call({
    url: "/get_profiling_data",
    callback: function(data) {
      downloadFile("profiling_data", JSON.stringify(data, null, 2), "json");
    },
  });
}

function showChangelogDiff(id) {
  call({
    url: `/get_changelog_history/${id}`,
    callback: function(changelog) {
      openPanel({
        name: "changelog_diff",
        content: `
          <div class="modal-body">
            ${
              changelog?.history?.properties
                ? `<nav
              class="navbar navbar-default nav-controls"
              role="navigation"
              style="width: 350px; display: flex;"
            >
              <select
                id="changelog-properties-${id}"
                name="changelog-properties"
                class="form-control"
              ></select>
              <div style="margin-left:10px;">
                <input
                  id="diff-value-type"
                  style="width: 200px;"
                  type="checkbox"
                  data-onstyle="info"
                  data-offstyle="primary"
                >
              </div>
              <button
                class="btn btn-info"
                id="compare-changelog-${id}-btn"
                data-tooltip="Compare"
                type="button"
                style="margin-left:10px;"
              >
                <span class="glyphicon glyphicon-adjust"></span>
              </button>
            </nav>`
                : ""
            }
            <div id="changelog-content-${id}" style="margin-top: 30px"></div>
          </div>`,
        title: "Result",
        id: id,
        callback: function() {
          const editor = initCodeMirror(`changelog-content-${id}`, "network");
          if (changelog?.history?.properties) {
            $(`#changelog-properties-${id}`)
              .append(`<option value="full_content">Full Content</option>`)
              .on("change", function() {
                let value = changelog.content;
                if ($(`#changelog-properties-${id}`).val() != "full_content") {
                  const valueType = $("#diff-value-type").prop("checked")
                    ? "old"
                    : "new";
                  value = changelog.history.properties[this.value][valueType];
                }
                editor.setValue(typeof value === "number" ? value.toString() : value);
                editor.refresh();
              });
            $("#diff-value-type")
              .bootstrapToggle({
                on: "Old Value",
                off: "New Value",
              })
              .change(function() {
                $(`#changelog-properties-${id}`).trigger("change");
              });
            for (const property of Object.keys(changelog.history.properties)) {
              $(`#changelog-properties-${id}`).append(
                `<option value="${property}">${property}</option>`
              );
            }
            $(`#changelog-properties-${id}`).selectpicker("refresh");
          }
          editor.setValue(changelog.content);
          editor.refresh();
          $(`#compare-changelog-${id}-btn`)
            .unbind("click")
            .on("click", function() {
              if ($(`#changelog-properties-${id}`).val() == "full_content") {
                return notify("A specific property must be selected.", "error", 5);
              }
              displayDiff("changelog", id, $(`#changelog-properties-${id}`).val());
            });
        },
      });
    },
  });
}

export function openDebugPanel() {
  openPanel({
    name: "debug",
    title: "Debug Panel",
    size: "1200px 500px",
    callback: function() {
      call({
        url: "/load_debug_snippets",
        callback: function(snippets) {
          for (const name of Object.keys(snippets)) {
            $("#debug-snippets").append(`<option value="${name}">${name}</option>`);
          }
          $("#debug-snippets")
            .val("empty.py")
            .on("change", function() {
              const value = snippets[this.value];
              editors[undefined]["code"].setValue(value);
            })
            .selectpicker("refresh");
        },
      });
    },
  });
}

function runDebugCode() {
  call({
    url: "/run_debug_code",
    form: "debug-form",
    callback: function(result) {
      $("#debug-output").val(result);
      notify("Code executed successfully.", "success", 5, true);
    },
  });
}

function getClusterStatus() {
  call({
    url: "/get_cluster_status",
    callback: function() {
      refreshTable("server");
      setTimeout(getClusterStatus, 15000);
    },
  });
}

function migrationsExport() {
  notify("Migration Export initiated.", "success", 5, true);
  call({
    url: "/migration_export",
    form: "migration-form",
    callback: function() {
      notify("Migration Export successful.", "success", 5, true);
    },
  });
}

function scanFolder() {
  call({
    url: `/scan_folder/${folderPath.replace(/\//g, ">")}`,
    callback: function() {
      refreshTable("file");
      notify("Scan successful.", "success", 5, true);
    },
  });
}

function showMigrationPanel() {
  openPanel({
    name: "database_migration",
    title: "Database Migration",
    size: "auto",
    callback: () => {
      call({
        url: "/get_migration_folders",
        callback: function(folders) {
          let list = document.getElementById("versions");
          folders.forEach((item) => {
            let option = document.createElement("option");
            option.textContent = option.value = item;
            list.appendChild(option);
          });
        },
      });
    },
  });
}

function revertChange(id) {
  call({
    url: `/revert_change/${id}`,
    callback: function() {
      notify("Changes reverted.", "success", 5, true);
    },
  });
}

function migrationsImport() {
  notify("Inventory Import initiated.", "success", 5, true);
  call({
    url: "/migration_import",
    form: "migration-form",
    callback: function(result) {
      notify(result, "success", 5, true);
    },
  });
}

function databaseDeletion() {
  notify("Starting Database Deletion", "success", 5, true);
  call({
    url: "/database_deletion",
    title: "Database Deletion",
    form: "database_deletion-form",
    callback: function() {
      notify("Database Deletion done.", "success", 5, true);
      $("#database_deletion").remove();
    },
  });
}

function oldInstancesDeletion() {
  notify("Instances Deletion initiated...", "success", 5, true);
  call({
    url: "/old_instances_deletion",
    form: "old_instances_deletion-form",
    callback: function() {
      notify("Log Deletion done.", "success", 5, true);
      $("#old_instances_deletion").remove();
    },
  });
}

function getGitContent() {
  call({
    url: "/get_git_content",
    callback: function() {
      notify("Successfully pulled content from git.", "success", 5, true);
    },
  });
}

function editFile(id, filename, filepath) {
  call({
    url: `/edit_file/${filename}`,
    callback: function(content) {
      if (content.error) {
        refreshTable("file");
        return notify(content.error, "error", 5);
      }
      openPanel({
        name: "file_editor",
        title: `Edit ${filepath}`,
        id: id,
        callback: () => {
          const display = document.getElementById(`file_content-${id}`);
          // eslint-disable-next-line new-cap
          let fileEditor = (editors[id] = CodeMirror.fromTextArea(display, {
            lineWrapping: true,
            lineNumbers: true,
            theme: "cobalt",
            mode: "python",
            extraKeys: { "Ctrl-F": "findPersistent" },
          }));
          fileEditor.setSize("100%", "100%");
          fileEditor.setValue(content);
          fileEditor.refresh();
        },
      });
    },
  });
}

function saveFile(file) {
  $(`[id="file_content-${file}"]`).text(editors[file].getValue());
  call({
    url: `/save_file/${file}`,
    form: `file-content-form-${file}`,
    callback: function() {
      notify("File successfully saved.", "success", 5, true);
      $(`[id="file_editor-${file}"`).remove();
      refreshTable("file");
    },
  });
}

function showFileUploadPanel(folder) {
  if (!folder) folder = folderPath;
  const pathId = folder.replace(/\//g, "-") || 1;
  openPanel({
    name: "upload_files",
    title: `Upload files to ${folder}`,
    size: "700 615",
    id: pathId,
    callback: () => {
      const element = document.getElementById(`dropzone-${pathId}`);
      let dropzone = new Dropzone(element, {
        url: "/upload_files",
        autoProcessQueue: false,
        addRemoveLinks: true,
        parallelUploads: 10,
        queuecomplete: () => {
          $(".dz-remove").remove();
          notify("Files successfully uploaded.", "success", 5, true);
          setTimeout(() => refreshTable("file"), 500);
        },
        init: function() {
          this.on("addedfile", function(file) {
            if (dropzone.files.slice(0, -1).some((f) => f.name == file.name)) {
              notify("There is already a file with the same name.", "error", 5);
              dropzone.removeFile(file);
            }
          });
        },
        timeout: settings.files.upload_timeout,
      });
      $(`[id="dropzone-submit-${pathId}"]`).click(function() {
        $(`[id="folder-${pathId}"]`).val(folder);
        dropzone.processQueue();
      });
    },
  });
}

export function showFolderPanel(id) {
  if (id) return;
  $(`#folder-path`).prop("readonly", true);
  $(`#folder-filename`).prop("readonly", false);
}

export function showStorePanel(id) {
  if (id) return;
  $("#store-scoped_name").prop("readonly", false);
  $("#store-path").prop("readonly", true);
}

function showProfile() {
  openPanel({
    name: "profile",
    size: "800 auto",
    title: "Profile",
    id: user.id,
    callback: () => {
      call({
        url: `/get/user/${user.id}`,
        data: { properties_only: true },
        callback: function(user) {
          for (const [page, endpoint] of Object.entries(rbac.all_pages)) {
            if (!user.is_admin && !user.pages.includes(page)) continue;
            const option = `<option value='${endpoint}'>${page}</option>`;
            $(`#profile-landing_page-${user.id}`).append(option);
          }
          $(`#profile-landing_page-${user.id}`)
            .val(user.landing_page)
            .selectpicker("refresh");
          processInstance("profile", user);
        },
      });
    },
  });
}

function saveProfile() {
  call({
    url: "/save_profile",
    form: `profile-form-${user.id}`,
    callback: function() {
      notify("Profile saved.", "success", 5, true);
      $(`#profile-${user.id}`).remove();
    },
  });
}

export function showCredentialPanel(id) {
  const postfix = id ? `-${id}` : "";
  $(`#credential-subtype${postfix}`)
    .change(function() {
      if (this.value == "password") {
        $(`#credential-private_key-div${postfix}`).hide();
        $(`#credential-password-div${postfix}`).show();
      } else {
        $(`#credential-password-div${postfix}`).hide();
        $(`#credential-private_key-div${postfix}`).show();
      }
    })
    .trigger("change");
}

function showServerTime() {
  call({
    url: "/get_time",
    callback: function(time) {
      $("#server-time").html(`Server Time: ${time}`);
    },
  });
}

function updateDeviceRbac() {
  notify("RBAC Update Initiated.", "success", 5, true);
  call({
    url: "/update_device_rbac",
    callback: function() {
      notify("RBAC Update successful", "success", 5, true);
    },
  });
}

configureNamespace("administration", [
  databaseDeletion,
  displayFiles,
  downloadProfilingData,
  editFile,
  enterFolder,
  enterStore,
  getClusterStatus,
  getGitContent,
  migrationsExport,
  migrationsImport,
  oldInstancesDeletion,
  runDebugCode,
  saveFile,
  saveProfile,
  scanFolder,
  showChangelogDiff,
  showFileUploadPanel,
  showMigrationPanel,
  showProfile,
  showServerTime,
  revertChange,
  updateDeviceRbac,
]);
