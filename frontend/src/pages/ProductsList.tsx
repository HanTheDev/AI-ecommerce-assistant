import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
  stock: number;
};

export default function ProductsList() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selected, setSelected] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState(1);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8001/products")
      .then((res) => res.json())
      .then((data) => setProducts(data))
      .catch((err) => console.error("Fetch error:", err));
  }, []);

  const handleAddToCart = async (productId: number) => {
    if (!user) {
      navigate("/login");
      return;
    }

    try {
      const res = await fetch("http://localhost:8001/orders/cart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: quantity,
        }),
      });

      if (res.ok) {
        alert("Added to cart successfully!");
        setQuantity(1);
      } else {
        const error = await res.json();
        alert(error.detail || "Failed to add to cart");
      }
    } catch (err) {
      alert("Error adding to cart");
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Our Products</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Available Products</h2>
          <div className="divide-y">
            {products.map((p) => (
              <div
                key={p.id}
                className="p-4 cursor-pointer hover:bg-gray-50 transition duration-150"
                onClick={() => setSelected(p)}
              >
                <h3 className="font-medium text-gray-900">{p.name}</h3>
                <p className="text-sm text-gray-500">Price: ${p.price}</p>
              </div>
            ))}
          </div>
        </div>

        {selected && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">{selected.name}</h2>
            <p className="text-gray-600 mb-4">{selected.description}</p>
            <div className="flex justify-between items-center bg-gray-50 p-4 rounded-lg">
              <div>
                <p className="text-sm text-gray-500">Available Stock</p>
                <p className="font-semibold text-gray-900">
                  {selected.stock} units
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Price</p>
                <p className="text-2xl font-bold text-blue-600">
                  ${selected.price}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="number"
                min="1"
                max={selected.stock}
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                className="w-20 p-2 border rounded"
              />
              <button
                onClick={() => handleAddToCart(selected.id)}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Add to Cart
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
