const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch {
    throw new Error("Impossible de joindre l’API. Vérifiez que le backend est démarré.");
  }

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
  updateClient: (id, payload) =>
    request(`/clients/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteClient: (id) =>
    request(`/clients/${id}/`, { method: "DELETE" }),
  createMeal: (payload) =>
    request("/meals/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateMeal: (id, payload) =>
    request(`/meals/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteMeal: (id) =>
    request(`/meals/${id}/`, { method: "DELETE" }),
  getDrivers: () => request("/delivery-drivers/"),
  getAvailableDrivers: () => request("/delivery-drivers/available/"),
  createDriver: (payload) =>
    request("/delivery-drivers/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateDriverStatus: (id, status) =>
    request(`/delivery-drivers/${id}/status/`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
  updateDriverLocation: (id, payload) =>
    request(`/delivery-drivers/${id}/location/`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  getOrders: () => request("/orders/"),
  createOrder: (payload) =>
    request("/orders/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getOrder: (id) => request(`/orders/${id}/`),
  getOrderStatus: (id) => request(`/orders/${id}/status/`),
  updateOrderStatus: (id, status) =>
    request(`/orders/${id}/status/`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
};

export { API_BASE_URL };
