// Centralized number & currency formatting utilities for ProfitSync AI

/**
 * Formats a currency value rounded to the nearest whole rupee (₹) with zero decimals.
 * Example: 73.56 -> ₹74, 270.71 -> ₹271
 */
export const formatRupee = (val) => {
  const rounded = Math.round(Number(val) || 0);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  }).format(rounded);
};

export const formatCurrency = formatRupee;

/**
 * Formats predicted demand as a clean whole integer with no decimals.
 * Example: 3.2 -> "3 units", 3.7 -> "4 units"
 */
export const formatDemandUnits = (val) => {
  const rounded = Math.round(Number(val) || 0);
  return `${rounded} units`;
};

/**
 * Formats integer count values with standard locale commas.
 * Example: 14820 -> "14,820"
 */
export const formatInteger = (val) => {
  return Math.round(Number(val) || 0).toLocaleString("en-IN");
};
