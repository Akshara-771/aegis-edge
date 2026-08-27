import { useEffect, useMemo, useState } from "react";
import "./App.css";

const initialTelemetry = {
  timestamp: 0,
  temperature: 0,
  voltage: 0,
  rpm: 0,
  fault: "NONE",
  ml_prediction: "NORMAL",
  rule_prediction: "NONE",
};

function Chart({ title, data, dataKey, unit, maxPoints = 30 }) {
  const values = data.map((item) => Number(item[dataKey]) || 0);

  if (values.length === 0) {
    return (
      <div className="chart-card">
        <div className="chart-title">{title}</div>
        <div className="chart-empty">Waiting for telemetry...</div>
      </div>
    );
  }

  const width = 700;
  const height = 220;
  const padding = 30;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const points = values
    .map((value, index) => {
      const x =
        padding +
        (index / Math.max(values.length - 1, 1)) * (width - padding * 2);

      const y =
        height - padding - ((value - min) / range) * (height - padding * 2);

      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="chart-card">
      <div className="chart-heading">
        <div>
          <h3>{title}</h3>
          <p>Live · last {Math.min(data.length, maxPoints)} samples</p>
        </div>

        <strong>
          {values[values.length - 1].toFixed(dataKey === "temperature" ? 1 : 2)}
          {unit}
        </strong>
      </div>

      <svg
        className="chart"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
      >
        <line
          x1={padding}
          y1={padding}
          x2={width - padding}
          y2={padding}
          className="grid-line"
        />

        <line
          x1={padding}
          y1={height / 2}
          x2={width - padding}
          y2={height / 2}
          className="grid-line"
        />

        <line
          x1={padding}
          y1={height - padding}
          x2={width - padding}
          y2={height - padding}
          className="grid-line"
        />

        <polyline points={points} fill="none" className="chart-line" />

        {values.length > 0 && (
          <circle
            cx={points.split(" ").at(-1).split(",")[0]}
            cy={points.split(" ").at(-1).split(",")[1]}
            r="5"
            className="chart-point"
          />
        )}
      </svg>

      <div className="chart-scale">
        <span>{max.toFixed(1)}</span>
        <span>{min.toFixed(1)}</span>
      </div>
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

    socket.onopen = () => {
      console.log("Connected to Aegis Edge");
      setConnected(true);
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      // Initial history sent by the backend after connection.
      if (message.type === "history") {
        const historicalData = message.data || [];

        if (historicalData.length > 0) {
          const latest = historicalData[historicalData.length - 1];

          setTelemetry(latest);
          setHistory(historicalData.slice(-30));

          // Rebuild fault history from stored telemetry.
          const events = [];

          historicalData.forEach((data, index) => {
            if (data.fault === "NONE") {
              return;
            }

            const previous = historicalData[index - 1];

            if (!previous || previous.fault !== data.fault) {
              events.push({
                timestamp: data.timestamp,
                fault: data.fault,
                ml: data.ml_prediction,
                rule: data.rule_prediction,
              });
            }
          });

          setFaultEvents(events.slice(-10).reverse());
        }

        return;
      }

      // Normal live telemetry message.
      const data = message;

      setTelemetry(data);

      setHistory((previous) => {
        const updated = [...previous, data];
        return updated.slice(-30);
      });

      if (data.fault !== "NONE") {
        setFaultEvents((previous) => {
          const last = previous[0];

          if (!last || last.fault !== data.fault) {
            return [
              {
                timestamp: data.timestamp,
                fault: data.fault,
                ml: data.ml_prediction,
                rule: data.rule_prediction,
              },
              ...previous,
            ].slice(0, 10);
          }

          return previous;
        });
      }
    };

    socket.onclose = () => {
      setConnected(false);
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setConnected(false);
    };

    return () => socket.close();
  }, []);

  const isFault = telemetry.fault !== "NONE";

  const predictionsAgree =
    telemetry.ml_prediction === telemetry.rule_prediction ||
    (telemetry.ml_prediction === "NORMAL" &&
      telemetry.rule_prediction === "NONE");

  const temperatureHistory = useMemo(
    () =>
      history.map((item) => ({
        ...item,
        temperature: item.temperature,
      })),
    [history],
  );

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AEGIS EDGE</h1>
          <p>Embedded AI Fault Detection System</p>
        </div>

        <div className={`connection ${connected ? "online" : "offline"}`}>
          <span className="status-dot"></span>
          {connected ? "LIVE" : "OFFLINE"}
        </div>
      </header>

      <main>
        <section className={`system-status ${isFault ? "fault" : "normal"}`}>
          <div>
            <span className="status-label">SYSTEM STATUS</span>
            <h2>{isFault ? "FAULT DETECTED" : "SYSTEM NORMAL"}</h2>
          </div>

          <div className="fault-name">{telemetry.fault}</div>
        </section>

        <section className="sensor-grid">
          <div className="card">
            <span className="card-label">TEMPERATURE</span>
            <strong>{telemetry.temperature.toFixed(1)}°C</strong>
          </div>

          <div className="card">
            <span className="card-label">VOLTAGE</span>
            <strong>{telemetry.voltage.toFixed(2)} V</strong>
          </div>

          <div className="card">
            <span className="card-label">RPM</span>
            <strong>{telemetry.rpm}</strong>
          </div>

          <div className="card">
            <span className="card-label">TIMESTAMP</span>
            <strong>{telemetry.timestamp} ms</strong>
          </div>
        </section>

        <section className="prediction-grid">
          <div className="prediction-card">
            <div className="prediction-header">
              <span>ML PREDICTION</span>
              <span className="badge ml">TFLM</span>
            </div>

            <strong>{telemetry.ml_prediction}</strong>

            <div className="prediction-description">TensorFlow Lite Micro</div>
          </div>

          <div className="prediction-card">
            <div className="prediction-header">
              <span>RULE PREDICTION</span>
              <span className="badge rule">RULE</span>
            </div>

            <strong>{telemetry.rule_prediction}</strong>

            <div className="prediction-description">
              Deterministic fault detector
            </div>
          </div>

          <div className="prediction-card final">
            <div className="prediction-header">
              <span>DETECTION AGREEMENT</span>
            </div>

            <strong>{predictionsAgree ? "AGREE" : "DISAGREE"}</strong>

            <div className="prediction-description">ML vs rule engine</div>
          </div>
        </section>

        <section className="charts-section">
          <div className="section-heading">
            <div>
              <h2>Live Sensor Trends</h2>
              <p>Real-time measurements from the edge device</p>
            </div>
          </div>

          <div className="charts-grid">
            <Chart
              title="Temperature"
              data={temperatureHistory}
              dataKey="temperature"
              unit="°C"
            />

            <Chart title="Voltage" data={history} dataKey="voltage" unit=" V" />

            <Chart
              title="Motor Speed"
              data={history}
              dataKey="rpm"
              unit=" RPM"
            />
          </div>
        </section>

        <section className="events-section">
          <div className="section-heading">
            <div>
              <h2>Fault Events</h2>
              <p>Detected faults from the edge system</p>
            </div>

            <span>{faultEvents.length} events</span>
          </div>

          {faultEvents.length === 0 ? (
            <div className="empty-state">No faults detected yet.</div>
          ) : (
            <div className="events-list">
              {faultEvents.map((event, index) => (
                <div className="event-row" key={`${event.timestamp}-${index}`}>
                  <div className="event-indicator"></div>

                  <div className="event-main">
                    <strong>{event.fault}</strong>
                    <span>{event.timestamp} ms</span>
                  </div>

                  <div className="event-result">
                    <span>ML</span>
                    <strong>{event.ml}</strong>
                  </div>

                  <div className="event-result">
                    <span>RULE</span>
                    <strong>{event.rule}</strong>
                  </div>

                  <div className="event-status">
                    {event.ml === event.rule ? "✓ MATCH" : "⚠ MISMATCH"}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="history-section">
          <div className="section-heading">
            <div>
              <h2>Live Telemetry</h2>
              <p>Real-time data received from the edge system</p>
            </div>

            <span>{history.length} samples</span>
          </div>

          <div className="telemetry-table">
            <div className="table-header">
              <span>TIME</span>
              <span>TEMP</span>
              <span>VOLTAGE</span>
              <span>RPM</span>
              <span>ML</span>
              <span>RULE</span>
              <span>FAULT</span>
            </div>

            {history
              .slice()
              .reverse()
              .map((item, index) => (
                <div className="table-row" key={`${item.timestamp}-${index}`}>
                  <span>{item.timestamp}</span>
                  <span>{item.temperature.toFixed(1)}°C</span>
                  <span>{item.voltage.toFixed(2)} V</span>
                  <span>{item.rpm}</span>
                  <span>{item.ml_prediction}</span>
                  <span>{item.rule_prediction}</span>
                  <span className={item.fault !== "NONE" ? "fault-text" : ""}>
                    {item.fault}
                  </span>
                </div>
              ))}

            {history.length === 0 && (
              <div className="empty-state">Waiting for telemetry...</div>
            )}
          </div>
        </section>
      </main>

      <footer>Aegis Edge • Zephyr RTOS • TensorFlow Lite Micro</footer>
    </div>
  );
}

export default App;
