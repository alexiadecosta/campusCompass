import React, {useEffect, useState} from "react";
import api from "../api";

function Dashboard() {
  const [resources, setResources] = useState([]);
  useEffect(() => {
    api.get("/recommendations").then(res => setResources(res.data));
  }, []);
  return (
    <div>
      <h1> Your Recommendations </h1>
      {resources.map((resource,index) => (
      <div key={index}>
        <h3> {resource.title} </h3>
        <p> {resource.category} </p>
      </div>
      ))}
    </div>
  );
}
export default Dashboard;
