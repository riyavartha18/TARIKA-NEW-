import React, { useState } from 'react';
import demandForecastingVisual from '../../assets/demand_forecasting_visual.png';
import { useAuth } from '../../auth/AuthContext';
import { getDemandPredictionAnalytics, getSlowMovingInventory } from '../../services/api';
import {
  BrainCircuit,
  Search,
  RefreshCw,
  ArrowLeft,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Calendar,
  PackageSearch,
  TrendingDown,
  AlertTriangle,
  Archive,
  Box,
} from 'lucide-react';
import '../../styles/admin-portal.css';

export default function AdminAnalyticsView() {
  const { token: authContextToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  // Active view: 'overview' | 'demand_forecasting' | 'slow_inventory'
  const [activeView, setActiveView] = useState('overview');

  // Filters for product predictions table
  const [searchQuery, setSearchQuery] = useState('');
  const [demandFilter, setDemandFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  // === Slow-Moving Inventory State ===
  const [slowLoading, setSlowLoading] = useState(false);
  const [slowError, setSlowError] = useState(null);
  const [slowData, setSlowData] = useState(null);
  const [slowSearchQuery, setSlowSearchQuery] = useState('');
  const [slowStatusFilter, setSlowStatusFilter] = useState('ALL');
  const [slowWarehouseFilter, setSlowWarehouseFilter] = useState('ALL');

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

  const fetchSlowInventoryData = async () => {
    setSlowLoading(true);
    setSlowError(null);
    try {
      const activeToken = authContextToken || localStorage.getItem('iras_token') || localStorage.getItem('token');
      const res = await getSlowMovingInventory(activeToken);
      if (res.success) {
        setSlowData(res);
      } else {
        setSlowError(res.error || 'Failed to load slow-moving inventory data.');
      }
    } catch (err) {
      setSlowError('An unexpected error occurred while fetching slow-moving inventory data.');
    } finally {
      setSlowLoading(false);
    }
  };

  // Only fetch when first opening the detail view
  const handleOpenDetailView = () => {
    setActiveView('demand_forecasting');
    if (!data) {
      fetchAnalyticsData();
    }
  };

  const handleOpenSlowInventoryView = () => {
    setActiveView('slow_inventory');
    if (!slowData) {
      fetchSlowInventoryData();
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

  // === Slow-Moving Inventory Filtering (client-side) ===
  const slowItems = slowData?.items || [];
  const slowSummary = slowData?.summary || {};
  const slowWarehouses = slowData?.warehouses || [];

  const filteredSlowItems = slowItems.filter((item) => {
    const matchesSearch =
      item.product_name.toLowerCase().includes(slowSearchQuery.toLowerCase()) ||
      item.category_name.toLowerCase().includes(slowSearchQuery.toLowerCase());
    const matchesStatus = slowStatusFilter === 'ALL' || item.movement_status === slowStatusFilter;
    const matchesWarehouse = slowWarehouseFilter === 'ALL' || String(item.warehouse_id) === slowWarehouseFilter;
    return matchesSearch && matchesStatus && matchesWarehouse;
  });

  // Movement status badge style helper
  const getStatusStyle = (status) => {
    switch (status) {
      case 'VERY SLOW':
        return { backgroundColor: '#FEF2F2', color: '#DC2626', borderColor: '#FCA5A5' };
      case 'SLOW':
        return { backgroundColor: '#FFFBEB', color: '#D97706', borderColor: '#FDE68A' };
      case 'NORMAL':
        return { backgroundColor: '#ECFDF5', color: '#059669', borderColor: '#A7F3D0' };
      default:
        return { backgroundColor: '#F3F4F6', color: '#6B7280', borderColor: '#D1D5DB' };
    }
  };

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

          {/* DEMAND FORECASTING CARD */}
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
              Predicts next-month demand tiers (High, Medium, Low) for catalog products based on historical monthly transitions and features ( <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>units_sold</code> , <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>cart_quantity</code> , <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>wishlist_count</code> , <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>discount_percentage</code> , <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>notify_me_count</code> ) using a supervised Decision Tree Classifier.
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

          {/* ================================================================
              SLOW-MOVING INVENTORY CARD
             ================================================================ */}
          <div
            className="admin-card"
            style={{
              padding: '2.25rem',
              borderRadius: '20px',
              border: '1px solid rgba(216, 114, 126, 0.2)',
              cursor: 'pointer',
              transition: 'all 0.25s ease',
              boxShadow: '0 8px 30px rgba(31, 25, 27, 0.04)',
              backgroundColor: '#FFFFFF',
              marginTop: '1.75rem'
            }}
            onClick={handleOpenSlowInventoryView}
          >
            {/* Card Top Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div
                  style={{
                    width: '52px',
                    height: '52px',
                    borderRadius: '14px',
                    backgroundColor: '#FEF3C7',
                    color: '#D97706',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <PackageSearch size={26} />
                </div>
                <div>
                  <h2 style={{ fontFamily: "var(--font-serif, 'Playfair Display', serif)", fontSize: '1.6rem', fontWeight: 700, color: '#1F191B', margin: 0, lineHeight: 1.2 }}>
                    Slow-Moving Inventory
                  </h2>
                  <span style={{ fontSize: '0.75rem', color: '#9E8F94', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    FEATURE #2 &bull; INVENTORY VELOCITY ANALYSIS
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
              Identifies products whose current inventory is moving slowly based on historical sales velocity. Calculates <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>days_of_stock</code> from <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>current_stock</code> ÷ <code style={{ background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)', padding: '0.15rem 0.45rem', borderRadius: '5px', color: '#1F191B', fontSize: '0.85rem' }}>avg_daily_sales</code> and classifies each product-warehouse pair as <strong style={{ color: '#DC2626' }}>Very Slow</strong>, <strong style={{ color: '#D97706' }}>Slow</strong>, or <strong style={{ color: '#059669' }}>Normal</strong>.
            </p>

            {/* Visual Banner for Slow-Moving Inventory */}
            <div style={{
              marginBottom: '2rem',
              borderRadius: '14px',
              overflow: 'hidden',
              background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 40%, #FBBF24 100%)',
              border: '1px solid rgba(216, 114, 126, 0.1)',
              padding: '2rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '2rem',
              flexWrap: 'wrap'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Archive size={28} style={{ color: '#92400E' }} />
                <div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#92400E' }}>Very Slow</div>
                  <div style={{ fontSize: '0.8rem', color: '#78350F' }}>0 sales or 180+ days stock</div>
                </div>
              </div>
              <div style={{ width: '1px', height: '40px', background: 'rgba(146, 64, 14, 0.2)' }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <TrendingDown size={28} style={{ color: '#B45309' }} />
                <div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#92400E' }}>Slow</div>
                  <div style={{ fontSize: '0.8rem', color: '#78350F' }}>60–180 days of stock</div>
                </div>
              </div>
              <div style={{ width: '1px', height: '40px', background: 'rgba(146, 64, 14, 0.2)' }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Box size={28} style={{ color: '#15803D' }} />
                <div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#15803D' }}>Normal</div>
                  <div style={{ fontSize: '0.8rem', color: '#166534' }}>≤ 60 days of stock</div>
                </div>
              </div>
            </div>

            {/* Bottom Row Action */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '1.25rem', borderTop: '1px solid rgba(216, 114, 126, 0.15)', flexWrap: 'wrap', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.9rem', color: '#6B5E63' }}>
                Open product-level inventory velocity analysis
              </span>

              <button
                style={{
                  background: 'linear-gradient(135deg, #D97706 0%, #B45309 100%)',
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
                  boxShadow: '0 4px 14px rgba(217, 119, 6, 0.25)'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleOpenSlowInventoryView();
                }}
              >
                <span>View Inventory Analysis</span>
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
                  Next-month product demand predictions derived from historical database records.
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
              {/* Target Forecast Month Info Banner */}
              <div style={{
                background: 'linear-gradient(135deg, #FAF7F5 0%, #FBF1F0 100%)',
                border: '1px solid rgba(216, 114, 126, 0.25)',
                borderRadius: '14px',
                padding: '1.25rem 1.5rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '1rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{
                    width: '44px', height: '44px', borderRadius: '12px',
                    backgroundColor: '#FDF2F4', color: '#B8505E',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <Calendar size={22} />
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#8E3642', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Target Forecast Period
                    </span>
                    <h3 style={{ margin: '0.1rem 0 0', fontSize: '1.25rem', fontWeight: 800, color: '#1F191B', fontFamily: "var(--font-serif, 'Playfair Display', serif)" }}>
                      Next Month Forecast: <span style={{ color: '#B8505E' }}>{summary.next_forecast_period || summary.next_forecast_month || 'October 2026'}</span>
                    </h3>
                  </div>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#6B5E63' }}>
                  Historical Data up to: <strong style={{ color: '#1F191B' }}>{summary.latest_historical_month || 'September 2026'}</strong>
                </div>
              </div>

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
                      <th>Forecast Month</th>
                      <th>Latest Month Sold</th>
                      <th>Latest Cart Qty</th>
                      <th>Latest Wishlist</th>
                      <th>Latest Notify Me</th>
                      <th>Discount %</th>
                      <th>Predicted Next-Month Demand</th>
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
                              <span style={{ fontWeight: 700, color: '#B8505E', fontSize: '0.85rem' }}>
                                {p.next_forecast_period || p.next_month || summary.next_forecast_month || 'October 2026'}
                              </span>
                            </td>
                            <td>
                              <span style={{ fontWeight: 700, color: '#1F191B' }}>{p.latest_units_sold ?? p.units_sold}</span>
                            </td>
                            <td>{p.latest_cart_quantity ?? p.cart_quantity}</td>
                            <td>{p.latest_wishlist_count ?? p.wishlist_count}</td>
                            <td>{p.latest_notify_me_count ?? p.notify_me_count ?? 0}</td>
                            <td>{p.latest_discount_percentage ?? p.discount_percentage}%</td>
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
                        <td colSpan="10" style={{ textAlign: 'center', padding: '3rem 1rem', color: '#9E8F94' }}>
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

      {/* ==========================================================================
          DEDICATED DETAILED VIEW: SLOW-MOVING INVENTORY ANALYSIS
         ========================================================================== */}
      {activeView === 'slow_inventory' && (
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
                  Slow-Moving Inventory Analysis
                </h1>
                <p style={{ color: '#6B5E63', fontSize: '0.88rem', margin: 0 }}>
                  Product inventory velocity classification based on last 30 days of sales data.
                </p>
              </div>
            </div>

            <button
              onClick={fetchSlowInventoryData}
              className="tarika-btn-outline"
              style={{ padding: '0.55rem 1.1rem', fontSize: '0.82rem' }}
            >
              <RefreshCw size={14} />
              <span>Refresh Analysis</span>
            </button>
          </div>

          {/* Loading State */}
          {slowLoading && (
            <div style={{ padding: '4rem 1rem', textAlign: 'center' }}>
              <RefreshCw size={36} className="animate-spin" style={{ color: '#D97706', marginBottom: '1rem' }} />
              <h3 style={{ fontFamily: "var(--font-serif, 'Playfair Display', serif)", color: '#1F191B', margin: '0 0 0.5rem 0' }}>
                Analyzing Inventory Velocity...
              </h3>
              <p style={{ color: '#6B5E63', fontSize: '0.9rem', margin: 0 }}>
                Calculating sales velocity and stock movement from database...
              </p>
            </div>
          )}

          {/* Error State */}
          {!slowLoading && slowError && (
            <div style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', padding: '1.5rem', borderRadius: '12px', color: '#991B1B', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
                <AlertCircle size={20} color="#DC2626" />
                <strong style={{ fontSize: '1.05rem' }}>Slow-Moving Inventory Engine Notice</strong>
              </div>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.92rem' }}>{slowError}</p>
              <button className="tarika-btn-outline" onClick={fetchSlowInventoryData}>
                <RefreshCw size={14} /> Retry
              </button>
            </div>
          )}

          {/* Data Loaded */}
          {!slowLoading && !slowError && slowData && (
            <>
              {/* Analysis Info Banner */}
              <div style={{
                background: 'linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)',
                border: '1px solid rgba(217, 119, 6, 0.25)',
                borderRadius: '14px',
                padding: '1.25rem 1.5rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '1rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{
                    width: '44px', height: '44px', borderRadius: '12px',
                    backgroundColor: '#FEF3C7', color: '#D97706',
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <PackageSearch size={22} />
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#92400E', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Inventory Velocity Analysis
                    </span>
                    <h3 style={{ margin: '0.1rem 0 0', fontSize: '1.25rem', fontWeight: 800, color: '#1F191B', fontFamily: "var(--font-serif, 'Playfair Display', serif)" }}>
                      Sales Window: <span style={{ color: '#D97706' }}>{slowData.sales_window_start} → {slowData.analysis_date}</span>
                    </h3>
                  </div>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#6B5E63' }}>
                  Analysis Date: <strong style={{ color: '#1F191B' }}>{slowData.analysis_date}</strong>
                </div>
              </div>

              {/* Summary Metrics Grid */}
              <div className="admin-metrics-grid" style={{ marginBottom: '1.5rem' }}>
                <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
                  <p className="admin-metric-title">Total Inventory</p>
                  <p className="admin-metric-val" style={{ fontSize: '1.5rem' }}>{slowSummary.total_inventory || 0}</p>
                  <p className="admin-metric-subtext">Product-warehouse entries</p>
                </div>

                <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
                  <p className="admin-metric-title" style={{ color: '#DC2626' }}>Very Slow</p>
                  <p className="admin-metric-val" style={{ fontSize: '1.5rem', color: '#DC2626' }}>{slowSummary.very_slow || 0}</p>
                  <p className="admin-metric-subtext">No sales or 180+ days stock</p>
                </div>

                <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
                  <p className="admin-metric-title" style={{ color: '#D97706' }}>Slow</p>
                  <p className="admin-metric-val" style={{ fontSize: '1.5rem', color: '#D97706' }}>{slowSummary.slow || 0}</p>
                  <p className="admin-metric-subtext">60–180 days of stock</p>
                </div>

                <div className="admin-metric-card" style={{ padding: '1.1rem 1.25rem' }}>
                  <p className="admin-metric-title" style={{ color: '#059669' }}>Normal</p>
                  <p className="admin-metric-val" style={{ fontSize: '1.5rem', color: '#059669' }}>{slowSummary.normal || 0}</p>
                  <p className="admin-metric-subtext">Healthy movement ≤ 60 days</p>
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
                      value={slowSearchQuery}
                      onChange={(e) => setSlowSearchQuery(e.target.value)}
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

                  {/* Movement Status Filter Pills */}
                  <div style={{ display: 'flex', gap: '0.35rem', background: '#FAF7F5', padding: '0.25rem', borderRadius: '8px', border: '1px solid rgba(216, 114, 126, 0.2)' }}>
                    {['ALL', 'VERY SLOW', 'SLOW', 'NORMAL'].map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => setSlowStatusFilter(lvl)}
                        style={{
                          padding: '0.35rem 0.85rem',
                          fontSize: '0.78rem',
                          fontWeight: 700,
                          borderRadius: '6px',
                          border: 'none',
                          cursor: 'pointer',
                          background: slowStatusFilter === lvl ? '#FFFFFF' : 'transparent',
                          color: slowStatusFilter === lvl ? '#D97706' : '#6B5E63',
                          boxShadow: slowStatusFilter === lvl ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
                          transition: 'all 0.2s ease',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>

                  {/* Warehouse Dropdown */}
                  <select
                    value={slowWarehouseFilter}
                    onChange={(e) => setSlowWarehouseFilter(e.target.value)}
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
                    <option value="ALL">All Warehouses ({slowWarehouses.length})</option>
                    {slowWarehouses.map((wh) => (
                      <option key={wh.warehouse_id} value={String(wh.warehouse_id)}>{wh.warehouse_name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Slow-Moving Inventory Table */}
              <div className="admin-table-wrapper">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Category</th>
                      <th>Warehouse</th>
                      <th>Current Stock</th>
                      <th>Sales Last 30 Days</th>
                      <th>Avg Daily Sales</th>
                      <th>Days of Stock</th>
                      <th>Movement Status</th>
                      <th>Recommended Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSlowItems.length > 0 ? (
                      filteredSlowItems.map((item, idx) => {
                        const badgeStyle = getStatusStyle(item.movement_status);
                        const daysDisplay = item.days_of_stock >= 999999 ? '∞' : item.days_of_stock;

                        return (
                          <tr key={`${item.product_id}-${item.warehouse_id}-${idx}`}>
                            <td>
                              <strong style={{ color: '#1F191B', fontWeight: 600 }}>{item.product_name}</strong>
                            </td>
                            <td>
                              <span style={{ color: '#6B5E63', fontSize: '0.85rem' }}>{item.category_name}</span>
                            </td>
                            <td>
                              <span style={{ color: '#6B5E63', fontSize: '0.85rem' }}>{item.warehouse_name}</span>
                            </td>
                            <td>
                              <span style={{ fontWeight: 700, color: '#1F191B' }}>{item.current_stock}</span>
                            </td>
                            <td>
                              <span style={{ fontWeight: 600, color: item.sales_last_30_days === 0 ? '#DC2626' : '#1F191B' }}>
                                {item.sales_last_30_days}
                              </span>
                            </td>
                            <td>
                              <span style={{ color: '#6B5E63' }}>{item.avg_daily_sales}</span>
                            </td>
                            <td>
                              <span style={{
                                fontWeight: 700,
                                color: daysDisplay === '∞' ? '#DC2626' : item.days_of_stock > 180 ? '#DC2626' : item.days_of_stock > 60 ? '#D97706' : '#059669'
                              }}>
                                {daysDisplay}
                              </span>
                            </td>
                            <td>
                              <span className="admin-metric-status" style={badgeStyle}>
                                {item.movement_status}
                              </span>
                            </td>
                            <td>
                              <span style={{ fontSize: '0.82rem', color: '#6B5E63', fontStyle: 'italic' }}>
                                {item.recommended_action}
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan="9" style={{ textAlign: 'center', padding: '3rem 1rem', color: '#9E8F94' }}>
                          No inventory items found matching the selected filters.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', fontSize: '0.82rem', color: '#6B5E63' }}>
                <span>Showing <strong>{filteredSlowItems.length}</strong> of {slowSummary.total_inventory || 0} inventory entries</span>
                <span>Dataset Source: <code style={{ fontSize: '0.75rem' }}>public.inventory</code> + <code style={{ fontSize: '0.75rem' }}>public.order_items</code> (Supabase)</span>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
