import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
  stock: number;
};

export default function Admin() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    stock: "",
  });
  const [editId, setEditId] = useState<number | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  // Protect route
  useEffect(() => {
    if (!user?.is_admin) {
      navigate("/");
    }
  }, [user, navigate]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:8001/products");
      if (!res.ok) throw new Error("Failed to fetch products");
      setProducts(await res.json());
    } catch (err) {
      setError("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      setLoading(true);
      const method = editId ? "PUT" : "POST";
      const url = editId
        ? `http://localhost:8001/products/${editId}`
        : "http://localhost:8001/products";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: form.name,
          description: form.description,
          price: parseFloat(form.price),
          stock: parseInt(form.stock),
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to save product");
      }

      setForm({ name: "", description: "", price: "", stock: "" });
      setEditId(null);
      fetchProducts();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this product?")) {
      return;
    }

    try {
      setLoading(true);
      const res = await fetch(`http://localhost:8001/products/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        throw new Error("Failed to delete product");
      }

      fetchProducts();
    } catch (err) {
      setError("Failed to delete product");
    } finally {
      setLoading(false);
    }
  };

  if (!user?.is_admin) {
    return null;
  }

  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8 text-gray-800 border-b pb-4">
        Product Management
      </h1>

      {error && (
        <div className="bg-red-50 text-red-500 p-4 rounded-md mb-6">
          {error}
        </div>
      )}

      {/* Add / Update Form */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Product Name
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              rows={3}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Price
            </label>
            <input
              type="number"
              step="0.01"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stock
            </label>
            <input
              type="number"
              value={form.stock}
              onChange={(e) => setForm({ ...form, stock: e.target.value })}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className={`col-span-2 py-2 px-4 bg-gradient-to-r from-blue-600 to-blue-700 
              text-white rounded-md hover:from-blue-700 hover:to-blue-800 
              transition duration-300 shadow-md ${
                loading ? "opacity-50 cursor-not-allowed" : ""
              }`}
          >
            {loading
              ? "Processing..."
              : editId
              ? "Update Product"
              : "Add Product"}
          </button>
        </form>
      </div>

      {/* Product List */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Product List</h2>
        {loading && <div className="text-center py-4">Loading...</div>}
        <div className="grid gap-4">
          {products.map((p) => (
            <div
              key={p.id}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition duration-150"
            >
              <div className="flex-1 grid grid-cols-4 gap-4">
                <div>
                  <p className="font-semibold text-gray-700">Name</p>
                  <p>{p.name}</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-700">Description</p>
                  <p className="truncate">{p.description}</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-700">Price</p>
                  <p>${p.price.toFixed(2)}</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-700">Stock</p>
                  <p>{p.stock}</p>
                </div>
              </div>
              <div className="flex space-x-2 ml-4">
                <button
                  onClick={() => {
                    setEditId(p.id);
                    setForm({
                      name: p.name,
                      description: p.description,
                      price: p.price.toString(),
                      stock: p.stock.toString(),
                    });
                  }}
                  disabled={loading}
                  className="px-3 py-1 bg-amber-500 text-white rounded-md hover:bg-amber-600 
                    transition duration-150 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(p.id)}
                  disabled={loading}
                  className="px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600 
                    transition duration-150 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}