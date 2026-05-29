import React, {useState} from "react";
function Signup() {
  const [email, setEmail]=useState("");
  const validateGMU=() => {
    if (!email.endsWith("@gmu.edu")){
      alert("Must use GMU email");
    }
  };
  return (
    <div>
      <h1> Create Account </h1>
      <input
        type="email"
        onChange={(e) => setEmail(e.target.value)}
      />
      <button onClick={validateGMU}>
        Sign Up
      </button>
    </div>
  );
}
export default Signup;
