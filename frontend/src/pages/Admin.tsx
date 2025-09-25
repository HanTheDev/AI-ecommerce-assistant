import { useState } from "react";

export default function Admin() {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");
  const [desc, setDesc] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem("token");
    const res = await fetch("http://localhost:8001/products", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name,
        description: desc,
        price: parseFloat(price),
        stock: parseInt(stock),
      }),
    });
    console.log(await res.json());
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 space-y-2">
      <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      <input placeholder="Price" value={price} onChange={e => setPrice(e.target.value)} />
      <input placeholder="Stock" value={stock} onChange={e => setStock(e.target.value)} />
      <textarea placeholder="Description" value={desc} onChange={e => setDesc(e.target.value)} />
      <button type="submit">Add Product</button>
    </form>
  );
}