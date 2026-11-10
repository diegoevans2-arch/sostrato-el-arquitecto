// ---------- estado común de la simulación de alertas (A1–A4). Lo controla la demo por postMessage o, suelta, la propia vista.
const QS = new URLSearchParams(location.search);
const EMBED = QS.has("embed");
if (EMBED) document.documentElement.classList.add("embed");
const ANIOS = [2027, 2028, 2029, 2030, 2031];
const PERIODOS = [[10, "1.er semestre"], [20, "2.º semestre"], [5, "AV · T1"], [15, "AV · T2"], [25, "AV · T3"]];
const ESCENARIOS = [["bajo", "Bajo"], ["base", "Base"], ["alto", "Alto"]];
const RANGOS_UI = [["todos", "Todos los tamaños"], ["0-20", "0–20"], ["21-40", "21–40"], ["41-60", "41–60"], ["60 o más", "60 o más"]];
const ESTADO = {
  campus: (QS.get("campus") || "TODOS").toUpperCase(),
  anio: +(QS.get("anio") || 2027),
  per: +(QS.get("per") || 10),
  esc: QS.get("esc") || "base",
  rango: QS.get("rango") || "todos",
};
// V1 · semáforo sobre PROB_SATURA_TAMANO (en %): vigilancia ≥ 10, ALERTA ≥ 25 (la que se informa), crítica ≥ 50
const NIVELES = [
  { n: "sin alerta", c: null, i: "" },
  { n: "vigilancia", c: "#fab219", i: "▲" },
  { n: "alerta", c: "#ec835a", i: "◆" },
  { n: "crítica", c: "#d03b3b", i: "●" },
];
const nivel = p => (p >= 50 ? 3 : p >= 25 ? 2 : p >= 10 ? 1 : 0);
const nomPer = per => (PERIODOS.find(p => p[0] === per) || [0, ""])[1];
const clavePer = () => ESTADO.anio * 100 + ESTADO.per;

function avisos() {
  const a = [];
  if (ESTADO.anio === 2031) a.push("2031 es extrapolado: el modelo se validó hasta un horizonte de 4 años.");
  if (ESTADO.anio === 2027 && ESTADO.esc !== "base") a.push("2027 · escenario " + ESTADO.esc + ": banda de Euribia: otra definición, no comparable con 2028–2031 (suma los cuantiles de Euribia por tipo de curso).");
  return a;
}
function pintarAvisos(id = "avisos") {
  const el = document.getElementById(id); if (!el) return;
  el.innerHTML = avisos().map(t => `<span class="aviso-chip">⚠ ${t}</span>`).join("");
}
function alCambiar(render) {
  addEventListener("message", e => { if (e.data && e.data.cirilo) { Object.assign(ESTADO, e.data.estado); render(); } });
  if (!EMBED) montarControles(render);
}
function montarControles(render) {
  const el = document.getElementById("ctl"); if (!el) return;
  const sel = (id, opts, v) => `<select data-k="${id}" class="ctl-sel">${opts.map(([k, t]) => `<option value="${k}"${String(k) === String(v) ? " selected" : ""}>${t}</option>`).join("")}</select>`;
  el.innerHTML = `<span>Año</span>${sel("anio", ANIOS.map(a => [a, a + (a === 2031 ? " (extrap.)" : "")]), ESTADO.anio)}
    <span>Período</span>${sel("per", PERIODOS, ESTADO.per)}<span>Escenario</span>${sel("esc", ESCENARIOS, ESTADO.esc)}
    <span>Tamaño</span>${sel("rango", RANGOS_UI, ESTADO.rango)}`;
  el.querySelectorAll("select").forEach(s => s.onchange = () => {
    const k = s.dataset.k; ESTADO[k] = ["anio", "per"].includes(k) ? +s.value : s.value; render();
  });
}
function tooltip() {
  const tip = document.getElementById("tip");
  return {
    show(ev, html) { tip.innerHTML = html; tip.style.left = Math.min(ev.clientX + 14, innerWidth - 290) + "px"; tip.style.top = ev.clientY + 14 + "px"; tip.style.opacity = 1; },
    hide() { tip.style.opacity = 0; },
  };
}
