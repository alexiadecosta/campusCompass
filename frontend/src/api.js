// Simple frontend API helper used by the React pages.
// All requests are sent to the backend running on localhost:5000.
const baseURL = "http://localhost:5000";

async function handleResponse(response) {
  const content = await response.text();
  const data = content ? JSON.parse(content) : null;

  if (!response.ok) {
    const error = new Error(data?.error || response.statusText || "Request failed");
    error.response = { data };
    throw error;
  }

  return { data };
}

function makeHeaders(extra = {}) {
  const headers = { "Content-Type": "application/json", ...extra };
  const token = localStorage.getItem('token');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

export default {
  get: (path) => fetch(`${baseURL}${path}`, { headers: makeHeaders() }).then(handleResponse),
  post: (path, body) =>
    fetch(`${baseURL}${path}`, {
      method: "POST",
      headers: makeHeaders(),
      body: JSON.stringify(body),
    }).then(handleResponse),
  delete: (path) =>
    fetch(`${baseURL}${path}`, {
      method: "DELETE",
      headers: makeHeaders(),
    }).then(handleResponse),
};
