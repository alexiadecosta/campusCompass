import React from "react";
import { Link } from "react-router-dom";

function Landing() {
  return (
    <div>
      <h1>Welcome to Campus Compass</h1>
      <p>Find campus resources and create your account to get personalized recommendations.</p>
      <div style={{ marginTop: "20px" }}>
        <Link to="/signup">
          <button>Sign Up</button>
        </Link>
        <Link to="/login" style={{ marginLeft: "10px" }}>
          <button>Log In</button>
        </Link>
        <Link to="/dashboard" style={{ marginLeft: "10px" }}>
          <button>View Recommendations</button>
        </Link>
      </div>
    </div>
  );
}

export default Landing;
