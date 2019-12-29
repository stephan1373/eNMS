/*
global
echarts: false
*/

import { adjustHeight, call } from "./base.js";

const diagrams = {};
const defaultProperties = {
  device: "model",
  link: "model",
  user: "name",
  service: "vendor",
  workflow: "vendor",
  task: "status",
};

function drawDiagrams(diagram, result) {
  const options = {
    tooltip: {
      formatter: "{b} : {c} ({d}%)",
    },
    series: [
      {
        type: "pie",
        data: result.data,
      },
    ],
    label: {
      normal: {
        formatter: '{b} ({c})',
      }
    }
  }
  if (result.legend.length < 10) {
    options.legend = {
      orient: 'horizontal',
      bottom: 0,
      data: result.legend,
    };
  }
  diagram.setOption(options);
}

function parseData(data) {
  let result = [];
  let legend = [];
  for (let [key, value] of Object.entries(data)) {
    key = key || "Empty string";
    result.push({
      value: value,
      name: key,
    });
    legend.push(key)
  }
  return {data: result, legend: legend};
}

export function initDashboard() {
  call("/count_models", function(result) {
    for (const type of Object.keys(defaultProperties)) {
      $(`#count-${type}`).text(result.counters[type]);
    }
    for (const [type, objects] of Object.entries(result.properties)) {
      const diagram = echarts.init(document.getElementById(type));
      drawDiagrams(diagram, parseData(objects));
      diagrams[type] = diagram;
    }
    adjustHeight();
  });

  $.each(defaultProperties, function(type) {
    $(`#${type}-properties`)
      .selectpicker()
      .on("change", function() {
        call(`/counters/${this.value}/${type}`, function(objects) {
          drawDiagrams(diagrams[type], parseData(objects));
        });
      });
  });
}
