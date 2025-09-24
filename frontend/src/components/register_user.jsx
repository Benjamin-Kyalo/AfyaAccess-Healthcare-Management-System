import React, { useState } from "react";
import { registerUser } from "../api";
import { useNavigate } from "react-router-dom";

const ROLES = [
  "Medical Officer / Doctor",
  "Nurse",
  "Clinical Officer",
  "Pharmacist",
  "Laboratory Technologist",
  "Radiographer / Imaging Specialist",
  "Midwife",
  "Facility Administrator / Manager",
  "Records & IT Officer",
  "Support Staff"
];

export default function RegisterUser() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setMsg("");

    try {
      await registerUser({ username, password, role });
      setMsg("Registration successful! Please login.");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError("Failed to register: " + err.message);
    }
  };

  return (
    <div className="form-container">
      <h2>Register New User</h2>
      {error && <p className="error">{error}</p>}
      {msg && <p className="success">{msg}</p>}

      <form onSubmit={handleSubmit}>
        <label>Username</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />

        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />

        <label>Role</label>
        <select value={role} onChange={(e) => setRole(e.target.value)} required>
          <option value="">Select Role</option>
          {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
        </select>

        <button type="submit">Register</button>
      </form>
    </div>
  );
}
