//import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Dashboard.css";
//import api from "../api";

function Dashboard() {
  const navigate = useNavigate();
  //const [resources, setResources] = useState([]);
  
  const categories = [
  { title: "Student Organizations", category: "student_orgs" },
  { title: "Food", category: "food" },
  { title: "Campus Events", category: "events" },
  { title: "Career Resources", category: "career" },
  { title: "Academic Resources", category: "academic" },
  { title: "Wellness & Support", category: "wellness" }
];
  const username = localStorage.getItem('username');//added username info 

  //useEffect(() => {
    //const email = localStorage.getItem('email');
    //const path = email
      //? `/recommendations?email=${encodeURIComponent(email)}`
      //: '/recommendations';

    // Fetch either all resources or recommendations filtered by the logged-in user's interests.
    //api.get(path).then((res) => setResources(res.data));
  //}, []);
  
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
	
	  
     <h2 style={{ padding: "10px" }} >Find a new activity:</h2>
	   <div className="resource-grid">
	     {categories.map((item, index) => (
		 <button key={index} className={`resource-card ${item.category}`}>
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