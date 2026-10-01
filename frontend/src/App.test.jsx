/* @vitest-environment jsdom */
import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./api", () => ({
  api: {
    getTodayMeals: vi.fn(),
    getClients: vi.fn().mockResolvedValue([]),
    getDrivers: vi.fn().mockResolvedValue([]),
    createClient: vi.fn(),
    createOrder: vi.fn(),
  },
}));

import App from "./App";
import { api } from "./api";

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    api.getClients.mockResolvedValue([]);
    api.getDrivers.mockResolvedValue([]);
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
