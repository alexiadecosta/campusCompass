import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

function Interests() {
  // Available interest tags loaded from the backend
  const [tags, setTags] = useState([]);
  // Selected tags stored as a Set for fast lookup
  const [selected, setSelected] = useState(new Set());
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch the list of available tags for interest selection.
    // Expected response: ["tag1", "tag2", ...]
    api.get('/tags').then((res) => setTags(res.data));
  }, []);

  const toggle = (tag) => {
    const next = new Set(selected);
    if (next.has(tag)) next.delete(tag);
    else next.add(tag);
    setSelected(next);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const email = localStorage.getItem('email');
    if (!email) {
      setMessage('No user email found; please log in or sign up.');
      return;
    }
    try {
      const interests = Array.from(selected);
      const res = await api.post('/set_interests', { email, interests });
      setMessage(res.data.message || 'Interests saved');
      navigate('/dashboard');
    } catch (err) {
      setMessage(err.response?.data?.error || err.message || 'Could not save interests');
    }
  };

  return (
    <div>
      <h1>Select Your Interests</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {tags.map((tag) => (
            <label key={tag} style={{ border: '1px solid #ccc', padding: '6px' }}>
              <input
                type="checkbox"
                checked={selected.has(tag)}
                onChange={() => toggle(tag)}
              />
              {tag}
            </label>
          ))}
        </div>
        <div style={{ marginTop: '12px' }}>
          <button type="submit">Save Interests</button>
        </div>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Interests;
