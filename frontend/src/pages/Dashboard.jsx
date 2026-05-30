import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

function Dashboard() {
  const [resources, setResources] = useState([]);

  useEffect(() => {
    const email = localStorage.getItem('email');
    const path = email
      ? `/recommendations?email=${encodeURIComponent(email)}`
      : '/recommendations';

    api.get(path).then((res) => setResources(res.data));
  }, []);

  return (
    <div>
      <h1>Your Recommendations</h1>
      {resources.length === 0 ? (
        <p>No recommendations available yet.</p>
      ) : (
        resources.map((resource, index) => (
          <div key={index}>
            <h3>{resource.title}</h3>
            <p>{resource.category}</p>
          </div>
        ))
      )}
      <p>
        <Link to="/">Return to Home</Link>
      </p>
    </div>
  );
}
export default Dashboard;