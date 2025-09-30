import "./index.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import ProductsList from "./pages/ProductsList";
import Admin from "./pages/Admin";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Cart from "./pages/Cart";
import OrderHistory from "./pages/OrderHistory";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function ProtectedAdminRoute() {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!user.is_admin) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">
            Unauthorized Access
          </h1>
          <p className="text-gray-600">
            You don't have permission to access this page.
          </p>
          <Link
            to="/"
            className="mt-4 inline-block text-blue-600 hover:underline"
          >
            Return to Home
          </Link>
        </div>
      </div>
    );
  }

  return <Admin />;
}

function Navigation() {
  const { user } = useAuth();

  const navLinks = [
    {
      to: "/products",
      label: "Products",
      show: true,
    },
    {
      to: "/cart",
      label: "Cart",
      show: !!user,
    },
    {
      to: "/orders",
      label: "Orders",
      show: !!user,
    },
    {
      to: "/admin",
      label: "Admin",
      show: user?.is_admin,
    },
  ];

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex space-x-8 items-center">
            <Link to="/" className="text-xl font-bold text-blue-600">
              EcomAI
            </Link>
            <div className="hidden md:flex space-x-4">
              {navLinks
                .filter((link) => link.show)
                .map(({ to, label }) => (
                  <Link
                    key={to}
                    to={to}
                    className="px-3 py-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50 transition duration-150"
                  >
                    {label}
                  </Link>
                ))}
            </div>
          </div>
          {user ? (
            <Link
              to="/profile"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-150"
            >
              Profile
            </Link>
          ) : (
            <Link
              to="/login"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-150"
            >
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navigation />

        <Routes>
          <Route
            path="/"
            element={
              <div className="min-h-[80vh] bg-gradient-to-br from-blue-50 to-indigo-50">
                <div className="max-w-6xl mx-auto px-4 py-16">
                  <div className="text-center">
                    <h1 className="text-5xl font-bold text-gray-900 mb-6">
                      Welcome to EcomAI Assistant
                    </h1>
                    <p className="text-xl text-gray-600 mb-8">
                      Your intelligent shopping companion powered by AI
                    </p>
                    <div className="flex justify-center space-x-4">
                      <Link
                        to="/products"
                        className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-300 shadow-md"
                      >
                        Browse Products
                      </Link>
                      <Link
                        to="/login"
                        className="px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-50 transition duration-300 shadow-md border border-blue-200"
                      >
                        Sign In
                      </Link>
                    </div>
                  </div>

                  <div className="mt-16 grid md:grid-cols-3 gap-8">
                    <div className="bg-white p-6 rounded-xl shadow-md">
                      <div className="text-blue-600 text-2xl mb-4">🛍️</div>
                      <h3 className="text-xl font-semibold mb-2">
                        Smart Shopping
                      </h3>
                      <p className="text-gray-600">
                        Discover products with AI-powered recommendations
                      </p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-md">
                      <div className="text-blue-600 text-2xl mb-4">🔒</div>
                      <h3 className="text-xl font-semibold mb-2">
                        Secure Platform
                      </h3>
                      <p className="text-gray-600">
                        Shop with confidence on our secure platform
                      </p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-md">
                      <div className="text-blue-600 text-2xl mb-4">⚡</div>
                      <h3 className="text-xl font-semibold mb-2">
                        Fast Delivery
                      </h3>
                      <p className="text-gray-600">
                        Quick and reliable shipping to your doorstep
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            }
          />
          <Route path="/products" element={<ProductsList />} />
          <Route path="/admin" element={<ProtectedAdminRoute />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cart"
            element={
              <ProtectedRoute>
                <Cart />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders"
            element={
              <ProtectedRoute>
                <OrderHistory />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
