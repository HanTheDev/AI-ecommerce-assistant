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
          </div>
        )}
      </div>
    </div>
  );
}
