import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";

function Login() {
  // login form state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/login", { email, password });
      setMessage(res.data.message || "Logged in");
      // Persist the logged-in user's email for personalization.
      localStorage.setItem('email', email);
      navigate("/dashboard");
    } catch (err) {
      setMessage(err.response?.data?.error || err.message || "Login failed");
    }
  };

  return (
    <div>
      <h1>Log In</h1>
      <form onSubmit={handleLogin}>
        <div>
          <label>Email</label>
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
        <button type="submit">Log In</button>
      </form>
      {message && <p>{message}</p>}
      <p>
        <Link to="/">Return to Home</Link>
      </p>
      <p>
        <Link to="/signup">Create an account</Link>
      </p>
    </div>
  );
}

export default Login;
