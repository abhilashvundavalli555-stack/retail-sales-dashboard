const $ = (selector) => document.querySelector(selector);
const money = (value) => new Intl.NumberFormat("en-US", {
  style: "currency", currency: "USD", maximumFractionDigits: 0,
}).format(value);
const compactMoney = (value) => {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}m`;
  if (value >= 10_000) return `$${(value / 1_000).toFixed(0)}k`;
  return money(value);
};
const number = (value) => new Intl.NumberFormat("en-US").format(value);
const palette = ["#ed7860", "#8c75e8", "#79a4d5", "#72b99f"];

function svgElement(name, attributes = {}) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  return node;
}

function drawTrend(items) {
  const host = $("#trend-chart");
  host.replaceChildren();
  if (!items.length) return;
  const width = Math.max(host.clientWidth || 500, items.length * 38);
  const height = 220;
  const padding = { top: 12, right: 12, bottom: 32, left: 52 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const max = Math.max(...items.flatMap((item) => [item.sales, item.profit]), 1) * 1.16;
  const svg = svgElement("svg", {
    viewBox: `0 0 ${width} ${height}`, role: "presentation",
    preserveAspectRatio: "none", class: "trend-svg",
  });
  for (let index = 0; index <= 4; index += 1) {
    const y = padding.top + plotHeight * index / 4;
    const line = svgElement("line", { x1: padding.left, y1: y, x2: width - padding.right, y2: y, class: "grid-line" });
    const label = svgElement("text", { x: padding.left - 9, y: y + 4, "text-anchor": "end", class: "axis-label" });
    label.textContent = compactMoney(max * (4 - index) / 4);
    svg.append(line, label);
  }
  const pointFor = (value, index) => ({
    x: padding.left + plotWidth * (items.length === 1 ? 0.5 : index / (items.length - 1)),
    y: padding.top + plotHeight * (1 - value / max),
  });
  for (const [key, color, className] of [["sales", "#ed7860", "line-sales"], ["profit", "#8c75e8", "line-profit"]]) {
    const points = items.map((item, index) => pointFor(item[key], index));
    const path = svgElement("path", {
      d: points.map((point, index) => `${index ? "L" : "M"} ${point.x} ${point.y}`).join(" "),
      fill: "none", stroke: color, "stroke-width": key === "sales" ? 3 : 2,
      "stroke-linecap": "round", "stroke-linejoin": "round", class: className,
    });
    svg.append(path);
    points.forEach((point, index) => {
      const circle = svgElement("circle", {
        cx: point.x, cy: point.y, r: key === "sales" ? 3.5 : 2.5,
        fill: color, class: "trend-point",
      });
      const title = svgElement("title");
      title.textContent = `${items[index].month}: ${key} ${money(items[index][key])}`;
      circle.append(title);
      svg.append(circle);
    });
  }
  items.forEach((item, index) => {
    const point = pointFor(0, index);
    const label = svgElement("text", {
      x: point.x, y: height - 8, "text-anchor": "middle", class: "axis-label month-label",
    });
    label.textContent = new Date(`${item.month}-15T12:00:00`).toLocaleDateString("en-US", { month: "short" });
    svg.append(label);
  });
  host.append(svg);
}

function drawCategories(categories) {
  const chart = $("#category-chart");
  const legend = $("#category-legend");
  chart.replaceChildren();
  legend.replaceChildren();
  const total = categories.reduce((sum, item) => sum + item.sales, 0);
  if (!total) return;
  const svg = svgElement("svg", { viewBox: "0 0 160 160", class: "donut-svg", role: "presentation" });
  const background = svgElement("circle", { cx: 80, cy: 80, r: 60, fill: "none", stroke: "#eef2ef", "stroke-width": 17 });
  svg.append(background);
  let offset = 0;
  const circumference = 2 * Math.PI * 60;
  categories.forEach((item, index) => {
    const share = item.sales / total;
    const circle = svgElement("circle", {
      cx: 80, cy: 80, r: 60, fill: "none", stroke: palette[index % palette.length],
      "stroke-width": 17, "stroke-dasharray": `${share * circumference} ${circumference}`,
      "stroke-dashoffset": -offset, transform: "rotate(-90 80 80)", class: "donut-segment",
    });
    const title = svgElement("title");
    title.textContent = `${item.name}: ${money(item.sales)} (${(share * 100).toFixed(1)}%)`;
    circle.append(title);
    svg.append(circle);
    offset += share * circumference;

    const entry = document.createElement("div");
    entry.className = "legend-entry";
    const dot = document.createElement("i");
    dot.style.backgroundColor = palette[index % palette.length];
    const label = document.createElement("span");
    label.textContent = item.name;
    const amount = document.createElement("strong");
    amount.textContent = `${(share * 100).toFixed(0)}%`;
    entry.append(dot, label, amount);
    legend.append(entry);
  });
  const center = svgElement("text", { x: 80, y: 76, "text-anchor": "middle", class: "donut-total" });
  center.textContent = categories.length.toString();
  const caption = svgElement("text", { x: 80, y: 94, "text-anchor": "middle", class: "donut-caption" });
  caption.textContent = "categories";
  svg.append(center, caption);
  chart.append(svg);
}

function renderRegions(regions) {
  const host = $("#region-list");
  host.replaceChildren();
  const max = Math.max(...regions.map((item) => item.sales), 1);
  regions.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "region-row";
    const top = document.createElement("div");
    top.className = "region-top";
    const name = document.createElement("span");
    name.textContent = item.name;
    const amount = document.createElement("strong");
    amount.textContent = money(item.sales);
    top.append(name, amount);
    const track = document.createElement("div");
    track.className = "progress-track";
    const fill = document.createElement("span");
    fill.style.width = `${item.sales / max * 100}%`;
    fill.style.backgroundColor = palette[index % palette.length];
    track.append(fill);
    row.append(top, track);
    host.append(row);
  });
}

function renderProducts(products) {
  const host = $("#product-list");
  host.replaceChildren();
  products.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "product-row";
    const rank = document.createElement("span");
    rank.className = "product-rank";
    rank.textContent = String(index + 1).padStart(2, "0");
    const info = document.createElement("span");
    info.className = "product-info";
    const name = document.createElement("strong");
    name.textContent = item.name;
    const details = document.createElement("small");
    details.textContent = `${item.units} units sold`;
    info.append(name, details);
    const amount = document.createElement("strong");
    amount.className = "product-sales";
    amount.textContent = money(item.sales);
    row.append(rank, info, amount);
    host.append(row);
  });
}

function renderOrders(transactions, count) {
  const body = $("#orders-body");
  body.replaceChildren();
  $("#order-count").textContent = `${number(count)} orders`;
  $("#table-caption").textContent = `Showing ${transactions.length} of ${number(count)} fictional orders`;
  transactions.forEach((order) => {
    const row = document.createElement("tr");
    const values = [
      [order.order_id, "order-id"], [order.product, "product-cell"],
      [order.category, "category-pill"], [order.region, "region-cell"],
      [new Date(`${order.date}T12:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }), "date-cell"],
      [money(order.sales), "amount-cell align-right"],
    ];
    values.forEach(([text, className]) => {
      const cell = document.createElement("td");
      cell.className = className;
      cell.textContent = text;
      row.append(cell);
    });
    body.append(row);
  });
}

function updateDashboard(data) {
  $("#kpi-sales").textContent = money(data.kpis.sales);
  $("#kpi-profit").textContent = money(data.kpis.profit);
  $("#kpi-margin").textContent = `${data.kpis.margin}%`;
  $("#kpi-orders").textContent = number(data.kpis.orders);
  $("#kpi-units").textContent = number(data.kpis.units);
  $("#kpi-average").textContent = money(data.kpis.average_order);
  const months = data.monthly;
  $("#trend-range").firstChild.textContent = months.length
    ? `${new Date(`${months[0].month}-15T12:00:00`).toLocaleDateString("en-US", { month: "short", year: "numeric" })} – ${new Date(`${months[months.length - 1].month}-15T12:00:00`).toLocaleDateString("en-US", { month: "short", year: "numeric" })}`
    : "Selected period";
  drawTrend(months);
  drawCategories(data.categories);
  renderRegions(data.regions);
  renderProducts(data.products);
  renderOrders(data.transactions, data.count);
}

let requestNumber = 0;
async function loadDashboard() {
  const currentRequest = ++requestNumber;
  const params = new URLSearchParams();
  [["start", $("#start-date").value], ["end", $("#end-date").value],
    ["region", $("#region-filter").value], ["category", $("#category-filter").value]]
    .forEach(([key, value]) => { if (value) params.set(key, value); });
  $("#status-message").textContent = "Updating your dashboard…";
  try {
    const response = await fetch(`/api/dashboard?${params}`);
    const data = await response.json();
    if (currentRequest !== requestNumber) return;
    if (!response.ok) throw new Error(data.error || "Could not load dashboard data.");
    updateDashboard(data);
    $("#status-message").textContent = "";
  } catch (error) {
    if (currentRequest === requestNumber) $("#status-message").textContent = error.message;
  }
}

["#start-date", "#end-date", "#region-filter", "#category-filter"]
  .forEach((selector) => $(selector).addEventListener("change", loadDashboard));
$("#reset-filters").addEventListener("click", () => {
  $("#start-date").value = $("#start-date").min;
  $("#end-date").value = $("#end-date").max;
  $("#region-filter").value = "";
  $("#category-filter").value = "";
  loadDashboard();
});
$("#export-button").addEventListener("click", async () => {
  const params = new URLSearchParams({
    start: $("#start-date").value,
    end: $("#end-date").value,
    region: $("#region-filter").value,
    category: $("#category-filter").value,
  });
  $("#status-message").textContent = "Preparing your filtered CSV report…";
  try {
    const response = await fetch(`/api/export?${params}`);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || "Could not export this report.");
    }
    const link = document.createElement("a");
    link.href = URL.createObjectURL(await response.blob());
    link.download = "northstar-retail-summary.csv";
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
    $("#status-message").textContent = "Your filtered CSV report is downloading.";
  } catch (error) {
    $("#status-message").textContent = error.message || "Could not export this report.";
  }
});
window.addEventListener("resize", () => loadDashboard());
loadDashboard();
