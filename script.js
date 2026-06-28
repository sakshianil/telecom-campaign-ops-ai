const fallbackRows = [
  ["TL-001", "Maribel Santos", "Small Business", "Manila", "Business Fiber", "118", "2", "820", "3", "Low", "18", "Email", "Contract ending soon", "66", "High", "Plan upgrade: Email value bundle, then phone follow-up"],
  ["TL-003", "Luz Mendoza", "Residential", "Davao", "Home Broadband", "52", "1", "410", "4", "Medium", "9", "Phone", "Repeated complaints", "80", "High", "Retention rescue: Priority phone call with service recovery offer"],
  ["TL-006", "Nestor Garcia", "Enterprise", "Manila", "Business Fiber", "310", "3", "2100", "5", "Low", "6", "Phone", "High value at risk", "66", "High", "Plan upgrade: Email value bundle, then phone follow-up"],
  ["TL-014", "Jose Mercado", "Small Business", "Manila", "VoIP Bundle", "103", "0", "310", "4", "High", "3", "Phone", "Contract expired", "92", "High", "Retention rescue: Priority phone call with service recovery offer"],
  ["TL-020", "Joel Pascual", "Small Business", "Iloilo", "Business Fiber", "130", "6", "980", "0", "Low", "48", "Email", "Expansion prospect", "84", "High", "Plan upgrade: Email value bundle, then phone follow-up"]
];

const headers = [
  "lead_id",
  "customer_name",
  "segment",
  "region",
  "service_type",
  "monthly_spend_usd",
  "contract_months_remaining",
  "data_usage_gb",
  "support_tickets_90d",
  "payment_risk",
  "last_contact_days",
  "preferred_channel",
  "current_status",
  "campaign_score",
  "priority",
  "recommended_action"
];

function toObjects(rows) {
  return rows.map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index]])));
}

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const [headerLine, ...body] = lines;
  const parseLine = (line) => {
    const values = [];
    let value = "";
    let insideQuotes = false;

    for (const char of line) {
      if (char === '"') {
        insideQuotes = !insideQuotes;
      } else if (char === "," && !insideQuotes) {
        values.push(value);
        value = "";
      } else {
        value += char;
      }
    }

    values.push(value);
    return values;
  };

  const parsedHeaders = parseLine(headerLine);
  return body.map((line) => {
    const values = parseLine(line);
    return Object.fromEntries(parsedHeaders.map((header, index) => [header, values[index] || ""]));
  });
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value;
  }
}

function campaignName(action) {
  return action.split(":")[0];
}

function renderMetrics(rows) {
  const high = rows.filter((row) => row.priority === "High").length;
  const business = rows.filter((row) => ["Small Business", "Enterprise"].includes(row.segment)).length;
  const avg = Math.round(rows.reduce((sum, row) => sum + Number(row.campaign_score), 0) / rows.length);

  setText("totalLeads", rows.length);
  setText("highPriority", high);
  setText("businessAccounts", business);
  setText("avgScore", avg);
}

function renderQueue(rows) {
  const container = document.getElementById("priorityQueue");
  const topRows = [...rows].sort((a, b) => Number(b.campaign_score) - Number(a.campaign_score)).slice(0, 6);
  container.innerHTML = topRows.map((row) => `
    <article class="queue-item">
      <span class="score">${row.campaign_score}</span>
      <div>
        <strong>${row.customer_name}</strong>
        <p>${row.segment} | ${row.service_type} | ${row.region}</p>
      </div>
      <span class="badge">${row.priority}</span>
    </article>
  `).join("");
}

function renderMix(rows) {
  const container = document.getElementById("campaignMix");
  const counts = rows.reduce((acc, row) => {
    const key = campaignName(row.recommended_action);
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const max = Math.max(...Object.values(counts));

  container.innerHTML = Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => `
      <div class="mix-item">
        <div class="mix-row">
          <span>${name}</span>
          <span>${count}</span>
        </div>
        <div class="bar" aria-hidden="true"><span style="width:${Math.max(12, (count / max) * 100)}%"></span></div>
      </div>
    `).join("");
}

function renderTable(rows) {
  const body = document.getElementById("leadRows");
  body.innerHTML = rows
    .sort((a, b) => Number(b.campaign_score) - Number(a.campaign_score))
    .slice(0, 12)
    .map((row) => `
      <tr>
        <td><strong>${row.lead_id}</strong><br>${row.customer_name}</td>
        <td>${row.segment}<br>${row.region}</td>
        <td>${row.service_type}</td>
        <td><span class="badge">${row.priority}</span></td>
        <td>${row.recommended_action}</td>
      </tr>
    `).join("");
}

function render(rows) {
  renderMetrics(rows);
  renderQueue(rows);
  renderMix(rows);
  renderTable(rows);
}

fetch("data/campaign_segments.csv")
  .then((response) => {
    if (!response.ok) {
      throw new Error("Segment file not available");
    }
    return response.text();
  })
  .then((text) => render(parseCsv(text)))
  .catch(() => render(toObjects(fallbackRows)));
