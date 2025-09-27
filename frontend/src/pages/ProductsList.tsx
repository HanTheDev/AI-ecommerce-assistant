import { useEffect, useState } from "react";

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

  useEffect(() => {
    fetch("http://localhost:8001/products")
      .then((res) => {
        console.log("Response status:", res.status);
        return res.json();
      })
      .then((data) => {
        console.log("Fetched products:", data);
        setProducts(data);
      })
      .catch((err) => console.error("Fetch error:", err));
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-red-500 text-3xl">Hello Tailwind</h2>
      <h1 className="text-xl font-bold mb-4">Products</h1>
      <ul className="space-y-2">
        {products.map((p) => (
          <li
            key={p.id}
            className="p-2 border rounded cursor-pointer hover:bg-gray-50"
            onClick={() => setSelected(p)}
          >
            {p.name} - ${p.price}
          </li>
        ))}
      </ul>

      {selected && (
        <div className="mt-4 p-4 border rounded">
          <h2 className="text-lg font-bold">{selected.name}</h2>
          <p>{selected.description}</p>
          <p className="text-sm text-gray-600">Stock: {selected.stock}</p>
          <p className="font-semibold">Price: ${selected.price}</p>
        </div>
      )}
    </div>
  );
}
