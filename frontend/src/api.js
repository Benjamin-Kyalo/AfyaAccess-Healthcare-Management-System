const API_URL = "http://localhost:8000/api"; // adjust if needed

// LOGIN user (expects { username, password })
export async function loginUser(credentials) {
  const res = await fetch(`${API_URL}/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  if (!res.ok) throw new Error("Login failed: " + res.status);

  const data = await res.json();
  // backend should return { access, refresh, user: {username, role} }
  if (data?.access) {
    localStorage.setItem("token", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));
  }
  return data;
}

// REGISTER user
export async function registerUser(userObj) {
  const res = await fetch(`${API_URL}/users/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userObj),
  });
  if (!res.ok) throw new Error("Registration failed: " + res.status);
  return res.json();
}

// CREATE a new patient
export async function createPatient(patientObj) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/patients/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(patientObj),
  });
  return res.json();
}

// GET all patients
export async function fetchPatients() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/patients/`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return res.json();
}

// UPDATE a patient
export async function updatePatient(patientId, updateObj) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/patients/${patientId}/`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(updateObj),
  });
  return res.json();
}
