// frontend/src/components/dashboard.jsx
import React, { useEffect, useState } from "react";
import { fetchPatients, updatePatient } from "../api";

/*
 Dashboard: central hub.
 Shows a grid/list of recent patients with status tags and a quick "advance status" action.
*/

const STATUS_LABELS = {
  billing: "Sent to Billing",
  consultation: "Doctor Consultation",
  lab: "Lab Requested",
  done: "Completed"
};

// order for advancing status
const STATUS_ORDER = ["billing", "consultation", "lab", "done"];

export default function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    loadPatients();
  }, []);

  async function loadPatients() {
    try {
      setLoading(true);
      const data = await fetchPatients();
      setPatients(Array.isArray(data) ? data : []);
      setLoading(false);
    } catch (err) {
      setLoading(false);
      console.error(err);
      setMsg("Failed to load patients");
    }
  }

  // advance to next status in STATUS_ORDER
  async function advanceStatus(p) {
    const currentIndex = STATUS_ORDER.indexOf(p.status || "billing");
    const next = STATUS_ORDER[Math.min(currentIndex + 1, STATUS_ORDER.length - 1)];
    if (next === p.status) return; // already at final
    try {
      const updated = await updatePatient(p.id, { status: next });
      // optimistic update
      setPatients(prev => prev.map(i => (i.id === p.id ? updated : i)));
      setMsg(`Patient ${p.id} moved to "${STATUS_LABELS[next]}"`);
    } catch (err) {
      console.error(err);
      setMsg("Failed to update status");
    }
  }

  if (loading) return <div className="container card">Loading...</div>;

  return (
      <div className="container">
          <h1>Welcome to AfyaAccess Patient Dashboard</h1>
      {/* <h2>Dashboard — Patient Flow</h2> */}
      {msg && <p className={msg.startsWith("Failed") ? "error" : "success"}>{msg}</p>}

      <div className="grid">
        {patients.map(p => (
          <div className="card patient-card" key={p.id}>
            <div className="patient-header">
              <div className="patient-name">{p.first_name || "—"} {p.last_name || ""}</div>
              <div className={`status-chip status-${p.status || "billing"}`}>
                {STATUS_LABELS[p.status] || "Unknown"}
              </div>
            </div>

            <div className="patient-body">
              <div><strong>DOB:</strong> {p.date_of_birth || "N/A"}</div>
              <div><strong>Phone:</strong> {p.phone || "N/A"}</div>
              <div><strong>Address:</strong> {p.address || "N/A"}</div>
            </div>

            <div className="patient-actions">
              <button className="btn small" onClick={() => advanceStatus(p)}>
                Advance
              </button>
              <button className="btn small ghost" onClick={() => navigator.clipboard.writeText(String(p.id))}>
                Copy ID
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
