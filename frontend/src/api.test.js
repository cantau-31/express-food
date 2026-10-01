import { afterEach, describe, expect, it, vi } from "vitest";
import { API_BASE_URL, api } from "./api";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function mockResponse({
  ok = true,
  status = 200,
  data = {},
} = {}) {
  return {
    ok,
    status,
    json: vi.fn().mockResolvedValue(data),
  };
}

describe("API client", () => {
  it("charge le menu du jour avec la bonne URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      mockResponse({ data: [{ id: "meal-1", name: "Plat" }] })
    );
    vi.stubGlobal("fetch", fetchMock);

    const data = await api.getTodayMeals();

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/meals/today/`,
      expect.objectContaining({
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
      })
    );
    expect(data[0].id).toBe("meal-1");
  });

  it("envoie une création de commande en POST JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      mockResponse({ status: 201, data: { id: "order-1" } })
    );
    vi.stubGlobal("fetch", fetchMock);

    const payload = {
      client_id: "client-1",
      items: [{ meal_id: "meal-1", quantity: 2 }],
    };

    await api.createOrder(payload);

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/orders/`,
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(payload),
      })
    );
  });

  it("retourne null pour une réponse 204", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 204,
        json: vi.fn(),
      })
    );

    await expect(api.deleteClient("client-1")).resolves.toBeNull();
  });

  it("remonte le message detail du backend", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        mockResponse({
          ok: false,
          status: 400,
          data: { detail: "Commande invalide." },
        })
      )
    );

    await expect(
      api.createOrder({ client_id: "x", items: [] })
    ).rejects.toThrow("Commande invalide.");
  });

  it("concatène les erreurs de validation par champ", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        mockResponse({
          ok: false,
          status: 400,
          data: {
            email: ["Email invalide."],
            phone: ["Téléphone invalide."],
          },
        })
      )
    );

    await expect(
      api.createClient({
        first_name: "R",
        last_name: "O",
        email: "bad",
        phone: "x",
        address: "Test",
      })
    ).rejects.toThrow("Email invalide. Téléphone invalide.");
  });

  it("affiche une erreur claire lorsque le backend est injoignable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("network")));

    await expect(api.getClients()).rejects.toThrow(
      "Impossible de joindre l’API. Vérifiez que le backend est démarré."
    );
  });
});
