/*
global
alertify: false
CodeMirror: false
settings: true
csrf_token: false
eNMS: true
formProperties: false
job: false
jsPanel: false
moment: false
page: false
relations: false
relationships: false
*/

import { tables } from "./table.js";
import { creationMode, processWorkflowData, workflow } from "./workflow.js";

export let editors = {};
export let userIsActive = true;
let topZ = 1000;

export function detectUserInactivity() {
  let timer;
  window.onload = resetTimer;
  window.onmousemove = resetTimer;
  window.onmousedown = resetTimer;
  window.ontouchstart = resetTimer;
  window.onclick = resetTimer;
  window.onkeypress = resetTimer;
  window.addEventListener("scroll", resetTimer, true);

  function setUserInactive() {
    userIsActive = false;
  }

  function resetTimer() {
    clearTimeout(timer);
    userIsActive = true;
    timer = setTimeout(setUserInactive, 180000);
  }
}

const panelThemes = {
  logs: { bgContent: "#1B1B1B" },
  device_data: { bgContent: "#1B1B1B" },
  file: { bgContent: "#1B1B1B" },
};

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrf_token);
    }
    if (!settings.url.includes("filtering")) {
      document.body.style.cursor = "progress";
    }
  },
  complete: function() {
    document.body.style.cursor = "default";
  },
});

function loadScript(url, id) {
  let script = document.createElement("script");
  script.onload = function() {
    try {
      job(id);
    } catch (e) {
      notify("Failed to load script", "error", 5);
    }
  };
  script.src = url;
  document.head.appendChild(script);
}

export function openUrl(url) {
  let win = window.open(url, "_blank");
  win.focus();
}

export function cantorPairing(x, y) {
  return ((x + y) * (x + y + 1)) / 2 + y;
}

function processResults(callback, results) {
  if (results === false) {
    notify("HTTP Error 403 – Forbidden", "error", 5);
  } else if (results && results.alert) {
    if (Array.isArray(results.alert)) {
      results.alert.map((e) => notify(e, "error", 5));
    } else {
      notify(results.alert, "error", 5);
    }
  } else if (results && results.invalid_form) {
    for (const [field, error] of Object.entries(results.errors)) {
      notify(`Wrong input for "${field}": ${error}`, "error", 20);
    }
  } else {
    if (callback) callback(results);
  }
}

export const call = function({ url, data, form, callback }) {
  let params = {
    type: "POST",
    url: url,
    success: function(results) {
      processResults(callback, results);
    },
  };
  if (data) {
    Object.assign(params, {
      data: JSON.stringify(data),
      contentType: "application/json",
      dataType: "json",
    });
  } else if (form) {
    params.data = $(`[id="${form}"]`).serialize();
  }
  $.ajax(params);
};

export function serializeForm(form) {
  const data = JSON.parse(JSON.stringify($(form).serializeArray()));
  let result = {};
  data.forEach((property) => {
    if (relations.includes(property.name)) {
      if (!(property.name in result)) result[property.name] = [];
      result[property.name].push(property.value);
    } else {
      if (property.value) result[property.name] = property.value;
    }
  });
  return result;
}

export const deleteInstance = function(type, id) {
  call({
    url: `/delete_instance/${type}/${id}`,
    callback: function(result) {
      $(`#instance_deletion-${id}`).remove();
      if (type.includes("service") || type == "workflow") {
        type = "service";
        if (localStorage.getItem("path").includes(id)) {
          localStorage.removeItem("path");
        }
      }
      tables[type]
        .row($(`#${id}`))
        .remove()
        .draw(false);
      const name = result.name ? `'${result.name}'` : "";
      notify(`${type.toUpperCase()} ${name} deleted.`, "error", 5);
    },
  });
};

export function createTooltips() {
  $("[data-tooltip]").each(function() {
    jsPanel.tooltip.create({
      id: `tooltip-${$(this)
        .attr("data-tooltip")
        .replace(/\s/g, "")}`,
      content: `<p style="margin-right: 10px; margin-left: 10px; color: black">
        <b>${$(this).attr("data-tooltip")}</b></p>`,
      contentSize: "auto",
      connector: true,
      delay: 800,
      header: false,
      position: {
        my: "center-bottom",
        at: "center-top",
        of: this,
      },
      target: this,
      theme: "primary filledlight",
    });
  });
}

export const setupContextSensitiveHelp = function(panel, name, type, id) {
  // Originally tried passing the 'ajax' and 'contentAjax' options inside showHelpPanel.
  // This did not work for me originally so used some fallback code to use xhr directly.
  // @TODO: try again later with contentAjax was
  // Original:
  //  $(".context-help").each(function(index, elem) {
  //      $(elem).on('click', function() {
  //        showHelpPanel(elem, $(elem).attr("help_url"), $(elem).attr("for"));
  //      });
  //  });
  $(".context-help").each(function(index, elem) {
    let xhr = null;
    // By convention, 'elem' will be now be an icon but will have similar attributes
    // to its nearby 'label.'
    let helpUrl = $(elem).attr("help_url") || "no_help_found.html";
    let labelFor = $(elem).attr("for");
    xhr = $.ajax({
      url: `${helpUrl}`,
      xhrFields: { withCredentials: true },
    })
      .done(function(data) {
        xhr = null;
        $(elem).on("click", function() {
          showHelpPanel(elem, type, labelFor, data);
        });
      })
      .fail(function(err) {
        xhr = null;
        notify(`Failed to load help at ${helpUrl || "help url not found"} for element ${labelFor || "no label for element"}`, "error", 5);
      });
    setTimeout(function() {
      if (xhr) {
        xhr.abort();
        xhr = null;
      }
    }, 3500);
    return $.when(xhr).then(elem);
  });
};

export function openPanel({
  name,
  title,
  id,
  callback,
  type,
  duplicate,
  content,
  size,
}) {
  const panelId = id ? `${name}-${id}` : name;
  if ($(`#${panelId}`).length) {
    $(`#${panelId}`).css("zIndex", ++topZ);
    return;
  }
  let kwargs = {
    container: ".right_column",
    id: panelId,
    border: "2px solid #2A3F52",
    theme: panelThemes[name] || "light filledlight",
    headerLogo: "../static/img/logo.png",
    contentOverflow: "hidden scroll",
    contentSize: size || {
      width: () => window.innerWidth * 0.5,
      height: () => window.innerHeight * 0.75,
    },
    position: "center-top 0 10",
    headerTitle: title,
    maximizedMargin: 10,
    dragit: {
      opacity: 0.6,
      containment: 0,
    },
    resizeit: {
      containment: 0,
    },
  };
  if (content) {
    kwargs.content = content;
  } else {
    kwargs.contentAjax = {
      url: `../form/${name}`,
      done: function(panel) {
        panel.content.innerHTML = this.responseText;
        preprocessForm(panel, id, type, duplicate);
        configureForm(name, id, panelId);
        setupContextSensitiveHelp(panel, name, type, id);
        if (callback) callback(panel);
      },
    };
  }
  jsPanel.create(kwargs);
  if (callback && content) callback(content);
}

export function createTooltip({
  name,
  target,
  container,
  url,
  persistent,
  position,
  autoshow,
  title,
  content,
  callback,
  size,
}) {
  if ($(target).length) {
    let kwargs = {
      autoshow: autoshow,
      id: `tooltip-${name}`,
      container: container,
      contentSize: size || "auto",
      connector: true,
      delay: 0,
      mode: "sticky",
      position: position,
      target: target,
      ttipEvent: "click",
      theme: "light",
    };
    if (content) {
      kwargs.content = content;
    } else {
      kwargs.contentAjax = {
        url: url,
        done: function(panel) {
          panel.content.innerHTML = this.responseText;
          preprocessForm(panel);
          configureForm(name);
          if (callback) callback(panel);
        },
      };
    }
    if (title) {
      Object.assign(kwargs, { headerTitle: title, headerControls: "closeonly" });
    } else {
      kwargs.header = false;
    }
    if (persistent) {
      kwargs.onbeforeclose = function() {
        $(this).hide();
      };
    }
    jsPanel.tooltip.create(kwargs);
    if (persistent) {
      $(target).on("click", function() {
        $(`#tooltip-${name}`).show();
      });
    }
  }
}

export function showDeletionPanel(instance) {
  openPanel({
    name: "instance_deletion",
    title: `Delete ${instance.name}`,
    size: "auto",
    id: instance.id,
    type: instance.type,
  });
}

export function preprocessForm(panel, id, type, duplicate) {
  if (type) {
    panel.querySelectorAll(".add-type").forEach((el) => {
      $(el).prop("id", `${$(el).attr("id")}-${type}`);
    });
  }
  panel.querySelectorAll(".add-id").forEach((el) => {
    if (duplicate) {
      const property =
        type.includes("service") || type == "workflow" ? "scoped_name" : "name";
      if ([property, "id"].includes(el.name)) return;
    }
    if (id) $(el).prop("id", `${$(el).attr("id")}-${id}`);
  });
  panel.querySelectorAll(".btn-id").forEach((el) => {
    if (id) {
      $(el).attr(
        "onclick",
        type ? `${el.value}("${type}", "${id}")` : `${el.value}("${id}")`
      );
    } else {
      $(el).attr("onclick", type ? `${el.value}("${type}")` : `${el.value}()`);
    }
  });
  panel.querySelectorAll(".doc-link").forEach((el) => {
    $(el).attr("href", `${settings.app.documentation_url}${$(el).attr("href")}`);
  });
}

export function initSelect(el, model, parentId, single) {
  el.select2({
    multiple: !single,
    closeOnSelect: single ? true : false,
    dropdownParent: parentId ? $(`#${parentId}`) : $(document.body),
    ajax: {
      url: `/multiselect_filtering/${model}`,
      type: "POST",
      delay: 250,
      contentType: "application/json",
      data: function(params) {
        return JSON.stringify({
          term: params.term || "",
          page: params.page || 1,
        });
      },
      processResults: function(data, params) {
        params.page = params.page || 1;
        return {
          results: data.items,
          pagination: {
            more: params.page * 10 < data.total_count,
          },
        };
      },
    },
  });
}

export function configureForm(form, id, panelId) {
  if (!formProperties[form]) return;
  for (const [property, field] of Object.entries(formProperties[form])) {
    const fieldId = id ? `${form}-${property}-${id}` : `${form}-${property}`;
    let el = $(`#${fieldId}`);
    if (!el.length) el = $(`#${property}`);
    if (field.type == "date") {
      el.datetimepicker({
        format: "DD/MM/YYYY HH:mm:ss",
        widgetPositioning: {
          horizontal: "left",
          vertical: "bottom",
        },
        useCurrent: false,
      });
    } else if (["list", "multiselect"].includes(field.type)) {
      const elClass = el.attr("class");
      el.selectpicker({
        liveSearch: elClass ? !elClass.includes("no-search") : false,
        actionsBox: true,
        selectedTextFormat: "count > 3",
      });
    } else if (field.type == "code") {
      let editor = CodeMirror.fromTextArea(el[0], {
        lineWrapping: true,
        lineNumbers: true,
        extraKeys: { "Ctrl-F": "findPersistent" },
        matchBrackets: true,
        mode: "python",
        scrollbarStyle: "overlay",
      });
      editor.on("change", () => editor.save());
      if (!editors[id]) editors[id] = {};
      editors[id][property] = editor;
    } else if (["object", "object-list"].includes(field.type)) {
      let model;
      if (relationships[form]) {
        model = relationships[form][property].model;
      } else {
        model = field.model;
      }
      initSelect(el, model, panelId, field.type == "object");
    }
  }
}

function showServicePanel(type, id, mode) {
  const typeInput = $(id ? `#${type}-class-${id}` : `#${type}-class`);
  typeInput.val(type).prop("disabled", true);
  $(id ? `#${type}-name-${id}` : `#${type}-name`).prop("disabled", true);
  if (id) {
    $(`#${type}-shared-${id}`).prop("disabled", true);
    if (mode == "duplicate" && type == "workflow") {
      $(`#original-${id}`).val(id);
    }
  }
  $(id ? `#${type}-workflows-${id}` : `#${type}-workflows`).prop("disabled", true);
  $(id ? `#${type}-wizard-${id}` : `#${type}-wizard`).smartWizard({
    enableAllSteps: true,
    keyNavigation: false,
    transitionEffect: "none",
    onShowStep: function() {
      Object.keys(editors[id]).forEach(function(field) {
        editors[id][field].refresh();
      });
    },
  });
  $(".buttonFinish,.buttonNext,.buttonPrevious").hide();
  $(id ? `#${type}-wizard-${id}` : `#${type}-wizard`).smartWizard("fixHeight");
  if (mode == "run") {
    $(`#${type}-btn-${id}`)
      .removeClass("btn-success")
      .addClass("btn-primary")
      .attr("onclick", `eNMS.automation.parameterizedRun('${type}', ${id})`)
      .text("Run");
    $(".readonly-when-run").prop("readonly", true);
  }
}

export function showTypePanel(type, id, mode) {
  openPanel({
    name: type,
    id: id,
    callback: function(panel) {
      if (type == "workflow" || type.includes("service")) {
        showServicePanel(type, id, mode);
      }
      if (id) {
        const properties = type === "pool" ? "_properties" : "";
        call({
          url: `/get${properties}/${type}/${id}`,
          callback: function(instance) {
            const action = mode ? mode.toUpperCase() : "EDIT";
            panel.setHeaderTitle(`${action} ${type} - ${instance.name}`);
            processInstance(type, instance);
          },
        });
      } else {
        panel.setHeaderTitle(`Create a New ${type}`);
        if (page == "workflow_builder" && creationMode == "create_service") {
          $(`#${type}-workflows`).append(new Option(workflow.name, workflow.id));
          $(`#${type}-workflows`)
            .val(workflow.id)
            .trigger("change");
        }
      }
      if (type.includes("service")) {
        loadScript(`../static/js/services/${type}.js`, id);
      }
    },
    type: type,
    duplicate: mode == "duplicate",
  });
}

function updateProperty(instance, el, property, value, type) {
  let propertyType;
  if (formProperties[type][property]) {
    propertyType = formProperties[type][property].type;
  } else {
    propertyType = "str";
  }
  if (propertyType.includes("bool")) {
    el.prop("checked", value);
  } else if (propertyType.includes("dict") || propertyType == "json") {
    el.val(value ? JSON.stringify(value) : "{}");
  } else if (["list", "multiselect"].includes(propertyType)) {
    try {
      el.selectpicker("deselectAll");
    } catch (e) {
      // ignore
    }
    el.selectpicker("val", value);
    el.selectpicker("render");
  } else if (propertyType == "object-list") {
    value.forEach((o) => el.append(new Option(o.name, o.id)));
    el.val(value.map((p) => p.id)).trigger("change");
  } else if (propertyType == "object") {
    el.append(new Option(value.name, value.id))
      .val(value.id)
      .trigger("change");
  } else if (propertyType == "code") {
    const editor = editors[instance.id][property];
    if (editor) editor.setValue(value);
  } else if (propertyType == "field-list") {
    for (let [index, form] of value.entries()) {
      for (const [key, value] of Object.entries(form)) {
        $(`#${type}-${property}-${index}-${key}-${instance.id}`).val(value);
      }
    }
  } else {
    el.val(value);
  }
}

function processInstance(type, instance) {
  for (const [property, value] of Object.entries(instance)) {
    const el = $(
      instance ? `#${type}-${property}-${instance.id}` : `#${type}-${property}`
    );
    updateProperty(instance, el, property, value, type);
  }
}

export function processData(type, id) {
  if (type.includes("service") || type == "workflow") {
    $(id ? `#${type}-workflows-${id}` : `#${type}-workflows`).prop("disabled", false);
    if (id) $(`#${type}-shared-${id}`).prop("disabled", false);
  }
  call({
    url: `/update/${type}`,
    form: id ? `edit-${type}-form-${id}` : `edit-${type}-form`,
    callback: (instance) => {
      const tableType =
        type.includes("service") || type == "workflow" ? "service" : type;
      if (page.includes("table")) tables[tableType].ajax.reload(null, false);
      $(id ? `#${type}-${id}` : `#${type}`).remove();
      if (page == "workflow_builder") processWorkflowData(instance, id);
      notify(
        `${type.toUpperCase()} ${instance.name ? `'${instance.name}' ` : ""}${
          id ? "updated" : "created"
        }.`,
        "success",
        5
      );
    },
  });
}

(function($, jstree, undefined) {
  "use strict";

  $.jstree.plugins.html_row = function(options, parent) {
    // eslint-disable-next-line
    this.redraw_node = function(nodeId, ...args) {
      let el = parent.redraw_node.apply(this, [nodeId, ...args]);
      if (el) {
        let node = this._model.data[nodeId];
        this.settings.html_row.default(el, node);
      }
      return el;
    };
  };
})(jQuery);

export function copyToClipboard(text, isId) {
  if (isId) text = $(`#${text}`).val();
  let dummy = document.createElement("textarea");
  document.body.appendChild(dummy);
  dummy.value = text;
  dummy.select();
  document.execCommand("copy");
  document.body.removeChild(dummy);
  notify(`Copied to Clipboard: ${text}`, "success", 5);
}

(function($, window) {
  $.fn.contextMenu = function(settings) {
    return this.each(function() {
      $(this).on("contextmenu", function(e) {
        if (e.ctrlKey) {
          return;
        }
        const $menu = $(settings.menuSelector)
          .show()
          .css({
            position: "absolute",
            left: getMenuPosition(e.clientX, "width", "scrollLeft"),
            top: getMenuPosition(e.clientY, "height", "scrollTop"),
          })
          .off("click")
          .on("click", "a", function(e) {
            $menu.hide();
            const $selectedMenu = $(e.target);
            settings.menuSelected.call(this, $selectedMenu);
          });
        return false;
      });
      $(".dropdown-submenu a.menu-submenu").on("click", function(e) {
        const isHidden = $(this)
          .next("ul")
          .is(":hidden");
        $(".dropdown-submenu a.menu-submenu")
          .next("ul")
          .hide();
        $(this)
          .next("ul")
          .toggle(isHidden);
        e.stopPropagation();
        e.preventDefault();
      });
      $("body").click(function() {
        $(".dropdown-submenu a.menu-submenu")
          .next("ul")
          .hide();
        $(settings.menuSelector).hide();
      });
    });

    function getMenuPosition(mouse, direction, scrollDir) {
      const win = $(window)[direction]();
      const scroll = $(window)[scrollDir]();
      const menu = $(settings.menuSelector)[direction]();
      const offset =
        direction == "width" ? $(".left_column").width() : $(".header").height() + 2;
      let position = mouse + scroll - offset;
      if (mouse + menu > win && menu < mouse) {
        position -= menu;
      }
      return position;
    }
  };
})(jQuery, window);

export function notify(...args) {
  const alerts = JSON.parse(localStorage.getItem("alerts"));
  localStorage.setItem(
    "alerts",
    JSON.stringify([...alerts, [...args, moment().format("MMMM Do YYYY, h:mm:ss a")]])
  );
  const alert = alerts.length + 1 > 99 ? "99+" : alerts.length + 1;
  $("#alert-number").text(alert);
  alertify.notify(...args);
}

function showAllAlerts() {
  openPanel({
    name: "alerts_table",
    callback: () => {
      $("#alerts-table")
        // eslint-disable-next-line new-cap
        .DataTable({
          columns: [{ width: "200px" }, { width: "60px" }, null],
        })
        .order([0, "desc"])
        .draw();
    },
    content: `
      <div class="modal-body">
        <table 
          id="alerts-table"
          class="table table-striped table-bordered table-hover wrap"
          style="width:100%"
        >
          <thead>
            <tr>
                <th>Date</th>
                <th>Type</th>
                <th style="word-wrap: break-word">Content</th>
            </tr>
          </thead>
          <tbody>
          ${getAlerts()}
          </tbody>
        </table>
      <div>
    `,
  });
}

const copyToClipboardButton = `<img data-placement="top" data-toggle="tooltip"
   title="Copy to Clipboard" class="copy_to_clipboard" src="/static/help/clippy.svg"
   width="15" alt="Copy to clipboard"/>`;

const showCopiedMessage = function(element, message) {
  let original = $(element).attr("data-original-title");
  $(element)
    .attr("data-original-title", message)
    .tooltip("show");
  setTimeout(function() {
    $(element)
      .attr("data-original-title", message)
      .tooltip("hide");
    $(element).attr("data-original-title", original);
  }, 3000);
};

const formatCodeBlock = function(elem) {
  let helpTarget = $(elem).attr("help-target");
  let copyToTargetButton = `<img data-placement="top" data-toggle="tooltip"
    title="Copy to Target" class="copy_to_target" src="/static/help/clippy.svg"
    width="15" alt="Copy to target"/>`;
  let copyClipboardHtml = `<div>${
    helpTarget ? copyToTargetButton : ""
  } ${copyToClipboardButton}</div>`;
  // eslint-disable-next-line new-cap
  let cm = CodeMirror(
    function(elt) {
      $(elem.parentNode).prepend(copyClipboardHtml);
      let parent = elem.parentNode;
      parent.replaceChild(elt, elem);
      let copyToClipboardImage = $(parent)
        .find(".copy_to_clipboard")
        .get(0);
      $(copyToClipboardImage).tooltip();
      $(copyToClipboardImage).on("click", function(elem) {
        copyToClipboard(cm.getValue());
        showCopiedMessage(copyToClipboardImage, "Copied to clipboard!");
      });
      if (helpTarget) {
        let copyToTargetImage = $(parent)
          .find(".copy_to_target")
          .get(0);
        $(copyToTargetImage).tooltip();
        $(copyToTargetImage).on("click", function(elem) {
          let realTarget = $(`#${helpTarget}`).first();
          if (realTarget) {
            $(realTarget).val(cm.getValue());
          }
          showCopiedMessage(copyToTargetImage, "Copied to target!");
        });
      }
      $(parent)
        .find(".CodeMirror")
        .css("height", "fit-content");
    },
    {
      value: ($(elem).text() || "").trim(),
      lineWrapping: true,
      lineNumbers: true,
      readOnly: false,
      mode: { name: $(elem).attr("language") || "javascript", json: true },
    }
  );

  let highlight = $(elem).attr("highlight");
  if (highlight) {
    let cursor = cm.getSearchCursor(new RegExp(highlight));
    while (cursor.findNext()) {
      cm.markText(cursor.from(), cursor.to(), { className: "highlight" });
    }
  }
};

const reformatCodeBlocks = function(element, type, targetName) {
  $(element)
    .find("code")
    .each(function(index, elem) {
      let realTarget = $(`[id^="${type}-${targetName}"]`)
        .first()
        .attr("id");
      $(elem).attr("help-target", realTarget);
      formatCodeBlock(elem);
    });
};

function showHelpPanel(
  elem,
  type,
  parameterName,
  initialContent,
  title = "Help Panel"
) {
  $(`[id^="context-help-panel"]`).each((index, elem) => {
    elem.close();
  });
  jsPanel.create({
    container: ".right_column",
    id: `context-help-panel-${parameterName || "unknown"}`,
    selector: "body",
    position: "center right 0 50",
    headerTitle: title,
    maximizedMargin: 10,
    theme: "light filledlight",
    border: "2px solid #2A3F52",
    headerLogo: "../static/img/logo.png",
    contentOverflow: "hidden scroll",
    contentSize: {
      width: () => Math.min(window.innerWidth * 0.6, 750),
    },
    dragit: {
      opacity: 0.6,
    },
    content: initialContent,
    callback: function(panel) {
      reformatCodeBlocks(panel, type, parameterName);
    },
  });
}

function getAlerts(preview) {
  let alerts = JSON.parse(localStorage.getItem("alerts")).reverse();
  if (preview) alerts = alerts.splice(0, 4);
  return alerts
    .map((alert) => {
      if (preview) {
        const color = alert[1] == "error" ? "f87979" : "5BBD72";
        const fontSize = preview ? "11px" : "14px";
        return `
          <li
            style="background: #${color}; pointer-events: none; margin: 2px 6px"
          >
          <a style="word-wrap: break-word; color: #FFFFFF">
          <span class="time" style="font-size: ${fontSize}">
            ${alert[3]}
          </span>
          <span>${alert[0]}</span>
          </a>
        </li>`;
      } else {
        return `
        <tr>
          <td>${alert[3]}</td>
          <td>${alert[1]}</td>
          <td>${alert[0]}</td>
        </tr>`;
      }
    })
    .join("");
}

function clearAlerts() {
  localStorage.setItem("alerts", "[]");
  $("#alert-number").empty();
}

export function createAlerts() {
  $("#alerts").empty().append(`
    ${getAlerts(true)}
    <li style="margin: 3px 6px 0; padding: 10px; margin-bottom: 6px;">
      <div class="text-center">
        <a class="dropdown-item" onclick="eNMS.base.showAllAlerts()">
          <strong>See All Alerts</strong>
          <i class="fa fa-angle-right"></i>
        </a>
      </div>
    </li>
    <li style="margin: 3px 6px 0; padding: 10px; margin-bottom: 6px;">
      <div class="text-center">
        <a class="dropdown-item" onclick="eNMS.base.clearAlerts()">
          <strong>Clear All Alerts</strong>
          <i class="fa fa-remove"></i>
        </a>
      </div>
    </li>
  `);
}

export function configureNamespace(namespace, functions) {
  eNMS[namespace] = {};
  functions.forEach((f) => (eNMS[namespace][f.name] = f));
}

function fullScreen() {
  if (
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  ) {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    }
  } else {
    const element = document.documentElement;
    if (element.requestFullscreen) {
      element.requestFullscreen();
    } else if (element.mozRequestFullScreen) {
      element.mozRequestFullScreen();
    } else if (element.webkitRequestFullscreen) {
      element.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
    } else if (element.msRequestFullscreen) {
      element.msRequestFullscreen();
    }
  }
}

configureNamespace("base", [
  call,
  clearAlerts,
  copyToClipboard,
  createAlerts,
  deleteInstance,
  fullScreen,
  processData,
  showAllAlerts,
  showDeletionPanel,
  openPanel,
  showTypePanel,
  showHelpPanel,
]);
