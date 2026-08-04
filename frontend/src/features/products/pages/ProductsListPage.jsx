import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Search,
  Package,
  ChevronRight,
  ShoppingBag,
  Sparkles,
  ChevronLeft,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";
import { ProductDetailDrawer } from "../components/ProductDetailDrawer";
import { ProductCard, ProductCardSkeleton } from "../components/ProductCard";

export const ProductsListPage = () => {
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("ALL");
  const [page, setPage] = useState(1);
  const limit = 15;

  // Fetch paginated products from API
  const { data, isLoading, error } = useQuery({
    queryKey: ["productsList", page, search, category],
    queryFn: async () => {
      const categoryParam = category === "ALL" ? "" : category;
      const res = await apiClient.get("products", {
        params: {
          page,
          limit,
          search: search || undefined,
          category: categoryParam || undefined,
        },
      });
      return res.data;
    },
  });

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1); // Reset to page 1 on new search
  };

  const handleCategoryChange = (e) => {
    setCategory(e.target.value);
    setPage(1); // Reset to page 1 on filter
  };

  if (error) {
    return (
      <div className="badge badge-danger" style={{ width: "100%", padding: "var(--space-4)" }}>
        Failed to load product catalogue. Please check your backend connection.
      </div>
    );
  }

  const items = data?.items || [];
  const totalCount = data?.total_count || 0;
  const pagesCount = data?.pages_count || 1;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* Header Toolbar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            Product Catalogue
          </h2>
          <p style={{ color: "var(--gray-text-muted)", fontSize: "14px" }}>
            Browse master registry of retailer-owned SKUs and inspect demand-pricing anomalies.
          </p>
        </div>
      </div>

      {/* Filter Controls Card */}
      <div
        className="card"
        style={{
          padding: "var(--space-4) var(--space-5)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "var(--space-4)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <ShoppingBag size={18} style={{ color: "var(--gray-text-muted)" }} />
          <span style={{ fontSize: "14px", fontWeight: 700 }}>Total SKUs: {totalCount}</span>
        </div>

        <div style={{ display: "flex", gap: "var(--space-3)", flexWrap: "wrap" }}>
          {/* Search Input */}
          <div style={{ position: "relative" }}>
            <Search size={14} style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", color: "var(--gray-text-muted)" }} />
            <input
              type="text"
              placeholder="Search SKU or name..."
              value={search}
              onChange={handleSearchChange}
              style={{
                paddingLeft: "32px",
                height: "36px",
                fontSize: "13px",
                backgroundColor: "rgba(15, 23, 42, 0.6)",
                borderColor: "var(--gray-border)",
                color: "#FFFFFF",
                borderRadius: "var(--radius-default)",
                width: "220px",
              }}
            />
          </div>

          {/* Category Filter */}
          <select
            value={category}
            onChange={handleCategoryChange}
            style={{
              height: "36px",
              fontSize: "13px",
              backgroundColor: "rgba(15, 23, 42, 0.6)",
              borderColor: "var(--gray-border)",
              color: "#FFFFFF",
              borderRadius: "var(--radius-default)",
              padding: "0 var(--space-3)",
            }}
          >
            <option value="ALL">All Categories</option>
            <option value="Dairy">Dairy</option>
            <option value="Bakery">Bakery</option>
            <option value="Beverages">Beverages</option>
            <option value="Snacks">Snacks</option>
            <option value="Household">Household</option>
            <option value="Personal Care">Personal Care</option>
          </select>
        </div>
      </div>

      {/* Responsive Grid of Executive Product Cards */}
      {isLoading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "var(--space-4)" }}>
          {[...Array(6)].map((_, idx) => (
            <ProductCardSkeleton key={idx} />
          ))}
        </div>
      ) : items.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "var(--space-4)" }}>
          {items.map((prod) => (
            <ProductCard
              key={prod.id}
              product={prod}
              onSelect={(id) => setSelectedProductId(id)}
            />
          ))}
        </div>
      ) : (
        <div style={{ padding: "80px var(--space-4)", textAlign: "center" }} className="card">
          <Package size={48} style={{ color: "var(--gray-text-muted)", marginBottom: "var(--space-3)", opacity: 0.5 }} />
          <h4 style={{ color: "var(--gray-text-muted)", marginBottom: "var(--space-2)" }}>No products found in catalogue.</h4>
          <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", marginBottom: "var(--space-4)" }}>
            Upload your first sales CSV dataset to start AI demand forecasting and price optimization analysis.
          </p>
        </div>
      )}

      {/* Pagination Controls */}
      {pagesCount > 1 && (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "var(--space-4)", marginTop: "var(--space-4)" }}>
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn btn-secondary btn-pill"
            style={{ width: "36px", height: "36px", padding: 0, justifyContent: "center" }}
          >
            <ChevronLeft size={16} />
          </button>
          <span style={{ fontSize: "14px", color: "var(--gray-text-muted)" }}>
            Page <strong>{page}</strong> of <strong>{pagesCount}</strong>
          </span>
          <button
            onClick={() => setPage((p) => Math.min(pagesCount, p + 1))}
            disabled={page === pagesCount}
            className="btn btn-secondary btn-pill"
            style={{ width: "36px", height: "36px", padding: 0, justifyContent: "center" }}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      )}

      {/* Slide-over diagnostics drawer */}
      {selectedProductId && (
        <ProductDetailDrawer
          productId={selectedProductId}
          onClose={() => setSelectedProductId(null)}
        />
      )}
    </div>
  );
};
