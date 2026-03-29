import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState([]);

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData,
    });

    const result = await res.json();
    setData(result);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Churn Prediction Dashboard</h1>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />

      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Upload
      </button>

      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default App;
