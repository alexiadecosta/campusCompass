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

export default {
  get: (path) => fetch(`${baseURL}${path}`).then(handleResponse),
  post: (path, body) =>
    fetch(`${baseURL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(handleResponse),
};
