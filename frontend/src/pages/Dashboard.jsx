//import React, { useEffect, useState } from "react";
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Dashboard.css";
import api from "../api";

function Dashboard() {
  const navigate = useNavigate();
  //const [resources, setResources] = useState([]);
  
  const categories = [
  { title: "Student Organizations", category: "student_orgs" },
  { title: "Food", category: "food" },
  { title: <>Campus<br />Events</>, category: "events" },
  { title: <>Career<br />Resources</>, category: "career" },
  { title: "Academic Resources", category: "academic" },
  { title: "Wellness & Support", category: "wellness" }
];
  const username = localStorage.getItem('username');//added username info 
  const [saved, setSaved] = useState([]);

  //useEffect(() => {
    //const email = localStorage.getItem('email');
    //const path = email
      //? `/recommendations?email=${encodeURIComponent(email)}`
      //: '/recommendations';

    // Fetch either all resources or recommendations filtered by the logged-in user's interests.
    //api.get(path).then((res) => setResources(res.data));
  //}, []);

  useEffect(() => {
    api.get('/saved')
      .then((res) => setSaved(res.data || []))
      .catch(() => setSaved([]));
  }, []);
  
  return (
    <div>

	 <div className="top-banner">
	   <div className="banner-left">
	     Welcome, {username}
	   </div>
	  
	   <div className="banner-right">
	     <button>Favorites</button>
		 <button>Account</button>
		 
		 <button 
		   onClick={() => {
			 localStorage.removeItem("username");
			 navigate("/");
		   }}
		 >
		 Sign out
		</button>
	   </div>
	</div>
  
  {saved.length > 0 && (
    <div style={{ padding: '8px 12px', background: '#f8f9fa', display: 'flex', gap: '8px', overflowX: 'auto' }}>
      {saved.map((r) => (
        <div key={r.id} style={{ minWidth: 180, border: '1px solid #ddd', borderRadius: 6, padding: 8 }}>
          <strong>{r.title}</strong>
          <div style={{ fontSize: 12, color: '#666' }}>{r.category}</div>
          <div style={{ marginTop: 6 }}>
            <button onClick={() => navigate(`/resources?category=${r.category}`)} style={{ marginRight: 8 }}>View</button>
          </div>
        </div>
      ))}
    </div>
  )}
	  
     <h2 style={{ padding: "10px" }} >Find a new activity:</h2>
	   <div className="resource-grid">
	     {categories.map((item, index) => (
		 <button 
		   key={index} 
		   className={`resource-card ${item.category}`}
		   onClick={() => navigate(`/resources?category=${item.category}`)}
		 >
             <h3>{item.title}</h3>
           </button>
         ))}
	   </div>
       <p>
         <Link to="/">Return to Home</Link>
       </p>
   </div>
 );
}
export default Dashboard;