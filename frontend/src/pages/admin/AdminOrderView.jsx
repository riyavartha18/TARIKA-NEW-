import React, { useState, useEffect, useCallback } from 'react';
import {
  Package,
  CheckCircle2,
  AlertTriangle,
  Search,
  Filter,
  Eye,
  RefreshCw,
  X,
  Warehouse as WarehouseIcon,
  ShoppingBag,
  CreditCard,
  User,
  MapPin,
  Clock,
  XCircle,
  Truck,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';
import { getAdminOrders, getAdminOrderDetail } from '../../services/api';

/* ─── Status Badge Helper ────────────────────────────────────────────────── */
function StatusBadge({ status }) {
  const s = (status || '').toLowerCase();
  let bg, color, border, label, Icon;

  if (s.includes('pending')) {
    bg = '#FFFBEB'; color = '#B45309'; border = '#FDE68A'; label = 'Pending'; Icon = Clock;
  } else if (s.includes('processing')) {
    bg = '#EFF6FF'; color = '#1D4ED8'; border = '#BFDBFE'; label = 'Processing'; Icon = RefreshCw;
  } else if (s.includes('delivered') || s.includes('completed')) {
    bg = '#ECFDF5'; color = '#059669'; border = '#A7F3D0'; label = 'Delivered'; Icon = CheckCircle2;
  } else if (s.includes('shipped')) {
    bg = '#F0FDF4'; color = '#15803D'; border = '#BBF7D0'; label = 'Shipped'; Icon = Truck;
  } else if (s.includes('cancelled') || s.includes('failed')) {
    bg = '#FEF2F2'; color = '#B91C1C'; border = '#FECACA'; label = 'Cancelled'; Icon = XCircle;
  } else {
    bg = '#F3F4F6'; color = '#6B7280'; border = '#D1D5DB'; label = status || 'Unknown'; Icon = Package;
  }

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '0.35rem',
      padding: '0.25rem 0.7rem', borderRadius: '9999px',
      backgroundColor: bg, color, border: `1px solid ${border}`,
      fontSize: '0.75rem', fontWeight: 700, whiteSpace: 'nowrap',
    }}>
      <Icon size={12} />
      {label}
    </span>
  );
}

/* ─── KPI Summary Card ───────────────────────────────────────────────────── */
function KpiCard({ label, value, icon: Icon, iconBg, iconColor, accentColor }) {
  return (
    <div className="admin-metric-card" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '1rem', padding: '1.15rem 1.35rem' }}>
      <div style={{
        width: 46, height: 46, borderRadius: 12, flexShrink: 0,
        backgroundColor: iconBg, color: iconColor,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={22} />
      </div>
      <div>
        <p className="admin-metric-title" style={{ marginBottom: 2 }}>{label}</p>
        <p className="admin-metric-val" style={{ fontSize: '1.65rem', color: accentColor || '#1F191B' }}>{value}</p>
      </div>
    </div>
  );
}

/* ─── Main Component ─────────────────────────────────────────────────────── */
export default function AdminOrderView() {
  const { token } = useAuth();

  const [metrics, setMetrics] = useState({
    total_orders: 0,
    pending_orders: 0,
    processing_orders: 0,
    completed_orders: 0,
    cancelled_orders: 0,
  });
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const [selectedOrder, setSelectedOrder] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState(null);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    const activeToken = token || localStorage.getItem('iras_token') || localStorage.getItem('token');
    const res = await getAdminOrders(activeToken, { search: searchTerm, status: statusFilter });
    if (res.success) {
      setOrders(res.orders || []);
      if (res.metrics) setMetrics(res.metrics);
    } else {
      setError(res.error || 'Failed to load orders.');
    }
    setLoading(false);
  }, [token, searchTerm, statusFilter]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  const handleOpenDetails = async (orderId) => {
    setDetailsLoading(true);
    setDetailsError(null);
    setSelectedOrder({ order_id: orderId });
    const activeToken = token || localStorage.getItem('iras_token') || localStorage.getItem('token');
    const res = await getAdminOrderDetail(activeToken, orderId);
    if (res.success) {
      setSelectedOrder(res.order);
    } else {
      setDetailsError(res.error || 'Failed to load order details.');
    }
    setDetailsLoading(false);
  };

  const closeDetails = () => setSelectedOrder(null);

  const STATUS_PILLS = ['ALL', 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'];

  return (
    <div style={{ maxWidth: '1300px', margin: '0 auto' }}>

      {/* ── Page Heading ── */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{
            fontFamily: "var(--font-serif, 'Playfair Display', serif)",
            fontSize: '2rem', fontWeight: 700, color: '#1F191B',
            margin: '0 0 0.3rem 0', display: 'flex', alignItems: 'center', gap: '0.7rem',
          }}>
            <ShoppingBag size={28} style={{ color: '#B8505E' }} />
            Order Management
          </h1>
          <p style={{ color: '#6B5E63', fontSize: '0.92rem', margin: 0 }}>
            Monitor and manage retail orders across customers, warehouses, and fulfillment operations.
          </p>
        </div>

        <button
          onClick={fetchOrders}
          className="tarika-btn-outline"
          style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {/* ── KPI Cards ── */}
      <div className="admin-metrics-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', marginBottom: '1.75rem' }}>
        <KpiCard label="Total Orders"   value={metrics.total_orders}       icon={Package}      iconBg="#FAF7F5" iconColor="#6B5E63" />
        <KpiCard label="Pending"        value={metrics.pending_orders}      icon={Clock}        iconBg="#FFFBEB" iconColor="#D97706" accentColor="#D97706" />
        <KpiCard label="Processing"     value={metrics.processing_orders}   icon={RefreshCw}    iconBg="#EFF6FF" iconColor="#1D4ED8" accentColor="#1D4ED8" />
        <KpiCard label="Completed"      value={metrics.completed_orders}    icon={CheckCircle2} iconBg="#ECFDF5" iconColor="#059669" accentColor="#059669" />
        <KpiCard label="Cancelled"      value={metrics.cancelled_orders}    icon={XCircle}      iconBg="#FEF2F2" iconColor="#DC2626" accentColor="#DC2626" />
      </div>

      {/* ── Toolbar: Search + Status Filter ── */}
      <div className="admin-card" style={{ marginBottom: '1.5rem', padding: '1.1rem 1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          {/* Search */}
          <div style={{ flex: '1 1 280px', position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#9E8F94', pointerEvents: 'none' }} />
            <input
              type="text"
              placeholder="Search by Order ID, customer name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%', boxSizing: 'border-box',
                padding: '0.6rem 0.85rem 0.6rem 2.45rem',
                border: '1px solid rgba(216, 114, 126, 0.25)',
                borderRadius: '8px', fontSize: '0.87rem',
                backgroundColor: '#FAF7F5', color: '#1F191B', outline: 'none',
              }}
            />
          </div>

          {/* Status Filter Pills */}
          <div style={{ display: 'flex', gap: '0.3rem', background: '#FAF7F5', padding: '0.25rem', borderRadius: '8px', border: '1px solid rgba(216,114,126,0.2)', flexWrap: 'wrap' }}>
            <Filter size={14} style={{ alignSelf: 'center', marginLeft: '0.4rem', color: '#9E8F94', flexShrink: 0 }} />
            {STATUS_PILLS.map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                style={{
                  padding: '0.32rem 0.8rem',
                  fontSize: '0.78rem', fontWeight: 700,
                  borderRadius: '6px', border: 'none', cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  background: statusFilter === s ? '#FFFFFF' : 'transparent',
                  color: statusFilter === s ? '#B8505E' : '#6B5E63',
                  boxShadow: statusFilter === s ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
                  transition: 'all 0.18s ease',
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Orders Table ── */}
      <div className="admin-table-wrapper">
        {loading ? (
          <div style={{ padding: '4rem 1rem', textAlign: 'center' }}>
            <RefreshCw size={34} className="animate-spin" style={{ color: '#B8505E', marginBottom: '0.85rem' }} />
            <h3 style={{ fontFamily: "var(--font-serif, 'Playfair Display', serif)", color: '#1F191B', margin: '0 0 0.4rem 0' }}>
              Loading Orders...
            </h3>
            <p style={{ color: '#6B5E63', fontSize: '0.88rem', margin: 0 }}>Fetching order data from the server.</p>
          </div>
        ) : error ? (
          <div style={{ padding: '3rem 1.5rem', textAlign: 'center' }}>
            <AlertCircle size={34} style={{ color: '#DC2626', marginBottom: '0.85rem' }} />
            <h3 style={{ color: '#1F191B', margin: '0 0 0.4rem 0', fontSize: '1.1rem', fontWeight: 600 }}>
              Could Not Load Orders
            </h3>
            <p style={{ color: '#6B5E63', fontSize: '0.88rem', margin: '0 0 1rem 0' }}>{error}</p>
            <button
              className="tarika-btn-outline"
              onClick={fetchOrders}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.55rem 1.1rem', fontSize: '0.85rem' }}
            >
              <RefreshCw size={14} /> Retry
            </button>
          </div>
        ) : orders.length === 0 ? (
          <div style={{ padding: '4rem 1rem', textAlign: 'center' }}>
            <Package size={34} style={{ color: '#9E8F94', marginBottom: '0.85rem' }} />
            <p style={{ color: '#6B5E63', fontSize: '0.9rem', margin: 0 }}>No orders found matching your criteria.</p>
          </div>
        ) : (
          <table className="admin-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Warehouse</th>
                <th>Total</th>
                <th>Status</th>
                <th style={{ textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.order_id} style={{ transition: 'background 0.15s' }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#FAF7F5'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <td>
                    <code style={{ fontSize: '0.8rem', color: '#B8505E', fontWeight: 700 }}>
                      #{order.order_id.substring(0, 8).toUpperCase()}
                    </code>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: '#1F191B', fontSize: '0.87rem' }}>
                      {order.customer_name || 'Unknown'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#9E8F94' }}>
                      {order.customer_email || ''}
                    </div>
                  </td>
                  <td style={{ color: '#6B5E63', fontSize: '0.85rem', whiteSpace: 'nowrap' }}>
                    {order.order_date || 'N/A'}
                  </td>
                  <td>
                    {order.warehouse ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.85rem', color: '#1F191B' }}>
                        <WarehouseIcon size={13} style={{ color: '#9E8F94' }} />
                        {order.warehouse.warehouse_name}
                      </span>
                    ) : (
                      <span style={{ color: '#9E8F94', fontSize: '0.85rem', fontStyle: 'italic' }}>Unassigned</span>
                    )}
                  </td>
                  <td style={{ fontWeight: 700, color: '#1F191B' }}>
                    ₹{parseFloat(order.total_amount || 0).toFixed(2)}
                  </td>
                  <td><StatusBadge status={order.order_status} /></td>
                  <td style={{ textAlign: 'center' }}>
                    <button
                      onClick={() => handleOpenDetails(order.order_id)}
                      title="View Details"
                      style={{
                        background: 'transparent', border: '1px solid rgba(216,114,126,0.3)',
                        borderRadius: '8px', padding: '0.4rem 0.6rem',
                        cursor: 'pointer', color: '#B8505E',
                        display: 'inline-flex', alignItems: 'center',
                        transition: 'all 0.18s ease',
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.background = '#B8505E'; e.currentTarget.style.color = '#fff'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#B8505E'; }}
                    >
                      <Eye size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Row count footer */}
      {!loading && !error && orders.length > 0 && (
        <div style={{ marginTop: '1rem', fontSize: '0.82rem', color: '#6B5E63', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <span>Showing <strong>{orders.length}</strong> orders</span>
          <span>Dataset Source: <code style={{ fontSize: '0.75rem' }}>public.orders</code> (Supabase)</span>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════
          ORDER DETAIL MODAL
         ══════════════════════════════════════════════════════════ */}
      {selectedOrder && (
        <div
          onClick={closeDetails}
          style={{
            position: 'fixed', inset: 0, zIndex: 1000,
            backgroundColor: 'rgba(31, 25, 27, 0.55)',
            backdropFilter: 'blur(4px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: '1.5rem',
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: '#FFFFFF', borderRadius: '20px',
              width: '100%', maxWidth: '820px', maxHeight: '90vh',
              overflowY: 'auto', boxShadow: '0 25px 60px rgba(31,25,27,0.18)',
              border: '1px solid rgba(216,114,126,0.2)',
            }}
          >
            {/* Modal Header */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '1.4rem 1.75rem',
              borderBottom: '1px solid rgba(216,114,126,0.15)',
              position: 'sticky', top: 0, background: '#FFFFFF', zIndex: 1, borderRadius: '20px 20px 0 0',
            }}>
              <h2 style={{
                margin: 0, fontFamily: "var(--font-serif, 'Playfair Display', serif)",
                fontSize: '1.35rem', fontWeight: 700, color: '#1F191B',
                display: 'flex', alignItems: 'center', gap: '0.6rem',
              }}>
                <ShoppingBag size={22} style={{ color: '#B8505E' }} />
                Order Details
              </h2>
              <button
                onClick={closeDetails}
                style={{
                  background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.2)',
                  borderRadius: '8px', padding: '0.4rem', cursor: 'pointer',
                  color: '#6B5E63', display: 'flex', alignItems: 'center',
                  transition: 'all 0.18s',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = '#B8505E'; e.currentTarget.style.color = '#fff'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = '#FAF7F5'; e.currentTarget.style.color = '#6B5E63'; }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.75rem' }}>
              {detailsLoading ? (
                <div style={{ padding: '3rem', textAlign: 'center' }}>
                  <RefreshCw size={30} className="animate-spin" style={{ color: '#B8505E', marginBottom: '0.75rem' }} />
                  <p style={{ color: '#6B5E63', margin: 0 }}>Loading complete order information...</p>
                </div>
              ) : detailsError ? (
                <div style={{ padding: '2rem', textAlign: 'center' }}>
                  <AlertTriangle size={30} style={{ color: '#DC2626', marginBottom: '0.75rem' }} />
                  <p style={{ color: '#DC2626', margin: 0 }}>{detailsError}</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                  {/* Summary Strip */}
                  <div style={{
                    display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem',
                    background: '#FAF7F5', border: '1px solid rgba(216,114,126,0.15)',
                    borderRadius: '14px', padding: '1.25rem 1.5rem',
                  }}>
                    {[
                      { label: 'Order ID', value: `#${selectedOrder.order_id?.substring(0, 8).toUpperCase()}`, color: '#B8505E' },
                      { label: 'Date', value: selectedOrder.order_date || 'N/A' },
                      { label: 'Status', value: <StatusBadge status={selectedOrder.order_status} /> },
                      { label: 'Payment', value: (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                          <CreditCard size={13} style={{ color: '#9E8F94' }} />
                          {selectedOrder.payment_status || 'Unknown'}
                        </span>
                      )},
                    ].map(({ label, value, color }) => (
                      <div key={label}>
                        <p style={{ margin: '0 0 0.3rem 0', fontSize: '0.72rem', fontWeight: 700, color: '#9E8F94', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</p>
                        <p style={{ margin: 0, fontWeight: 600, color: color || '#1F191B', fontSize: '0.9rem' }}>{value}</p>
                      </div>
                    ))}
                  </div>

                  {/* Customer + Fulfillment */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
                    {/* Customer */}
                    <div style={{ border: '1px solid rgba(216,114,126,0.15)', borderRadius: '14px', padding: '1.25rem' }}>
                      <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.9rem', fontWeight: 700, color: '#1F191B', display: 'flex', alignItems: 'center', gap: '0.5rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(216,114,126,0.1)' }}>
                        <User size={15} style={{ color: '#9E8F94' }} /> Customer Information
                      </h3>
                      {selectedOrder.customer_name ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
                          {[
                            ['Name', selectedOrder.customer_name],
                            ['Email', selectedOrder.customer_email],
                            ['Phone', selectedOrder.customer_phone || 'N/A'],
                          ].map(([k, v]) => (
                            <p key={k} style={{ margin: 0 }}>
                              <span style={{ color: '#9E8F94', display: 'inline-block', minWidth: 52 }}>{k}:</span>
                              <span style={{ color: '#1F191B', fontWeight: 500 }}> {v}</span>
                            </p>
                          ))}
                        </div>
                      ) : (
                        <p style={{ color: '#9E8F94', fontSize: '0.85rem', fontStyle: 'italic', margin: 0 }}>No customer information available.</p>
                      )}
                    </div>

                    {/* Fulfillment */}
                    <div style={{ border: '1px solid rgba(216,114,126,0.15)', borderRadius: '14px', padding: '1.25rem' }}>
                      <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.9rem', fontWeight: 700, color: '#1F191B', display: 'flex', alignItems: 'center', gap: '0.5rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(216,114,126,0.1)' }}>
                        <Truck size={15} style={{ color: '#9E8F94' }} /> Fulfillment
                      </h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
                        <p style={{ margin: 0, display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                          <WarehouseIcon size={14} style={{ color: '#9E8F94', marginTop: 2, flexShrink: 0 }} />
                          <span>
                            <span style={{ color: '#9E8F94', display: 'block', fontSize: '0.75rem' }}>Assigned Warehouse</span>
                            <span style={{ color: '#1F191B', fontWeight: 500 }}>
                              {selectedOrder.warehouse ? selectedOrder.warehouse.warehouse_name : 'Unassigned'}
                            </span>
                          </span>
                        </p>
                        <p style={{ margin: 0, display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                          <MapPin size={14} style={{ color: '#9E8F94', marginTop: 2, flexShrink: 0 }} />
                          <span>
                            <span style={{ color: '#9E8F94', display: 'block', fontSize: '0.75rem' }}>Shipping Address</span>
                            <span style={{ color: '#1F191B', fontWeight: 500 }}>
                              {selectedOrder.shipping_address || 'No address provided'}
                            </span>
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Order Items */}
                  <div>
                    <h3 style={{ margin: '0 0 0.85rem 0', fontSize: '0.95rem', fontWeight: 700, color: '#1F191B', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Package size={16} style={{ color: '#B8505E' }} /> Order Items
                    </h3>
                    <div className="admin-table-wrapper">
                      <table className="admin-table">
                        <thead>
                          <tr>
                            <th>Product</th>
                            <th style={{ textAlign: 'right' }}>Unit Price</th>
                            <th style={{ textAlign: 'center' }}>Qty</th>
                            <th style={{ textAlign: 'right' }}>Subtotal</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedOrder.items && selectedOrder.items.length > 0 ? (
                            selectedOrder.items.map((item, idx) => (
                              <tr key={idx}>
                                <td>
                                  <div style={{ fontWeight: 600, color: '#1F191B', fontSize: '0.87rem' }}>
                                    {item.product_name || 'Unknown Product'}
                                  </div>
                                  <div style={{ fontSize: '0.75rem', color: '#9E8F94' }}>
                                    SKU: {item.sku || 'N/A'}
                                  </div>
                                </td>
                                <td style={{ textAlign: 'right', color: '#6B5E63' }}>
                                  ₹{parseFloat(item.unit_price || 0).toFixed(2)}
                                </td>
                                <td style={{ textAlign: 'center', fontWeight: 600 }}>{item.quantity}</td>
                                <td style={{ textAlign: 'right', fontWeight: 700, color: '#1F191B' }}>
                                  ₹{parseFloat(item.subtotal || (parseFloat(item.unit_price || 0) * parseInt(item.quantity || 0, 10))).toFixed(2)}
                                </td>
                              </tr>
                            ))
                          ) : (
                            <tr>
                              <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: '#9E8F94', fontStyle: 'italic' }}>
                                No items found for this order.
                              </td>
                            </tr>
                          )}
                        </tbody>
                        <tfoot>
                          <tr style={{ backgroundColor: '#FAF7F5' }}>
                            <td colSpan="3" style={{ textAlign: 'right', fontWeight: 700, color: '#6B5E63', fontSize: '0.85rem', padding: '0.85rem 1rem' }}>
                              Order Total
                            </td>
                            <td style={{ textAlign: 'right', fontWeight: 800, color: '#1F191B', fontSize: '1rem', padding: '0.85rem 1rem' }}>
                              ₹{parseFloat(selectedOrder.total_amount || 0).toFixed(2)}
                            </td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  </div>

                  {/* Info note */}
                  <div style={{
                    background: '#EFF6FF', border: '1px solid #BFDBFE',
                    borderRadius: '12px', padding: '0.9rem 1.1rem',
                    display: 'flex', alignItems: 'flex-start', gap: '0.6rem',
                    fontSize: '0.84rem', color: '#1E40AF',
                  }}>
                    <AlertTriangle size={15} style={{ marginTop: 2, flexShrink: 0 }} />
                    <p style={{ margin: 0 }}>
                      Order status modifications are managed exclusively by the Warehouse Manager module.
                      Administrators have view-only access to order status in this dashboard.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '1rem 1.75rem',
              borderTop: '1px solid rgba(216,114,126,0.15)',
              display: 'flex', justifyContent: 'flex-end',
              position: 'sticky', bottom: 0, background: '#FFFFFF', borderRadius: '0 0 20px 20px',
            }}>
              <button
                className="tarika-btn-outline"
                onClick={closeDetails}
                style={{ padding: '0.6rem 1.35rem', fontSize: '0.85rem' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
