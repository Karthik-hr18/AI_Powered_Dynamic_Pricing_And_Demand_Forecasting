import React from "react";
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react";

export const EnterprisePagination = ({
  currentPage = 1,
  totalPages = 1,
  totalItems = 0,
  itemsPerPage = 10,
  onPageChange,
  onItemsPerPageChange,
  itemLabel = "Products",
  pageSizeOptions = [10, 20, 50, 100],
}) => {
  const startItem = totalItems > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  // Generate page numbers array with ellipsis logic
  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      let start = Math.max(2, currentPage - 1);
      let end = Math.min(totalPages - 1, currentPage + 1);

      if (currentPage <= 3) {
        end = 4;
      } else if (currentPage >= totalPages - 2) {
        start = totalPages - 3;
      }

      if (start > 2) pages.push("...");

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (end < totalPages - 1) pages.push("...");
      pages.push(totalPages);
    }

    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className="enterprise-pagination-container">
      {/* LEFT: Item range counter */}
      <div className="pagination-left">
        <span className="pagination-summary-text">
          Showing <strong className="pagination-highlight">{startItem}–{endItem}</strong> of{" "}
          <strong className="pagination-highlight">{totalItems}</strong> {itemLabel}
        </span>
      </div>

      {/* CENTER: Rows per page selector */}
      <div className="pagination-center">
        <span className="pagination-rows-label">Rows</span>
        <select
          value={itemsPerPage}
          onChange={(e) => onItemsPerPageChange && onItemsPerPageChange(Number(e.target.value))}
          className="pagination-page-size-select"
          aria-label="Select items per page"
        >
          {pageSizeOptions.map((opt) => (
            <option key={opt} value={opt}>
              {opt} per page
            </option>
          ))}
        </select>
      </div>

      {/* RIGHT: Page Navigation Controls */}
      <div className="pagination-right">
        {/* First Page << */}
        <button
          onClick={() => onPageChange(1)}
          disabled={currentPage === 1}
          className="pagination-btn pagination-btn-nav desktop-only-btn"
          aria-label="First page"
        >
          <ChevronsLeft size={16} />
        </button>

        {/* Previous Page < */}
        <button
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className="pagination-btn pagination-btn-nav"
          aria-label="Previous page"
        >
          <ChevronLeft size={16} />
        </button>

        {/* Desktop Page Numbers */}
        <div className="pagination-page-numbers desktop-tablet-numbers">
          {pageNumbers.map((p, idx) => {
            if (p === "...") {
              return (
                <span key={`ellipsis-${idx}`} className="pagination-ellipsis">
                  ...
                </span>
              );
            }
            const isCurrent = p === currentPage;
            return (
              <button
                key={p}
                onClick={() => onPageChange(p)}
                className={`pagination-btn pagination-btn-num ${
                  isCurrent ? "pagination-btn-active" : ""
                }`}
                aria-current={isCurrent ? "page" : undefined}
              >
                {p}
              </button>
            );
          })}
        </div>

        {/* Mobile Page Counter Text */}
        <span className="pagination-mobile-text mobile-only-text">
          Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
        </span>

        {/* Next Page > */}
        <button
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage >= totalPages || totalItems === 0}
          className="pagination-btn pagination-btn-nav"
          aria-label="Next page"
        >
          <ChevronRight size={16} />
        </button>

        {/* Last Page >> */}
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={currentPage >= totalPages || totalItems === 0}
          className="pagination-btn pagination-btn-nav desktop-only-btn"
          aria-label="Last page"
        >
          <ChevronsRight size={16} />
        </button>
      </div>

      {/* Styled Pagination Utility CSS */}
      <style>{`
        .enterprise-pagination-container {
          padding: 12px 20px;
          border-top: 1px solid var(--gray-border, #E2E8F0);
          background-color: #FFFFFF;
          display: flex;
          justify-content: space-between;
          alignItems: center;
          gap: 16px;
          flex-wrap: wrap;
          border-bottom-left-radius: var(--radius-card, 12px);
          border-bottom-right-radius: var(--radius-card, 12px);
        }

        .pagination-left {
          display: flex;
          align-items: center;
        }

        .pagination-summary-text {
          font-size: 13px;
          color: var(--gray-text-muted, #64748B);
        }

        .pagination-highlight {
          color: var(--gray-text-primary, #0F172A);
          font-weight: 700;
        }

        .pagination-center {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .pagination-rows-label {
          font-size: 12px;
          color: var(--gray-text-muted, #64748B);
          font-weight: 500;
        }

        .pagination-page-size-select {
          height: 32px;
          padding: 0 10px;
          font-size: 12px;
          font-weight: 600;
          background-color: #FFFFFF;
          border: 1px solid var(--gray-border, #E2E8F0);
          color: var(--gray-text-primary, #0F172A);
          border-radius: 8px;
          cursor: pointer;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
          transition: border-color 150ms ease-in-out;
        }

        .pagination-page-size-select:focus {
          outline: none;
          border-color: var(--accent, #4F46E5);
        }

        .pagination-right {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .pagination-page-numbers {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .pagination-btn {
          height: 36px;
          min-width: 36px;
          padding: 0 10px;
          font-size: 13px;
          font-weight: 600;
          border-radius: 10px;
          border: 1px solid var(--gray-border, #E2E8F0);
          background-color: #FFFFFF;
          color: var(--gray-text-primary, #0F172A);
          display: inline-flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
          transition: all 150ms ease-in-out;
        }

        .pagination-btn:hover:not(:disabled) {
          background-color: #F8FAFC;
          border-color: #CBD5E1;
          transform: translateY(-1px);
        }

        .pagination-btn:active:not(:disabled) {
          transform: scale(0.97);
        }

        .pagination-btn:disabled {
          opacity: 0.4;
          cursor: not-allowed;
          box-shadow: none;
        }

        .pagination-btn-active {
          background-color: var(--accent, #4F46E5) !important;
          color: #FFFFFF !important;
          border-color: var(--accent, #4F46E5) !important;
          box-shadow: 0 2px 6px rgba(79, 70, 229, 0.3) !important;
        }

        .pagination-ellipsis {
          padding: 0 6px;
          color: var(--gray-text-muted, #64748B);
          font-size: 13px;
          font-weight: 600;
        }

        .mobile-only-text {
          display: none;
        }

        /* Responsive Breakpoints */
        @media (max-width: 767px) {
          .enterprise-pagination-container {
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 16px 12px;
            gap: 12px;
          }

          .pagination-left {
            order: 1;
          }

          .pagination-right {
            order: 2;
            width: 100%;
            justify-content: center;
            gap: 12px;
          }

          .pagination-center {
            order: 3;
          }

          .desktop-tablet-numbers, .desktop-only-btn {
            display: none !important;
          }

          .mobile-only-text {
            display: inline-block !important;
            font-size: 13px;
            color: var(--gray-text-muted, #64748B);
          }

          .pagination-btn {
            height: 44px;
            min-width: 44px;
            padding: 0 16px;
          }
        }
      `}</style>
    </div>
  );
};
