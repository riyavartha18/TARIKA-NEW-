import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../auth/AuthContext';
import {
  getDeliveryPartnerDashboard,
  getDeliveryPartnerMyDeliveries,
  getDeliveryPartnerDetail,
  updateDeliveryPartnerStatus,
} from '../../services/api';
import {
  Truck,
  Package,
  CheckCircle2,
  Clock,
  AlertCircle,
  LogOut,
  Search,
  MapPin,
  Phone,
  User,
  Eye,
  RefreshCw,
  Building,
  Navigation,
  AlertTriangle,
  X,
  Send,
  Sparkles,
  Flame,
  Tag,
} from 'lucide-react';
import '../../styles/tarika.css';
import '../../styles/customer-portal.css';

const STATUS_COLORS = {
  Assigned: { bg: '#FEF3C7', text: '#92400E', border: '#FDE68A' },
  'Picked Up': { bg: '#EEF2FF', text: '#3730A3', border: '#C7D2FE' },
  'In Transit': { bg: '#EFF6FF', text: '#1E40AF', border: '#BFDBFE' },
  Delivered: { bg: '#ECFDF5', text: '#065F46', border: '#A7F3D0' },
  Delayed: { bg: '#FFF7ED', text: '#9A3412', border: '#FFEDD5' },
  Failed: { bg: '#FEF2F2', text: '#991B1B', border: '#FECACA' },
};

export default function DeliveryPartnerPortal() {
  const { user, token, logout } = useAuth();

  const [activeTab, setActiveTab] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [metrics, setMetrics] = useState({
    total: 0,
    assigned: 0,
    picked_up: 0,
    in_transit: 0,
    delivered: 0,
    delayed: 0,
    failed: 0,
  });
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // Selected delivery detail modal state
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // Exception form state
  const [exceptionModalOpen, setExceptionModalOpen] = useState(false);
  const [exceptionDeliveryId, setExceptionDeliveryId] = useState(null);
  const [exceptionStatus, setExceptionStatus] = useState('Delayed');
  const [exceptionReason, setExceptionReason] = useState('');
  const [actionSubmitting, setActionSubmitting] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 4000);
  };

  const fetchDashboardData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);

    const [dashRes, listRes] = await Promise.all([
      getDeliveryPartnerDashboard(token),
      getDeliveryPartnerMyDeliveries(token, { status: activeTab, search: searchTerm }),
    ]);

    setLoading(false);
    setRefreshing(false);

    if (dashRes.success) {
      setMetrics(dashRes.metrics || {});
    }

    if (listRes.success) {
      setDeliveries(listRes.deliveries || []);
    } else {
      setError(listRes.error || 'Failed to load assigned deliveries.');
    }
  }, [token, activeTab, searchTerm]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const handleViewDetail = async (deliveryId) => {
    setDetailLoading(true);
    const res = await getDeliveryPartnerDetail(token, deliveryId);
    setDetailLoading(false);
    if (res.success) {
      setSelectedDelivery(res.delivery);
    } else {
      showToast(`Error: ${res.error}`);
    }
  };

  const handleStatusChange = async (deliveryId, newStatus, reason = '') => {
    setActionSubmitting(true);
    const res = await updateDeliveryPartnerStatus(token, deliveryId, newStatus, reason);
    setActionSubmitting(false);

    if (res.success) {
      showToast(`Status updated to "${newStatus}"!`);
      if (selectedDelivery && selectedDelivery.delivery_id === deliveryId) {
        setSelectedDelivery(res.delivery);
      }
      if (exceptionModalOpen) {
        setExceptionModalOpen(false);
        setExceptionReason('');
      }
      fetchDashboardData();
    } else {
      showToast(`Failed: ${res.error}`);
    }
  };

  const openExceptionModal = (deliveryId) => {
    setExceptionDeliveryId(deliveryId);
    setExceptionStatus('Delayed');
    setExceptionReason('');
    setExceptionModalOpen(true);
  };

  const submitException = (e) => {
    e.preventDefault();
    if (!exceptionReason.trim()) {
      showToast('Please provide a reason for the exception.');
      return;
    }
    handleStatusChange(exceptionDeliveryId, exceptionStatus, exceptionReason);
  };

  return (
    <div
      className="tarika-home"
      style={{
        minHeight: '100vh',
        backgroundColor: 'var(--tarika-bg, #FAF7F5)',
        color: 'var(--tarika-text-main, #1F191B)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            bottom: '2rem',
            right: '2rem',
            zIndex: 9999,
            background: '#FFFFFF',
            color: '#1F191B',
            padding: '1rem 1.5rem',
            borderRadius: '16px',
            border: '1px solid rgba(216, 114, 126, 0.35)',
            boxShadow: '0 12px 35px rgba(184, 80, 94, 0.18)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            fontSize: '0.9rem',
            fontWeight: '600',
            animation: 'fadeIn 0.3s ease',
          }}
        >
          <CheckCircle2 size={20} color="#B8505E" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Ticker Marquee Header */}
      <header style={{ position: 'sticky', top: 0, zIndex: 100 }}>
        <div className="customer-marquee-wrap">
          <div className="customer-marquee-track">
            {[1, 2, 3].map((loop) => (
              <React.Fragment key={loop}>
                <span className="customer-marquee-item">
                  <Truck size={13} /> TARIKA LOGISTICS NETWORK
                </span>
                <span className="customer-marquee-separator">•</span>
                <span className="customer-marquee-item">
                  <Sparkles size={13} /> EXPRESS FIELD FULFILLMENT
                </span>
                <span className="customer-marquee-separator">•</span>
                <span className="customer-marquee-item">
                  ATELIER GUARANTEE
                </span>
                <span className="customer-marquee-separator">•</span>
                <span className="customer-marquee-item">
                  <Flame size={13} /> REAL-TIME DISPATCH PORTAL
                </span>
                <span className="customer-marquee-separator">•</span>
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Main Navigation Bar */}
        <nav
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            borderBottom: '1px solid rgba(216, 114, 126, 0.18)',
            boxShadow: '0 4px 20px rgba(184, 80, 94, 0.06)',
            transition: 'all 0.3s ease',
          }}
        >
          <div
            style={{
              maxWidth: '1680px',
              margin: '0 auto',
              padding: '0.85rem 2rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            {/* Brand Logo & Subtitle */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '46px',
                  height: '46px',
                  borderRadius: '14px',
                  background: 'linear-gradient(135deg, #FBF1F0 0%, #F7E4E2 100%)',
                  border: '1px solid rgba(216, 114, 126, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#B8505E',
                  boxShadow: '0 4px 12px rgba(184, 80, 94, 0.1)',
                }}
              >
                <Truck size={24} />
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span
                    style={{
                      fontFamily: "'Playfair Display', serif",
                      fontSize: '1.6rem',
                      fontWeight: 700,
                      letterSpacing: '0.08em',
                      background: 'linear-gradient(135deg, #1F191B 0%, #B8505E 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    TARIKA
                  </span>
                  <span
                    style={{
                      padding: '0.25rem 0.65rem',
                      borderRadius: '20px',
                      background: '#FBF1F0',
                      color: '#B8505E',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      letterSpacing: '0.06em',
                      textTransform: 'uppercase',
                      border: '1px solid rgba(216, 114, 126, 0.3)',
                    }}
                  >
                    Delivery Partner
                  </span>
                </div>
                <div
                  style={{
                    fontSize: '0.58rem',
                    letterSpacing: '0.24em',
                    color: '#8E3642',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    marginTop: '2px',
                  }}
                >
                  FIELD DISPATCH PORTAL & FULFILLMENT
                </div>
              </div>
            </div>

            {/* User Profile & Action Controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: 600, fontSize: '0.925rem', color: '#1F191B' }}>
                  {user?.full_name || 'Delivery Partner'}
                </div>
                <div
                  style={{
                    fontSize: '0.8rem',
                    color: '#B8505E',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    justifyContent: 'flex-end',
                  }}
                >
                  <Building size={13} />
                  <span>{user?.courier_company || 'Independent Express'}</span>
                </div>
              </div>

              <button
                onClick={handleRefresh}
                className="tarika-btn-outline"
                disabled={refreshing}
                style={{
                  padding: '0.55rem 0.85rem',
                  borderRadius: '9999px',
                  fontSize: '0.85rem',
                }}
                title="Refresh Deliveries"
              >
                <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
              </button>

              <button
                onClick={logout}
                className="tarika-btn-outline"
                style={{
                  padding: '0.55rem 1.25rem',
                  borderRadius: '9999px',
                  fontSize: '0.85rem',
                  color: '#B8505E',
                  borderColor: 'rgba(216, 114, 126, 0.3)',
                }}
              >
                <LogOut size={16} />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content Area */}
      <main style={{ maxWidth: '1680px', width: '100%', margin: '2rem auto', padding: '0 2.5rem', flex: 1, boxSizing: 'border-box' }}>
        {/* Dispatch Dashboard Metrics Grid */}
        <section style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <div>
              <h2
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontSize: '1.35rem',
                  fontWeight: 700,
                  color: '#1F191B',
                  margin: 0,
                  letterSpacing: '0.02em',
                }}
              >
                Dispatch Dashboard Summary
              </h2>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.825rem', color: '#6B5E63' }}>
                Real-time queue tracking & dispatch status
              </p>
            </div>
            <span
              style={{
                fontSize: '0.825rem',
                color: '#6B5E63',
                background: '#FFFFFF',
                padding: '0.35rem 0.85rem',
                borderRadius: '20px',
                border: '1px solid #F0E2E0',
                boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
              }}
            >
              Total Assigned: <strong style={{ color: '#B8505E' }}>{metrics.total || 0}</strong>
            </span>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
              gap: '1.25rem',
            }}
          >
            {/* Metric Card: All */}
            <div
              onClick={() => setActiveTab('ALL')}
              style={{
                padding: '1.35rem 1.5rem',
                borderRadius: '20px',
                cursor: 'pointer',
                background: activeTab === 'ALL' ? '#FBF1F0' : '#FFFFFF',
                border: activeTab === 'ALL' ? '1px solid #D8727E' : '1px solid #F0E2E0',
                boxShadow: activeTab === 'ALL' ? '0 12px 32px rgba(184, 80, 94, 0.12)' : '0 8px 30px rgba(184, 80, 94, 0.06)',
                transition: 'all 0.25s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#6B5E63', fontWeight: 600, letterSpacing: '0.04em' }}>ALL ASSIGNED</span>
                <Package size={18} color="#B8505E" />
              </div>
              <div style={{ fontSize: '1.95rem', fontWeight: 800, color: '#1F191B', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {metrics.total || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6B5E63', marginTop: '0.25rem' }}>Deliveries in queue</div>
            </div>

            {/* Metric Card: Assigned */}
            <div
              onClick={() => setActiveTab('Assigned')}
              style={{
                padding: '1.35rem 1.5rem',
                borderRadius: '20px',
                cursor: 'pointer',
                background: activeTab === 'Assigned' ? '#FFFBEB' : '#FFFFFF',
                border: activeTab === 'Assigned' ? '1px solid #F59E0B' : '1px solid #F0E2E0',
                boxShadow: activeTab === 'Assigned' ? '0 12px 32px rgba(245, 158, 11, 0.15)' : '0 8px 30px rgba(184, 80, 94, 0.06)',
                transition: 'all 0.25s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#6B5E63', fontWeight: 600, letterSpacing: '0.04em' }}>ASSIGNED</span>
                <Clock size={18} color="#D97706" />
              </div>
              <div style={{ fontSize: '1.95rem', fontWeight: 800, color: '#D97706', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {metrics.assigned || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6B5E63', marginTop: '0.25rem' }}>Ready for pickup</div>
            </div>

            {/* Metric Card: Picked Up */}
            <div
              onClick={() => setActiveTab('Picked Up')}
              style={{
                padding: '1.35rem 1.5rem',
                borderRadius: '20px',
                cursor: 'pointer',
                background: activeTab === 'Picked Up' ? '#EEF2FF' : '#FFFFFF',
                border: activeTab === 'Picked Up' ? '1px solid #6366F1' : '1px solid #F0E2E0',
                boxShadow: activeTab === 'Picked Up' ? '0 12px 32px rgba(99, 102, 241, 0.15)' : '0 8px 30px rgba(184, 80, 94, 0.06)',
                transition: 'all 0.25s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#6B5E63', fontWeight: 600, letterSpacing: '0.04em' }}>PICKED UP</span>
                <Package size={18} color="#4F46E5" />
              </div>
              <div style={{ fontSize: '1.95rem', fontWeight: 800, color: '#4F46E5', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {metrics.picked_up || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6B5E63', marginTop: '0.25rem' }}>Collected from warehouse</div>
            </div>

            {/* Metric Card: In Transit */}
            <div
              onClick={() => setActiveTab('In Transit')}
              style={{
                padding: '1.35rem 1.5rem',
                borderRadius: '20px',
                cursor: 'pointer',
                background: activeTab === 'In Transit' ? '#EFF6FF' : '#FFFFFF',
                border: activeTab === 'In Transit' ? '1px solid #3B82F6' : '1px solid #F0E2E0',
                boxShadow: activeTab === 'In Transit' ? '0 12px 32px rgba(59, 130, 246, 0.15)' : '0 8px 30px rgba(184, 80, 94, 0.06)',
                transition: 'all 0.25s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#6B5E63', fontWeight: 600, letterSpacing: '0.04em' }}>IN TRANSIT</span>
                <Navigation size={18} color="#2563EB" />
              </div>
              <div style={{ fontSize: '1.95rem', fontWeight: 800, color: '#2563EB', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {metrics.in_transit || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6B5E63', marginTop: '0.25rem' }}>Out for delivery</div>
            </div>

            {/* Metric Card: Delivered */}
            <div
              onClick={() => setActiveTab('Delivered')}
              style={{
                padding: '1.35rem 1.5rem',
                borderRadius: '20px',
                cursor: 'pointer',
                background: activeTab === 'Delivered' ? '#ECFDF5' : '#FFFFFF',
                border: activeTab === 'Delivered' ? '1px solid #10B981' : '1px solid #F0E2E0',
                boxShadow: activeTab === 'Delivered' ? '0 12px 32px rgba(16, 185, 129, 0.15)' : '0 8px 30px rgba(184, 80, 94, 0.06)',
                transition: 'all 0.25s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#6B5E63', fontWeight: 600, letterSpacing: '0.04em' }}>DELIVERED</span>
                <CheckCircle2 size={18} color="#059669" />
              </div>
              <div style={{ fontSize: '1.95rem', fontWeight: 800, color: '#059669', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {metrics.delivered || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6B5E63', marginTop: '0.25rem' }}>Handed over</div>
            </div>

            {/* Metric Card: Delayed / Failed */}
            <div
              onClick={() => setActiveTab('Delayed')}
              style={{
                padding: '1.35rem 1.5rem',
                borderRadius: '20px',
                cursor: 'pointer',
                background: ['Delayed', 'Failed'].includes(activeTab) ? '#FBF1F0' : '#FFFFFF',
                border: ['Delayed', 'Failed'].includes(activeTab) ? '1px solid #D8727E' : '1px solid #F0E2E0',
                boxShadow: ['Delayed', 'Failed'].includes(activeTab) ? '0 12px 32px rgba(184, 80, 94, 0.15)' : '0 8px 30px rgba(184, 80, 94, 0.06)',
                transition: 'all 0.25s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', color: '#6B5E63', fontWeight: 600, letterSpacing: '0.04em' }}>EXCEPTIONS</span>
                <AlertTriangle size={18} color="#B8505E" />
              </div>
              <div style={{ fontSize: '1.95rem', fontWeight: 800, color: '#B8505E', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
                {(metrics.delayed || 0) + (metrics.failed || 0)}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6B5E63', marginTop: '0.25rem' }}>
                Delayed: {metrics.delayed || 0} | Failed: {metrics.failed || 0}
              </div>
            </div>
          </div>
        </section>

        {/* Filter Bar & Search */}
        <section style={{ marginBottom: '2rem' }}>
          <div
            style={{
              background: '#FFFFFF',
              borderRadius: '20px',
              border: '1px solid #F0E2E0',
              padding: '1rem 1.5rem',
              boxShadow: '0 6px 24px rgba(184, 80, 94, 0.05)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            {/* Status Filter Tabs */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
              {['ALL', 'Assigned', 'Picked Up', 'In Transit', 'Delivered', 'Delayed', 'Failed'].map((tab) => {
                const isActive = activeTab === tab;
                return (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    style={{
                      padding: '0.45rem 1.15rem',
                      borderRadius: '9999px',
                      fontSize: '0.825rem',
                      fontWeight: isActive ? 700 : 600,
                      border: isActive ? '1px solid #D8727E' : '1px solid #F0E2E0',
                      background: isActive ? '#FBF1F0' : 'transparent',
                      color: isActive ? '#B8505E' : '#6B5E63',
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    {tab === 'ALL' ? 'All Deliveries' : tab}
                  </button>
                );
              })}
            </div>

            {/* Search Input */}
            <div style={{ position: 'relative', width: '300px' }}>
              <Search
                size={16}
                color="#9E8F94"
                style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }}
              />
              <input
                type="text"
                placeholder="Search delivery, order or customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.85rem 0.6rem 2.4rem',
                  borderRadius: '12px',
                  background: '#FAF7F5',
                  border: '1px solid #F0E2E0',
                  color: '#1F191B',
                  fontSize: '0.85rem',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </div>
        </section>

        {/* My Deliveries List Section */}
        <section>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <h2
              style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: '1.35rem',
                fontWeight: 700,
                color: '#1F191B',
                margin: 0,
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <Package size={22} color="#B8505E" />
              <span>My Assigned Deliveries</span>
              <span
                style={{
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  padding: '0.2rem 0.65rem',
                  borderRadius: '12px',
                  background: '#FBF1F0',
                  color: '#B8505E',
                  border: '1px solid rgba(216, 114, 126, 0.2)',
                }}
              >
                {deliveries.length}
              </span>
            </h2>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '4rem 2rem', color: '#6B5E63' }}>
              <RefreshCw size={28} className="animate-spin" style={{ margin: '0 auto 1rem', color: '#B8505E' }} />
              <p style={{ fontWeight: 600 }}>Fetching assigned deliveries from backend...</p>
            </div>
          ) : error ? (
            <div
              style={{
                padding: '2.5rem 2rem',
                borderRadius: '20px',
                textAlign: 'center',
                background: '#FFFFFF',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                boxShadow: '0 8px 30px rgba(184, 80, 94, 0.06)',
              }}
            >
              <AlertCircle size={36} color="#DC2626" style={{ margin: '0 auto 1rem' }} />
              <p style={{ color: '#DC2626', fontWeight: 600 }}>{error}</p>
              <button
                onClick={fetchDashboardData}
                className="tarika-btn-outline"
                style={{ width: 'auto', margin: '1rem auto 0', borderRadius: '9999px' }}
              >
                Retry
              </button>
            </div>
          ) : deliveries.length === 0 ? (
            <div
              style={{
                padding: '4rem 2rem',
                borderRadius: '20px',
                textAlign: 'center',
                background: '#FFFFFF',
                border: '1px solid #F0E2E0',
                boxShadow: '0 8px 30px rgba(184, 80, 94, 0.06)',
              }}
            >
              <Package size={48} color="#9E8F94" style={{ margin: '0 auto 1rem', opacity: 0.6 }} />
              <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: '1.25rem', color: '#1F191B', marginBottom: '0.5rem' }}>
                No Deliveries Found
              </h3>
              <p style={{ color: '#6B5E63', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
                {activeTab !== 'ALL'
                  ? `There are currently no deliveries with status "${activeTab}" assigned to your profile.`
                  : 'You do not have any deliveries assigned to your delivery partner account yet.'}
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.25rem' }}>
              {deliveries.map((item) => {
                const statusStyle = STATUS_COLORS[item.delivery_status] || {
                  bg: '#F3F4F6',
                  text: '#374151',
                  border: '#E5E7EB',
                };

                return (
                  <div
                    key={item.delivery_id}
                    style={{
                      background: '#FFFFFF',
                      borderRadius: '20px',
                      padding: '1.5rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '1.25rem',
                      border: '1px solid #F0E2E0',
                      boxShadow: '0 8px 30px rgba(184, 80, 94, 0.06)',
                      transition: 'transform 0.2s ease, boxShadow 0.2s ease',
                    }}
                  >
                    {/* Top Row: Delivery ID, Order ID & Status Badge */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{ fontWeight: 800, fontSize: '1.05rem', color: '#1F191B', letterSpacing: '0.02em' }}>
                          {item.delivery_id}
                        </span>
                        <span style={{ color: '#6B5E63', fontSize: '0.85rem' }}>
                          Order: <strong>{item.order_id}</strong>
                        </span>
                      </div>

                      <span
                        style={{
                          padding: '0.35rem 0.85rem',
                          borderRadius: '20px',
                          background: statusStyle.bg,
                          color: statusStyle.text,
                          border: `1px solid ${statusStyle.border}`,
                          fontSize: '0.8rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {item.delivery_status}
                      </span>
                    </div>

                    {/* Middle Info Grid */}
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                        gap: '1rem',
                        padding: '1.15rem',
                        borderRadius: '14px',
                        background: '#FFFBF9',
                        border: '1px solid #F0E2E0',
                      }}
                    >
                      {/* Customer Info */}
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#9E8F94', marginBottom: '0.25rem', fontWeight: 700, letterSpacing: '0.05em' }}>
                          CUSTOMER DETAILS
                        </div>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#1F191B', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <User size={14} color="#B8505E" />
                          <span>{item.customer_name}</span>
                        </div>
                        {item.customer_phone && (
                          <div style={{ fontSize: '0.825rem', color: '#6B5E63', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                            <Phone size={13} color="#B8505E" />
                            <span>{item.customer_phone}</span>
                          </div>
                        )}
                      </div>

                      {/* Shipping Address */}
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#9E8F94', marginBottom: '0.25rem', fontWeight: 700, letterSpacing: '0.05em' }}>
                          SHIPPING LOCATION
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#1F191B', lineHeight: 1.4, display: 'flex', alignItems: 'flex-start', gap: '0.35rem' }}>
                          <MapPin size={15} color="#D8727E" style={{ flexShrink: 0, marginTop: '2px' }} />
                          <span>{item.customer_address || item.customer_city || 'Address provided on order'}</span>
                        </div>
                      </div>

                      {/* Order Amount & Items */}
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#9E8F94', marginBottom: '0.25rem', fontWeight: 700, letterSpacing: '0.05em' }}>
                          PACKAGE SUMMARY
                        </div>
                        <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#1F191B' }}>
                          ₹{Number(item.total_amount || 0).toLocaleString()} • {item.item_count || 1} Item(s)
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#6B5E63', marginTop: '0.25rem' }}>
                          Courier: <strong>{item.delivery_partner || user?.courier_company || 'Standard Express'}</strong>
                        </div>
                      </div>

                      {/* Timeline Dates */}
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#9E8F94', marginBottom: '0.25rem', fontWeight: 700, letterSpacing: '0.05em' }}>
                          DISPATCH & EXPECTED
                        </div>
                        <div style={{ fontSize: '0.825rem', color: '#6B5E63' }}>
                          Dispatched: {item.dispatch_date || 'N/A'}
                        </div>
                        <div style={{ fontSize: '0.825rem', color: '#B8505E', marginTop: '0.2rem', fontWeight: 700 }}>
                          Expected: {item.expected_delivery_date || 'Today'}
                        </div>
                      </div>
                    </div>

                    {/* Failure Reason Notification Banner if Delayed or Failed */}
                    {item.failure_reason && (
                      <div
                        style={{
                          padding: '0.75rem 1rem',
                          borderRadius: '12px',
                          background: '#FEF2F2',
                          border: '1px solid #FECACA',
                          color: '#991B1B',
                          fontSize: '0.85rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                        }}
                      >
                        <AlertTriangle size={16} color="#DC2626" />
                        <span>
                          <strong>Exception Reason:</strong> {item.failure_reason}
                        </span>
                      </div>
                    )}

                    {/* Bottom Action Buttons Bar */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: '0.75rem',
                        paddingTop: '0.5rem',
                        borderTop: '1px solid #F0E2E0',
                      }}
                    >
                      <button
                        onClick={() => handleViewDetail(item.delivery_id)}
                        className="tarika-btn-outline"
                        style={{ width: 'auto', padding: '0.5rem 1.25rem', fontSize: '0.85rem', borderRadius: '9999px' }}
                      >
                        <Eye size={15} />
                        <span>View Details</span>
                      </button>

                      {/* Quick Action Buttons per status */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                        {item.delivery_status === 'Assigned' && (
                          <button
                            onClick={() => handleStatusChange(item.delivery_id, 'Picked Up')}
                            disabled={actionSubmitting}
                            style={{
                              width: 'auto',
                              padding: '0.5rem 1.25rem',
                              fontSize: '0.85rem',
                              borderRadius: '9999px',
                              background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
                              color: '#FFFFFF',
                              border: 'none',
                              fontWeight: 600,
                              cursor: 'pointer',
                              boxShadow: '0 4px 14px rgba(99, 102, 241, 0.3)',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.4rem',
                            }}
                          >
                            <Package size={15} />
                            <span>Confirm Pickup</span>
                          </button>
                        )}

                        {(item.delivery_status === 'Assigned' || item.delivery_status === 'Picked Up') && (
                          <button
                            onClick={() => handleStatusChange(item.delivery_id, 'In Transit')}
                            disabled={actionSubmitting}
                            style={{
                              width: 'auto',
                              padding: '0.5rem 1.25rem',
                              fontSize: '0.85rem',
                              borderRadius: '9999px',
                              background: 'linear-gradient(135deg, #3B82F6, #2563EB)',
                              color: '#FFFFFF',
                              border: 'none',
                              fontWeight: 600,
                              cursor: 'pointer',
                              boxShadow: '0 4px 14px rgba(59, 130, 246, 0.3)',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.4rem',
                            }}
                          >
                            <Navigation size={15} />
                            <span>Start Delivery</span>
                          </button>
                        )}

                        {item.delivery_status !== 'Delivered' && (
                          <button
                            onClick={() => handleStatusChange(item.delivery_id, 'Delivered')}
                            disabled={actionSubmitting}
                            style={{
                              width: 'auto',
                              padding: '0.5rem 1.25rem',
                              fontSize: '0.85rem',
                              borderRadius: '9999px',
                              background: 'linear-gradient(135deg, #10B981, #059669)',
                              color: '#FFFFFF',
                              border: 'none',
                              fontWeight: 600,
                              cursor: 'pointer',
                              boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.4rem',
                            }}
                          >
                            <CheckCircle2 size={15} />
                            <span>Mark as Delivered</span>
                          </button>
                        )}

                        {item.delivery_status !== 'Delivered' && (
                          <button
                            onClick={() => openExceptionModal(item.delivery_id)}
                            style={{
                              width: 'auto',
                              padding: '0.5rem 1.15rem',
                              fontSize: '0.85rem',
                              borderRadius: '9999px',
                              background: '#FFF7ED',
                              border: '1px solid #FFEDD5',
                              color: '#C2410C',
                              fontWeight: 600,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.4rem',
                            }}
                          >
                            <AlertTriangle size={15} />
                            <span>Report Exception</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>

      {/* Subdued Boutique Footer */}
      <footer
        style={{
          borderTop: '1px solid rgba(216, 114, 126, 0.18)',
          backgroundColor: '#FFFFFF',
          padding: '2.5rem 2rem',
          marginTop: 'auto',
        }}
      >
        <div
          style={{
            maxWidth: '1680px',
            margin: '0 auto',
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1.5rem',
          }}
        >
          <div>
            <span
              style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: '1.3rem',
                fontWeight: 700,
                color: '#1F191B',
                letterSpacing: '0.08em',
              }}
            >
              TARIKA
            </span>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.78rem', color: '#9E8F94' }}>
              Field Dispatch & National Express Logistics • © 2026 TARIKA Retail Inc.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '2rem', fontSize: '0.82rem', color: '#6B5E63' }}>
            <span>Atelier Fulfillment</span>
            <span>Express Courier Guarantee</span>
            <span>Field Dispatch Center</span>
          </div>
        </div>
      </footer>

      {/* Delivery Detail Modal */}
      {selectedDelivery && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            background: 'rgba(31, 25, 27, 0.45)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.5rem',
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '720px',
              maxHeight: '90vh',
              overflowY: 'auto',
              borderRadius: '24px',
              padding: '2rem',
              position: 'relative',
              background: '#FFFFFF',
              border: '1px solid #F0E2E0',
              boxShadow: '0 25px 60px rgba(184, 80, 94, 0.15)',
              animation: 'modalFadeIn 0.3s ease',
            }}
          >
            {/* Close Button */}
            <button
              onClick={() => setSelectedDelivery(null)}
              style={{
                position: 'absolute',
                top: '1.5rem',
                right: '1.5rem',
                background: '#FBF1F0',
                border: 'none',
                color: '#6B5E63',
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              <X size={18} />
            </button>

            {/* Modal Header */}
            <div style={{ marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid #F0E2E0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <Truck size={22} color="#B8505E" />
                <h3
                  style={{
                    fontFamily: "'Playfair Display', serif",
                    fontSize: '1.45rem',
                    fontWeight: 700,
                    color: '#1F191B',
                    margin: 0,
                  }}
                >
                  Delivery Details ({selectedDelivery.delivery_id})
                </h3>
              </div>
              <p style={{ color: '#6B5E63', fontSize: '0.875rem', margin: 0 }}>
                Order #{selectedDelivery.order_id} • Assigned to {selectedDelivery.assigned_employee_name || user?.full_name}
              </p>
            </div>

            {/* Modal Content */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Status Banner */}
              <div
                style={{
                  padding: '1rem 1.25rem',
                  borderRadius: '14px',
                  background: STATUS_COLORS[selectedDelivery.delivery_status]?.bg || '#F3F4F6',
                  border: `1px solid ${STATUS_COLORS[selectedDelivery.delivery_status]?.border || '#E5E7EB'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#6B5E63', fontWeight: 700, letterSpacing: '0.05em' }}>CURRENT DELIVERY STATUS</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: STATUS_COLORS[selectedDelivery.delivery_status]?.text }}>
                    {selectedDelivery.delivery_status}
                  </div>
                </div>
                {selectedDelivery.actual_delivery_date && (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', color: '#6B5E63' }}>Delivered On</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#059669' }}>{selectedDelivery.actual_delivery_date}</div>
                  </div>
                )}
              </div>

              {/* Customer & Shipping Section */}
              <div
                style={{
                  padding: '1.25rem',
                  borderRadius: '16px',
                  background: '#FAF7F5',
                  border: '1px solid #F0E2E0',
                }}
              >
                <h4 style={{ fontFamily: "'Playfair Display', serif", fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: '#B8505E' }}>
                  Customer & Shipping Address
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem' }}>
                  <div>
                    <div style={{ color: '#9E8F94', fontSize: '0.78rem', fontWeight: 700 }}>RECIPIENT NAME</div>
                    <div style={{ fontWeight: 700, color: '#1F191B', marginTop: '2px' }}>{selectedDelivery.customer_name}</div>
                  </div>
                  <div>
                    <div style={{ color: '#9E8F94', fontSize: '0.78rem', fontWeight: 700 }}>CONTACT PHONE</div>
                    <div style={{ fontWeight: 700, color: '#B8505E', marginTop: '2px' }}>{selectedDelivery.customer_phone || 'N/A'}</div>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <div style={{ color: '#9E8F94', fontSize: '0.78rem', fontWeight: 700 }}>SHIPPING ADDRESS</div>
                    <div style={{ fontWeight: 600, color: '#1F191B', marginTop: '2px', lineHeight: 1.4 }}>
                      {selectedDelivery.shipping_address || 'Address registered with order'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Order Items List */}
              <div>
                <h4 style={{ fontFamily: "'Playfair Display', serif", fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: '#1F191B' }}>
                  Items in Package ({selectedDelivery.items?.length || 0})
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {selectedDelivery.items && selectedDelivery.items.length > 0 ? (
                    selectedDelivery.items.map((item, idx) => (
                      <div
                        key={idx}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.85rem 1rem',
                          borderRadius: '14px',
                          background: '#FFFFFF',
                          border: '1px solid #F0E2E0',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.02)',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                          <div
                            style={{
                              width: '44px',
                              height: '44px',
                              borderRadius: '10px',
                              background: '#FAF7F5',
                              border: '1px solid #F0E2E0',
                              overflow: 'hidden',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            {item.image ? (
                              <img src={item.image} alt={item.product_name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            ) : (
                              <Package size={22} color="#B8505E" />
                            )}
                          </div>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#1F191B' }}>{item.product_name}</div>
                            <div style={{ fontSize: '0.78rem', color: '#6B5E63' }}>
                              SKU: {item.sku || 'N/A'} {item.size && `• Size: ${item.size}`} {item.color && `• Color: ${item.color}`}
                            </div>
                          </div>
                        </div>

                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontWeight: 800, fontSize: '0.925rem', color: '#1F191B' }}>₹{Number(item.subtotal || 0).toLocaleString()}</div>
                          <div style={{ fontSize: '0.78rem', color: '#6B5E63' }}>Qty: {item.quantity}</div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div style={{ fontSize: '0.85rem', color: '#6B5E63', padding: '1rem', textAlign: 'center' }}>
                      Item details recorded on order profile.
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons inside Modal */}
              <div
                style={{
                  paddingTop: '1rem',
                  borderTop: '1px solid #F0E2E0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'flex-end',
                  gap: '0.75rem',
                }}
              >
                {selectedDelivery.delivery_status !== 'Delivered' && (
                  <button
                    onClick={() => {
                      handleStatusChange(selectedDelivery.delivery_id, 'Delivered');
                    }}
                    disabled={actionSubmitting}
                    style={{
                      width: 'auto',
                      padding: '0.65rem 1.6rem',
                      borderRadius: '9999px',
                      background: 'linear-gradient(135deg, #10B981, #059669)',
                      color: '#FFFFFF',
                      border: 'none',
                      fontWeight: 600,
                      cursor: 'pointer',
                      boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.4rem',
                    }}
                  >
                    <CheckCircle2 size={16} />
                    <span>Mark as Delivered</span>
                  </button>
                )}
                <button
                  onClick={() => setSelectedDelivery(null)}
                  className="tarika-btn-outline"
                  style={{ width: 'auto', padding: '0.65rem 1.5rem', borderRadius: '9999px' }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Exception Report Modal */}
      {exceptionModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1100,
            background: 'rgba(31, 25, 27, 0.45)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1.5rem',
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '480px',
              borderRadius: '24px',
              padding: '2rem',
              position: 'relative',
              background: '#FFFFFF',
              border: '1px solid rgba(216, 114, 126, 0.3)',
              boxShadow: '0 25px 60px rgba(184, 80, 94, 0.15)',
              animation: 'modalFadeIn 0.3s ease',
            }}
          >
            <button
              onClick={() => setExceptionModalOpen(false)}
              style={{
                position: 'absolute',
                top: '1.25rem',
                right: '1.25rem',
                background: '#FBF1F0',
                border: 'none',
                color: '#6B5E63',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              <X size={18} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', color: '#B8505E' }}>
              <AlertTriangle size={22} />
              <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#1F191B' }}>
                Report Delivery Exception
              </h3>
            </div>

            <form onSubmit={submitException} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.5rem', color: '#6B5E63', letterSpacing: '0.05em' }}>
                  EXCEPTION TYPE
                </label>
                <select
                  value={exceptionStatus}
                  onChange={(e) => setExceptionStatus(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.7rem 0.85rem',
                    borderRadius: '12px',
                    background: '#FAF7F5',
                    border: '1px solid #F0E2E0',
                    color: '#1F191B',
                    outline: 'none',
                    fontSize: '0.875rem',
                    boxSizing: 'border-box',
                  }}
                >
                  <option value="Delayed">Delayed (Customer not available / Traffic / Logistics delay)</option>
                  <option value="Failed">Failed (Invalid address / Customer rejected / Damaged package)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.5rem', color: '#6B5E63', letterSpacing: '0.05em' }}>
                  REASON / REMARKS
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="Describe the reason for delay or delivery failure..."
                  value={exceptionReason}
                  onChange={(e) => setExceptionReason(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.7rem 0.85rem',
                    borderRadius: '12px',
                    background: '#FAF7F5',
                    border: '1px solid #F0E2E0',
                    color: '#1F191B',
                    outline: 'none',
                    fontSize: '0.875rem',
                    resize: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setExceptionModalOpen(false)}
                  className="tarika-btn-outline"
                  style={{ width: 'auto', padding: '0.6rem 1.25rem', borderRadius: '9999px' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionSubmitting}
                  className="tarika-btn-primary"
                  style={{
                    width: 'auto',
                    padding: '0.6rem 1.6rem',
                    borderRadius: '9999px',
                    background: exceptionStatus === 'Failed' ? 'linear-gradient(135deg, #EF4444, #DC2626)' : 'linear-gradient(135deg, #D8727E 0%, #C45766 100%)',
                  }}
                >
                  <Send size={15} />
                  <span>Submit Exception</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
