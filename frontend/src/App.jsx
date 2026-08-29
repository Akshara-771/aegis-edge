import { useEffect, useMemo, useState } from "react";
import "./App.css";

const initialTelemetry = {
  timestamp: 0, temperature: 0, voltage: 0, rpm: 0,
  fault: "NONE", ml_prediction: "NORMAL", rule_prediction: "NONE",
};

const FAULTS = ["OVERHEAT", "LOW_VOLTAGE", "HIGH_RPM"];

function Sparkline({ data, dataKey }) {
  const values = data.map(x => Number(x[dataKey])).filter(Number.isFinite);
  if (!values.length) return <div className="sparkline-empty">Waiting for telemetry</div>;

  const width = 520, height = 150, pad = 10;
  const min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
  const points = values.map((v, i) => {
    const x = pad + (i / Math.max(values.length - 1, 1)) * (width - pad * 2);
    const y = height - pad - ((v - min) / range) * (height - pad * 2);
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg className="sparkline" viewBox={`0 0 ${width} ${height}`}>
      {[25, 50, 75].map(p => (
        <line key={p} x1={pad} x2={width-pad} y1={height*p/100} y2={height*p/100}
          className="chart-grid-line" />
      ))}
      <polyline points={points} className="chart-line" />
      <circle
        cx={points.split(" ").at(-1).split(",")[0]}
        cy={points.split(" ").at(-1).split(",")[1]}
        r="4" className="chart-point"
      />
    </svg>
  );
}

function FaultBars({ history }) {
  const counts = FAULTS.map(f => history.filter(x => x.fault === f).length);
  const max = Math.max(...counts, 1);
  return (
    <div className="mini-bars">
      {FAULTS.map((fault, i) => (
        <div className="bar-row" key={fault}>
          <span>{fault.replace("_", " ")}</span>
          <div className="bar-track"><div className="bar-fill"
            style={{ width: `${(counts[i] / max) * 100}%` }} /></div>
          <strong>{counts[i]}</strong>
        </div>
      ))}
    </div>
  );
}

function App() {
  const [telemetry, setTelemetry] = useState(initialTelemetry);
  const [connected, setConnected] = useState(false);
  const [history, setHistory] = useState([]);
  const [faultEvents, setFaultEvents] = useState([]);

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws");

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = e => { console.error("WebSocket error:", e); setConnected(false); };

    socket.onmessage = event => {
      const message = JSON.parse(event.data);

      if (message.type === "history") {
        const data = message.data || [];
        if (data.length) {
          setTelemetry(data.at(-1));
          setHistory(data.slice(-30));

          const events = [];
          data.forEach((item, index) => {
            if (item.fault === "NONE") return;
            const previous = data[index - 1];
            if (!previous || previous.fault !== item.fault) {
              events.push({
                timestamp: item.timestamp, fault: item.fault,
                ml: item.ml_prediction, rule: item.rule_prediction,
              });
            }
          });
          setFaultEvents(events.slice(-10).reverse());
        }
        return;
      }

      setTelemetry(message);
      setHistory(previous => [...previous, message].slice(-30));

      if (message.fault !== "NONE") {
        setFaultEvents(previous => {
          const last = previous[0];
          if (!last || last.fault !== message.fault) {
            return [{
              timestamp: message.timestamp, fault: message.fault,
              ml: message.ml_prediction, rule: message.rule_prediction,
            }, ...previous].slice(0, 10);
          }
          return previous;
        });
      }
    };

    return () => socket.close();
  }, []);

  const isFault = telemetry.fault !== "NONE";
  const predictionsAgree =
    telemetry.ml_prediction === telemetry.rule_prediction ||
    (telemetry.ml_prediction === "NORMAL" && telemetry.rule_prediction === "NONE");

  const agreementRate = useMemo(() => {
    if (!history.length) return null;
    const good = history.filter(x =>
      x.ml_prediction === x.rule_prediction ||
      (x.ml_prediction === "NORMAL" && x.rule_prediction === "NONE")
    ).length;
    return Math.round(good / history.length * 100);
  }, [history]);

  const faultSamples = history.filter(x => x.fault !== "NONE").length;
  const clock = telemetry.timestamp
    ? new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    : "--:--:--";

  const metrics = [
    ["TEMPERATURE", Number(telemetry.temperature).toFixed(1), "°C", "Thermal sensor", "pink"],
    ["VOLTAGE", Number(telemetry.voltage).toFixed(2), "V", "Supply monitor", "cyan"],
    ["MOTOR RPM", telemetry.rpm, "", "Motor speed", "violet"],
    ["EDGE TIMESTAMP", telemetry.timestamp, "ms", "Firmware timestamp", "blue"],
  ];

  return (
    <div className="dashboard-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <div><div className="brand-name">AEGIS EDGE</div><div className="brand-subtitle">AI MONITORING</div></div>
        </div>

        <nav className="nav">
          <div className="nav-label">MONITOR</div>
          <a className="nav-item active" href="#dashboard"><span>⌂</span>Dashboard</a>
          <a className="nav-item" href="#sensors"><span>◉</span>Live Sensors</a>
          <a className="nav-item" href="#faults"><span>!</span>Fault Events</a>
          <div className="nav-label second">ANALYSIS</div>
          <a className="nav-item" href="#predictions"><span>◇</span>ML vs Rule</a>
          <a className="nav-item" href="#telemetry"><span>▤</span>Telemetry</a>
          <a className="nav-item" href="#performance"><span>◌</span>Performance</a>
        </nav>

        <div className="sidebar-footer">
          <div className={`system-chip ${connected ? "online" : ""}`}>
            <span className="pulse-dot" />
            <div><strong>{connected ? "SYSTEM ONLINE" : "SYSTEM OFFLINE"}</strong><small>WebSocket telemetry</small></div>
          </div>
          <div className="stack-label">ZEPHYR · TFLM · RENODE</div>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div>
            <div className="eyebrow">EDGE OPERATIONS / REAL-TIME</div>
            <h1>Embedded AI Command Center</h1>
            <p>On-device fault detection and telemetry intelligence</p>
          </div>
          <div className="topbar-meta">
            <div className="clock"><span className="meta-label">LOCAL TIME</span><strong>{clock}</strong></div>
            <div className={`live-pill ${connected ? "connected" : ""}`}><span />{connected ? "LIVE" : "OFFLINE"}</div>
          </div>
        </header>

        <section className={`hero-status ${isFault ? "fault" : ""}`}>
          <div>
            <span className="eyebrow">SYSTEM STATUS</span>
            <h2>{isFault ? "FAULT DETECTED" : "SYSTEM NORMAL"}</h2>
            <p>{isFault
              ? `${telemetry.fault} condition detected by the edge pipeline.`
              : "All monitored conditions are currently within the detected normal state."}</p>
          </div>
          <div className="hero-status-right">
            <span className="status-caption">CURRENT FAULT</span>
            <strong>{telemetry.fault}</strong>
            <span className="status-time">{telemetry.timestamp || "--"} ms</span>
          </div>
        </section>

        <section className="metric-grid" id="sensors">
          {metrics.map(([label, value, unit, meta, tone]) => (
            <article className={`metric-card ${tone}`} key={label}>
              <div className="metric-top"><span className="metric-icon">●</span><span className="metric-label">{label}</span></div>
              <div className="metric-value">{value}<small>{unit}</small></div>
              <div className="metric-meta"><span>{meta}</span><span className="metric-live">● LIVE</span></div>
            </article>
          ))}
        </section>

        <section className="dashboard-grid">
          <article className="panel trends-panel">
            <div className="panel-heading">
              <div><span className="eyebrow">LIVE TELEMETRY</span><h3>Sensor Trends</h3></div>
              <span className="panel-badge">{history.length} samples</span>
            </div>
            <div className="trend-grid">
              {[
                ["Temperature", "temperature", `${Number(telemetry.temperature).toFixed(1)} °C`],
                ["Voltage", "voltage", `${Number(telemetry.voltage).toFixed(2)} V`],
                ["Motor RPM", "rpm", telemetry.rpm],
              ].map(([title, key, value]) => (
                <div className="trend-card" key={key}>
                  <div className="trend-header"><span>{title}</span><strong>{value}</strong></div>
                  <Sparkline data={history} dataKey={key} />
                  <div className="trend-scale"><span>RECENT SAMPLES</span><span>LIVE</span></div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel prediction-panel" id="predictions">
            <div className="panel-heading">
              <div><span className="eyebrow">DECISION ENGINE</span><h3>ML vs Rule</h3></div>
              <span className={`agreement-badge ${predictionsAgree ? "good" : "bad"}`}>
                {predictionsAgree ? "AGREE" : "MISMATCH"}
              </span>
            </div>
            <div className="prediction-stack">
              <div className="prediction-row">
                <div className="prediction-icon ml">AI</div>
                <div><span>ML PREDICTION</span><strong>{telemetry.ml_prediction}</strong></div><small>TFLM</small>
              </div>
              <div className="prediction-row">
                <div className="prediction-icon rule">R</div>
                <div><span>RULE PREDICTION</span><strong>{telemetry.rule_prediction}</strong></div><small>DETERMINISTIC</small>
              </div>
            </div>
            <div className="agreement-meter">
              <div className="meter-header"><span>Current-run agreement</span><strong>{agreementRate == null ? "--" : `${agreementRate}%`}</strong></div>
              <div className="meter-track"><div style={{ width: `${agreementRate ?? 0}%` }} /></div>
              <small>Calculated from telemetry currently held by the dashboard.</small>
            </div>
          </article>
        </section>

        <section className="dashboard-grid lower">
          <article className="panel" id="faults">
            <div className="panel-heading">
              <div><span className="eyebrow">INCIDENTS</span><h3>Fault Distribution</h3></div>
              <span className="panel-badge">{faultSamples} fault samples</span>
            </div>
            <FaultBars history={history} />
          </article>

          <article className="panel performance-panel" id="performance">
            <div className="panel-heading"><div><span className="eyebrow">VERIFIED EMBEDDED METRICS</span><h3>Model Performance</h3></div></div>
            <div className="performance-grid">
              <div><span>TEST ACCURACY</span><strong>98.75%</strong></div>
              <div><span>TFLM MEAN</span><strong>48 µs</strong></div>
              <div><span>INT8 MODEL</span><strong>3.5 KB</strong></div>
              <div><span>LATENCY RANGE</span><strong>40–51 µs</strong></div>
            </div>
          </article>
        </section>

        <section className="panel events-panel" id="telemetry">
          <div className="panel-heading">
            <div><span className="eyebrow">EVENT STREAM</span><h3>Recent Fault Events</h3></div>
            <span className="panel-badge">{faultEvents.length} events</span>
          </div>
          {faultEvents.length === 0 ? (
            <div className="empty-state"><span>✓</span><div><strong>No fault events recorded</strong><small>The edge system has not reported a fault in the current history.</small></div></div>
          ) : (
            <div className="event-table">
              <div className="event-table-header"><span>FAULT</span><span>TIMESTAMP</span><span>ML</span><span>RULE</span><span>RESULT</span></div>
              {faultEvents.map((event, i) => (
                <div className="event-table-row" key={`${event.timestamp}-${i}`}>
                  <span className="fault-name"><i />{event.fault}</span>
                  <span>{event.timestamp} ms</span><span>{event.ml}</span><span>{event.rule}</span>
                  <span className="match">{event.ml === event.rule ? "✓ MATCH" : "⚠ MISMATCH"}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="panel telemetry-panel">
          <div className="panel-heading">
            <div><span className="eyebrow">RAW STREAM</span><h3>Live Telemetry</h3></div>
            <span className="panel-badge">Last {history.length} samples</span>
          </div>
          <div className="telemetry-table">
            <div className="telemetry-header"><span>TIME</span><span>TEMP</span><span>VOLTAGE</span><span>RPM</span><span>ML</span><span>RULE</span><span>FAULT</span></div>
            {history.slice().reverse().map((item, i) => (
              <div className="telemetry-row" key={`${item.timestamp}-${i}`}>
                <span>{item.timestamp}</span><span>{Number(item.temperature).toFixed(1)}°C</span>
                <span>{Number(item.voltage).toFixed(2)} V</span><span>{item.rpm}</span>
                <span>{item.ml_prediction}</span><span>{item.rule_prediction}</span>
                <span className={item.fault !== "NONE" ? "fault-text" : "normal-text"}>{item.fault}</span>
              </div>
            ))}
            {!history.length && <div className="empty-state compact"><span>◌</span><div><strong>Waiting for telemetry</strong><small>Start the Aegis Edge runtime to receive live data.</small></div></div>}
          </div>
        </section>

        <footer><span>AEGIS EDGE</span><span>Zephyr RTOS</span><span>TensorFlow Lite Micro</span><span>Renode</span></footer>
      </main>
    </div>
  );
}

export default App;
