import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";

function Signup() {
  // form fields for creating a new account
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (event) => {
    event.preventDefault();

    // frontend validation: enforce GMU email domain
    if (!email.endsWith("@gmu.edu")) {
      setMessage("Please use a GMU email address.");
      return;
    }

    try {
      const response = await api.post("/signup", {
        username,
        email,
        password,
      });

      setMessage(response.data.message || "Account created successfully.");
      // Persist the logged-in user's email for interest selection and recommendations.
      localStorage.setItem('email', email);
      navigate("/interests");
    } catch (error) {
      setMessage(error.response?.data?.error || error.message || "Signup failed.");
    }
  };

  return (
    <div>
      <h1>Create Account</h1>
      <form onSubmit={handleSignup}>
        <div>
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>GMU Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Sign Up</button>
      </form>
      {message && <p>{message}</p>}
      <p>
        <Link to="/">Return to Home</Link>
      </p>
    </div>
  );
}

export default Signup;