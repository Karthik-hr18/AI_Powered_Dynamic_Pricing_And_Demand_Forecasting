import io
import matplotlib
matplotlib.use("Agg")  # Non-interactive thread-safe backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Theme colors
COLOR_BG = "#0F172A"
COLOR_CARD = "#1E293B"
COLOR_ACCENT = "#6366F1"
COLOR_SUCCESS = "#22C55E"
COLOR_DANGER = "#EF4444"
COLOR_WARNING = "#F59E0B"
COLOR_PURPLE = "#A855F7"
COLOR_TEXT = "#F8FAFC"
COLOR_MUTED = "#94A3B8"
COLOR_GRID = "rgba(255, 255, 255, 0.08)"

def create_revenue_trend_chart(daily_sales) -> io.BytesIO:
    """Generates a 30-day revenue trend line chart PNG."""
    fig, ax = plt.subplots(figsize=(6.5, 2.5), dpi=200)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    if daily_sales and len(daily_sales) > 0:
        dates = [datetime.strptime(item["date"], "%Y-%m-%d") for item in daily_sales]
        revenues = [item["revenue"] for item in daily_sales]

        ax.plot(dates, revenues, color=COLOR_ACCENT, linewidth=2, marker="o", markersize=3, label="Revenue ($)")
        ax.fill_between(dates, revenues, color=COLOR_ACCENT, alpha=0.15)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    else:
        ax.text(0.5, 0.5, "No revenue data available", color=COLOR_MUTED, ha="center", va="center", transform=ax.transAxes)

    ax.tick_params(colors=COLOR_MUTED, labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_MUTED)
    ax.spines["bottom"].set_color(COLOR_MUTED)
    ax.grid(True, color="#334155", linestyle="--", linewidth=0.5, alpha=0.5)

    plt.title("30-Day Revenue Trend", color=COLOR_TEXT, fontsize=10, fontweight="bold", pad=8)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf

def create_forecast_vs_actual_chart(forecast_vs_actual) -> io.BytesIO:
    """Generates 7-Day Actual vs AI Forecast comparison chart PNG."""
    fig, ax = plt.subplots(figsize=(6.5, 2.5), dpi=200)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    if forecast_vs_actual and len(forecast_vs_actual) > 0:
        dates = [item.get("date", f"Day {i+1}") for i, item in enumerate(forecast_vs_actual)]
        actuals = [item.get("actual", 0) for item in forecast_vs_actual]
        forecasts = [item.get("forecast", 0) for item in forecast_vs_actual]

        ax.plot(dates, actuals, color=COLOR_ACCENT, linewidth=2.5, marker="s", label="Actual Units Sold")
        ax.plot(dates, forecasts, color=COLOR_PURPLE, linewidth=2, linestyle="--", marker="o", label="AI Forecast")
        ax.legend(facecolor=COLOR_CARD, edgecolor=COLOR_MUTED, labelcolor=COLOR_TEXT, fontsize=7, loc="upper left")
    else:
        ax.text(0.5, 0.5, "No forecast tracking dataset available", color=COLOR_MUTED, ha="center", va="center", transform=ax.transAxes)

    ax.tick_params(colors=COLOR_MUTED, labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_MUTED)
    ax.spines["bottom"].set_color(COLOR_MUTED)
    ax.grid(True, color="#334155", linestyle="--", linewidth=0.5, alpha=0.5)

    plt.title("7-Day Actual Units Sold vs. AI Forecast", color=COLOR_TEXT, fontsize=10, fontweight="bold", pad=8)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf

def create_category_pie_chart(category_performance) -> io.BytesIO:
    """Generates Category Revenue Distribution chart PNG."""
    fig, ax = plt.subplots(figsize=(5.5, 2.5), dpi=200)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    if category_performance and len(category_performance) > 0:
        categories = [item.get("category", "Other") for item in category_performance]
        revenues = [item.get("revenue", 0) for item in category_performance]
        colors = [COLOR_ACCENT, COLOR_SUCCESS, COLOR_PURPLE, COLOR_WARNING, "#3B82F6", "#EC4899"]

        wedges, texts, autotexts = ax.pie(
            revenues,
            labels=categories,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors[: len(categories)],
            textprops=dict(color=COLOR_TEXT, fontsize=8),
        )
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(7)
            autotext.set_weight("bold")
    else:
        ax.text(0.5, 0.5, "No category breakdown data available", color=COLOR_MUTED, ha="center", va="center", transform=ax.transAxes)

    plt.title("Category Revenue Distribution", color=COLOR_TEXT, fontsize=10, fontweight="bold", pad=8)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf

def create_inventory_health_chart(inventory_health) -> io.BytesIO:
    """Generates Inventory Stock Health Distribution chart PNG."""
    fig, ax = plt.subplots(figsize=(6.5, 2.0), dpi=200)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    if inventory_health:
        healthy_pct = (inventory_health.get("healthy_pct") if isinstance(inventory_health, dict) else getattr(inventory_health, "healthy_pct", 80.0)) or 80.0
        overstock_pct = (inventory_health.get("overstock_risk_pct") if isinstance(inventory_health, dict) else getattr(inventory_health, "overstock_risk_pct", 15.0)) or 15.0
        stockout_pct = (inventory_health.get("stockout_risk_pct") if isinstance(inventory_health, dict) else getattr(inventory_health, "stockout_risk_pct", 5.0)) or 5.0

        categories = ["Healthy Stock", "Overstock Risk", "Stockout Risk"]
        pcts = [healthy_pct, overstock_pct, stockout_pct]
        bar_colors = [COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER]

        bars = ax.barh(categories, pcts, color=bar_colors, height=0.55)
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height() / 2, f"{width:.1f}%", va="center", color=COLOR_TEXT, fontsize=8, fontweight="bold")

        ax.set_xlim(0, 110)
    else:
        ax.text(0.5, 0.5, "No inventory health data available", color=COLOR_MUTED, ha="center", va="center", transform=ax.transAxes)

    ax.tick_params(colors=COLOR_MUTED, labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_MUTED)
    ax.spines["bottom"].set_color(COLOR_MUTED)
    ax.grid(True, color="#334155", linestyle="--", linewidth=0.5, alpha=0.5, axis="x")

    plt.title("Inventory Health Classification Breakdown", color=COLOR_TEXT, fontsize=10, fontweight="bold", pad=8)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf
