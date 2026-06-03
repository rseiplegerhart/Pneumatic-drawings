const COMP_TYPES = [
  { value: "cylinder_da",        label: "Double-acting cylinder" },
  { value: "cylinder_sa",        label: "Single-acting cylinder" },
  { value: "valve_52",           label: "5/2 Directional valve" },
  { value: "valve_32",           label: "3/2 Directional valve (NC)" },
  { value: "flow_control",       label: "Flow control valve" },
  { value: "check_valve",        label: "Check valve" },
  { value: "pressure_regulator", label: "Pressure regulator" },
  { value: "gauge",              label: "Pressure gauge" },
  { value: "supply",             label: "Air supply" },
  { value: "exhaust",            label: "Exhaust" },
];

const ACTUATORS = [
  { value: "solenoid", label: "Solenoid" },
  { value: "manual",   label: "Manual" },
  { value: "pilot",    label: "Pilot" },
  { value: "spring",   label: "Spring" },
];

let compCount = 0;
let connCount = 0;

function isValve(type) {
  return type === "valve_52" || type === "valve_32";
}

function typeOptions(selected) {
  return COMP_TYPES.map(t =>
    `<option value="${t.value}" ${t.value === selected ? "selected" : ""}>${t.label}</option>`
  ).join("");
}

function actuatorOptions(selected) {
  return ACTUATORS.map(a =>
    `<option value="${a.value}" ${a.value === selected ? "selected" : ""}>${a.label}</option>`
  ).join("");
}

function addComponent(defaults = {}) {
  const id = ++compCount;
  const type = defaults.comp_type || "cylinder_da";
  const valve = isValve(type);

  const html = `
    <div class="comp-row" id="comp-${id}">
      <label>Type
        <select id="comp-type-${id}" onchange="onTypeChange(${id})">
          ${typeOptions(type)}
        </select>
      </label>
      <label>Tag
        <input type="text" id="comp-tag-${id}" value="${defaults.tag || ""}" placeholder="e.g. V1">
      </label>
      <label>Description
        <input type="text" id="comp-label-${id}" value="${defaults.label || ""}" placeholder="e.g. Main valve">
      </label>
      <label>Column
        <input type="number" id="comp-col-${id}" value="${defaults.col ?? 0}" min="0" max="20">
      </label>
      <label>Row
        <input type="number" id="comp-row-${id}" value="${defaults.row ?? 0}" min="0" max="20">
      </label>
      <label id="actuator-label-${id}" style="display:${valve ? 'flex' : 'none'}">Actuator
        <select id="comp-actuator-${id}">
          ${actuatorOptions(defaults.actuator || "solenoid")}
        </select>
      </label>
      <label id="spring-label-${id}" style="display:${valve ? 'flex' : 'none'}">Spring return
        <select id="comp-spring-${id}">
          <option value="true"  ${defaults.spring_return !== false ? "selected" : ""}>Yes</option>
          <option value="false" ${defaults.spring_return === false  ? "selected" : ""}>No</option>
        </select>
      </label>
      <button class="btn-remove" onclick="removeComp(${id})">Remove</button>
    </div>`;

  document.getElementById("components-list").insertAdjacentHTML("beforeend", html);
  document.getElementById("no-components").style.display = "none";
}

function onTypeChange(id) {
  const type = document.getElementById(`comp-type-${id}`).value;
  const valve = isValve(type);
  document.getElementById(`actuator-label-${id}`).style.display = valve ? "flex" : "none";
  document.getElementById(`spring-label-${id}`).style.display   = valve ? "flex" : "none";
}

function removeComp(id) {
  document.getElementById(`comp-${id}`).remove();
  if (!document.querySelector(".comp-row"))
    document.getElementById("no-components").style.display = "";
}

function addConnection(defaults = {}) {
  const id = ++connCount;
  const html = `
    <div class="conn-row" id="conn-${id}">
      <label>From tag
        <input type="text" id="conn-from-tag-${id}" value="${defaults.from_tag || ""}" placeholder="e.g. V1">
      </label>
      <label>Port
        <input type="text" id="conn-from-port-${id}" value="${defaults.from_port || ""}" placeholder="e.g. 2(A)">
      </label>
      <label>To tag
        <input type="text" id="conn-to-tag-${id}" value="${defaults.to_tag || ""}" placeholder="e.g. CYL1">
      </label>
      <label>Port
        <input type="text" id="conn-to-port-${id}" value="${defaults.to_port || ""}" placeholder="e.g. A">
      </label>
      <button class="btn-remove" onclick="removeConn(${id})">Remove</button>
    </div>`;

  document.getElementById("connections-list").insertAdjacentHTML("beforeend", html);
  document.getElementById("no-connections").style.display = "none";
}

function removeConn(id) {
  document.getElementById(`conn-${id}`).remove();
  if (!document.querySelector(".conn-row"))
    document.getElementById("no-connections").style.display = "";
}

function collectData() {
  const components = [];
  document.querySelectorAll(".comp-row").forEach(row => {
    const id = row.id.replace("comp-", "");
    const type = document.getElementById(`comp-type-${id}`).value;
    components.push({
      comp_type:    type,
      tag:          document.getElementById(`comp-tag-${id}`).value.trim(),
      label:        document.getElementById(`comp-label-${id}`).value.trim(),
      col:          parseInt(document.getElementById(`comp-col-${id}`).value) || 0,
      row:          parseInt(document.getElementById(`comp-row-${id}`).value) || 0,
      actuator:     document.getElementById(`comp-actuator-${id}`)?.value || "solenoid",
      spring_return: document.getElementById(`comp-spring-${id}`)?.value !== "false",
    });
  });

  const connections = [];
  document.querySelectorAll(".conn-row").forEach(row => {
    const id = row.id.replace("conn-", "");
    connections.push({
      from_tag:  document.getElementById(`conn-from-tag-${id}`).value.trim(),
      from_port: document.getElementById(`conn-from-port-${id}`).value.trim(),
      to_tag:    document.getElementById(`conn-to-tag-${id}`).value.trim(),
      to_port:   document.getElementById(`conn-to-port-${id}`).value.trim(),
    });
  });

  return {
    title:    document.getElementById("title").value.trim(),
    drawn_by: document.getElementById("drawn_by").value.trim(),
    date:     document.getElementById("date").value,
    components,
    connections,
  };
}

async function interpret() {
  const prompt = document.getElementById("ai-prompt").value.trim();
  const btn    = document.querySelector(".btn-ai");
  const status = document.getElementById("ai-status");

  if (!prompt) {
    status.textContent = "Please enter a description first.";
    status.className = "error";
    return;
  }

  btn.disabled = true;
  status.textContent = "Asking Claude…";
  status.className = "";

  try {
    const resp = await fetch("/interpret", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.error || resp.statusText);
    }

    // Clear existing components and connections
    document.getElementById("components-list").innerHTML = "";
    document.getElementById("connections-list").innerHTML = "";
    compCount = 0;
    connCount = 0;
    document.getElementById("no-components").style.display = "";
    document.getElementById("no-connections").style.display = "";

    // Populate header fields
    if (data.title)    document.getElementById("title").value    = data.title;
    if (data.drawn_by) document.getElementById("drawn_by").value = data.drawn_by;
    if (data.date)     document.getElementById("date").value     = data.date;

    // Populate components
    (data.components || []).forEach(c => addComponent(c));

    // Populate connections
    (data.connections || []).forEach(c => addConnection(c));

    status.textContent = `Circuit generated: ${(data.components || []).length} component(s), ${(data.connections || []).length} connection(s). Review below and click Generate PDF when ready.`;
    status.className = "ok";

  } catch (err) {
    status.textContent = "Error: " + err.message;
    status.className = "error";
  } finally {
    btn.disabled = false;
  }
}

async function generate() {
  const btn    = document.querySelector(".btn-generate");
  const status = document.getElementById("status");

  const data = collectData();
  if (!data.components.length) {
    status.textContent = "Add at least one component first.";
    status.className = "error";
    return;
  }

  btn.disabled = true;
  status.textContent = "Generating…";
  status.className = "";

  try {
    const resp = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!resp.ok) {
      const msg = await resp.text();
      throw new Error(msg || resp.statusText);
    }

    const blob = await resp.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = (data.title || "circuit").replace(/\s+/g, "_") + ".pdf";
    a.click();
    URL.revokeObjectURL(url);
    status.textContent = "PDF downloaded.";
  } catch (err) {
    status.textContent = "Error: " + err.message;
    status.className = "error";
  } finally {
    btn.disabled = false;
  }
}

// Seed with a starter example so the form isn't blank
addComponent({ comp_type: "supply",             tag: "AIR",  label: "Air Supply",         col: 0, row: 0 });
addComponent({ comp_type: "pressure_regulator", tag: "PR1",  label: "Pressure Regulator", col: 1, row: 0 });
addComponent({ comp_type: "valve_52",           tag: "V1",   label: "5/2 Solenoid Valve", col: 2, row: 0, actuator: "solenoid", spring_return: true });
addComponent({ comp_type: "cylinder_da",        tag: "CYL1", label: "Clamp Cylinder",     col: 3, row: 0 });

addConnection({ from_tag: "AIR",  from_port: "A",    to_tag: "PR1",  to_port: "P"   });
addConnection({ from_tag: "PR1",  from_port: "A",    to_tag: "V1",   to_port: "1"   });
addConnection({ from_tag: "V1",   from_port: "2(A)", to_tag: "CYL1", to_port: "A"   });
addConnection({ from_tag: "V1",   from_port: "4(B)", to_tag: "CYL1", to_port: "B"   });
