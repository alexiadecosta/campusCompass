import React, { useEffect, useState } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import api from "../api";

function Resources() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const category = searchParams.get("category");
  const [resources, setResources] = useState([]);
  const [savedIds, setSavedIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Map category codes to display names
  const categoryNames = {
    student_orgs: "Student Organizations",
    food: "Food",
    events: "Campus Events",
    career: "Career Resources",
    academic: "Academic Resources",
    wellness: "Wellness & Support"
  };

  useEffect(() => {
    if (!category) {
      setError("No category selected");
      setLoading(false);
      return;
    }

    setLoading(true);
    api.get(`/resources?category=${encodeURIComponent(category)}`)
      .then((res) => {
        setResources(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load resources");
        setLoading(false);
      });
  }, [category]);

  useEffect(() => {
    // load saved resources for current user
    api.get('/saved')
      .then((res) => {
        const ids = new Set((res.data || []).map(r => r.id));
        setSavedIds(ids);
      })
      .catch(() => {});
  }, []);

  const toggleFavorite = async (resourceId) => {
    try {
      if (savedIds.has(resourceId)) {
        await api.delete(`/resource/${resourceId}/save`);
        const next = new Set(savedIds);
        next.delete(resourceId);
        setSavedIds(next);
      } else {
        await api.post(`/resource/${resourceId}/save`, {});
        const next = new Set(savedIds);
        next.add(resourceId);
        setSavedIds(next);
      }
    } catch (err) {
      alert(err.response?.data?.error || err.message || 'Failed to toggle favorite');
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <button 
        onClick={() => navigate("/dashboard")}
        style={{ marginBottom: "20px", padding: "8px 12px", cursor: "pointer" }}
      >
        ← Back to Dashboard
      </button>

      <h1>{categoryNames[category] || category}</h1>

      {loading && <p>Loading resources...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {!loading && !error && resources.length === 0 && (
        <p>No resources found in this category.</p>
      )}

      {!loading && !error && resources.length > 0 && (
        <div style={{ display: "grid", gap: "16px", marginTop: "20px" }}>
          {resources.map((resource) => (
            <div
              key={resource.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "16px",
                boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
                <div>
                  <h3 style={{ margin: "0 0 8px 0" }}>{resource.title}</h3>
                  {resource.tags && (
                    <p style={{ margin: "0", color: "#666", fontSize: "14px" }}>
                      Tags: {resource.tags}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => toggleFavorite(resource.id)}
                  style={{
                    padding: "6px 12px",
                    backgroundColor: savedIds.has(resource.id) ? "#e63946" : "#007bff",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer"
                  }}
                >
                  {savedIds.has(resource.id) ? '♥ Saved' : '♥ Add to Favorites'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Resources;
