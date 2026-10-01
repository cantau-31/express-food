/* @vitest-environment jsdom */
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./api", () => ({
  api: {
    getTodayMeals: vi.fn(),
    getClients: vi.fn().mockResolvedValue([]),
    getDrivers: vi.fn().mockResolvedValue([]),
    createClient: vi.fn(),
    createOrder: vi.fn(),
    getOrderStatus: vi.fn(),
    getOrder: vi.fn(),
  },
}));

import App from "./App";
import { api } from "./api";

describe("App", () => {
  afterEach(() => cleanup());

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    api.getClients.mockResolvedValue([]);
    api.getDrivers.mockResolvedValue([]);
    api.getOrderStatus.mockResolvedValue(null);
    api.getOrder.mockResolvedValue(null);
  });

  it("affiche l'accueil et les actions principales", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );

    expect(
      screen.getByRole("heading", {
        name: "Votre repas, prêt et livré rapidement.",
      })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: "Voir le menu du jour" })
    ).toHaveAttribute("href", "/menu");
    expect(
      screen.getByRole("link", { name: "Suivre une commande" })
    ).toHaveAttribute("href", "/tracking");
  });

  it("charge le menu du jour et ajoute un repas au panier", async () => {
    api.getTodayMeals.mockResolvedValue([
      {
        id: "meal-1",
        name: "Poulet citron",
        description: "Plat du jour",
        price: "12.99",
        type: "dish",
        available: true,
      },
    ]);

    render(
      <MemoryRouter initialEntries={["/menu"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Poulet citron")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Ajouter" }));

    expect(screen.getByRole("link", { name: /Panier/ })).toHaveTextContent("1");
    expect(JSON.parse(localStorage.getItem("express-food-cart"))).toEqual([
      expect.objectContaining({ id: "meal-1", quantity: 1 }),
    ]);
  });

  it("affiche le récapitulatif complet d'une commande suivie", async () => {
    api.getOrderStatus.mockResolvedValue({
      order_id: "order-123456",
      status: "accepted",
      driver: { first_name: "Lucas", latitude: 48.85, longitude: 2.35 },
      estimated_delivery_minutes: 20,
    });
    api.getOrder.mockResolvedValue({
      id: "order-123456",
      items: [
        {
          meal_id: "meal-1",
          name: "Poulet citron",
          quantity: 2,
          unit_price: "12.99",
          subtotal: "25.98",
        },
      ],
      subtotal: "25.98",
      delivery_fee: "0.00",
      total: "25.98",
      status: "accepted",
    });

    render(
      <MemoryRouter initialEntries={["/tracking/order-123456"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Lucas")).toBeInTheDocument();
    expect(screen.getByText("2 × Poulet citron")).toBeInTheDocument();
    expect(screen.getByText("Offerte")).toBeInTheDocument();
    expect(screen.getAllByText("25,98 €").length).toBeGreaterThan(0);
  });

  it("crée une commande depuis le checkout et ouvre le suivi", async () => {
    localStorage.setItem(
      "express-food-cart",
      JSON.stringify([
        {
          id: "meal-1",
          name: "Poulet citron",
          price: "12.99",
          type: "dish",
          quantity: 2,
        },
      ])
    );

    api.getClients.mockResolvedValue([
      {
        id: "client-1",
        first_name: "Rayen",
        last_name: "Ouanes",
        email: "rayen@example.com",
      },
    ]);
    api.createOrder.mockResolvedValue({
      id: "order-123456",
    });
    api.getOrderStatus.mockResolvedValue({
      order_id: "order-123456",
      status: "accepted",
      driver: { first_name: "Lucas", latitude: null, longitude: null },
      estimated_delivery_minutes: 20,
    });
    api.getOrder.mockResolvedValue({
      id: "order-123456",
      items: [
        {
          meal_id: "meal-1",
          name: "Poulet citron",
          quantity: 2,
          unit_price: "12.99",
          subtotal: "25.98",
        },
      ],
      subtotal: "25.98",
      delivery_fee: "0.00",
      total: "25.98",
      status: "accepted",
    });

    render(
      <MemoryRouter initialEntries={["/checkout"]}>
        <App />
      </MemoryRouter>
    );

    const select = await screen.findByLabelText("Client");
    fireEvent.change(select, { target: { value: "client-1" } });
    fireEvent.click(
      screen.getByRole("button", { name: "Commander maintenant" })
    );

    expect(api.createOrder).toHaveBeenCalledWith({
      client_id: "client-1",
      items: [{ meal_id: "meal-1", quantity: 2 }],
    });

    expect(
      await screen.findByRole("heading", { name: "Suivi de livraison" })
    ).toBeInTheDocument();

    expect(localStorage.getItem("express-food-cart")).toBe("[]");
  });

  it("affiche une erreur API dans le menu", async () => {
    api.getTodayMeals.mockRejectedValue(new Error("Backend indisponible"));

    render(
      <MemoryRouter initialEntries={["/menu"]}>
        <App />
      </MemoryRouter>
    );

    expect(await screen.findByText("Backend indisponible")).toBeInTheDocument();
  });
});
