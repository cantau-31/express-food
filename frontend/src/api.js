const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (response.status === 204) return null;

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      Object.values(data || {}).flat().join(" ") ||
      "Une erreur est survenue.";
    throw new Error(message);
  }

  return data;
}

export const api = {
  getTodayMeals: () => request("/meals/today/"),
  getMeals: () => request("/meals/"),
  getClients: () => request("/clients/"),
  createClient: (payload) =>
    request("/clients/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getDrivers: () => request("/delivery-drivers/"),
  getAvailableDrivers: () => request("/delivery-drivers/available/"),
  createOrder: (payload) =>
    request("/orders/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getOrder: (id) => request(`/orders/${id}/`),
  getOrderStatus: (id) => request(`/orders/${id}/status/`),
};

export { API_BASE_URL };
