import { useState, useEffect } from "react";

type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
  stock: number;
};

export default function Admin() {
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState({ name: "", description: "", price: "", stock: "" });
  const [editId, setEditId] = useState<number | null>(null);

  const token = localStorage.getItem("token");

  const fetchProducts = async () => {
    const res = await fetch("http://localhost:8001/products");
    setProducts(await res.json());
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const method = editId ? "PUT" : "POST";
    const url = editId
      ? `http://localhost:8001/products/${editId}`
      : "http://localhost:8001/products";

    await fetch(url, {
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

    setForm({ name: "", description: "", price: "", stock: "" });
    setEditId(null);
    fetchProducts();
  };

  const handleDelete = async (id: number) => {
    await fetch(`http://localhost:8001/products/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    fetchProducts();
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Admin Panel</h1>

      {/* Add / Update Form */}
      <form onSubmit={handleSubmit} className="space-y-2 mb-6">
        <input
          placeholder="Name"
          value={form.name}
          onChange={e => setForm({ ...form, name: e.target.value })}
          className="border p-2 w-full"
        />
        <input
          placeholder="Price"
          value={form.price}
          onChange={e => setForm({ ...form, price: e.target.value })}
          className="border p-2 w-full"
        />
        <input
          placeholder="Stock"
          value={form.stock}
          onChange={e => setForm({ ...form, stock: e.target.value })}
          className="border p-2 w-full"
        />
        <textarea
          placeholder="Description"
          value={form.description}
          onChange={e => setForm({ ...form, description: e.target.value })}
          className="border p-2 w-full"
        />
        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">
          {editId ? "Update Product" : "Add Product"}
        </button>
      </form>

      {/* Product List with Edit/Delete */}
      <ul className="space-y-2">
        {products.map(p => (
          <li key={p.id} className="p-2 border rounded flex justify-between">
            <span>{p.name} - ${p.price}</span>
            <div className="space-x-2">
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
                className="px-2 py-1 bg-yellow-500 text-white rounded"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(p.id)}
                className="px-2 py-1 bg-red-600 text-white rounded"
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}