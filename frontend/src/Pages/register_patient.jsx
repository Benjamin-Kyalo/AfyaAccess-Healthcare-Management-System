// src/pages/RegisterPatient.jsx
import React, { useState } from "react";

const RegisterPatient = () => {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "",
  });

  // handle form changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Patient Data:", formData); // later we send this to backend
  };

  return (
    <div>
      <h1>Register Patient</h1>
      <form onSubmit={handleSubmit}>
        <label>Name:</label>
        <input type="text" name="name" value={formData.name} onChange={handleChange} />

        <label>Age:</label>
        <input type="number" name="age" value={formData.age} onChange={handleChange} />

        <label>Gender:</label>
        <select name="gender" value={formData.gender} onChange={handleChange}>
          <option value="">Select...</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>

        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default RegisterPatient;
