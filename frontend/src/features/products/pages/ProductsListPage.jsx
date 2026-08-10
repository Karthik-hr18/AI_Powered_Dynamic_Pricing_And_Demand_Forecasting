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
import { EnterprisePagination } from "../../../shared/components/EnterprisePagination";
import { getErrorMessage } from "../../../shared/utils/errorHandler";
import { AlertTriangle, RefreshCw } from "lucide-react";

export const ProductsListPage = () => {
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [expandedProductId, setExpandedProductId] = useState(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("ALL");
  const [page, setPage] = useState(1);
  const limit = 15;

  // Fetch paginated products from API
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
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
    const errorMsg = getErrorMessage(error, "Unable to load product catalog. Please check your connection.");
    return (
      <div
        role="alert"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "48px 24px",
          backgroundColor: "#FFFFFF",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-card)",
          textAlign: "center",
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.05)",
        }}
      >
        <div
          style={{
            width: "48px",
            height: "48px",
            borderRadius: "12px",
            backgroundColor: "rgba(239, 68, 68, 0.1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: "16px",
          }}
        >
          <AlertTriangle size={24} style={{ color: "#EF4444" }} />
        </div>
        <h3 style={{ fontSize: "18px", fontWeight: 700, margin: "0 0 6px 0", color: "var(--gray-text-primary)" }}>
          Unable to Load Products
        </h3>
        <p style={{ fontSize: "14px", color: "var(--gray-text-muted)", maxWidth: "420px", margin: "0 0 20px 0", lineHeight: 1.5 }}>
          {errorMsg}
        </p>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="btn btn-primary"
          style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "8px 16px" }}
        >
          <RefreshCw size={14} className={isRefetching ? "spin-clockwise" : ""} />
          {isRefetching ? "Retrying..." : "Retry"}
        </button>
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
          <h2 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            Products
          </h2>
        </div>
      </div>

      {/* Filter Controls Card */}
      <div
        className="card"
        style={{
          padding: "var(--space-3) var(--space-4)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "var(--space-3)",
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
                height: "34px",
                fontSize: "12px",
                backgroundColor: "#FFFFFF",
                border: "1px solid var(--gray-border)",
                color: "var(--gray-text-primary)",
                borderRadius: "8px",
                width: "220px",
                boxShadow: "0 1px 2px rgba(0, 0, 0, 0.04)",
              }}
            />
          </div>

          {/* Category Filter */}
          <select
            value={category}
            onChange={handleCategoryChange}
            style={{
              height: "34px",
              fontSize: "12px",
              backgroundColor: "#FFFFFF",
              border: "1px solid var(--gray-border)",
              color: "var(--gray-text-primary)",
              borderRadius: "8px",
              padding: "0 var(--space-3)",
              boxShadow: "0 1px 2px rgba(0, 0, 0, 0.04)",
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
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "var(--space-4)" }}>
          {items.map((prod, idx) => (
            <ProductCard
              key={prod.id || prod.sku || `prod-${prod.sku_display || idx}`}
              product={prod}
              onSelect={(id) => setSelectedProductId(id)}
            />
          ))}
        </div>
      ) : (
        <div className="empty-state-container">
          <div className="empty-state-icon">
            <Package size={26} />
          </div>
          <h4 className="empty-state-title">
            {search || category !== "ALL" ? "No Matching Products Found" : "Product Catalog Empty"}
          </h4>
          <p className="empty-state-desc">
            {search || category !== "ALL"
              ? "We couldn't find any products matching your current search or category filter."
              : "Upload your store's sales CSV dataset to begin demand forecasting and price optimization."}
          </p>
          {search || category !== "ALL" ? (
            <button
              onClick={() => {
                setSearch("");
                setCategory("ALL");
                setPage(1);
              }}
              className="btn btn-secondary"
              style={{ fontSize: "13px", padding: "6px 14px" }}
            >
              Clear Filters
            </button>
          ) : (
            <a
              href="/uploads"
              className="btn btn-primary"
              style={{ fontSize: "13px", padding: "6px 16px", textDecoration: "none" }}
            >
              Upload Sales CSV
            </a>
          )}
        </div>
      )}

      {/* Enterprise Pagination Controls */}
      <div style={{ marginTop: "var(--space-4)" }}>
        <EnterprisePagination
          currentPage={page}
          totalPages={pagesCount}
          totalItems={totalCount}
          itemsPerPage={limit}
          onPageChange={(p) => setPage(p)}
          onItemsPerPageChange={() => {}}
          itemLabel="Products"
          pageSizeOptions={[15, 30, 60]}
        />
      </div>

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
