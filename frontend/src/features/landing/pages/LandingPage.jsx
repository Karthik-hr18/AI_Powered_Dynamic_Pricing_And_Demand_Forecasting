import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  TrendingUp,
  Package,
  Layers,
  Sparkles,
  BarChart2,
  FileText,
  UploadCloud,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ArrowRight,
  ShieldCheck,
  Zap,
  Activity,
  Award,
  Globe,
  Menu,
  X,
} from "lucide-react";

import { useAuth } from "../../../shared/hooks/useAuth";

export const LandingPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);

  // Scroll listener for sticky glassmorphism navbar
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Update document title for SEO
  useEffect(() => {
    document.title = "ProfitSync — Executive Retail Analytics & Demand Forecasting";
  }, []);

  const toggleFaq = (idx) => {
    setOpenFaq(openFaq === idx ? null : idx);
  };

  const handleCtaClick = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/register");
    }
  };

  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="landing-wrapper">
      {/* -------------------------------------------------------------------------- */}
      {/* MOBILE NAV BACKDROP */}
      {mobileNavOpen && (
        <div
          className="landing-mobile-backdrop"
          onClick={() => setMobileNavOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            backgroundColor: "rgba(9,13,22,0.5)",
            backdropFilter: "blur(4px)",
            zIndex: 200,
          }}
        />
      )}

      {/* MOBILE SIDEBAR DRAWER */}
      <div
        className="landing-mobile-sidebar"
        style={{
          position: "fixed",
          top: 0,
          right: mobileNavOpen ? 0 : "-100%",
          width: "280px",
          height: "100%",
          backgroundColor: "#FFFFFF",
          zIndex: 201,
          display: "flex",
          flexDirection: "column",
          padding: "24px 20px",
          gap: "8px",
          boxShadow: "-12px 0 40px rgba(0,0,0,0.08)",
          transition: "right 280ms cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      >
        {/* Sidebar header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
          <Link to="/" className="brand-logo" onClick={() => setMobileNavOpen(false)}>
            <div className="brand-icon-pill">P</div>
            <span className="brand-text">ProfitSync</span>
          </Link>
          <button
            onClick={() => setMobileNavOpen(false)}
            style={{ background: "#F1F5F9", border: "none", borderRadius: "50%", width: "36px", height: "36px", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: "#64748B" }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Nav links */}
        {[
          { label: "Features", href: "#features" },
          { label: "How It Works", href: "#how-it-works" },
          { label: "Why ProfitSync", href: "#comparison" },
          { label: "FAQ", href: "#faq" },
        ].map((item) => (
          <a
            key={item.href}
            href={item.href}
            onClick={() => setMobileNavOpen(false)}
            style={{
              display: "block",
              padding: "14px 16px",
              borderRadius: "10px",
              color: "#0F172A",
              fontWeight: 600,
              fontSize: "15px",
              textDecoration: "none",
              minHeight: "44px",
              lineHeight: "1.4",
              transition: "background 150ms ease",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#F8FAFC")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
          >
            {item.label}
          </a>
        ))}

        <div style={{ borderTop: "1px solid #E2E8F0", marginTop: "12px", paddingTop: "16px", display: "flex", flexDirection: "column", gap: "10px" }}>
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              onClick={() => setMobileNavOpen(false)}
              className="btn btn-primary btn-pill"
              style={{ width: "100%", justifyContent: "center", height: "46px", fontSize: "15px" }}
            >
              Go to Dashboard
              <ArrowRight size={16} />
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                onClick={() => setMobileNavOpen(false)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "46px",
                  padding: "0 16px",
                  borderRadius: "9999px",
                  border: "1.5px solid #4F46E5",
                  color: "#4F46E5",
                  fontWeight: 600,
                  fontSize: "15px",
                  textDecoration: "none",
                }}
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileNavOpen(false)}
                className="btn btn-primary btn-pill"
                style={{ width: "100%", justifyContent: "center", height: "46px", fontSize: "15px" }}
              >
                Get Started Free
              </Link>
            </>
          )}
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* NAVBAR */}
      {/* -------------------------------------------------------------------------- */}
      <header className={`landing-navbar ${isScrolled ? "scrolled" : ""}`}>
        <div className="landing-container nav-container">
          <Link to="/" className="brand-logo">
            <div className="brand-icon-pill">P</div>
            <span className="brand-text">ProfitSync</span>
          </Link>

          {/* Desktop nav links with subtle underline hover */}
          <nav className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#comparison">Why ProfitSync</a>
            <a href="#faq">FAQ</a>
          </nav>

          {/* Desktop CTA buttons */}
          <div className="nav-actions">
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary btn-pill nav-cta-btn">
                Go to Dashboard
                <ArrowRight size={14} />
              </Link>
            ) : (
              <>
                <Link to="/login" className="nav-link-login">Sign In</Link>
                <Link to="/register" className="btn btn-primary btn-pill nav-cta-btn">
                  Get Started
                </Link>
              </>
            )}
          </div>

          {/* Mobile hamburger button */}
          <button
            className="nav-hamburger"
            onClick={() => setMobileNavOpen(true)}
            aria-label="Open navigation menu"
            style={{
              display: "none",
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: "6px",
              color: "#0F172A",
              borderRadius: "8px",
            }}
          >
            <Menu size={24} />
          </button>
        </div>
      </header>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 1: HERO */}
      {/* -------------------------------------------------------------------------- */}
      <section className="hero-section">
        <div className="landing-container hero-grid">
          <div className="hero-content">
            <div className="hero-badge">
              <ShieldCheck size={14} className="badge-icon" />
              Enterprise Retail Analytics
            </div>
            <h1 className="hero-title">
              Pricing decisions backed by real business insights.
            </h1>
            <p className="hero-subtitle">
              Monitor sales trends, forecast inventory demand, evaluate pricing recommendations, and export executive reports from one unified analytics platform.
            </p>
            <div className="hero-ctas">
              <button onClick={handleCtaClick} className="btn btn-primary btn-lg btn-pill hero-cta-primary">
                Get Started Free
                <ArrowRight size={16} />
              </button>
              <Link
                to={isAuthenticated ? "/dashboard" : "/login"}
                className="hero-cta-ghost btn-pill"
              >
                View Live Demo
              </Link>
            </div>
            <div className="hero-trust-metrics">
              <div className="metric-item">
                <strong>99.4%</strong>
                <span>Forecast Accuracy</span>
              </div>
              <div className="metric-divider" />
              <div className="metric-item">
                <strong>₹4.2M+</strong>
                <span>Revenue Analyzed</span>
              </div>
              <div className="metric-divider" />
              <div className="metric-item">
                <strong>Instant</strong>
                <span>Report Exports</span>
              </div>
            </div>
          </div>

          {/* Right Hero Dashboard Visual */}
          <div className="hero-visual">
            <div className="browser-mockup">
              <div className="browser-header">
                <div className="browser-dots">
                  <span className="dot red" />
                  <span className="dot yellow" />
                  <span className="dot green" />
                </div>
                <div className="browser-address">profitsync.app/dashboard</div>
              </div>
              <div className="browser-body">
                {/* Mini Mock Dashboard UI */}
                <div className="mock-kpi-row">
                  <div className="mock-card">
                    <span className="mock-label">30-Day Revenue</span>
                    <strong className="mock-value">₹1,42,850</strong>
                    <span className="mock-trend green">+12.4% vs last mo</span>
                  </div>
                  <div className="mock-card">
                    <span className="mock-label">Forecasted Demand</span>
                    <strong className="mock-value">12,450 Units</strong>
                    <span className="mock-trend purple">High Confidence</span>
                  </div>
                  <div className="mock-card">
                    <span className="mock-label">Inventory Health</span>
                    <strong className="mock-value">94/100</strong>
                    <span className="mock-trend green">Healthy</span>
                  </div>
                </div>

                <div className="mock-chart-container">
                  <div className="mock-chart-header">
                    <span>Demand & Sales Trend</span>
                    <span className="mock-badge">7-Day Forecast</span>
                  </div>
                  <div className="mock-chart-bars">
                    <div className="bar-column"><div className="bar" style={{ height: "45%" }} /><span>Mon</span></div>
                    <div className="bar-column"><div className="bar" style={{ height: "60%" }} /><span>Tue</span></div>
                    <div className="bar-column"><div className="bar" style={{ height: "75%" }} /><span>Wed</span></div>
                    <div className="bar-column"><div className="bar" style={{ height: "50%" }} /><span>Thu</span></div>
                    <div className="bar-column"><div className="bar active" style={{ height: "90%" }} /><span>Fri</span></div>
                    <div className="bar-column"><div className="bar" style={{ height: "65%" }} /><span>Sat</span></div>
                    <div className="bar-column"><div className="bar" style={{ height: "80%" }} /><span>Sun</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 2: TRUSTED FEATURES */}
      {/* -------------------------------------------------------------------------- */}
      <section id="features" className="features-section">
        <div className="landing-container">
          <div className="section-header center">
            <span className="section-tag">Core Features</span>
            <h2 className="section-title">Built for high-performance retail analytics</h2>
            <p className="section-desc">
              Everything you need to turn raw point-of-sale data into actionable profit strategies.
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-wrapper accent">
                <BarChart2 size={24} />
              </div>
              <h3>Sales Analytics</h3>
              <p>Track revenue, unit volumes, and profit margins with clear executive dashboards.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper success">
                <TrendingUp size={24} />
              </div>
              <h3>Demand Forecasting</h3>
              <p>Predict upcoming 7-day SKU demand accurately to align inventory replenishment.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper warning">
                <Zap size={24} />
              </div>
              <h3>Pricing Recommendations</h3>
              <p>Automate optimal price points based on elasticity, cost, and sales velocity.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper purple">
                <Package size={24} />
              </div>
              <h3>Inventory Monitoring</h3>
              <p>Prevent stockout risks and overstock drag with continuous stock health metrics.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper info">
                <FileText size={24} />
              </div>
              <h3>Executive Reports</h3>
              <p>Export executive PDF and CSV reports for board reviews and store management.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper primary">
                <UploadCloud size={24} />
              </div>
              <h3>CSV & Excel Import</h3>
              <p>Upload sales files in seconds without complex database integration required.</p>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 3: HOW IT WORKS */}
      {/* -------------------------------------------------------------------------- */}
      <section id="how-it-works" className="timeline-section">
        <div className="landing-container">
          <div className="section-header center">
            <span className="section-tag">Workflow</span>
            <h2 className="section-title">How ProfitSync Works</h2>
            <p className="section-desc">
              Go from raw sales uploads to optimized pricing decisions in five simple steps.
            </p>
          </div>

          <div className="timeline-grid">
            <div className="timeline-step">
              <div className="step-num">1</div>
              <h4>Upload Sales Data</h4>
              <p>Drag and drop standard sales CSV or Excel export files into the upload manager.</p>
            </div>

            <div className="timeline-step">
              <div className="step-num">2</div>
              <h4>Data Processing</h4>
              <p>Automated validation checks clean and structure data across categories and SKUs.</p>
            </div>

            <div className="timeline-step">
              <div className="step-num">3</div>
              <h4>Business Analytics</h4>
              <p>Algorithms analyze historical trends, margin velocity, and sales patterns.</p>
            </div>

            <div className="timeline-step">
              <div className="step-num">4</div>
              <h4>Pricing Strategy</h4>
              <p>Receive actionable price adjustments and inventory health warnings per product.</p>
            </div>

            <div className="timeline-step">
              <div className="step-num">5</div>
              <h4>Executive Action</h4>
              <p>Apply recommendations or export formatted executive reports instantly.</p>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 4: DASHBOARD PREVIEW */}
      {/* -------------------------------------------------------------------------- */}
      <section className="preview-section">
        <div className="landing-container">
          <div className="section-header center">
            <span className="section-tag">Platform Preview</span>
            <h2 className="section-title">Clean, intuitive analytics dashboard</h2>
            <p className="section-desc">
              Designed specifically for fast retail decision making with zero clutter.
            </p>
          </div>

          <div className="large-preview-card">
            <div className="preview-header">
              <div className="browser-dots">
                <span className="dot red" />
                <span className="dot yellow" />
                <span className="dot green" />
              </div>
              <div className="preview-title">ProfitSync Executive Dashboard</div>
            </div>
            <div className="preview-body">
              {/* Callout badges — hidden on mobile via CSS */}
              <div className="preview-badge-callout callout-1 preview-callout-hide-mobile">
                <TrendingUp size={14} /> Revenue Opportunities: +₹24,500
              </div>
              <div className="preview-badge-callout callout-2 preview-callout-hide-mobile">
                <ShieldCheck size={14} /> Inventory Health: 94% Healthy
              </div>

              {/* Inline callouts for mobile only */}
              <div className="preview-inline-callouts">
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "12px" }}>
                  <span className="preview-inline-badge" style={{ borderColor: "#10B981", color: "#34D399" }}>
                    <TrendingUp size={11} /> Revenue Opportunities: +₹24,500
                  </span>
                  <span className="preview-inline-badge" style={{ borderColor: "#4F46E5", color: "#818CF8" }}>
                    <ShieldCheck size={11} /> Inventory Health: 94% Healthy
                  </span>
                </div>
              </div>

              <div className="mock-grid-main">
                <div className="mock-panel full">
                  <h4>Active Product Diagnostics Grid</h4>
                  <div className="mock-table-scroll-wrapper">
                    <div className="mock-table">
                      <div className="table-header-row">
                        <span>SKU</span><span>Product Name</span><span>Category</span><span>Forecast</span><span>Recommended</span><span>Status</span>
                      </div>
                      <div className="table-data-row">
                        <span>SKU-8821</span><span>Organic Green Tea 250g</span><span>Beverages</span><span>320 Units</span><span className="green">₹145.00</span><span className="badge-status success">Healthy</span>
                      </div>
                      <div className="table-data-row">
                        <span>SKU-4412</span><span>Basmati Rice 5kg</span><span>Grains</span><span>1,420 Units</span><span className="green">₹620.00</span><span className="badge-status warning">Stockout Risk</span>
                      </div>
                      <div className="table-data-row">
                        <span>SKU-9904</span><span>Dark Chocolate 100g</span><span>Snacks</span><span>180 Units</span><span className="green">₹95.00</span><span className="badge-status primary">Stable</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 5: BUSINESS BENEFITS */}
      {/* -------------------------------------------------------------------------- */}
      <section className="benefits-section">
        <div className="landing-container benefits-grid">
          <div className="benefits-illustration">
            <div className="benefit-card-stat">
              <Award size={32} style={{ color: "var(--accent)" }} />
              <div>
                <strong>+14.8% Average Profit Margin</strong>
                <p>Retail stores utilizing automated price recommendations see immediate margin gains.</p>
              </div>
            </div>
            <div className="benefit-card-stat">
              <Activity size={32} style={{ color: "#059669" }} />
              <div>
                <strong>Zero Manual Spreadsheets</strong>
                <p>Eliminate human error and manual formula tracking across hundreds of SKUs.</p>
              </div>
            </div>
          </div>

          <div className="benefits-content">
            <span className="section-tag">Business Value</span>
            <h2 className="section-title">Engineered to drive retail profitability</h2>
            <ul className="benefits-list">
              <li>
                <CheckCircle2 size={20} className="check-icon" />
                <div>
                  <strong>Increase Pricing Confidence</strong>
                  <p>Base price adjustments on data trends rather than guesswork.</p>
                </div>
              </li>
              <li>
                <CheckCircle2 size={20} className="check-icon" />
                <div>
                  <strong>Reduce Stockout Risks</strong>
                  <p>Receive early alerts when fast-selling inventory runs low.</p>
                </div>
              </li>
              <li>
                <CheckCircle2 size={20} className="check-icon" />
                <div>
                  <strong>Centralize Multi-Category Reporting</strong>
                  <p>Consolidate all retail categories into a single executive dashboard.</p>
                </div>
              </li>
              <li>
                <CheckCircle2 size={20} className="check-icon" />
                <div>
                  <strong>Generate Instant PDF Reports</strong>
                  <p>Create board-ready PDF summaries in a single click.</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 6: WHY CHOOSE THIS PLATFORM */}
      {/* -------------------------------------------------------------------------- */}
      <section id="comparison" className="comparison-section">
        <div className="landing-container">
          <div className="section-header center">
            <span className="section-tag">Comparison</span>
            <h2 className="section-title">Traditional Spreadsheets vs ProfitSync</h2>
            <p className="section-desc">See why modern retailers are upgrading from legacy tools.</p>
          </div>

          <div className="comparison-grid">
            {/* Traditional Column */}
            <div className="comparison-card traditional">
              <div className="comparison-header">
                <h3>Traditional Spreadsheets</h3>
                <p>Manual static reporting</p>
              </div>
              <ul className="comparison-list">
                <li><XCircle size={18} className="cross-icon" /> Manual VLOOKUP formulas and broken links</li>
                <li><XCircle size={18} className="cross-icon" /> Delayed reporting and stale sales data</li>
                <li><XCircle size={18} className="cross-icon" /> Static pricing with no demand responsiveness</li>
                <li><XCircle size={18} className="cross-icon" /> No automated stockout risk alerts</li>
                <li><XCircle size={18} className="cross-icon" /> Fragmented files across store managers</li>
              </ul>
            </div>

            {/* ProfitSync Column */}
            <div className="comparison-card platform highlight">
              <div className="recommended-badge">Recommended</div>
              <div className="comparison-header">
                <h3>ProfitSync Platform</h3>
                <p>Automated retail analytics</p>
              </div>
              <ul className="comparison-list">
                <li><CheckCircle2 size={18} className="check-icon" /> Automated CSV data cleaning & processing</li>
                <li><CheckCircle2 size={18} className="check-icon" /> Live executive dashboards & instant updates</li>
                <li><CheckCircle2 size={18} className="check-icon" /> 7-day demand forecasting & price optimization</li>
                <li><CheckCircle2 size={18} className="check-icon" /> Automated inventory health & risk alerts</li>
                <li><CheckCircle2 size={18} className="check-icon" /> One-click executive PDF report generation</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 7: TESTIMONIALS */}
      {/* -------------------------------------------------------------------------- */}
      <section className="testimonials-section">
        <div className="landing-container">
          <div className="section-header center">
            <span className="section-tag">Proven Results</span>
            <h2 className="section-title">Trusted by retail businesses</h2>
          </div>

          <div className="testimonials-grid">
            <div className="testimonial-card">
              <p className="testimonial-quote">
                "ProfitSync gave us clear visibility into SKU demand. We reduced stockout risks by 35% during holiday sale peaks."
              </p>
              <div className="testimonial-author">
                <strong>Apex Supermarkets</strong>
                <span>Grocery Superstore Chain</span>
              </div>
            </div>

            <div className="testimonial-card">
              <p className="testimonial-quote">
                "The price recommendations helped us adjust margins without hurting unit sales volume. The PDF report exports save us hours."
              </p>
              <div className="testimonial-author">
                <strong>HealthCare Pharma</strong>
                <span>Retail Pharmacy Network</span>
              </div>
            </div>

            <div className="testimonial-card">
              <p className="testimonial-quote">
                "Simple to use and zero learning curve. We uploaded our monthly sales file and had diagnostic insights in less than two minutes."
              </p>
              <div className="testimonial-author">
                <strong>Express Mart</strong>
                <span>Convenience Retail Store</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 8: FAQ */}
      {/* -------------------------------------------------------------------------- */}
      <section id="faq" className="faq-section">
        <div className="landing-container">
          <div className="section-header center">
            <span className="section-tag">FAQ</span>
            <h2 className="section-title">Frequently Asked Questions</h2>
          </div>

          <div className="faq-accordion">
            {[
              {
                q: "What file formats are supported for sales uploads?",
                a: "ProfitSync supports standard CSV and Excel (.xlsx) sales export files from POS systems, Shopify, Square, and custom inventory exports.",
              },
              {
                q: "How secure is my business sales data?",
                a: "Your data is protected with enterprise encryption in transit and at rest. We enforce strict role-based access controls and never share your proprietary store metrics.",
              },
              {
                q: "Can I export executive reports for my team?",
                a: "Yes, you can generate formatted PDF executive reports and download structured CSV datasets at any time from the Report Center.",
              },
              {
                q: "Do I need technical knowledge or coding skills?",
                a: "Not at all. ProfitSync is designed for store owners, category managers, and retail executives. Simply upload your sales spreadsheet to view instant analytics.",
              },
              {
                q: "Can I try ProfitSync with sample demo data?",
                a: "Yes! Every account includes pre-loaded sample datasets so you can explore all forecasting, pricing, and report features immediately.",
              },
            ].map((faq, idx) => (
              <div
                key={idx}
                className={`faq-item ${openFaq === idx ? "active" : ""}`}
                onClick={() => toggleFaq(idx)}
              >
                <div className="faq-question">
                  <span>{faq.q}</span>
                  <ChevronDown size={18} className="faq-arrow" />
                </div>
                {openFaq === idx && <div className="faq-answer">{faq.a}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* SECTION 9: CALL TO ACTION BANNER */}
      {/* -------------------------------------------------------------------------- */}
      <section className="cta-banner-section">
        <div className="landing-container">
          <div className="cta-banner-card">
            <h2>Ready to improve retail pricing decisions?</h2>
            <p>Join retail businesses using ProfitSync for analytics and forecasting.</p>
            <div className="cta-actions">
              <button onClick={handleCtaClick} className="btn btn-primary btn-lg btn-pill">
                Create Free Account
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* -------------------------------------------------------------------------- */}
      {/* FOOTER */}
      {/* -------------------------------------------------------------------------- */}
      <footer className="landing-footer">
        <div className="landing-container footer-grid">
          <div className="footer-brand">
            <div className="brand-logo">
              <div className="brand-icon-pill">P</div>
              <span className="brand-text">ProfitSync</span>
            </div>
            <p className="footer-tagline">
              Enterprise retail analytics, 7-day demand forecasting, and price optimization.
            </p>
          </div>

          <div className="footer-column">
            <h4>Product</h4>
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#comparison">Why ProfitSync</a>
            <Link to={isAuthenticated ? "/dashboard" : "/login"}>Dashboard</Link>
          </div>

          <div className="footer-column">
            <h4>Resources</h4>
            <a href="#faq">FAQ</a>
            <Link to="/login">Sign In</Link>
            <Link to="/register">Create Account</Link>
          </div>

          <div className="footer-column">
            <h4>Legal</h4>
            <a href="#privacy">Privacy Policy</a>
            <a href="#terms">Terms of Service</a>
            <a href="#security">Security Overview</a>
          </div>
        </div>

        <div className="landing-container footer-bottom">
          <span>&copy; {new Date().getFullYear()} ProfitSync Inc. All rights reserved.</span>
          <div className="footer-socials">
            <a href="https://github.com/Karthik-hr18/AI_Powered_Dynamic_Pricing_And_Demand_Forecasting" target="_blank" rel="noopener noreferrer">
              <Globe size={16} /> GitHub Repository
            </a>
          </div>
        </div>
      </footer>

      {/* -------------------------------------------------------------------------- */}
      {/* EMBEDDED STYLESHEET FOR SAAS LANDING PAGE */}
      {/* -------------------------------------------------------------------------- */}
      <style>{`
        .landing-wrapper {
          background-color: #F8FAFC;
          color: #0F172A;
          font-family: var(--font-sans, system-ui, -apple-system, sans-serif);
          overflow-x: hidden;
        }

        .landing-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 24px;
        }

        /* Navbar */
        .landing-navbar {
          position: sticky;
          top: 0;
          z-index: 100;
          background-color: rgba(248, 250, 252, 0.92);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border-bottom: 1px solid #E2E8F0;
          transition: all 200ms ease-in-out;
          box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }
        .landing-navbar.scrolled {
          background-color: rgba(255, 255, 255, 0.98);
          border-bottom-color: #CBD5E1;
          box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }
        .nav-container {
          height: 72px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        .brand-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          text-decoration: none;
        }
        .brand-icon-pill {
          width: 34px;
          height: 34px;
          background: linear-gradient(135deg, #4F46E5, #3730A3);
          color: #FFFFFF;
          border-radius: 9px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 16px;
          box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
        }
        .brand-text {
          font-size: 18px;
          font-weight: 800;
          color: #0F172A;
          letter-spacing: -0.025em;
        }
        .nav-links {
          display: flex;
          gap: 4px;
          align-items: center;
        }
        .nav-links a {
          text-decoration: none;
          color: #475569;
          font-size: 14px;
          font-weight: 500;
          padding: 6px 14px;
          border-radius: 8px;
          transition: all 150ms ease;
          position: relative;
        }
        .nav-links a:hover {
          color: #4F46E5;
          background-color: #EEF2FF;
        }
        .nav-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .nav-link-login {
          text-decoration: none;
          color: #0F172A;
          font-size: 14px;
          font-weight: 600;
          padding: 8px 14px;
          border-radius: 8px;
          transition: background 150ms ease;
        }
        .nav-link-login:hover {
          background-color: #F1F5F9;
        }
        .nav-cta-btn {
          font-size: 14px !important;
          height: 38px !important;
          padding: 0 18px !important;
          box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        }

        /* Hero Section */
        .hero-section {
          padding: 80px 0 100px 0;
          background: radial-gradient(circle at 80% 20%, rgba(79, 70, 229, 0.06) 0%, transparent 50%);
        }
        .hero-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 48px;
          align-items: center;
        }
        .hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background-color: #EEF2FF;
          color: #4F46E5;
          padding: 6px 14px;
          border-radius: 9999px;
          font-size: 12px;
          font-weight: 600;
          margin-bottom: 20px;
        }
        .hero-title {
          font-size: 48px;
          font-weight: 800;
          line-height: 1.15;
          letter-spacing: -0.03em;
          color: #0F172A;
          margin-bottom: 20px;
        }
        .hero-subtitle {
          font-size: 17px;
          line-height: 1.6;
          color: #475569;
          margin-bottom: 32px;
        }
        .hero-ctas {
          display: flex;
          gap: 16px;
          margin-bottom: 40px;
          align-items: center;
        }
        .hero-cta-primary {
          box-shadow: 0 8px 24px rgba(79, 70, 229, 0.3) !important;
          transition: all 200ms ease !important;
        }
        .hero-cta-primary:hover {
          transform: translateY(-2px) !important;
          box-shadow: 0 12px 32px rgba(79, 70, 229, 0.4) !important;
        }
        .hero-cta-ghost {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          height: 48px;
          padding: 0 24px;
          font-size: 15px;
          font-weight: 600;
          color: #0F172A;
          background-color: #FFFFFF;
          border: 1.5px solid #CBD5E1;
          border-radius: 9999px;
          text-decoration: none;
          transition: all 200ms ease;
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
          cursor: pointer;
        }
        .hero-cta-ghost:hover {
          border-color: #4F46E5;
          color: #4F46E5;
          background-color: #EEF2FF;
          box-shadow: 0 4px 14px rgba(79, 70, 229, 0.15);
        }
        .btn-lg {
          height: 48px;
          padding: 0 24px;
          font-size: 15px;
        }
        .hero-trust-metrics {
          display: flex;
          align-items: center;
          gap: 24px;
          padding-top: 24px;
          border-top: 1px solid #E2E8F0;
        }
        .metric-item strong {
          display: block;
          font-size: 20px;
          font-weight: 800;
          color: #0F172A;
        }
        .metric-item span {
          font-size: 12px;
          color: #64748B;
        }
        .metric-divider {
          width: 1px;
          height: 32px;
          background-color: #E2E8F0;
        }

        /* Hero Visual Browser Mockup */
        .browser-mockup {
          background-color: #FFFFFF;
          border: 1px solid #CBD5E1;
          border-radius: 14px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
          overflow: hidden;
        }
        .browser-header {
          background-color: #F1F5F9;
          padding: 10px 16px;
          display: flex;
          align-items: center;
          border-bottom: 1px solid #E2E8F0;
        }
        .browser-dots {
          display: flex;
          gap: 6px;
        }
        .dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }
        .dot.red { background-color: #EF4444; }
        .dot.yellow { background-color: #F59E0B; }
        .dot.green { background-color: #10B981; }
        .browser-address {
          margin-left: 20px;
          font-size: 11px;
          color: #64748B;
          background-color: #FFFFFF;
          padding: 3px 12px;
          border-radius: 6px;
          border: 1px solid #E2E8F0;
        }
        .browser-body {
          padding: 20px;
        }
        .mock-kpi-row {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 20px;
        }
        .mock-card {
          background-color: #F8FAFC;
          border: 1px solid #E2E8F0;
          border-radius: 8px;
          padding: 12px;
        }
        .mock-label {
          font-size: 10px;
          color: #64748B;
          display: block;
        }
        .mock-value {
          font-size: 15px;
          font-weight: 700;
          color: #0F172A;
          display: block;
          margin: 2px 0;
        }
        .mock-trend {
          font-size: 10px;
          font-weight: 600;
        }
        .mock-trend.green { color: #059669; }
        .mock-trend.purple { color: #4F46E5; }

        .mock-chart-container {
          background-color: #F8FAFC;
          border: 1px solid #E2E8F0;
          border-radius: 8px;
          padding: 16px;
        }
        .mock-chart-header {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          font-weight: 700;
          margin-bottom: 16px;
        }
        .mock-badge {
          background-color: #EEF2FF;
          color: #4F46E5;
          font-size: 10px;
          padding: 2px 6px;
          border-radius: 4px;
        }
        .mock-chart-bars {
          height: 120px;
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
        }
        .bar-column {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          height: 100%;
          justify-content: flex-end;
        }
        .bar {
          width: 24px;
          background-color: #CBD5E1;
          border-radius: 4px 4px 0 0;
          transition: height 300ms ease;
        }
        .bar.active {
          background-color: #4F46E5;
        }
        .bar-column span {
          font-size: 10px;
          color: #64748B;
        }

        /* Section Commons */
        .section-header {
          margin-bottom: 48px;
        }
        .section-header.center {
          text-align: center;
        }
        .section-tag {
          font-size: 12px;
          font-weight: 700;
          color: #4F46E5;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          display: block;
          margin-bottom: 8px;
        }
        .section-title {
          font-size: 36px;
          font-weight: 800;
          letter-spacing: -0.02em;
          color: #0F172A;
          margin-bottom: 12px;
        }
        .section-desc {
          font-size: 16px;
          color: #64748B;
          max-width: 600px;
          margin: 0 auto;
        }

        /* Features Section */
        .features-section {
          padding: 90px 0;
          background-color: #FFFFFF;
          border-top: 1px solid #E2E8F0;
        }
        .features-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 32px;
        }
        .feature-card {
          background-color: #F8FAFC;
          border: 1px solid #E2E8F0;
          border-radius: 12px;
          padding: 28px;
          transition: all 200ms ease-in-out;
        }
        .feature-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.04);
          border-color: #CBD5E1;
        }
        .feature-icon-wrapper {
          width: 48px;
          height: 48px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 20px;
        }
        .feature-icon-wrapper.accent { background-color: #EEF2FF; color: #4F46E5; }
        .feature-icon-wrapper.success { background-color: #D1FAE5; color: #059669; }
        .feature-icon-wrapper.warning { background-color: #FEF3C7; color: #D97706; }
        .feature-icon-wrapper.purple { background-color: #F3E8FF; color: #9333EA; }
        .feature-icon-wrapper.info { background-color: #E0F2FE; color: #0284C7; }
        .feature-icon-wrapper.primary { background-color: #F1F5F9; color: #334155; }

        .feature-card h3 {
          font-size: 18px;
          font-weight: 700;
          color: #0F172A;
          margin-bottom: 8px;
        }
        .feature-card p {
          font-size: 14px;
          color: #64748B;
          line-height: 1.5;
        }

        /* Timeline Section */
        .timeline-section {
          padding: 90px 0;
          background-color: #F8FAFC;
        }
        .timeline-grid {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 20px;
        }
        .timeline-step {
          background-color: #FFFFFF;
          border: 1px solid #E2E8F0;
          border-radius: 12px;
          padding: 24px 18px;
          position: relative;
        }
        .step-num {
          width: 32px;
          height: 32px;
          background-color: #4F46E5;
          color: #FFFFFF;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 14px;
          margin-bottom: 16px;
        }
        .timeline-step h4 {
          font-size: 15px;
          font-weight: 700;
          color: #0F172A;
          margin-bottom: 6px;
        }
        .timeline-step p {
          font-size: 12px;
          color: #64748B;
          line-height: 1.5;
        }

        /* Preview Section */
        .preview-section {
          padding: 90px 0;
          background-color: #FFFFFF;
          border-top: 1px solid #E2E8F0;
        }
        .large-preview-card {
          background-color: #0F172A;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 24px 48px rgba(0, 0, 0, 0.15);
          color: #FFFFFF;
        }
        .preview-header {
          background-color: #1E293B;
          padding: 14px 20px;
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .preview-title {
          font-size: 13px;
          color: #94A3B8;
          font-weight: 600;
        }
        .preview-body {
          padding: 32px;
          position: relative;
        }
        .preview-badge-callout {
          position: absolute;
          background-color: #FFFFFF;
          color: #0F172A;
          padding: 8px 16px;
          border-radius: 9999px;
          font-size: 12px;
          font-weight: 700;
          box-shadow: 0 10px 20px rgba(0,0,0,0.2);
          display: flex;
          align-items: center;
          gap: 8px;
          z-index: 10;
        }
        .callout-1 { top: 20px; right: 40px; border: 1px solid #10B981; }
        .callout-2 { bottom: 20px; left: 40px; border: 1px solid #4F46E5; }
        /* Inline callouts: shown only on mobile */
        .preview-inline-callouts { display: none; }
        .preview-inline-badge {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          font-size: 10px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 9999px;
          border: 1px solid;
          background-color: rgba(15,23,42,0.6);
        }
        /* Table scroll wrapper */
        .mock-table-scroll-wrapper {
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
        }

        .mock-grid-main {
          background-color: #1E293B;
          border-radius: 12px;
          padding: 24px;
        }
        .mock-panel h4 {
          font-size: 16px;
          font-weight: 700;
          margin-bottom: 16px;
          color: #F8FAFC;
        }
        .mock-table {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .table-header-row, .table-data-row {
          display: grid;
          grid-template-columns: 1fr 2fr 1fr 1fr 1fr 1fr;
          padding: 10px 14px;
          font-size: 12px;
        }
        .table-header-row {
          color: #94A3B8;
          font-weight: 600;
          border-bottom: 1px solid #334155;
        }
        .table-data-row {
          background-color: #0F172A;
          border-radius: 6px;
          color: #E2E8F0;
        }
        .badge-status {
          font-size: 10px;
          padding: 2px 8px;
          border-radius: 9999px;
          width: fit-content;
          font-weight: 600;
        }
        .badge-status.success { background-color: rgba(16, 185, 129, 0.2); color: #34D399; }
        .badge-status.warning { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; }
        .badge-status.primary { background-color: rgba(99, 102, 241, 0.2); color: #818CF8; }

        /* Benefits Section */
        .benefits-section {
          padding: 90px 0;
          background-color: #F8FAFC;
        }
        .benefits-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 64px;
          align-items: center;
        }
        .benefits-illustration {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .benefit-card-stat {
          background-color: #FFFFFF;
          border: 1px solid #E2E8F0;
          border-radius: 14px;
          padding: 24px;
          display: flex;
          gap: 18px;
          align-items: flex-start;
          box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        }
        .benefit-card-stat strong {
          display: block;
          font-size: 16px;
          color: #0F172A;
          margin-bottom: 4px;
        }
        .benefit-card-stat p {
          font-size: 13px;
          color: #64748B;
          margin: 0;
        }

        .benefits-list {
          list-style: none;
          padding: 0;
          margin: 24px 0 0 0;
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .benefits-list li {
          display: flex;
          gap: 14px;
          align-items: flex-start;
        }
        .check-icon {
          color: #059669;
          flex-shrink: 0;
          margin-top: 2px;
        }
        .benefits-list strong {
          display: block;
          font-size: 15px;
          color: #0F172A;
        }
        .benefits-list p {
          font-size: 13px;
          color: #64748B;
          margin: 2px 0 0 0;
        }

        /* Comparison Section */
        .comparison-section {
          padding: 90px 0;
          background-color: #FFFFFF;
          border-top: 1px solid #E2E8F0;
        }
        .comparison-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 32px;
          max-width: 960px;
          margin: 0 auto;
        }
        .comparison-card {
          border: 1px solid #E2E8F0;
          border-radius: 16px;
          padding: 32px;
          background-color: #F8FAFC;
          position: relative;
        }
        .comparison-card.highlight {
          background-color: #FFFFFF;
          border-color: #4F46E5;
          box-shadow: 0 12px 30px rgba(79, 70, 229, 0.08);
        }
        .recommended-badge {
          position: absolute;
          top: -12px;
          right: 24px;
          background-color: #4F46E5;
          color: #FFFFFF;
          font-size: 11px;
          font-weight: 700;
          padding: 3px 12px;
          border-radius: 9999px;
        }
        .comparison-header {
          margin-bottom: 24px;
          padding-bottom: 16px;
          border-bottom: 1px solid #E2E8F0;
        }
        .comparison-header h3 {
          font-size: 20px;
          font-weight: 800;
          color: #0F172A;
          margin-bottom: 4px;
        }
        .comparison-header p {
          font-size: 13px;
          color: #64748B;
          margin: 0;
        }
        .comparison-list {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .comparison-list li {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 14px;
          color: #334155;
        }
        .cross-icon {
          color: #EF4444;
          flex-shrink: 0;
        }

        /* Testimonials Section */
        .testimonials-section {
          padding: 90px 0;
          background-color: #F8FAFC;
        }
        .testimonials-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 24px;
        }
        .testimonial-card {
          background-color: #FFFFFF;
          border: 1px solid #E2E8F0;
          border-radius: 12px;
          padding: 28px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
        }
        .testimonial-quote {
          font-size: 14px;
          color: #334155;
          line-height: 1.6;
          font-style: italic;
          margin-bottom: 24px;
        }
        .testimonial-author strong {
          display: block;
          font-size: 14px;
          color: #0F172A;
        }
        .testimonial-author span {
          font-size: 12px;
          color: #64748B;
        }

        /* FAQ Section */
        .faq-section {
          padding: 90px 0;
          background-color: #FFFFFF;
          border-top: 1px solid #E2E8F0;
        }
        .faq-accordion {
          max-width: 800px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .faq-item {
          background-color: #F8FAFC;
          border: 1px solid #E2E8F0;
          border-radius: 12px;
          padding: 18px 24px;
          cursor: pointer;
          transition: all 150ms ease;
        }
        .faq-item.active {
          border-color: #4F46E5;
          background-color: #FFFFFF;
        }
        .faq-question {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-weight: 700;
          font-size: 15px;
          color: #0F172A;
        }
        .faq-arrow {
          transition: transform 200ms ease;
          color: #64748B;
        }
        .faq-item.active .faq-arrow {
          transform: rotate(180deg);
          color: #4F46E5;
        }
        .faq-answer {
          margin-top: 12px;
          font-size: 14px;
          color: #475569;
          line-height: 1.6;
          border-top: 1px solid #F1F5F9;
          padding-top: 12px;
        }

        /* CTA Banner */
        .cta-banner-section {
          padding: 60px 0 90px 0;
          background-color: #F8FAFC;
        }
        .cta-banner-card {
          background: linear-gradient(135deg, #4F46E5, #3730A3);
          border-radius: 20px;
          padding: 60px 40px;
          text-align: center;
          color: #FFFFFF;
          box-shadow: 0 20px 40px rgba(79, 70, 229, 0.2);
        }
        .cta-banner-card h2 {
          font-size: 32px;
          font-weight: 800;
          margin-bottom: 12px;
        }
        .cta-banner-card p {
          font-size: 16px;
          color: #E0E7FF;
          margin-bottom: 28px;
        }
        .cta-actions {
          display: flex;
          justify-content: center;
        }
        .cta-banner-card .btn-primary {
          background-color: #FFFFFF;
          color: #4F46E5;
        }
        .cta-banner-card .btn-primary:hover {
          background-color: #F8FAFC;
        }

        /* Footer */
        .landing-footer {
          background-color: #0F172A;
          color: #94A3B8;
          padding: 80px 0 32px 0;
        }
        .footer-grid {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 1fr;
          gap: 48px;
          margin-bottom: 60px;
        }
        .footer-brand .brand-text {
          color: #FFFFFF;
        }
        .footer-tagline {
          font-size: 13px;
          line-height: 1.6;
          color: #94A3B8;
          margin-top: 16px;
          max-width: 320px;
        }
        .footer-column h4 {
          color: #FFFFFF;
          font-size: 14px;
          font-weight: 700;
          margin-bottom: 16px;
        }
        .footer-column a {
          display: block;
          color: #94A3B8;
          text-decoration: none;
          font-size: 13px;
          margin-bottom: 10px;
          transition: color 150ms ease;
        }
        .footer-column a:hover {
          color: #FFFFFF;
        }
        .footer-bottom {
          border-top: 1px solid #1E293B;
          padding-top: 24px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 12px;
        }
        .footer-socials a {
          color: #94A3B8;
          text-decoration: none;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        /* Responsive Breakpoints */
        @media (max-width: 1023px) {
          .hero-grid, .benefits-grid { grid-template-columns: 1fr; }
          .hero-visual { display: none; }
          .features-grid { grid-template-columns: repeat(2, 1fr); }
          .timeline-grid { grid-template-columns: repeat(2, 1fr); }
          .testimonials-grid { grid-template-columns: 1fr; }
          .footer-grid { grid-template-columns: 1fr 1fr; }
        }

        @media (max-width: 767px) {
          /* Navbar: hide desktop links, show hamburger */
          .nav-links { display: none; }
          .nav-actions { display: none; }
          .nav-hamburger { display: flex !important; align-items: center; justify-content: center; }

          /* Navbar premium design enhancements */
          .landing-navbar {
            border-bottom: 1px solid #E2E8F0 !important;
            background-color: rgba(255, 255, 255, 0.98) !important;
          }
          .nav-container { height: 60px !important; }

          /* Hero section: stack vertically, readable on mobile */
          .hero-section { padding: 48px 0 56px 0; }
          .hero-grid { grid-template-columns: 1fr; gap: 32px; }
          .hero-title { font-size: 30px; line-height: 1.2; }
          .hero-subtitle { font-size: 15px; }

          /* Show browser mockup on mobile but smaller */
          .hero-visual {
            display: block !important;
            width: 100%;
          }
          .browser-mockup {
            border-radius: 10px !important;
          }
          .browser-body { padding: 14px !important; }
          .mock-kpi-row {
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 8px !important;
            margin-bottom: 12px !important;
          }
          .mock-card {
            padding: 8px !important;
          }
          .mock-value { font-size: 12px !important; }
          .mock-label { font-size: 9px !important; }
          .mock-trend { font-size: 9px !important; }
          .mock-chart-bars { height: 72px !important; }
          .bar { width: 16px !important; }
          .bar-column span { font-size: 8px !important; }

          /* Hero CTA buttons: stack vertically */
          .hero-ctas {
            flex-direction: column !important;
            gap: 12px !important;
            margin-bottom: 28px !important;
          }
          .hero-cta-primary, .hero-ctas .btn-lg {
            width: 100% !important;
            height: 48px !important;
            justify-content: center !important;
            font-size: 15px !important;
          }
          .hero-cta-ghost {
            width: 100% !important;
            height: 48px !important;
            justify-content: center !important;
            font-size: 15px !important;
            background-color: #F1F5F9 !important;
            border-color: #CBD5E1 !important;
            color: #334155 !important;
          }

          /* Trust metrics: horizontal scroll or wrap */
          .hero-trust-metrics {
            display: grid !important;
            grid-template-columns: 1fr 1fr 1fr !important;
            gap: 16px !important;
            padding-top: 20px !important;
          }
          .metric-divider { display: none !important; }
          .metric-item { text-align: center; }
          .metric-item strong { font-size: 16px !important; }
          .metric-item span { font-size: 11px !important; }

          /* Preview section: fix the "Clean Analytics Dashboard" card on mobile */
          .preview-section { padding: 56px 0 !important; }
          .preview-body {
            padding: 16px !important;
            position: static !important;
          }
          /* Hide absolute callout bubbles on mobile (they overlap content) */
          .preview-callout-hide-mobile { display: none !important; }
          /* Show inline callout badges instead */
          .preview-inline-callouts { display: block !important; }
          /* Table: constrain width and allow horizontal scroll */
          .mock-table-scroll-wrapper {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            margin-right: -4px;
          }
          .mock-table { min-width: 540px !important; }
          .table-header-row, .table-data-row {
            grid-template-columns: 1fr 2fr 1fr 1fr 1fr 1fr !important;
            font-size: 10px !important;
            padding: 8px 10px !important;
          }
          .mock-grid-main { padding: 14px !important; border-radius: 8px !important; }
          .mock-panel h4 { font-size: 13px !important; margin-bottom: 10px !important; }
          .large-preview-card { border-radius: 12px !important; }

          /* Other sections */
          .section-title { font-size: 26px; }
          .features-grid, .timeline-grid, .comparison-grid { grid-template-columns: 1fr; }
          .footer-grid { grid-template-columns: 1fr; }
          .footer-bottom { flex-direction: column; gap: 12px; text-align: center; }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
