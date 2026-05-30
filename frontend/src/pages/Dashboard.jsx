import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

function Dashboard() {
  const [resources, setResources] = useState([]);

  useEffect(() => {
    api.get("/recommendations").then((res) => setResources(res.data));
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