import { useState } from "react";
import "./App.css";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState([]);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Server error");

      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error(err);
      alert("Failed to connect to backend");
    }
  };

  // 🔍 FILTERING
  const filteredData = data.filter((row) => {
    const matchSearch = JSON.stringify(row)
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchFilter = filter === "All" ? true : row.Risk === filter;

    return matchSearch && matchFilter;
  });

  // 📊 KPI COUNT
  const count = (type) => data.filter((d) => d.Risk === type).length;

  const avgChurn =
    data.length > 0
      ? (
          data.reduce(
            (sum, d) => sum + Number(d["Churn Probability"] || 0),
            0,
          ) / data.length
        ).toFixed(2)
      : 0;

  // 📊 CHART
  const chartData = {
    labels: ["High Risk", "Medium Risk", "Low Risk"],
    datasets: [
      {
        data: [count("High Risk"), count("Medium Risk"), count("Low Risk")],
        backgroundColor: ["#ef4444", "#f59e0b", "#10b981"],
        borderWidth: 0,
      },
    ],
  };

  // 🎨 COLOR
  const getColor = (risk) => {
    if (risk === "High Risk") return "high";
    if (risk === "Medium Risk") return "medium";
    return "low";
  };

  // 📥 DOWNLOAD
  const downloadCSV = () => {
    if (data.length === 0) return;

    const headers = Object.keys(data[0]);
    const rows = data.map((obj) => headers.map((h) => obj[h]));

    const csv =
      headers.join(",") + "\n" + rows.map((row) => row.join(",")).join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "churn_results.csv";
    a.click();
  };

  // 🧠 EXPLAINABILITY (BASIC)
  const getReason = (row) => {
    const prob = Number(row["Churn Probability"]) || 0;

    if (prob > 0.7) return "High probability of churn";
    if (prob > 0.4) return "Moderate churn risk";
    return "Low churn risk";
  };

  return (
    <div className="container">
      <h1>Churn Analytics</h1>
      <p className="subtitle">
        Upload customer data, predict churn risk, and take action.
      </p>

      {/* 🔼 UPLOAD */}
      <div className="top-bar">
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Run Prediction</button>
      </div>

      {/* 📊 KPI CARDS */}
      <div className="cards">
        <div className="card">
          <h4>Avg Churn</h4>
          <p>{avgChurn}</p>
        </div>
        <div className="card high">
          <h4>High Risk</h4>
          <p>{count("High Risk")}</p>
        </div>
        <div className="card medium">
          <h4>Medium Risk</h4>
          <p>{count("Medium Risk")}</p>
        </div>
        <div className="card low">
          <h4>Low Risk</h4>
          <p>{count("Low Risk")}</p>
        </div>
      </div>

      {/* 🔍 SEARCH + FILTER */}
      <div className="controls">
        <input
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <div className="filters">
          {["All", "High Risk", "Medium Risk", "Low Risk"].map((f) => (
            <button
              key={f}
              className={filter === f ? "active" : ""}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* 📊 CHART */}
      <div className="chart-box">
        <h3>Risk Distribution</h3>
        <Doughnut data={chartData} />
      </div>

      {/* 📊 TABLE */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Churn %</th>
              <th>Risk</th>
              <th>Action</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((row, i) => {
              const prob = Number(row["Churn Probability"]) || 0;

              return (
                <tr key={i}>
                  <td>
                    <div className="progress">
                      <div
                        className="bar"
                        style={{ width: `${prob * 100}%` }}
                      ></div>
                    </div>
                    {(prob * 100).toFixed(0)}%
                  </td>

                  <td className={getColor(row.Risk)}>{row.Risk}</td>
                  <td>{row.Action}</td>
                  <td>{getReason(row)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
