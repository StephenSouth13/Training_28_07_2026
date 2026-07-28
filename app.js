/* ==========================================================================
   UEH Advanced Data Analytics Portal - Dynamic Application Controller
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Global state
  let diabetesStats = null;
  let wineStatsRed = null;
  let wineStatsWhite = null;
  let currentWineMatrix = "red"; // 'red' or 'white'

  // Tab Navigation Controls
  const btnDiabetes = document.getElementById("btn-tab-diabetes");
  const btnWine = document.getElementById("btn-tab-wine");
  const btnSql = document.getElementById("btn-tab-sql");

  const secDiabetes = document.getElementById("section-diabetes");
  const secWine = document.getElementById("section-wine");
  const secSql = document.getElementById("section-sql");

  function switchTab(activeBtn, activeSec, activeClass) {
    [btnDiabetes, btnWine, btnSql].forEach(btn => {
      btn.className = "nav-btn";
    });
    [secDiabetes, secWine, secSql].forEach(sec => {
      sec.classList.add("hidden");
    });

    activeBtn.classList.add(activeClass);
    activeSec.classList.remove("hidden");
  }

  btnDiabetes.addEventListener("click", () => switchTab(btnDiabetes, secDiabetes, "active-diabetes"));
  btnWine.addEventListener("click", () => switchTab(btnWine, secWine, "active-wine"));
  btnSql.addEventListener("click", () => switchTab(btnSql, secSql, "active-sql"));

  // Fetch and Load All Data Artifacts
  async function loadData() {
    try {
      const [
        resDiabKpis, resDiabBivariate, resDiabAge, resDiabStats, resDiabGlucose,
        resWineKpis, resWineBivariate, resWineRed, resWineWhite,
        resSqlSchema, resSqlQueries
      ] = await Promise.all([
        fetch("data/diabetes_kpis.json").then(r => r.json()),
        fetch("data/diabetes_bivariate.json").then(r => r.json()),
        fetch("data/diabetes_age_dist.json").then(r => r.json()),
        fetch("data/diabetes_stats.json").then(r => r.json()),
        fetch("data/diabetes_univariate_glucose.json").then(r => r.json()),
        fetch("data/wine_kpis.json").then(r => r.json()),
        fetch("data/wine_bivariate.json").then(r => r.json()),
        fetch("data/wine_stats_red.json").then(r => r.json()),
        fetch("data/wine_stats_white.json").then(r => r.json()),
        fetch("sql/schema.sql").then(r => r.text()),
        fetch("sql/analytical_queries.sql").then(r => r.text())
      ]);

      diabetesStats = resDiabStats;
      wineStatsRed = resWineRed;
      wineStatsWhite = resWineWhite;

      // Update Diabetes KPIs
      document.getElementById("diab-kpi-patients").textContent = `${resDiabKpis.total_patients} bệnh nhân`;
      document.getElementById("diab-kpi-rate").textContent = `${resDiabKpis.diabetes_rate}%`;
      document.getElementById("diab-kpi-cases").textContent = `Dương tính: ${resDiabKpis.diabetic_cases} ca`;
      document.getElementById("diab-kpi-glucose").textContent = `${resDiabKpis.avg_glucose} mg/dL`;
      document.getElementById("diab-kpi-bmi").textContent = `${resDiabKpis.avg_bmi} kg/m²`;

      // Render Diabetes Charts
      renderDiabetesUnivariateChart(resDiabGlucose);
      renderDiabetesBivariateChart(resDiabBivariate);
      renderDiabetesAgeChart(resDiabAge);

      // Populate Diabetes Stats Table
      populateTable("table-diabetes-stats", resDiabStats);

      // Update Wine KPIs
      document.getElementById("wine-kpi-red").textContent = `${resWineKpis.total_red_samples.toLocaleString()} records`;
      document.getElementById("wine-kpi-white").textContent = `${resWineKpis.total_white_samples.toLocaleString()} records`;
      document.getElementById("wine-kpi-red-q").textContent = `${resWineKpis.avg_red_quality} ⭐`;
      document.getElementById("wine-kpi-white-q").textContent = `${resWineKpis.avg_white_quality} ⭐`;

      // Render Wine Trend Chart
      renderWineTrendChart(resWineBivariate);

      // Populate Wine Stats Table
      populateTable("table-wine-stats", resWineRed);

      // Populate SQL Viewer
      document.getElementById("sql-schema-code").textContent = resSqlSchema;
      document.getElementById("sql-analytical-code").textContent = resSqlQueries;

    } catch (err) {
      console.error("Error loading dashboard data:", err);
    }
  }

  // --- CHART RENDERING FUNCTIONS --- //

  // 1. Diabetes Glucose Univariate Curve Chart
  function renderDiabetesUnivariateChart(data) {
    const ctx = document.getElementById("chart-diabetes-univariate").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map(d => d.range),
        datasets: [{
          label: "Mật độ mẫu",
          data: data.map(d => d["Mật độ mẫu"]),
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.15)",
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: "#3b82f6"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { backgroundColor: "#0f172a", borderColor: "#334155", borderWidth: 1 }
        },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } }
        }
      }
    });
  }

  // 2. Diabetes Bivariate Health Metrics Grouped Bar Chart
  function renderDiabetesBivariateChart(data) {
    const healthy = data.find(d => d.Outcome === 0) || {};
    const diabetic = data.find(d => d.Outcome === 1) || {};
    
    const ctx = document.getElementById("chart-diabetes-bivariate").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Glucose", "Huyết áp", "BMI"],
        datasets: [
          {
            label: "Khỏe mạnh",
            data: [healthy.Glucose || 0, healthy.BloodPressure || 0, healthy.BMI || 0],
            backgroundColor: "#10b981",
            borderRadius: 4
          },
          {
            label: "Tiểu đường",
            data: [diabetic.Glucose || 0, diabetic.BloodPressure || 0, diabetic.BMI || 0],
            backgroundColor: "#f43f5e",
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { family: "JetBrains Mono", size: 11 } } },
          tooltip: { backgroundColor: "#0f172a", borderColor: "#334155", borderWidth: 1 }
        },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } }
        }
      }
    });
  }

  // 3. Diabetes Age Group Stacked Bar Chart
  function renderDiabetesAgeChart(data) {
    const ctx = document.getElementById("chart-diabetes-age").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: data.map(d => d.AgeGroup),
        datasets: [
          {
            label: "Khỏe mạnh",
            data: data.map(d => d.Healthy),
            backgroundColor: "#3b82f6",
            stack: "Stack 0"
          },
          {
            label: "Tiểu đường",
            data: data.map(d => d.Diabetic),
            backgroundColor: "#f59e0b",
            stack: "Stack 0"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { family: "JetBrains Mono", size: 11 } } },
          tooltip: { backgroundColor: "#0f172a", borderColor: "#334155", borderWidth: 1 }
        },
        scales: {
          x: { stacked: true, grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } },
          y: { stacked: true, grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } }
        }
      }
    });
  }

  // 4. Wine Alcohol vs Quality Dual Trend Line Chart
  function renderWineTrendChart(data) {
    const ctx = document.getElementById("chart-wine-trend").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map(d => d.quality),
        datasets: [
          {
            label: "Rượu đỏ (Alcohol)",
            data: data.map(d => d["Rượu đỏ (Alcohol)"]),
            borderColor: "#f43f5e",
            backgroundColor: "#f43f5e",
            tension: 0.3,
            borderWidth: 3,
            pointRadius: 5
          },
          {
            label: "Rượu trắng (Alcohol)",
            data: data.map(d => d["Rượu trắng (Alcohol)"]),
            borderColor: "#f59e0b",
            backgroundColor: "#f59e0b",
            tension: 0.3,
            borderWidth: 3,
            pointRadius: 5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#94a3b8", font: { family: "JetBrains Mono", size: 11 } } },
          tooltip: { backgroundColor: "#0f172a", borderColor: "#334155", borderWidth: 1 }
        },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } }
        }
      }
    });
  }

  // Populate Summary Statistics Matrix Table
  function populateTable(tableId, statsObj) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody || !statsObj) return;

    tbody.innerHTML = "";
    Object.keys(statsObj).forEach(feature => {
      const row = statsObj[feature];
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td style="font-weight: 700; color: #f8fafc; font-family: var(--font-sans);">${feature}</td>
        <td class="cell-highlight-blue">${row.mean}</td>
        <td style="color: #e2e8f0;">${row.median}</td>
        <td style="color: #94a3b8;">${row.mode}</td>
        <td style="color: #64748b;">${row.variance}</td>
        <td style="color: #94a3b8;">${row.std_dev}</td>
        <td class="cell-highlight-emerald">${row.min}</td>
        <td style="color: #818cf8; font-weight: 600;">${row.q1}</td>
        <td style="color: #c084fc; font-weight: 600;">${row.q3}</td>
        <td class="cell-highlight-rose">${row.max}</td>
        <td class="cell-highlight-amber">${row.iqr}</td>
        <td style="color: #e2e8f0;">${row.skewness}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Wine Table Matrix Sub-Switch Controls
  const btnWineRed = document.getElementById("btn-wine-matrix-red");
  const btnWineWhite = document.getElementById("btn-wine-matrix-white");

  if (btnWineRed && btnWineWhite) {
    btnWineRed.addEventListener("click", () => {
      btnWineRed.classList.add("active");
      btnWineWhite.classList.remove("active");
      currentWineMatrix = "red";
      if (wineStatsRed) populateTable("table-wine-stats", wineStatsRed);
    });

    btnWineWhite.addEventListener("click", () => {
      btnWineWhite.classList.add("active");
      btnWineRed.classList.remove("active");
      currentWineMatrix = "white";
      if (wineStatsWhite) populateTable("table-wine-stats", wineStatsWhite);
    });
  }

  // Search Table Filter
  const searchInput = document.getElementById("search-diabetes-table");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const term = e.target.value.toLowerCase();
      const rows = document.querySelectorAll("#table-diabetes-stats tbody tr");
      rows.forEach(r => {
        const text = r.children[0].textContent.toLowerCase();
        r.style.display = text.includes(term) ? "" : "none";
      });
    });
  }

  // Initial Data Load
  loadData();
});
