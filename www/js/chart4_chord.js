// Acknowledgments: I used ChatGPT to ask for examples of Chord diagrams, labels, ticks and how to link the dropdown to the chart. 
// Global chord data (for all modes & dates)
let chordDataAll = null;

// Load real data once
const chordDataPromise = d3
  .json("data/chart4_chord_all.json")
  .then(d => {
    chordDataAll = d;
    return d;
  });

function updateCountryOptions(selectEl, nodes) {
  if (!selectEl) return;
  const prev = selectEl.value || "all";
  selectEl.innerHTML = "";

  const allOpt = document.createElement("option");
  allOpt.value = "all";
  allOpt.textContent = "All countries";
  selectEl.appendChild(allOpt);

  nodes
    .slice()
    .sort((a, b) => a.localeCompare(b))
    .forEach(name => {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      selectEl.appendChild(opt);
    });

  if ([...selectEl.options].some(o => o.value === prev)) {
    selectEl.value = prev;
  } else {
    selectEl.value = "all";
  }
}

async function renderChordChart(
  selectedCountry = "all",
  focus = "all",
  mode = "region_region",
  dateKey = null
) {
  const container = d3.select("#chart4-container");
  container.selectAll("*").remove(); // clear previous chart

  const width = 600;
  const height = 600;
  const innerRadius = Math.min(width, height) * 0.35;
  const outerRadius = innerRadius + 10;

  const svg = container
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("preserveAspectRatio", "xMidYMid meet")
    .append("g")
    .attr("transform", `translate(${width / 2},${height / 2})`);

  // --- Load real data ---
  const data = chordDataAll || (await chordDataPromise);

  const modeData = data.modes[mode];

  // If no dateKey is provided, use first available date in that mode
  if (!dateKey) {
    dateKey = modeData.dates[0];
  }

  const nodes = modeData.nodes;
  const matrix = modeData.matrices[dateKey];
  const sourceTotals = matrix.map(row => d3.sum(row));
  const formatTn = d3.format(",.2f");


  // --- Chord layout ---
  const chord = d3.chordDirected()
    .padAngle(0.05)
    .sortSubgroups(d3.descending)(matrix);

  const arc = d3.arc()
    .innerRadius(innerRadius)
    .outerRadius(outerRadius);

  const ribbon = d3.ribbonArrow()
    .radius(innerRadius)
    .padAngle(1 / innerRadius);

  const color = d3.scaleOrdinal()
    .domain(d3.range(nodes.length))
    .range(d3.schemeTableau10);


  const group = svg.append("g")
    .attr("class", "groups")
    .selectAll("g")
    .data(chord.groups)
    .join("g");

  let selectedIndex =
    selectedCountry === "all" ? null : nodes.indexOf(selectedCountry);
  if (selectedIndex === -1) {
    selectedIndex = null;
  }

  group.append("path")
    .attr("d", arc)
    .attr("fill", d => color(d.index))
    .attr("stroke", d => d3.color(color(d.index)).darker(0.5))
    .style("opacity", d =>
      selectedIndex === null || d.index === selectedIndex ? 1 : 0.45
    );

  group.append("text")
    .each(d => { d.angle = (d.startAngle + d.endAngle) / 2; })
    .attr("dy", "0.35em")
    .attr("transform", d => `
      rotate(${(d.angle * 180) / Math.PI - 90})
      translate(${outerRadius + 5})
      ${d.angle > Math.PI ? "rotate(180)" : ""}
    `)
    .style("font-size", "11px")
    .style("text-anchor", d => (d.angle > Math.PI ? "end" : "start"))
    .text(d => nodes[d.index]);


  svg.append("g")
    .attr("class", "ribbons")
    .selectAll("path")
    .data(chord)
    .join("path")
    .attr("d", ribbon)
    .attr("fill", d => color(d.source.index))
    .attr("stroke", d => d3.color(color(d.source.index)).darker(0.6))
    .style("opacity", d => {
      if (selectedIndex === null) return 0.9;
      return d.source.index === selectedIndex ||
        d.target.index === selectedIndex
        ? 1
        : 0.12;
    })
    .append("title")
    .text(d => {
      const from = nodes[d.source.index];
      const to = nodes[d.target.index];
      const value = d.source.value;
      const total = sourceTotals[d.source.index] || 0;
      const pct = total ? ((value / total) * 100).toFixed(1) : "0.0";
      return `${from} → ${to}: ${formatTn(value.toLocaleString())} USD tn (${pct}% of ${from})`;
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const modeSelect = document.getElementById("c4-mode-select");
  const countrySelect = document.getElementById("c4-country-select");
  const focusSelect = document.getElementById("c4-focus-select");
  const dateSlider = document.getElementById("c4-date-slider");
  const dateLabel = document.getElementById("c4-date-label");
  const dateStartLabel = document.getElementById("c4-date-start");
  const dateEndLabel = document.getElementById("c4-date-end");

  function syncDateControls(modeData) {
    if (!dateSlider || !modeData?.dates?.length) return;
    dateSlider.min = 0;
    dateSlider.max = modeData.dates.length - 1;
    if (Number(dateSlider.value) > Number(dateSlider.max)) {
      dateSlider.value = dateSlider.max;
    }
    const idx = Number(dateSlider.value);
    const dateStr = modeData.dates[idx] || modeData.dates[modeData.dates.length - 1];
    if (dateLabel) {
      dateLabel.textContent = dateStr;
    }
    if (dateStartLabel) {
      dateStartLabel.textContent = modeData.dates[0] || "";
    }
    if (dateEndLabel) {
      dateEndLabel.textContent =
        modeData.dates[modeData.dates.length - 1] || "";
    }
    return { index: idx, dateKey: dateStr };
  }

  async function updateChart() {
    const mode = modeSelect ? modeSelect.value : "region_region";
    const focus = focusSelect ? focusSelect.value : "all";

    const data = chordDataAll || (await chordDataPromise);
    const modeData = data.modes[mode];
    if (!modeData) {
      console.warn("Mode not found in chord data:", mode);
      return;
    }

    updateCountryOptions(countrySelect, modeData.nodes);
    const selectedCountry = countrySelect ? countrySelect.value : "all";

    const dateMeta = syncDateControls(modeData);
    const dateKey = dateMeta?.dateKey || (modeData.dates ? modeData.dates[modeData.dates.length - 1] : null);

    await renderChordChart(selectedCountry, focus, mode, dateKey);
  }

  modeSelect?.addEventListener("change", updateChart);
  countrySelect?.addEventListener("change", updateChart);
  focusSelect?.addEventListener("change", updateChart);
  dateSlider?.addEventListener("input", updateChart);

  updateChart();
});
