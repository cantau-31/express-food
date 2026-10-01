export const FREE_DELIVERY_THRESHOLD = 19.99;
export const DEFAULT_DELIVERY_FEE = 2.99;

export function calculateCartTotals(cart) {
  const subtotal = cart.reduce(
    (sum, item) => sum + Number(item.price) * Number(item.quantity),
    0
  );

  const deliveryFee =
    subtotal === 0 || subtotal >= FREE_DELIVERY_THRESHOLD
      ? 0
      : DEFAULT_DELIVERY_FEE;

  return {
    subtotal,
    deliveryFee,
    total: subtotal + deliveryFee,
    missingForFreeDelivery:
      subtotal > 0 && subtotal < FREE_DELIVERY_THRESHOLD
        ? FREE_DELIVERY_THRESHOLD - subtotal
        : 0,
  };
}
