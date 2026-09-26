import React, { useState } from 'react';
import demandForecastingVisual from '../../assets/demand_forecasting_visual.png';
import { useAuth } from '../../auth/AuthContext';
import { getDemandPredictionAnalytics } from '../../services/api';
import {
  BrainCircuit,
  Search,
  RefreshCw,
  ArrowLeft,
  AlertCircle,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';
import '../../styles/admin-portal.css';

export default function AdminAnalyticsView() {
  const { token: authContextToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  // Active view: 'overview' | 'demand_forecasting'
  const [activeView, setActiveView] = useState('overview');

  // Filters for product predictions table
  const [searchQuery, setSearchQuery] = useState('');
  const [demandFilter, setDemandFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  const fetchAnalyticsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const activeToken = authContextToken || localStorage.getItem('iras_token') || localStorage.getItem('token');
      const res = await getDemandPredictionAnalytics(activeToken);
      if (res.success) {
        setData(res);
      } else {
        setError(res.error || 'Failed to load demand prediction analytics.');
      }
    } catch (err) {
      setError('An unexpected error occurred while fetching demand prediction analytics.');
    } finally {
      setLoading(false);
    }
  };

  // Only fetch when first opening the detail view
  const handleOpenDetailView = () => {
    setActiveView('demand_forecasting');
    if (!data) {
      fetchAnalyticsData();
    }
  };

  const { summary = {}, product_predictions = [] } = data || {};

  // Filtered products list
  const filteredProducts = product_predictions.filter((prod) => {
    const matchesSearch =
      prod.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prod.category_name.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesDemand = demandFilter === 'ALL' || prod.predicted_demand.toUpperCase() === demandFilter;
    const matchesCategory = categoryFilter === 'ALL' || prod.category_name === categoryFilter;

    return matchesSearch && matchesDemand && matchesCategory;
  });

  const categoriesList = Array.from(new Set(product_predictions.map((p) => p.category_name))).filter(Boolean);

  const highCount = summary.predicted_distribution?.High || 0;
  const medCount = summary.predicted_distribution?.Medium || 0;
  const lowCount = summary.predicted_distribution?.Low || 0;
  const totalCount = summary.total_products || product_predictions.length;

  return (
    <div>
      {/* ==========================================================================
          MAIN OVERVIEW PAGE: PREDICTIVE DATA MINING MODULES
         ========================================================================== */}
      {activeView === 'overview' && (
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          {/* Section Title */}
          <div style={{ marginBottom: '1.75rem' }}>
            <h1 style={{ fontFamily: "var(--font-serif, 'Playfair Display', serif)", fontSize: '2rem', fontWeight: 700, color: '#1F191B', margin: '0 0 0.35rem 0' }}>
              Predictive Data Mining Modules
            </h1>
            <p style={{ color: '#6B5E63', fontSize: '0.92rem', margin: 0 }}>
              Independent analytical modules designed for machine learning, forecasting, and pattern discovery.
            </p>
          </div>

          {/* DEMAND FORECASTING CARD (EXACT UI MATCHING SCREENSHOT) */}
          <div
            className="admin-card"
            style={{
              padding: '2.25rem',
              borderRadius: '20px',
              border: '1px solid rgba(216, 114, 126, 0.2)',
              cursor: 'pointer',
              transition: 'all 0.25s ease',
              boxShadow: '0 8px 30px rgba(31, 25, 27, 0.04)',
              backgroundColor: '#FFFFFF'
            }}
            onClick={handleOpenDetailView}
          >
            {/* Card Top Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div
                  style={{
                    width: '52px',
                    height: '52px',
                    borderRadius: '14px',
                    backgroundColor: '#FDF2F4',
                    color: '#B8505E',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <BrainCircuit size={26} />
                </div>
                <div>
                  <h2 style={{ fontFamily: "var(--font-serif, 'Playfair Display', serif)", fontSize: '1.6rem', fontWeight: 700, color: '#1F191B', margin: 0, lineHeight: 1.2 }}>
                    Demand Forecasting
                  </h2>
                  <span style={{ fontSize: '0.75rem', color: '#9E8F94', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    FEATURE #1 &bull; PREDICTIVE CLASSIFIER
                  </span>
                </div>
              </div>

              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.4rem 0.95rem',
                  borderRadius: '9999px',
                  backgroundColor: '#ECFDF5',
                  border: '1px solid #A7F3D0',
                  color: '#059669',
                  fontSize: '0.82rem',
                  fontWeight: 600
                }}
              >
                <CheckCircle2 size={14} />
                Active Engine
              </span>
            </div>

            {/* Description */}
            <p style={{ color: '#6B5E63', fontSize: '0.95rem', lineHeight: 1.6, margin: '0 0 1.75rem 0' }}>
              Classifies catalog products into High, Medium, and Low demand tiers based on historical metrics ( <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>units_sold</code> , <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>cart_quantity</code> , <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>wishlist_count</code> , <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>discount_percentage</code> ).
            </p>

            {/* Demand Forecasting Visual Banner */}
            <div style={{ marginBottom: '2rem', borderRadius: '14px', overflow: 'hidden', background: '#FAF7F5', border: '1px solid rgba(216, 114, 126, 0.1)' }}>
              <img
                src={demandForecastingVisual}
                alt="Demand Forecasting — High, Medium, Low tier distribution visual"
                style={{ width: '100%', maxHeight: '220px', objectFit: 'cover', display: 'block' }}
              />
            </div>

            {/* Bottom Row Action */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '1.25rem', borderTop: '1px solid rgba(216, 114, 126, 0.15)', flexWrap: 'wrap', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.9rem', color: '#6B5E63' }}>
                Open product-level demand predictions
              </span>

              <button
                style={{
                  background: 'linear-gradient(135deg, #B8505E 0%, #8E3642 100%)',
                  color: '#FFFFFF',
                  padding: '0.7rem 1.5rem',
                  borderRadius: '9999px',
                  border: 'none',
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  boxShadow: '0 4px 14px rgba(184, 80, 94, 0.25)'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleOpenDetailView();
                }}
              >
                <span>View Demand Details</span>
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==========================================================================
          DEDICATED DETAILED VIEW: DEMAND FORECASTING RESULTS
         ========================================================================== */}
      {activeView === 'demand_forecasting' && (
        <>
          {/* Back Navigation Bar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <button
                onClick={() => setActiveView('overview')}
                className="tarika-btn-outline"
                style={{ padding: '0.55rem 1.1rem', fontSize: '0.82rem' }}
              >
                <ArrowLeft size={16} />
                <span>Back to Analytics Hub</span>
              </button>
              <div>
                <h1 style={{ fontFamily: "var(--font-serif, 'Playfair Display', serif)", fontSize: '1.85rem', fontWeight: 700, color: '#1F191B', margin: '0 0 0.2rem 0' }}>
                  Demand Forecasting Results
                </h1>
                <p style={{ color: '#6B5E63', fontSize: '0.88rem', margin: 0 }}>
                  Product-wise demand predictions and metrics derived from historical database records.
                </p>
              </div>
            </div>

            <button
              onClick={fetchAnalyticsData}
              className="tarika-btn-outline"
              style={{ padding: '0.55rem 1.1rem', fontSize: '0.82rem' }}
            >
              <RefreshCw size={14} />
              <span>Refresh Predictions</span>
            </button>
          </div>

          {/* Loading State */}
          {loading && (
            <div style={{ padding: '4rem 1rem', textAlign: 'center' }}>
              <RefreshCw size={36} className="animate-spin" style={{ color: '#B8505E', marginBottom: '1rem' }} />
              <h3 style={{ fontFamily: "var(--font-serif, 'Playfair Display', serif)", color: '#1F191B', margin: '0 0 0.5rem 0' }}>
                Running Demand Prediction Engine...
              </h3>
              <p style={{ color: '#6B5E63', fontSize: '0.9rem', margin: 0 }}>
                Processing historical demand data from Supabase...
              </p>
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <div style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', padding: '1.5rem', borderRadius: '12px', color: '#991B1B', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
                <AlertCircle size={20} color="#DC2626" />
                <strong style={{ fontSize: '1.05rem' }}>Demand Forecasting Engine Notice</strong>
              </div>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.92rem' }}>{error}</p>
              <button className="tarika-btn-outline" onClick={fetchAnalyticsData}>
                <RefreshCw size={14} /> Retry
              </button>
            </div>
          )}

          {/* Data Loaded */}
          {!loading && !error && data && (
            <>
          {/* Metrics Grid */}
          <div className="admin-metrics-grid" style={{ marginBottom: '1.5rem' }}>
            <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
              <p className="admin-metric-title">Filtered Products</p>
              <p className="admin-metric-val" style={{ fontSize: '1.5rem' }}>{filteredProducts.length}</p>
              <p className="admin-metric-subtext">Of {totalCount} catalog items</p>
            </div>

            <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
              <p className="admin-metric-title" style={{ color: '#059669' }}>High Demand</p>
              <p className="admin-metric-val" style={{ fontSize: '1.5rem', color: '#059669' }}>{highCount}</p>
              <p className="admin-metric-subtext">Top velocity products</p>
            </div>

            <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
              <p className="admin-metric-title" style={{ color: '#D97706' }}>Medium Demand</p>
              <p className="admin-metric-val" style={{ fontSize: '1.5rem', color: '#D97706' }}>{medCount}</p>
              <p className="admin-metric-subtext">Steady order volume</p>
            </div>

            <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
              <p className="admin-metric-title" style={{ color: '#DC2626' }}>Low Demand</p>
              <p className="admin-metric-val" style={{ fontSize: '1.5rem', color: '#DC2626' }}>{lowCount}</p>
              <p className="admin-metric-subtext">Low velocity products</p>
            </div>
          </div>

          {/* Search & Filter Bar */}
          <div className="admin-card" style={{ marginBottom: '1.5rem', padding: '1.15rem 1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              {/* Search Box */}
              <div style={{ flex: '1 1 280px', position: 'relative' }}>
                <Search size={17} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#9E8F94' }} />
                <input
                  type="text"
                  placeholder="Search product name or category..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.85rem 0.6rem 2.5rem',
                    border: '1px solid rgba(216, 114, 126, 0.25)',
                    borderRadius: '8px',
                    fontSize: '0.88rem',
                    outline: 'none',
                    backgroundColor: '#FAF7F5',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              {/* Demand Tier Filter Pills */}
              <div style={{ display: 'flex', gap: '0.35rem', background: '#FAF7F5', padding: '0.25rem', borderRadius: '8px', border: '1px solid rgba(216, 114, 126, 0.2)' }}>
                {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setDemandFilter(lvl)}
                    style={{
                      padding: '0.35rem 0.85rem',
                      fontSize: '0.78rem',
                      fontWeight: 700,
                      borderRadius: '6px',
                      border: 'none',
                      cursor: 'pointer',
                      background: demandFilter === lvl ? '#FFFFFF' : 'transparent',
                      color: demandFilter === lvl ? '#B8505E' : '#6B5E63',
                      boxShadow: demandFilter === lvl ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {lvl}
                  </button>
                ))}
              </div>

              {/* Category Dropdown */}
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                style={{
                  padding: '0.6rem 0.85rem',
                  fontSize: '0.85rem',
                  borderRadius: '8px',
                  border: '1px solid rgba(216, 114, 126, 0.25)',
                  backgroundColor: '#FAF7F5',
                  color: '#1F191B',
                  outline: 'none'
                }}
              >
                <option value="ALL">All Categories ({categoriesList.length})</option>
                {categoriesList.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Product Demand Predictions Table */}
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Product Key</th>
                  <th>Product Name</th>
                  <th>Category</th>
                  <th>Avg Units Sold</th>
                  <th>Avg Cart Qty</th>
                  <th>Avg Wishlist</th>
                  <th>Avg Discount %</th>
                  <th>Predicted Demand</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.length > 0 ? (
                  filteredProducts.map((p) => {
                    const isHigh = p.predicted_demand === 'High';
                    const isMed = p.predicted_demand === 'Medium';
                    const statusStyle = isHigh
                      ? { backgroundColor: '#ECFDF5', color: '#059669', borderColor: '#A7F3D0' }
                      : isMed
                      ? { backgroundColor: '#FFFBEB', color: '#D97706', borderColor: '#FDE68A' }
                      : { backgroundColor: '#FEF2F2', color: '#DC2626', borderColor: '#FCA5A5' };

                    return (
                      <tr key={p.product_key}>
                        <td>
                          <code style={{ fontSize: '0.78rem', color: '#9E8F94' }}>#{p.product_key}</code>
                        </td>
                        <td>
                          <strong style={{ color: '#1F191B', fontWeight: 600 }}>{p.product_name}</strong>
                        </td>
                        <td>
                          <span style={{ color: '#6B5E63', fontSize: '0.85rem' }}>{p.category_name}</span>
                        </td>
                        <td>
                          <span style={{ fontWeight: 700, color: '#1F191B' }}>{p.units_sold}</span>
                        </td>
                        <td>{p.cart_quantity}</td>
                        <td>{p.wishlist_count}</td>
                        <td>{p.discount_percentage}%</td>
                        <td>
                          <span className="admin-metric-status" style={statusStyle}>
                            {p.predicted_demand} Demand
                          </span>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '3rem 1rem', color: '#9E8F94' }}>
                      No products found matching the selected search or category filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', fontSize: '0.82rem', color: '#6B5E63' }}>
            <span>Showing <strong>{filteredProducts.length}</strong> of {totalCount} catalog products</span>
            <span>Dataset Source: <code style={{ fontSize: '0.75rem' }}>public.fact_demand</code> (Supabase)</span>
          </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
