import { useEffect, useState } from "react";
import { api } from "./api";

const tabs = [
  ["clients", "Clients"],
  ["meals", "Plats & desserts"],
  ["orders", "Commandes"],
  ["drivers", "Livreurs"],
];

const orderStatuses = [
  "pending",
  "accepted",
  "preparing",
  "out_for_delivery",
  "delivered",
  "cancelled",
];

const driverStatuses = ["available", "offline"];

export default function AdminDashboard() {
  const [tab, setTab] = useState("clients");

  return (
    <section className="page admin-page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">Gestion opérationnelle</span>
          <h1>Administration</h1>
        </div>
      </div>

      <div className="admin-tabs">
        {tabs.map(([key, label]) => (
          <button
            key={key}
            className={tab === key ? "active" : ""}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "clients" && <ClientsAdmin />}
      {tab === "meals" && <MealsAdmin />}
      {tab === "orders" && <OrdersAdmin />}
      {tab === "drivers" && <DriversAdmin />}
    </section>
  );
}

function ClientsAdmin() {
  const empty = {
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    address: "",
  };
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(empty);
  const [editing, setEditing] = useState(null);
  const [message, setMessage] = useState("");

  const load = () => api.getClients().then(setItems);
  useEffect(() => { load(); }, []);

  const submit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      if (editing) {
        await api.updateClient(editing, form);
      } else {
        await api.createClient(form);
      }
      setForm(empty);
      setEditing(null);
      setMessage("Client enregistré.");
      load();
    } catch (error) {
      setMessage(error.message);
    }
  };

  const edit = (client) => {
    setEditing(client.id);
    setForm({
      first_name: client.first_name,
      last_name: client.last_name,
      email: client.email,
      phone: client.phone,
      address: client.address,
    });
  };

  const remove = async (id) => {
    if (!window.confirm("Supprimer ce client ?")) return;
    await api.deleteClient(id);
    load();
  };

  return (
    <div className="admin-grid">
      <form className="form-card" onSubmit={submit}>
        <h2>{editing ? "Modifier le client" : "Ajouter un client"}</h2>
        <div className="form-grid">
          {[
            ["first_name", "Prénom"],
            ["last_name", "Nom"],
            ["email", "Email"],
            ["phone", "Téléphone"],
            ["address", "Adresse"],
          ].map(([key, label]) => (
            <label key={key} className={key === "address" ? "span-2" : ""}>
              {label}
              <input
                required
                type={key === "email" ? "email" : "text"}
                value={form[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              />
            </label>
          ))}
        </div>
        {message && <p className="admin-message">{message}</p>}
        <div className="admin-actions">
          <button className="button primary">{editing ? "Enregistrer" : "Ajouter"}</button>
          {editing && (
            <button type="button" className="button secondary" onClick={() => { setEditing(null); setForm(empty); }}>
              Annuler
            </button>
          )}
        </div>
      </form>

      <AdminList title="Clients" count={items.length}>
        {items.map((client) => (
          <AdminRow key={client.id}>
            <div>
              <strong>{client.first_name} {client.last_name}</strong>
              <span>{client.email}</span>
              <small>{client.address}</small>
            </div>
            <div className="row-actions">
              <button onClick={() => edit(client)}>Modifier</button>
              <button className="danger-link" onClick={() => remove(client.id)}>Supprimer</button>
            </div>
          </AdminRow>
        ))}
      </AdminList>
    </div>
  );
}

function MealsAdmin() {
  const today = new Date().toISOString().slice(0, 10);
  const empty = {
    name: "",
    description: "",
    price: "",
    type: "dish",
    date: today,
    image_url: "",
    available: true,
  };
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(empty);
  const [editing, setEditing] = useState(null);
  const [message, setMessage] = useState("");

  const load = () => api.getMeals().then(setItems);
  useEffect(() => { load(); }, []);

  const submit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      if (editing) await api.updateMeal(editing, form);
      else await api.createMeal(form);
      setForm(empty);
      setEditing(null);
      setMessage("Repas enregistré.");
      load();
    } catch (error) {
      setMessage(error.message);
    }
  };

  const edit = (meal) => {
    setEditing(meal.id);
    setForm({
      name: meal.name,
      description: meal.description || "",
      price: meal.price,
      type: meal.type,
      date: meal.date,
      image_url: meal.image_url || "",
      available: meal.available,
    });
  };

  const remove = async (id) => {
    if (!window.confirm("Supprimer ce repas ?")) return;
    await api.deleteMeal(id);
    load();
  };

  return (
    <div className="admin-grid">
      <form className="form-card" onSubmit={submit}>
        <h2>{editing ? "Modifier le repas" : "Ajouter au menu"}</h2>
        <div className="form-grid">
          <label>
            Nom
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Prix
            <input required inputMode="decimal" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
          </label>
          <label>
            Type
            <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
              <option value="dish">Plat</option>
              <option value="dessert">Dessert</option>
            </select>
          </label>
          <label>
            Date
            <input type="date" required value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
          </label>
          <label className="span-2">
            Description
            <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <label className="span-2">
            Image URL
            <input value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} />
          </label>
          <label className="checkbox-label span-2">
            <input type="checkbox" checked={form.available} onChange={(e) => setForm({ ...form, available: e.target.checked })} />
            Disponible à la commande
          </label>
        </div>
        {message && <p className="admin-message">{message}</p>}
        <div className="admin-actions">
          <button className="button primary">{editing ? "Enregistrer" : "Ajouter"}</button>
          {editing && <button type="button" className="button secondary" onClick={() => { setEditing(null); setForm(empty); }}>Annuler</button>}
        </div>
      </form>

      <AdminList title="Repas" count={items.length}>
        {items.map((meal) => (
          <AdminRow key={meal.id}>
            <div>
              <strong>{meal.name}</strong>
              <span>{meal.type === "dessert" ? "Dessert" : "Plat"} · {meal.price} €</span>
              <small>{meal.date} · {meal.available ? "Disponible" : "Indisponible"}</small>
            </div>
            <div className="row-actions">
              <button onClick={() => edit(meal)}>Modifier</button>
              <button className="danger-link" onClick={() => remove(meal.id)}>Supprimer</button>
            </div>
          </AdminRow>
        ))}
      </AdminList>
    </div>
  );
}

function OrdersAdmin() {
  const [items, setItems] = useState([]);
  const [message, setMessage] = useState("");

  const load = () => api.getOrders().then(setItems);
  useEffect(() => { load(); }, []);

  const update = async (id, status) => {
    setMessage("");
    try {
      await api.updateOrderStatus(id, status);
      setMessage("Statut mis à jour.");
      load();
    } catch (error) {
      setMessage(error.message);
    }
  };

  return (
    <div className="admin-panel">
      <div className="panel-heading">
        <div>
          <h2>Commandes</h2>
          <span>{items.length} au total</span>
        </div>
        <button className="button secondary small" onClick={load}>Actualiser</button>
      </div>
      {message && <p className="admin-message">{message}</p>}
      <div className="table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Commande</th>
              <th>Total</th>
              <th>Livreur</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {items.map((order) => (
              <tr key={order.id}>
                <td>#{order.id.slice(-6)}</td>
                <td>{order.total} €</td>
                <td>{order.delivery_driver_id ? order.delivery_driver_id.slice(-6) : "—"}</td>
                <td>
                  <select value={order.status} onChange={(e) => update(order.id, e.target.value)}>
                    {orderStatuses.map((status) => <option key={status}>{status}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DriversAdmin() {
  const empty = { first_name: "", last_name: "", phone: "", status: "available" };
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(empty);
  const [locations, setLocations] = useState({});
  const [message, setMessage] = useState("");

  const load = () => api.getDrivers().then(setItems);
  useEffect(() => { load(); }, []);

  const submit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      await api.createDriver(form);
      setForm(empty);
      setMessage("Livreur ajouté.");
      load();
    } catch (error) {
      setMessage(error.message);
    }
  };

  const setStatus = async (id, status) => {
    try {
      await api.updateDriverStatus(id, status);
      load();
    } catch (error) {
      setMessage(error.message);
    }
  };

  const saveLocation = async (id) => {
    const location = locations[id] || {};
    const latitude = Number(location.latitude);
    const longitude = Number(location.longitude);

    if (
      location.latitude === "" ||
      location.longitude === "" ||
      !Number.isFinite(latitude) ||
      !Number.isFinite(longitude) ||
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      setMessage("Saisissez une latitude (-90 à 90) et une longitude (-180 à 180) valides.");
      return;
    }

    try {
      await api.updateDriverLocation(id, { latitude, longitude });
      setMessage("Position mise à jour.");
      load();
    } catch (error) {
      setMessage(error.message);
    }
  };

  return (
    <div className="admin-grid">
      <form className="form-card" onSubmit={submit}>
        <h2>Ajouter un livreur</h2>
        <div className="form-grid">
          <label>
            Prénom
            <input required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          </label>
          <label>
            Nom
            <input required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          </label>
          <label>
            Téléphone
            <input required value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </label>
          <label>
            Statut initial
            <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              {driverStatuses.map((status) => <option key={status}>{status}</option>)}
            </select>
          </label>
        </div>
        {message && <p className="admin-message">{message}</p>}
        <button className="button primary">Ajouter</button>
      </form>

      <AdminList title="Livreurs" count={items.length}>
        {items.map((driver) => {
          const location = locations[driver.id] || {
            latitude: driver.latitude ?? "",
            longitude: driver.longitude ?? "",
          };
          return (
            <AdminRow key={driver.id}>
              <div className="driver-admin-content">
                <strong>{driver.first_name} {driver.last_name}</strong>
                <span>{driver.phone}</span>
                <div className="mini-fields">
                  <select value={driver.status} onChange={(e) => setStatus(driver.id, e.target.value)} disabled={driver.status === "delivering"}>
                    <option value="available">available</option>
                    <option value="offline">offline</option>
                    {driver.status === "delivering" && <option value="delivering">delivering</option>}
                  </select>
                  <input
                    placeholder="Latitude"
                    value={location.latitude}
                    onChange={(e) => setLocations({ ...locations, [driver.id]: { ...location, latitude: e.target.value } })}
                  />
                  <input
                    placeholder="Longitude"
                    value={location.longitude}
                    onChange={(e) => setLocations({ ...locations, [driver.id]: { ...location, longitude: e.target.value } })}
                  />
                  <button onClick={() => saveLocation(driver.id)}>Position</button>
                </div>
              </div>
            </AdminRow>
          );
        })}
      </AdminList>
    </div>
  );
}

function AdminList({ title, count, children }) {
  return (
    <div className="admin-panel">
      <div className="panel-heading">
        <h2>{title}</h2>
        <span>{count}</span>
      </div>
      <div className="admin-list">{children}</div>
    </div>
  );
}

function AdminRow({ children }) {
  return <div className="admin-row">{children}</div>;
}
