import { useEffect, useMemo, useState } from "react";
import {
  Link,
  NavLink,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";
import { api } from "./api";
import { calculateCartTotals } from "./cart";
import AdminDashboard from "./AdminDashboard";

const money = (value) =>
  new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  }).format(Number(value || 0));

function Layout({ cartCount, children }) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link className="brand" to="/">
          <span className="brand-mark">EF</span>
          <span>
            <strong>Express Food</strong>
            <small>Livré en moins de 20 min</small>
          </span>
        </Link>

        <nav className="nav">
          <NavLink to="/menu">Menu</NavLink>
          <NavLink to="/checkout">Commande</NavLink>
          <NavLink to="/drivers">Livreurs</NavLink>
          <NavLink to="/admin">Gestion</NavLink>
          <NavLink className="cart-link" to="/cart">
            Panier <span>{cartCount}</span>
          </NavLink>
        </nav>
      </header>

      <main>{children}</main>

      <footer className="footer">
        <strong>IPSSI Express Food</strong>
        <span>Frontend React — Rayen</span>
      </footer>
    </div>
  );
}

function HomePage() {
  return (
    <section className="hero page">
      <div className="hero-copy">
        <span className="eyebrow">Cuisine du jour · Livraison à vélo</span>
        <h1>Votre repas, prêt et livré rapidement.</h1>
        <p>
          Deux plats et deux desserts préparés chaque jour. Commandez en ligne,
          suivez votre livreur et profitez de la livraison offerte dès 19,99 €.
        </p>
        <div className="hero-actions">
          <Link className="button primary" to="/menu">
            Voir le menu du jour
          </Link>
          <Link className="button secondary" to="/tracking">
            Suivre une commande
          </Link>
        </div>
      </div>

      <div className="hero-card">
        <div className="hero-card-top">
          <span>Express</span>
          <strong>≤ 20 min</strong>
        </div>
        <div className="delivery-visual" aria-hidden="true">
          <span>🚲</span>
        </div>
        <div className="hero-stats">
          <div><strong>4</strong><span>choix / jour</span></div>
          <div><strong>19,99 €</strong><span>livraison offerte</span></div>
        </div>
      </div>
    </section>
  );
}

function MenuPage({ cart, setCart }) {
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getTodayMeals()
      .then(setMeals)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const add = (meal) => {
    setCart((current) => {
      const existing = current.find((item) => item.id === meal.id);
      if (existing) {
        return current.map((item) =>
          item.id === meal.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...current, { ...meal, quantity: 1 }];
    });
  };

  return (
    <section className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">Préparé aujourd'hui</span>
          <h1>Menu du jour</h1>
        </div>
        <Link className="button secondary" to="/cart">
          Voir le panier ({cart.reduce((n, item) => n + item.quantity, 0)})
        </Link>
      </div>

      {loading && <StateCard text="Chargement du menu..." />}
      {error && <StateCard error text={error} />}

      {!loading && !error && (
        <div className="meal-grid">
          {meals.map((meal) => (
            <article className="meal-card" key={meal.id}>
              <div className="meal-photo">
                {meal.image_url ? (
                  <img src={meal.image_url} alt={meal.name} />
                ) : (
                  <span>{meal.type === "dessert" ? "🍰" : "🍽️"}</span>
                )}
              </div>
              <div className="meal-body">
                <span className="tag">
                  {meal.type === "dessert" ? "Dessert" : "Plat"}
                </span>
                <h2>{meal.name}</h2>
                <p>{meal.description || "Préparé aujourd'hui par notre équipe."}</p>
                <div className="meal-footer">
                  <strong>{money(meal.price)}</strong>
                  <button className="button primary small" onClick={() => add(meal)}>
                    Ajouter
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function CartPage({ cart, setCart }) {
  const { subtotal, deliveryFee, total, missingForFreeDelivery } = useMemo(
    () => calculateCartTotals(cart),
    [cart]
  );

  const changeQuantity = (id, delta) => {
    setCart((current) =>
      current
        .map((item) =>
          item.id === id
            ? { ...item, quantity: Math.max(0, item.quantity + delta) }
            : item
        )
        .filter((item) => item.quantity > 0)
    );
  };

  if (!cart.length) {
    return (
      <section className="page narrow">
        <StateCard text="Votre panier est vide.">
          <Link className="button primary" to="/menu">
            Choisir un repas
          </Link>
        </StateCard>
      </section>
    );
  }

  return (
    <section className="page checkout-grid">
      <div>
        <span className="eyebrow">Votre sélection</span>
        <h1>Panier</h1>
        <div className="cart-list">
          {cart.map((item) => (
            <article className="cart-item" key={item.id}>
              <div>
                <strong>{item.name}</strong>
                <span>{money(item.price)} / unité</span>
              </div>
              <div className="quantity">
                <button onClick={() => changeQuantity(item.id, -1)}>-</button>
                <strong>{item.quantity}</strong>
                <button onClick={() => changeQuantity(item.id, 1)}>+</button>
              </div>
              <strong>{money(Number(item.price) * item.quantity)}</strong>
            </article>
          ))}
        </div>
      </div>

      <aside className="summary-card">
        <h2>Récapitulatif</h2>
        <SummaryLine label="Sous-total" value={money(subtotal)} />
        <SummaryLine
          label="Livraison"
          value={deliveryFee === 0 ? "Offerte" : money(deliveryFee)}
        />
        {subtotal < 19.99 && (
          <p className="hint">
            Plus que {money(missingForFreeDelivery)} pour profiter de la livraison offerte.
          </p>
        )}
        <div className="summary-total">
          <span>Total estimé</span>
          <strong>{money(total)}</strong>
        </div>
        <Link className="button primary full" to="/checkout">
          Continuer
        </Link>
      </aside>
    </section>
  );
}

function CheckoutPage({ cart, clearCart }) {
  const [clients, setClients] = useState([]);
  const [clientId, setClientId] = useState("");
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    address: "",
  });
  const [mode, setMode] = useState("existing");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    api.getClients().then(setClients).catch(() => setClients([]));
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    if (!cart.length) {
      setError("Ajoutez d'abord au moins un repas.");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      let selectedClient = clientId;
      if (mode === "new") {
        const client = await api.createClient(form);
        selectedClient = client.id;
      }
      if (!selectedClient) throw new Error("Sélectionnez un client.");

      const order = await api.createOrder({
        client_id: selectedClient,
        items: cart.map((item) => ({
          meal_id: item.id,
          quantity: item.quantity,
        })),
      });

      clearCart();
      navigate(`/tracking/${order.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="page narrow">
      <span className="eyebrow">Finaliser</span>
      <h1>Votre commande</h1>

      <form className="form-card" onSubmit={submit}>
        <div className="segmented">
          <button
            type="button"
            className={mode === "existing" ? "active" : ""}
            onClick={() => setMode("existing")}
          >
            Client existant
          </button>
          <button
            type="button"
            className={mode === "new" ? "active" : ""}
            onClick={() => setMode("new")}
          >
            Nouveau client
          </button>
        </div>

        {mode === "existing" ? (
          <label>
            Client
            <select value={clientId} onChange={(e) => setClientId(e.target.value)}>
              <option value="">Sélectionner...</option>
              {clients.map((client) => (
                <option value={client.id} key={client.id}>
                  {client.first_name} {client.last_name} — {client.email}
                </option>
              ))}
            </select>
          </label>
        ) : (
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
                  onChange={(e) =>
                    setForm((current) => ({
                      ...current,
                      [key]: e.target.value,
                    }))
                  }
                />
              </label>
            ))}
          </div>
        )}

        {error && <p className="form-error">{error}</p>}

        <button className="button primary full" disabled={submitting}>
          {submitting ? "Commande en cours..." : "Commander maintenant"}
        </button>
      </form>
    </section>
  );
}

function TrackingSearchPage() {
  const [id, setId] = useState("");
  const navigate = useNavigate();

  return (
    <section className="page narrow">
      <span className="eyebrow">Suivi en temps réel</span>
      <h1>Suivre une commande</h1>
      <form
        className="form-card inline-form"
        onSubmit={(event) => {
          event.preventDefault();
          if (id.trim()) navigate(`/tracking/${id.trim()}`);
        }}
      >
        <label>
          Identifiant de commande
          <input
            value={id}
            onChange={(e) => setId(e.target.value)}
            placeholder="Ex. 66f..."
          />
        </label>
        <button className="button primary">Afficher le suivi</button>
      </form>
    </section>
  );
}

function TrackingPage() {
  const { id } = useParams();
  const [tracking, setTracking] = useState(null);
  const [error, setError] = useState("");

  const load = () => {
    api
      .getOrderStatus(id)
      .then(setTracking)
      .catch((err) => setError(err.message));
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 15000);
    return () => clearInterval(timer);
  }, [id]);

  if (error) return <section className="page narrow"><StateCard error text={error} /></section>;
  if (!tracking) return <section className="page narrow"><StateCard text="Chargement du suivi..." /></section>;

  const steps = ["pending", "accepted", "preparing", "out_for_delivery", "delivered"];
  const current = steps.indexOf(tracking.status);

  return (
    <section className="page narrow">
      <span className="eyebrow">Commande #{id.slice(-6)}</span>
      <h1>Suivi de livraison</h1>

      <div className="tracking-card">
        <div className="eta">
          <span>Temps estimé</span>
          <strong>
            {tracking.estimated_delivery_minutes == null
              ? "En attente"
              : `${tracking.estimated_delivery_minutes} min`}
          </strong>
        </div>

        <div className="timeline">
          {steps.map((step, index) => (
            <div className={index <= current ? "timeline-step done" : "timeline-step"} key={step}>
              <span />
              <div>
                <strong>{statusLabel(step)}</strong>
                <small>{index <= current ? "Étape atteinte" : "À venir"}</small>
              </div>
            </div>
          ))}
        </div>

        <div className="driver-card">
          <span className="driver-icon">🚲</span>
          <div>
            <small>Livreur</small>
            <strong>{tracking.driver?.first_name || "Attribution en cours"}</strong>
            {tracking.driver?.latitude != null && (
              <span>
                Position : {tracking.driver.latitude.toFixed(4)}, {tracking.driver.longitude.toFixed(4)}
              </span>
            )}
          </div>
          <button className="button secondary small" onClick={load}>
            Actualiser
          </button>
        </div>
      </div>
    </section>
  );
}

function DriversPage() {
  const [drivers, setDrivers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getDrivers().then(setDrivers).catch((err) => setError(err.message));
  }, []);

  return (
    <section className="page">
      <div className="page-heading">
        <div>
          <span className="eyebrow">Flotte de livraison</span>
          <h1>Livreurs</h1>
        </div>
      </div>
      {error && <StateCard error text={error} />}
      <div className="driver-grid">
        {drivers.map((driver) => (
          <article className="driver-list-card" key={driver.id}>
            <div className="avatar">{driver.first_name?.[0] || "L"}</div>
            <div>
              <strong>{driver.first_name} {driver.last_name}</strong>
              <span>{driver.phone}</span>
            </div>
            <StatusBadge status={driver.status} />
          </article>
        ))}
      </div>
    </section>
  );
}

function SummaryLine({ label, value }) {
  return <div className="summary-line"><span>{label}</span><strong>{value}</strong></div>;
}

function StateCard({ text, error = false, children }) {
  return (
    <div className={error ? "state-card error" : "state-card"}>
      <strong>{text}</strong>
      {children}
    </div>
  );
}

function StatusBadge({ status }) {
  return <span className={`status status-${status}`}>{statusLabel(status)}</span>;
}

function statusLabel(status) {
  return {
    pending: "En attente",
    accepted: "Acceptée",
    preparing: "Préparation",
    out_for_delivery: "En livraison",
    delivered: "Livrée",
    cancelled: "Annulée",
    available: "Disponible",
    delivering: "En livraison",
    offline: "Hors ligne",
  }[status] || status;
}

export default function App() {
  const [cart, setCart] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("express-food-cart") || "[]");
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem("express-food-cart", JSON.stringify(cart));
  }, [cart]);

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <Layout cartCount={cartCount}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/menu" element={<MenuPage cart={cart} setCart={setCart} />} />
        <Route path="/cart" element={<CartPage cart={cart} setCart={setCart} />} />
        <Route
          path="/checkout"
          element={<CheckoutPage cart={cart} clearCart={() => setCart([])} />}
        />
        <Route path="/tracking" element={<TrackingSearchPage />} />
        <Route path="/tracking/:id" element={<TrackingPage />} />
        <Route path="/drivers" element={<DriversPage />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="*" element={<section className="page narrow"><StateCard text="Page introuvable." /></section>} />
      </Routes>
    </Layout>
  );
}
