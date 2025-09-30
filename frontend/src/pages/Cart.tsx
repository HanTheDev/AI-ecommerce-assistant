import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type CartItem = {
  id: number;
  product: {
    id: number;
    name: string;
    price: number;
  };
  quantity: number;
};

type CartData = {
  items: CartItem[];
  total: number;
};

export default function Cart() {
  const [cart, setCart] = useState<CartData>({ items: [], total: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const res = await fetch("http://localhost:8001/orders/cart", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      console.error("Error fetching cart:", err);
    }
  };

  const removeItem = async (itemId: number) => {
    try {
      const res = await fetch(`http://localhost:8001/orders/cart/${itemId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (res.ok) {
        fetchCart();
      }
    } catch (err) {
      console.error("Error removing item:", err);
    }
  };

  const handleCheckout = async () => {
    try {
      const res = await fetch("http://localhost:8001/orders/checkout", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (res.ok) {
        alert("Order placed successfully!");
        navigate("/orders");
      } else {
        const error = await res.json();
        alert(error.detail || "Checkout failed");
      }
    } catch (err) {
      alert("Error during checkout");
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>

      {cart.items.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Your cart is empty</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            {cart.items.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between py-4 border-b"
              >
                <div>
                  <h3 className="font-medium">{item.product.name}</h3>
                  <p className="text-sm text-gray-500">
                    Quantity: {item.quantity} × ${item.product.price}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <p className="font-bold">
                    ${(item.quantity * item.product.price).toFixed(2)}
                  </p>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">Total:</h3>
              <p className="text-2xl font-bold">${cart.total.toFixed(2)}</p>
            </div>
            <button
              onClick={handleCheckout}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700"
            >
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </div>
  );
}
