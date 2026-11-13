const $ = (selector) => document.querySelector(selector);
const inr = (value) => new Intl.NumberFormat("en-IN", {
  style: "currency", currency: "INR", maximumFractionDigits: 0,
}).format(value || 0);
const count = (value) => new Intl.NumberFormat("en-IN").format(value || 0);
const colors = ["#347b58", "#e3a06a", "#6889a2", "#98ad77", "#bb795d", "#8d7ba4", "#d0b65f", "#7d9e9a"];

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function moneyCompact(value) {
  if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`;
  if (value >= 1000) return `₹${(value / 1000).toFixed(0)}k`;
  return inr(value);
}

function renderKpis(kpis) {
  for (const item of kpis) {
    const value = item.unit === "inr" ? inr(item.value) : count(item.value);
    $(`#value-${item.id}`).textContent = value;
    const delta = $(`#delta-${item.id}`);
    delta.classList.toggle("negative", item.delta !== null && item.delta < 0);
    delta.textContent = item.delta === null ? "—" : `${item.delta >= 0 ? "↑" : "↓"} ${Math.abs(item.delta)}%`;
    $(`#sub-${item.id}`).textContent = item.sub || (item.id === "bills" ? "bills rung through" : "vs previous period");
    const host = $(`#spark-${item.id}`);
    host.replaceChildren();
    const max = Math.max(...item.spark, 1);
    for (const amount of item.spark.slice(-14)) {
      const bar = node("i");
      bar.style.height = `${Math.max(14, amount / max * 100)}%`;
      host.append(bar);
    }
  }
}

function svg(name, attributes = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  return element;
}

function renderTrend(rows) {
  const host = $("#trend-chart");
  host.replaceChildren();
  if (!rows.length) return;
  const width = Math.max(host.clientWidth || 500, rows.length * 22);
  const height = 190;
  const pad = { left: 47, right: 8, top: 10, bottom: 23 };
  const plotWidth = width - pad.left - pad.right;
  const plotHeight = height - pad.top - pad.bottom;
  const max = Math.max(...rows.flatMap((row) => [row.sales, row.profit]), 1) * 1.16;
  const chart = svg("svg", { viewBox: `0 0 ${width} ${height}`, class: "trend-svg", role: "presentation", preserveAspectRatio: "none" });
  for (let i = 0; i <= 3; i += 1) {
    const y = pad.top + plotHeight * i / 3;
    chart.append(svg("line", { x1: pad.left, y1: y, x2: width - pad.right, y2: y, class: "grid-line" }));
    const label = svg("text", { x: pad.left - 7, y: y + 3, "text-anchor": "end", class: "axis-label" });
    label.textContent = moneyCompact(max * (3 - i) / 3);
    chart.append(label);
  }
  const point = (value, index) => ({
    x: pad.left + plotWidth * (rows.length === 1 ? .5 : index / (rows.length - 1)),
    y: pad.top + plotHeight * (1 - value / max),
  });
  for (const [key, color] of [["sales", "#347b58"], ["profit", "#e3a06a"]]) {
    const points = rows.map((row, i) => point(row[key], i));
    chart.append(svg("path", {
      d: points.map((p, i) => `${i ? "L" : "M"} ${p.x} ${p.y}`).join(" "),
      fill: "none", stroke: color, "stroke-width": key === "sales" ? 2.5 : 1.8,
      "stroke-linecap": "round", "stroke-linejoin": "round",
    }));
    points.forEach((p, i) => {
      const circle = svg("circle", { cx: p.x, cy: p.y, r: 2.4, fill: color });
      const title = svg("title");
      title.textContent = `${rows[i].date}: ${key} ${inr(rows[i][key])}`;
      circle.append(title);
      chart.append(circle);
    });
  }
  rows.forEach((row, i) => {
    if (i % 5 !== 0 && i !== rows.length - 1) return;
    const p = point(0, i);
    const label = svg("text", { x: p.x, y: height - 5, "text-anchor": "middle", class: "axis-label" });
    label.textContent = new Date(`${row.date}T12:00:00`).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
    chart.append(label);
  });
  host.append(chart);
}

function renderActions(actions) {
  const host = $("#action-list");
  host.replaceChildren();
  $("#action-count").textContent = count(actions.length);
  $("#nav-stock-count").textContent = actions.filter((item) => item.type === "urgent" || item.type === "warning").length;
  if (!actions.length) {
    host.append(node("p", "empty-message", "All quiet for now. Your shelves are looking good."));
    return;
  }
  actions.slice(0, 7).forEach((item) => {
    const row = node("a", `action-item ${item.type}`);
    row.href = item.href;
    const icon = node("span", "action-icon", item.icon);
    const copy = node("span", "action-copy");
    copy.append(node("strong", "", item.title), node("span", "", item.detail));
    const value = node("span", "action-value");
    value.append(document.createTextNode(item.type === "warning" ? count(item.value) : inr(item.value)));
    value.append(node("small", "", item.value_label));
    row.append(icon, copy, value);
    host.append(row);
  });
}

function renderCompactList(selector, rows, type) {
  const host = $(selector);
  host.replaceChildren();
  const selected = rows.slice(0, 3);
  if (!selected.length) {
    host.append(node("div", "empty-message", "Nothing to flag right now."));
    return;
  }
  selected.forEach((item) => {
    const row = node("div", "compact-row");
    const copy = node("span");
    copy.append(node("strong", "", item.name));
    const secondary = type === "expiry"
      ? `${item.units} units · ${item.days_left} day${item.days_left === 1 ? "" : "s"} left`
      : type === "reorder"
        ? `${item.stock} left · ${item.cover_days} days of cover`
        : `${item.margin}% margin · target ${item.target_margin}%`;
    copy.append(node("small", "", secondary));
    const value = type === "expiry" ? inr(item.loss) : type === "reorder" ? `${count(item.suggested_qty)} units` : inr(item.suggested_price);
    row.append(copy, node("span", "compact-value", value));
    host.append(row);
  });
}

function renderProducts(products) {
  const host = $("#product-list");
  host.replaceChildren();
  products.slice(0, 4).forEach((product, index) => {
    const row = node("div", "compact-row");
    const rank = node("span", "product-rank", String(index + 1).padStart(2, "0"));
    const copy = node("span");
    copy.append(node("strong", "", product.name), node("small", "", `${product.category} · ${count(product.units)} units sold`));
    row.append(rank, copy, node("span", "compact-value", inr(product.sales)));
    host.append(row);
  });
}

function renderCategories(categories) {
  const host = $("#category-chart");
  const legend = $("#category-legend");
  host.replaceChildren();
  legend.replaceChildren();
  const total = categories.reduce((sum, item) => sum + item.share, 0) || 1;
  const circle = 2 * Math.PI * 53;
  const chart = svg("svg", { viewBox: "0 0 140 140", class: "donut-svg", role: "presentation" });
  chart.append(svg("circle", { cx: 70, cy: 70, r: 53, fill: "none", stroke: "#eef2ed", "stroke-width": 15 }));
  let offset = 0;
  categories.forEach((item, index) => {
    const segment = svg("circle", {
      cx: 70, cy: 70, r: 53, fill: "none", stroke: colors[index % colors.length], "stroke-width": 15,
      "stroke-dasharray": `${item.share / total * circle} ${circle}`,
      "stroke-dashoffset": -offset, transform: "rotate(-90 70 70)",
    });
    const title = svg("title");
    title.textContent = `${item.name}: ${item.share}%`;
    segment.append(title);
    chart.append(segment);
    offset += item.share / total * circle;
    const row = node("div", "category-row");
    const dot = node("i");
    dot.style.backgroundColor = colors[index % colors.length];
    row.append(dot, node("span", "", item.name), node("b", "", `${item.share}%`));
    legend.append(row);
  });
  const center = svg("text", { x: 70, y: 66, "text-anchor": "middle", class: "donut-total" });
  center.textContent = String(categories.length);
  const caption = svg("text", { x: 70, y: 83, "text-anchor": "middle", class: "donut-caption" });
  caption.textContent = "categories";
  chart.append(center, caption);
  host.append(chart);
}

function renderExpiry(rows) {
  $("#expiry-count").textContent = `${rows.length} items`;
  renderCompactList("#expiry-list", rows, "expiry");
}

function renderReorder(rows) {
  $("#reorder-count").textContent = `${rows.length} items`;
  renderCompactList("#reorder-list", rows, "reorder");
}

function renderMargins(rows) {
  $("#margin-count").textContent = `${rows.length} items`;
  renderCompactList("#margin-list", rows, "margin");
}

function renderInventory(products, total) {
  const body = $("#inventory-body");
  body.replaceChildren();
  $("#inventory-total").textContent = `${count(total)} products`;
  $("#inventory-footer").textContent = `Showing ${count(products.length)} of ${count(total)} products · Stock values are illustrative`;
  if (!products.length) {
    const row = document.createElement("tr");
    const cell = node("td", "loading", "No products match. Try another search.");
    cell.colSpan = 7;
    row.append(cell);
    body.append(row);
    return;
  }
  products.slice(0, 14).forEach((product) => {
    const row = document.createElement("tr");
    const nameCell = document.createElement("td");
    const info = node("span", "sku-name");
    info.append(node("strong", "", product.name), node("small", "", product.sku));
    nameCell.append(info);
    const category = node("td", "", product.category);
    const stockCell = document.createElement("td");
    const rate = product.demand || 1;
    const cover = product.stock / rate;
    const badge = node("span", `stock-badge${cover < product.lead_days + 1 ? " critical" : cover < product.lead_days + 3 ? " low" : ""}`, `${count(product.stock)} units`);
    stockCell.append(badge);
    const price = node("td", "", inr(product.price));
    const cost = node("td", "", inr(product.cost));
    const supplier = node("td", "", product.supplier);
    let note = "In good shape";
    if (product.tag === "cost-up") note = "Supplier cost changed";
    else if (product.tag === "dead") note = "Slow-moving stock";
    else if (product.tag === "overstock") note = "Overstocked";
    else if (product.tag === "expiry") note = "Expiry watch";
    else if (cover < product.lead_days + 1) note = "Reorder soon";
    const noteCell = node("td", `product-note${product.tag === "expiry" || product.tag === "dead" ? " note-alert" : ""}`, note);
    row.append(nameCell, category, stockCell, price, cost, supplier, noteCell);
    body.append(row);
  });
}

function renderPeople(data) {
  $("#lapsed-count").textContent = count(data.customers_lapsed);
  $("#winback-estimate").textContent = `~${inr(data.totals.average_bill * 3)}`;
  const avatars = $("#customer-avatars");
  avatars.replaceChildren();
  data.winback_names.slice(0, 3).forEach((name) => {
    avatars.append(node("span", "customer-avatar", name.split(" ").map((part) => part[0]).join("")));
  });
  const host = $("#bundle-list");
  host.replaceChildren();
  data.bundle_ideas.forEach((idea) => {
    const chip = node("div", "bundle-chip");
    chip.append(node("span", "", idea.items), node("b", "", idea.lift));
    host.append(chip);
  });
}

function renderDashboard(data) {
  renderKpis(data.kpis);
  renderTrend(data.trend);
  renderActions(data.actions);
  renderCategories(data.categories);
  renderExpiry(data.expiry);
  renderReorder(data.reorder);
  renderMargins(data.margin_alerts);
  renderProducts(data.top_products);
  renderPeople(data);
  const hour = data.peak_hour;
  $("#peak-hour").textContent = `${hour % 12 || 12}:00 ${hour >= 12 ? "pm" : "am"}`;
}

let requestId = 0;
async function loadDashboard() {
  const id = ++requestId;
  $("#status-message").textContent = "Putting your shop's numbers together…";
  try {
    const response = await fetch(`/api/dashboard?days=${encodeURIComponent($("#period-select").value)}`);
    const data = await response.json();
    if (id !== requestId) return;
    if (!response.ok) throw new Error(data.error || "Couldn't load the shop summary.");
    renderDashboard(data);
    $("#status-message").textContent = "";
  } catch (error) {
    if (id === requestId) $("#status-message").textContent = error.message;
  }
}

let inventoryRequestId = 0;
async function loadInventory() {
  const id = ++inventoryRequestId;
  const params = new URLSearchParams({
    category: $("#category-filter").value,
    q: $("#inventory-search").value.trim(),
  });
  try {
    const response = await fetch(`/api/inventory?${params}`);
    const data = await response.json();
    if (id !== inventoryRequestId) return;
    if (!response.ok) throw new Error(data.error || "Couldn't load the shelf list.");
    renderInventory(data.products, data.count);
  } catch (error) {
    $("#inventory-footer").textContent = error.message;
  }
}

function formatToday() {
  $("#today-label").textContent = new Date(`${window.SHOP_TODAY}T12:00:00`).toLocaleDateString("en-IN", {
    weekday: "short", day: "numeric", month: "short", year: "numeric",
  });
}

async function downloadSheet() {
  const button = $("#export-button");
  button.disabled = true;
  $("#status-message").textContent = "Making your shop sheet…";
  try {
    const response = await fetch(`/api/export?days=${encodeURIComponent($("#period-select").value)}`);
    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.error || "Couldn't prepare the sheet.");
    }
    const link = document.createElement("a");
    link.href = URL.createObjectURL(await response.blob());
    link.download = "shoppilot-daily-action-sheet.csv";
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    $("#status-message").textContent = "Your ShopPilot sheet is ready.";
  } catch (error) {
    $("#status-message").textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

$("#period-select").addEventListener("change", loadDashboard);
$("#category-filter").addEventListener("change", loadInventory);
$("#inventory-search").addEventListener("input", loadInventory);
$("#export-button").addEventListener("click", downloadSheet);
$("#reorder-export").addEventListener("click", downloadSheet);
window.addEventListener("resize", () => loadDashboard());
formatToday();
loadDashboard();
loadInventory();
