import { describe, expect, it } from "vitest";
import {
  FREE_DELIVERY_THRESHOLD,
  calculateCartTotals,
} from "./cart";

describe("calculateCartTotals", () => {
  it("calcule correctement le sous-total", () => {
    const result = calculateCartTotals([
      { price: "12.99", quantity: 2 },
      { price: "4.50", quantity: 1 },
    ]);

    expect(result.subtotal).toBeCloseTo(30.48, 2);
    expect(result.total).toBeCloseTo(30.48, 2);
  });

  it("applique les frais sous le seuil", () => {
    const result = calculateCartTotals([
      { price: "12.99", quantity: 1 },
    ]);

    expect(result.deliveryFee).toBeCloseTo(2.99, 2);
    expect(result.total).toBeCloseTo(15.98, 2);
    expect(result.missingForFreeDelivery).toBeCloseTo(7.0, 2);
  });

  it("offre la livraison exactement à 19,99 €", () => {
    const result = calculateCartTotals([
      { price: FREE_DELIVERY_THRESHOLD, quantity: 1 },
    ]);

    expect(result.deliveryFee).toBe(0);
    expect(result.total).toBeCloseTo(FREE_DELIVERY_THRESHOLD, 2);
    expect(result.missingForFreeDelivery).toBe(0);
  });

  it("ne facture rien pour un panier vide", () => {
    const result = calculateCartTotals([]);

    expect(result.subtotal).toBe(0);
    expect(result.deliveryFee).toBe(0);
    expect(result.total).toBe(0);
  });
});
