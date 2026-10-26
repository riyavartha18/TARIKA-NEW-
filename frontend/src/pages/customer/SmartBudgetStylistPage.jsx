import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ShoppingBag,
  Heart,
  SlidersHorizontal,
  ChevronDown,
  Check,
  CheckCircle2,
  Calendar,
  Layers,
  ShoppingBag as BagIcon,
  Tag,
  ArrowRight,
  Eye,
  X,
  Share2,
  Info,
  GraduationCap,
  Coffee,
  Wine,
  Briefcase,
  Flame,
  Feather,
  Gem,
  Footprints,
  Flower2,
  Crown,
  Compass,
  AlertCircle
} from 'lucide-react';

import Navbar from '../../components/home/Navbar';
import FeatureFooter from '../../components/home/FeatureFooter';
import { useCustomer, CustomerProvider } from '../../context/CustomerContext';
import { useAuth } from '../../auth/AuthContext';
import { getSmartStylistLooks } from '../../services/api';

// Occasion options with Lucide icons
const OCCASIONS = [
  { id: 'College', label: 'College', icon: GraduationCap },
  { id: 'Casual', label: 'Casual', icon: Coffee },
  { id: 'Party', label: 'Party', icon: Wine },
  { id: 'Formal', label: 'Formal', icon: Briefcase },
  { id: 'Festive', label: 'Festive', icon: Sparkles },
];

// Style preference options with Lucide icons
const STYLES = [
  { id: 'Minimal', label: 'Minimal', icon: Feather },
  { id: 'Chic', label: 'Chic', icon: Gem },
  { id: 'Streetwear', label: 'Streetwear', icon: Footprints },
  { id: 'Traditional', label: 'Traditional', icon: Flower2 },
  { id: 'Elegant', label: 'Elegant', icon: Crown },
];

// Fashion direction options (Western, Ethnic, Indo-Western, Dresses & Jumpsuits, Surprise Me)
const FASHION_DIRECTIONS = [
  { id: 'Surprise Me', label: 'Surprise Me', subtitle: 'All Compatible Categories' },
  { id: 'Western', label: 'Western', subtitle: 'Tops, Jeans & Co-ords' },
  { id: 'Ethnic', label: 'Ethnic', subtitle: 'Kurtas, Sarees & Palazzos' },
  { id: 'Indo-Western', label: 'Indo-Western', subtitle: 'Kurti + Denim Fusion' },
  { id: 'Dresses & Jumpsuits', label: 'Dresses & Jumpsuits', subtitle: 'One-Piece Elegance' },
];

// Curated color swatches
const COLOR_SWATCHES = [
  { name: 'Black', hex: '#1C1819', border: '#3A3234' },
  { name: 'White', hex: '#FFFFFF', border: '#D5C9C7' },
  { name: 'Beige', hex: '#E7DACB', border: '#C7B4A1' },
  { name: 'Pink', hex: '#E99AA8', border: '#C86E80' },
  { name: 'Red', hex: '#BD2031', border: '#9E1524' },
  { name: 'Blue', hex: '#2A5C8A', border: '#1C4266' },
  { name: 'Green', hex: '#2F6B48', border: '#1F4F33' },
  { name: 'Yellow', hex: '#E6A728', border: '#C28717' },
  { name: 'Purple', hex: '#77478E', border: '#5B3070' },
  { name: 'Maroon', hex: '#6E1D2A', border: '#50101B' },
];

// Preset quick-select price chips matching target budget criteria
const BUDGET_PRESETS = [500, 799, 1000, 1499, 1999];

export default function SmartBudgetStylistPage({ insideCustomerPortal = false }) {
  // Wrap with CustomerProvider fallback if not already inside one
  return insideCustomerPortal ? (
    <SmartBudgetStylistInner insideCustomerPortal={true} />
  ) : (
    <CustomerProvider>
      <SmartBudgetStylistInner insideCustomerPortal={false} />
    </CustomerProvider>
  );
}

function SmartBudgetStylistInner({ insideCustomerPortal }) {
  const { addToBag, toggleWishlist, isWishlisted, addToast, openProductDetail } = useCustomer();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Styling state
  const [budget, setBudget] = useState(1000);
  const [occasion, setOccasion] = useState('College');
  const [stylePreference, setStylePreference] = useState('Chic');
  const [fashionDirection, setFashionDirection] = useState('Surprise Me');
  const [selectedColors, setSelectedColors] = useState(['Pink']);
  const [sortBy, setSortBy] = useState('match');

  // Results state
  const [outfits, setOutfits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [detailModalOutfit, setDetailModalOutfit] = useState(null);
  const [addingToBagMap, setAddingToBagMap] = useState({});

  const stylingPanelRef = useRef(null);
  const resultsRef = useRef(null);

  // Fetch initial curated looks
  useEffect(() => {
    fetchOutfits();
    // Scroll to top on first mount
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const fetchOutfits = async (customParams = {}) => {
    setLoading(true);
    setError(null);

    const payload = {
      budget: customParams.budget ?? budget,
      occasion: customParams.occasion ?? occasion,
      style: customParams.stylePreference ?? stylePreference,
      fashion_direction: customParams.fashionDirection ?? fashionDirection,
      preferred_colors: customParams.selectedColors ?? selectedColors,
      sort_by: customParams.sortBy ?? sortBy,
      limit: 6,
    };

    try {
      const res = await getSmartStylistLooks(payload);
      if (res.success && Array.isArray(res.outfits)) {
        setOutfits(res.outfits);
      } else {
        setError(res.error || 'Failed to curate outfits for the selected criteria.');
        setOutfits([]);
      }
    } catch (err) {
      setError('Network connection error while fetching styled outfits.');
      setOutfits([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLooksSubmit = (e) => {
    if (e) e.preventDefault();
    fetchOutfits();
    // Scroll smoothly to results
    if (resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleSortChange = (newSort) => {
    setSortBy(newSort);
    fetchOutfits({ sortBy: newSort });
  };

  const handleColorToggle = (colorName) => {
    setSelectedColors((prev) =>
      prev.includes(colorName) ? prev.filter((c) => c !== colorName) : [...prev, colorName]
    );
  };

  const handleAddOutfitToBag = async (outfit) => {
    if (!outfit || !outfit.items || outfit.items.length === 0) return;

    setAddingToBagMap((prev) => ({ ...prev, [outfit.id]: true }));
    let addedCount = 0;

    for (const item of outfit.items) {
      try {
        const res = await addToBag({
          product_id: item.product_id,
          name: item.product_name,
          base_price: item.base_price,
          sale_price: item.selling_price,
          image: item.image,
          in_stock: true,
        });
        if (res?.success) addedCount++;
      } catch (e) {
        console.error('Error adding outfit item to bag:', e);
      }
    }

    setAddingToBagMap((prev) => ({ ...prev, [outfit.id]: false }));

    if (addedCount > 0) {
      addToast(
        `Added complete "${outfit.name}" look (${addedCount} items) to your bag!`,
        'success'
      );
    } else if (!isAuthenticated) {
      addToast('Please sign in to add this outfit to your shopping bag.', 'info');
    }
  };

  const scrollToStylingPanel = () => {
    if (stylingPanelRef.current) {
      stylingPanelRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div
      style={{
        backgroundColor: '#FAF7F5',
        minHeight: '100vh',
        color: '#1F191B',
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      {/* If visited outside CustomerPortal, show home Navbar */}
      {!insideCustomerPortal && <Navbar />}

      {/* 1. FASHION HERO BANNER */}
      <section
        style={{
          background: 'linear-gradient(135deg, #FBF4F2 0%, #F5EAE6 50%, #F8EFE9 100%)',
          borderBottom: '1px solid rgba(216, 114, 126, 0.16)',
          position: 'relative',
          overflow: 'hidden',
          padding: '3rem 2rem 3.5rem 2rem',
        }}
      >
        <div
          style={{
            maxWidth: '1440px',
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            alignItems: 'center',
            gap: '3rem',
          }}
        >
          {/* Hero Left Content */}
          <div style={{ maxWidth: '620px' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                backgroundColor: 'rgba(255, 255, 255, 0.85)',
                border: '1px solid rgba(216, 114, 126, 0.28)',
                padding: '0.35rem 0.95rem',
                borderRadius: '9999px',
                fontSize: '0.74rem',
                fontWeight: 700,
                color: '#B8505E',
                letterSpacing: '0.14em',
                textTransform: 'uppercase',
                marginBottom: '1.25rem',
                backdropFilter: 'blur(8px)',
              }}
            >
              <Sparkles size={13} color="#B8505E" />
              <span>Smart AI Fashion Atelier</span>
            </div>

            <h1
              style={{
                fontFamily: "'Playfair Display', Georgia, serif",
                fontSize: 'clamp(2.4rem, 4.5vw, 3.8rem)',
                fontWeight: 700,
                lineHeight: 1.15,
                color: '#1C1819',
                margin: '0 0 1rem 0',
                letterSpacing: '-0.01em',
              }}
            >
              Your Budget. Your Style.{' '}
              <span
                style={{
                  display: 'block',
                  color: '#C45766',
                  fontStyle: 'italic',
                  fontWeight: 500,
                  fontFamily: "'Playfair Display', Georgia, serif",
                }}
              >
                Your Perfect Look.
              </span>
            </h1>

            <p
              style={{
                fontSize: '1.05rem',
                lineHeight: 1.6,
                color: '#5C4E52',
                margin: '0 0 2rem 0',
                fontWeight: 400,
              }}
            >
              Discover complete outfits curated around your budget, your occasion and your
              personal style. Real catalog pieces, perfect color harmony, and effortless 1-click
              shopping.
            </p>

            {/* 4 Feature Badges */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '1rem',
                marginBottom: '2.25rem',
              }}
            >
              <div style={featureBadgeStyle}>
                <Sparkles size={18} color="#B8505E" />
                <div>
                  <span style={featureTitleStyle}>Multiple looks</span>
                  <span style={featureSubStyle}>One budget</span>
                </div>
              </div>

              <div style={featureBadgeStyle}>
                <Calendar size={18} color="#B8505E" />
                <div>
                  <span style={featureTitleStyle}>Curated for</span>
                  <span style={featureSubStyle}>your occasion</span>
                </div>
              </div>

              <div style={featureBadgeStyle}>
                <Layers size={18} color="#B8505E" />
                <div>
                  <span style={featureTitleStyle}>Real products</span>
                  <span style={featureSubStyle}>from our collection</span>
                </div>
              </div>

              <div style={featureBadgeStyle}>
                <ShoppingBag size={18} color="#B8505E" />
                <div>
                  <span style={featureTitleStyle}>Ready to shop</span>
                  <span style={featureSubStyle}>in one click</span>
                </div>
              </div>
            </div>

            {/* CTA Button */}
            <button
              onClick={scrollToStylingPanel}
              style={{
                backgroundColor: '#B8505E',
                color: '#FFFFFF',
                border: 'none',
                padding: '0.9rem 2rem',
                borderRadius: '9999px',
                fontSize: '0.95rem',
                fontWeight: 600,
                letterSpacing: '0.04em',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.65rem',
                boxShadow: '0 8px 24px rgba(184, 80, 94, 0.28)',
                transition: 'all 0.25s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#9E3E4B';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 12px 28px rgba(184, 80, 94, 0.38)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#B8505E';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(184, 80, 94, 0.28)';
              }}
            >
              <Sparkles size={17} />
              <span>Style My Outfit</span>
              <ArrowRight size={16} />
            </button>
          </div>

          {/* Hero Right Visual with Handwritten Flourish */}
          <div
            style={{
              position: 'relative',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <div
              style={{
                position: 'relative',
                borderRadius: '24px',
                overflow: 'hidden',
                boxShadow: '0 20px 50px rgba(184, 80, 94, 0.16)',
                border: '6px solid rgba(255, 255, 255, 0.8)',
                maxWidth: '440px',
                width: '100%',
                maxHeight: '480px',
              }}
            >
              <img
                src="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=900&auto=format&fit=crop&q=80"
                alt="Tarika Fashion Style"
                style={{
                  width: '100%',
                  height: '480px',
                  objectFit: 'cover',
                  display: 'block',
                }}
              />

              {/* Floating luxury tag */}
              <div
                style={{
                  position: 'absolute',
                  bottom: '18px',
                  left: '18px',
                  right: '18px',
                  backgroundColor: 'rgba(255, 255, 255, 0.92)',
                  backdropFilter: 'blur(12px)',
                  padding: '12px 18px',
                  borderRadius: '16px',
                  border: '1px solid rgba(216, 114, 126, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <span style={{ fontSize: '0.68rem', fontWeight: 700, color: '#B8505E', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                    Curated Collection
                  </span>
                  <div style={{ fontFamily: "'Playfair Display', serif", fontSize: '1.05rem', fontWeight: 700, color: '#1C1819' }}>
                    Ethnic, Western & Fusion Looks
                  </div>
                </div>
                <div
                  style={{
                    backgroundColor: '#FDECEF',
                    color: '#B8505E',
                    padding: '6px 12px',
                    borderRadius: '9999px',
                    fontSize: '0.76rem',
                    fontWeight: 700,
                  }}
                >
                  Under ₹5,000
                </div>
              </div>
            </div>

            {/* Handwritten script annotation */}
            <div
              style={{
                position: 'absolute',
                top: '12px',
                right: '-10px',
                fontFamily: "'Playfair Display', cursive, serif",
                fontStyle: 'italic',
                fontSize: '1.75rem',
                color: '#B8505E',
                transform: 'rotate(-5deg)',
                textShadow: '0 2px 8px rgba(255, 255, 255, 0.8)',
                pointerEvents: 'none',
                lineHeight: 1.1,
              }}
            >
              Style made <br />
              for you ♡
            </div>
          </div>
        </div>
      </section>

      {/* 2. STYLING CONTROLS PANEL */}
      <section
        ref={stylingPanelRef}
        id="styling-panel"
        style={{
          maxWidth: '1440px',
          margin: '-20px auto 3rem auto',
          padding: '0 2rem',
          position: 'relative',
          zIndex: 10,
        }}
      >
        <div
          style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '24px',
            padding: '2.5rem',
            boxShadow: '0 16px 45px rgba(184, 80, 94, 0.09)',
            border: '1px solid rgba(216, 114, 126, 0.18)',
          }}
        >
          {/* Section Heading */}
          <div style={{ marginBottom: '2rem' }}>
            <h2
              style={{
                fontFamily: "'Playfair Display', Georgia, serif",
                fontSize: '1.9rem',
                fontWeight: 700,
                color: '#1C1819',
                margin: '0 0 0.35rem 0',
              }}
            >
              Let's Find Your Look
            </h2>
            <p style={{ margin: 0, fontSize: '0.92rem', color: '#6E5D62' }}>
              Tell us your preferences and we'll create beautiful outfit combinations just for you.
            </p>
          </div>

          <form onSubmit={handleCreateLooksSubmit}>
            {/* 4 Primary Control Columns */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '2.25rem',
                alignItems: 'start',
              }}
            >
              {/* 1. Your Budget */}
              <div style={controlColumnStyle}>
                <div style={controlLabelStyle}>
                  <span>1. Your Budget (₹)</span>
                </div>

                <div
                  style={{
                    fontFamily: "'Playfair Display', serif",
                    fontSize: '2.2rem',
                    fontWeight: 700,
                    color: '#B8505E',
                    textAlign: 'center',
                    margin: '0.25rem 0 1rem 0',
                  }}
                >
                  ₹ {Number(budget).toLocaleString('en-IN')}
                </div>

                {/* Range Slider */}
                <input
                  type="range"
                  min="500"
                  max="5000"
                  step="100"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  style={{
                    width: '100%',
                    accentColor: '#B8505E',
                    cursor: 'pointer',
                    height: '6px',
                    borderRadius: '4px',
                    marginBottom: '0.4rem',
                  }}
                />

                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.78rem',
                    color: '#8A7B80',
                    fontWeight: 600,
                    marginBottom: '1rem',
                  }}
                >
                  <span>₹500</span>
                  <span>₹5,000</span>
                </div>

                {/* Quick-Select Price Chips */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.35rem' }}>
                  {BUDGET_PRESETS.map((p) => {
                    const isSelected = budget === p;
                    return (
                      <button
                        key={p}
                        type="button"
                        onClick={() => setBudget(p)}
                        style={{
                          backgroundColor: isSelected ? '#FDECEF' : '#FAF7F5',
                          color: isSelected ? '#B8505E' : '#4A3D41',
                          border: isSelected ? '1.5px solid #B8505E' : '1px solid rgba(216, 114, 126, 0.2)',
                          padding: '0.45rem 0.2rem',
                          borderRadius: '8px',
                          fontSize: '0.78rem',
                          fontWeight: isSelected ? 700 : 500,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          textAlign: 'center',
                        }}
                      >
                        ₹{p.toLocaleString('en-IN')}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* 2. Occasion */}
              <div style={controlColumnStyle}>
                <div style={controlLabelStyle}>
                  <span>2. Occasion</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.55rem' }}>
                  {OCCASIONS.map((occ) => {
                    const isSelected = occasion === occ.id;
                    const IconComponent = occ.icon;
                    return (
                      <button
                        key={occ.id}
                        type="button"
                        onClick={() => setOccasion(occ.id)}
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '0.35rem',
                          padding: '0.75rem 0.4rem',
                          backgroundColor: isSelected ? '#FDECEF' : '#FAF7F5',
                          color: isSelected ? '#B8505E' : '#4A3D41',
                          border: isSelected ? '1.5px solid #B8505E' : '1px solid rgba(216, 114, 126, 0.2)',
                          borderRadius: '12px',
                          fontSize: '0.8rem',
                          fontWeight: isSelected ? 700 : 500,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                        }}
                      >
                        <IconComponent size={18} color={isSelected ? '#B8505E' : '#6E5D62'} />
                        <span>{occ.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* 3. Your Style */}
              <div style={controlColumnStyle}>
                <div style={controlLabelStyle}>
                  <span>3. Your Style</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.55rem' }}>
                  {STYLES.map((sty) => {
                    const isSelected = stylePreference === sty.id;
                    const IconComponent = sty.icon;
                    return (
                      <button
                        key={sty.id}
                        type="button"
                        onClick={() => setStylePreference(sty.id)}
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '0.35rem',
                          padding: '0.75rem 0.4rem',
                          backgroundColor: isSelected ? '#FDECEF' : '#FAF7F5',
                          color: isSelected ? '#B8505E' : '#4A3D41',
                          border: isSelected ? '1.5px solid #B8505E' : '1px solid rgba(216, 114, 126, 0.2)',
                          borderRadius: '12px',
                          fontSize: '0.8rem',
                          fontWeight: isSelected ? 700 : 500,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                        }}
                      >
                        <IconComponent size={18} color={isSelected ? '#B8505E' : '#6E5D62'} />
                        <span>{sty.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* 4. Preferred Colours */}
              <div style={controlColumnStyle}>
                <div style={controlLabelStyle}>
                  <span>4. Preferred Colours</span>
                  <span style={{ fontSize: '0.72rem', color: '#9E8F94', fontWeight: 400 }}>Optional</span>
                </div>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(5, 1fr)',
                    gap: '0.65rem',
                    justifyItems: 'center',
                  }}
                >
                  {COLOR_SWATCHES.map((c) => {
                    const isSelected = selectedColors.includes(c.name);
                    return (
                      <button
                        key={c.name}
                        type="button"
                        onClick={() => handleColorToggle(c.name)}
                        title={c.name}
                        style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          backgroundColor: c.hex,
                          border: isSelected ? '2.5px solid #B8505E' : `1.5px solid ${c.border}`,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          padding: 0,
                          boxShadow: isSelected ? '0 0 0 2px #FDECEF' : 'none',
                          transition: 'all 0.2s ease',
                        }}
                      >
                        {isSelected && (
                          <Check
                            size={14}
                            color={c.name === 'White' || c.name === 'Beige' ? '#1C1819' : '#FFFFFF'}
                            strokeWidth={3}
                          />
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Selected Color Names Display */}
                <div
                  style={{
                    marginTop: '0.75rem',
                    fontSize: '0.76rem',
                    color: '#6E5D62',
                    textAlign: 'center',
                  }}
                >
                  {selectedColors.length > 0 ? (
                    <span>Selected: <strong>{selectedColors.join(', ')}</strong></span>
                  ) : (
                    <span>Any color harmony</span>
                  )}
                </div>
              </div>
            </div>

            {/* Fashion Category Direction Selector (Western, Ethnic, Indo-Western, Dresses, Surprise Me) */}
            <div
              style={{
                marginTop: '2rem',
                paddingTop: '1.75rem',
                borderTop: '1px solid rgba(216, 114, 126, 0.15)',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '1rem',
                  flexWrap: 'wrap',
                  gap: '0.5rem',
                }}
              >
                <div>
                  <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#1C1819' }}>
                    Fashion Category Direction
                  </span>
                  <span style={{ fontSize: '0.78rem', color: '#8A7B80', marginLeft: '8px' }}>
                    Choose a tailored fashion mood or explore all combinations
                  </span>
                </div>
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
                  gap: '0.75rem',
                }}
              >
                {FASHION_DIRECTIONS.map((dir) => {
                  const isSelected = fashionDirection === dir.id;
                  return (
                    <button
                      key={dir.id}
                      type="button"
                      onClick={() => setFashionDirection(dir.id)}
                      style={{
                        padding: '0.75rem 1rem',
                        backgroundColor: isSelected ? '#FDECEF' : '#FAF7F5',
                        border: isSelected ? '1.5px solid #B8505E' : '1px solid rgba(216, 114, 126, 0.2)',
                        borderRadius: '14px',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.2s ease',
                      }}
                    >
                      <div
                        style={{
                          fontSize: '0.86rem',
                          fontWeight: 700,
                          color: isSelected ? '#B8505E' : '#1C1819',
                          marginBottom: '2px',
                        }}
                      >
                        {dir.label}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#8A7B80' }}>
                        {dir.subtitle}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Prominent Action Button */}
            <div
              style={{
                marginTop: '2.5rem',
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              <button
                type="submit"
                disabled={loading}
                style={{
                  backgroundColor: '#B8505E',
                  color: '#FFFFFF',
                  border: 'none',
                  padding: '1rem 3.5rem',
                  borderRadius: '9999px',
                  fontSize: '1rem',
                  fontWeight: 700,
                  letterSpacing: '0.04em',
                  cursor: loading ? 'wait' : 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  boxShadow: '0 8px 25px rgba(184, 80, 94, 0.32)',
                  transition: 'all 0.25s ease',
                  opacity: loading ? 0.75 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.backgroundColor = '#9E3E4B';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 12px 30px rgba(184, 80, 94, 0.42)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading) {
                    e.currentTarget.style.backgroundColor = '#B8505E';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(184, 80, 94, 0.32)';
                  }
                }}
              >
                <Sparkles size={18} />
                <span>{loading ? 'Curating Looks...' : 'Create My Looks'}</span>
                <ArrowRight size={18} />
              </button>
            </div>
          </form>
        </div>
      </section>

      {/* 3. OUTFIT RESULTS ("Looks Curated for You") */}
      <section
        ref={resultsRef}
        id="curated-results"
        style={{
          maxWidth: '1440px',
          margin: '0 auto',
          padding: '1rem 2rem 5rem 2rem',
        }}
      >
        {/* Results Header with Sorting */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-end',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            marginBottom: '2rem',
            paddingBottom: '1rem',
            borderBottom: '1px solid rgba(216, 114, 126, 0.15)',
          }}
        >
          <div>
            <h2
              style={{
                fontFamily: "'Playfair Display', Georgia, serif",
                fontSize: '2rem',
                fontWeight: 700,
                color: '#1C1819',
                margin: '0 0 0.35rem 0',
              }}
            >
              Looks Curated for You
            </h2>
            <p style={{ margin: 0, fontSize: '0.92rem', color: '#6E5D62' }}>
              Here are some beautiful outfit combinations within your{' '}
              <strong>₹{budget.toLocaleString('en-IN')}</strong> budget for a{' '}
              <strong>{occasion}</strong> look with a <strong>{stylePreference}</strong> style.
            </p>
          </div>

          {/* Sort Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <span style={{ fontSize: '0.85rem', color: '#6E5D62', fontWeight: 500 }}>Sort by</span>
            <div style={{ position: 'relative' }}>
              <select
                value={sortBy}
                onChange={(e) => handleSortChange(e.target.value)}
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid rgba(216, 114, 126, 0.25)',
                  borderRadius: '10px',
                  padding: '0.5rem 2.2rem 0.5rem 1rem',
                  fontSize: '0.86rem',
                  fontWeight: 600,
                  color: '#1C1819',
                  outline: 'none',
                  cursor: 'pointer',
                  appearance: 'none',
                  WebkitAppearance: 'none',
                }}
              >
                <option value="match">Best Match</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="savings_desc">Highest Savings</option>
                <option value="score_desc">Compatibility Score</option>
              </select>
              <ChevronDown
                size={15}
                color="#8A7B80"
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  pointerEvents: 'none',
                }}
              />
            </div>
          </div>
        </div>

        {/* Loading State Skeleton */}
        {loading && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
              gap: '2rem',
            }}
          >
            {[1, 2, 3].map((n) => (
              <div
                key={n}
                style={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '20px',
                  padding: '1.25rem',
                  border: '1px solid rgba(216, 114, 126, 0.15)',
                  minHeight: '520px',
                  animation: 'pulse 1.5s infinite',
                }}
              >
                <div style={{ width: '100%', height: '320px', backgroundColor: '#F5EBE8', borderRadius: '14px', marginBottom: '1rem' }} />
                <div style={{ width: '60%', height: '22px', backgroundColor: '#F5EBE8', borderRadius: '6px', marginBottom: '0.5rem' }} />
                <div style={{ width: '90%', height: '14px', backgroundColor: '#F5EBE8', borderRadius: '4px', marginBottom: '1rem' }} />
                <div style={{ width: '100%', height: '40px', backgroundColor: '#F5EBE8', borderRadius: '10px' }} />
              </div>
            ))}
          </div>
        )}

        {/* Error / Empty State */}
        {!loading && outfits.length === 0 && (
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '20px',
              padding: '4rem 2rem',
              textAlign: 'center',
              border: '1px dashed rgba(216, 114, 126, 0.35)',
            }}
          >
            <AlertCircle size={44} color="#B8505E" style={{ marginBottom: '1rem' }} />
            <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: '1.5rem', margin: '0 0 0.5rem 0' }}>
              No Outfits Found in this Budget
            </h3>
            <p style={{ color: '#6E5D62', maxWidth: '480px', margin: '0 auto 1.5rem auto', fontSize: '0.92rem' }}>
              Try increasing your budget slider, selecting 'Surprise Me' fashion direction, or choosing other color preferences.
            </p>
            <button
              onClick={() => {
                setBudget(2500);
                setFashionDirection('Surprise Me');
                fetchOutfits({ budget: 2500, fashionDirection: 'Surprise Me' });
              }}
              style={{
                backgroundColor: '#B8505E',
                color: '#FFFFFF',
                border: 'none',
                padding: '0.75rem 1.75rem',
                borderRadius: '9999px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Reset to Recommended Settings
            </button>
          </div>
        )}

        {/* Outfits Grid */}
        {!loading && outfits.length > 0 && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
              gap: '2rem',
              alignItems: 'stretch',
            }}
          >
            {outfits.map((outfit) => (
              <OutfitCard
                key={outfit.id}
                outfit={outfit}
                onViewDetails={() => setDetailModalOutfit(outfit)}
                onAddOutfitToBag={() => handleAddOutfitToBag(outfit)}
                isAdding={Boolean(addingToBagMap[outfit.id])}
                onProductClick={(p) => openProductDetail(p)}
                isWishlisted={isWishlisted}
                toggleWishlist={toggleWishlist}
              />
            ))}
          </div>
        )}
      </section>

      {/* 4. LOOK DETAILS MODAL */}
      {detailModalOutfit && (
        <OutfitDetailModal
          outfit={detailModalOutfit}
          onClose={() => setDetailModalOutfit(null)}
          onAddOutfitToBag={() => handleAddOutfitToBag(detailModalOutfit)}
          isAdding={Boolean(addingToBagMap[detailModalOutfit.id])}
          openProductDetail={openProductDetail}
        />
      )}

      {/* Footer */}
      {!insideCustomerPortal && <FeatureFooter />}
    </div>
  );
}

// -------------------------------------------------------------
// OUTFIT CARD COMPONENT (WITH ACTUAL PRODUCT IMAGE COLLAGE)
// -------------------------------------------------------------
function OutfitCard({
  outfit,
  onViewDetails,
  onAddOutfitToBag,
  isAdding,
  onProductClick,
  isWishlisted,
  toggleWishlist,
}) {
  const items = outfit.items || [];
  const heroItem = items[0] || null;
  const companionItems = items.slice(1);

  return (
    <div
      style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '20px',
        overflow: 'hidden',
        border: '1px solid rgba(216, 114, 126, 0.18)',
        boxShadow: '0 8px 30px rgba(184, 80, 94, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 16px 40px rgba(184, 80, 94, 0.14)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 8px 30px rgba(184, 80, 94, 0.08)';
      }}
    >
      {/* Visual Collage of Actual Product Images */}
      <div
        style={{
          position: 'relative',
          height: '310px',
          padding: '12px',
          backgroundColor: '#FAF5F3',
          borderBottom: '1px solid rgba(216, 114, 126, 0.12)',
        }}
      >
        {/* Most Popular / Tag Badge */}
        <div
          style={{
            position: 'absolute',
            top: '20px',
            left: '20px',
            zIndex: 10,
            backgroundColor: '#D8727E',
            color: '#FFFFFF',
            fontSize: '0.68rem',
            fontWeight: 700,
            padding: '0.25rem 0.65rem',
            borderRadius: '9999px',
            letterSpacing: '0.04em',
            boxShadow: '0 4px 12px rgba(216, 114, 126, 0.35)',
          }}
        >
          {outfit.tag || 'Curated Look'}
        </div>

        {/* Category Pill Badge */}
        <div
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            zIndex: 10,
            backgroundColor: 'rgba(255, 255, 255, 0.92)',
            backdropFilter: 'blur(8px)',
            color: '#8E3642',
            fontSize: '0.68rem',
            fontWeight: 700,
            padding: '0.2rem 0.6rem',
            borderRadius: '9999px',
            border: '1px solid rgba(216, 114, 126, 0.25)',
          }}
        >
          {outfit.fashion_direction}
        </div>

        {/* Top-Right Heart Icon */}
        {heroItem && (
          <button
            onClick={() => toggleWishlist(heroItem)}
            style={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              zIndex: 10,
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              border: 'none',
              borderRadius: '50%',
              width: '34px',
              height: '34px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
              transition: 'all 0.2s ease',
            }}
          >
            <Heart
              size={17}
              color="#B8505E"
              fill={isWishlisted(heroItem.product_id) ? '#B8505E' : 'none'}
            />
          </button>
        )}

        {/* Collage Layout: Left Hero Image + Right Companion Tiles */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '56% 44%',
            gap: '8px',
            height: '100%',
          }}
        >
          {/* Main Hero Product (Top / Dress / Saree / Kurti) */}
          <div
            onClick={() => heroItem && onProductClick(heroItem)}
            style={{
              borderRadius: '14px',
              overflow: 'hidden',
              backgroundColor: '#EDE1DD',
              position: 'relative',
              cursor: 'pointer',
            }}
          >
            <img
              src={heroItem?.image || 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&auto=format&fit=crop&q=80'}
              alt={heroItem?.product_name || 'Hero Piece'}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                display: 'block',
                transition: 'transform 0.3s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.04)')}
              onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
            />
          </div>

          {/* Right Column: 2 or 3 Tiles (Bottoms, Footwear, Bag) */}
          <div
            style={{
              display: 'grid',
              gridTemplateRows: companionItems.length > 2 ? '1fr 1fr 1fr' : '1fr 1fr',
              gap: '8px',
              height: '100%',
            }}
          >
            {companionItems.slice(0, 3).map((item, i) => (
              <div
                key={item.product_id || i}
                onClick={() => onProductClick(item)}
                style={{
                  borderRadius: '12px',
                  overflow: 'hidden',
                  backgroundColor: '#EDE1DD',
                  position: 'relative',
                  cursor: 'pointer',
                }}
              >
                <img
                  src={item.image || 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&auto=format&fit=crop&q=80'}
                  alt={item.product_name}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    display: 'block',
                    transition: 'transform 0.3s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.06)')}
                  onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Card Body Details */}
      <div style={{ padding: '1.25rem 1.4rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Name and Price Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'baseline',
            justifyContent: 'space-between',
            marginBottom: '0.45rem',
            gap: '0.5rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.45rem' }}>
            <span
              style={{
                fontSize: '1rem',
                fontWeight: 700,
                color: '#B8505E',
                fontFamily: "'Playfair Display', serif",
              }}
            >
              {outfit.index_number}
            </span>
            <h3
              style={{
                fontFamily: "'Playfair Display', Georgia, serif",
                fontSize: '1.2rem',
                fontWeight: 700,
                color: '#1C1819',
                margin: 0,
              }}
            >
              {outfit.name}
            </h3>
          </div>

          {/* Pricing */}
          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <span
              style={{
                fontSize: '1.25rem',
                fontWeight: 700,
                color: '#B8505E',
              }}
            >
              ₹ {Number(outfit.total_price).toLocaleString('en-IN')}
            </span>
            {outfit.original_price > outfit.total_price && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', justifyContent: 'flex-end' }}>
                <span style={{ fontSize: '0.78rem', color: '#9E8F94', textDecoration: 'line-through' }}>
                  ₹{Number(outfit.original_price).toLocaleString('en-IN')}
                </span>
                <span
                  style={{
                    fontSize: '0.68rem',
                    color: '#2F6B48',
                    fontWeight: 700,
                  }}
                >
                  {outfit.discount_percent}% OFF
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Short Editorial Description */}
        <p
          style={{
            fontSize: '0.82rem',
            color: '#6E5D62',
            lineHeight: 1.45,
            margin: '0 0 1rem 0',
          }}
        >
          {outfit.description}
        </p>

        {/* Individual Item Thumbnails Strip */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${Math.min(items.length, 4)}, 1fr)`,
            gap: '0.5rem',
            marginBottom: '1rem',
            padding: '0.65rem',
            backgroundColor: '#FAF7F5',
            borderRadius: '12px',
            border: '1px solid rgba(216, 114, 126, 0.12)',
          }}
        >
          {items.slice(0, 4).map((it) => (
            <div
              key={it.product_id}
              onClick={() => onProductClick(it)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                cursor: 'pointer',
              }}
            >
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  backgroundColor: '#EAE1DF',
                  marginBottom: '4px',
                }}
              >
                <img
                  src={it.image || 'https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=600&auto=format&fit=crop&q=80'}
                  alt={it.product_name}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>
              <span
                style={{
                  fontSize: '0.68rem',
                  color: '#4A3D41',
                  maxWidth: '75px',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  lineHeight: 1.2,
                }}
              >
                {it.product_name}
              </span>
              <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#1C1819', marginTop: '2px' }}>
                ₹{Number(it.selling_price).toLocaleString('en-IN')}
              </span>
            </div>
          ))}
        </div>

        {/* Budget Remaining Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            backgroundColor: '#EDF5EE',
            border: '1px solid #D2E7D4',
            padding: '0.45rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.78rem',
            fontWeight: 600,
            color: '#28623D',
            marginBottom: '1.25rem',
          }}
        >
          <div
            style={{
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              backgroundColor: '#E5A93C',
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.65rem',
              fontWeight: 800,
            }}
          >
            ₹
          </div>
          <span>
            ₹ {Math.max(0, Number(outfit.remaining_budget)).toLocaleString('en-IN')} remaining from your budget
          </span>
        </div>

        {/* Action Buttons: View Details & Add Outfit to Bag */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.35fr', gap: '0.65rem', marginTop: 'auto' }}>
          <button
            type="button"
            onClick={onViewDetails}
            style={{
              backgroundColor: '#FFFFFF',
              color: '#B8505E',
              border: '1.5px solid #B8505E',
              borderRadius: '9999px',
              padding: '0.6rem 0.5rem',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'center',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#FDECEF';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#FFFFFF';
            }}
          >
            View Details
          </button>

          <button
            type="button"
            disabled={isAdding}
            onClick={onAddOutfitToBag}
            style={{
              backgroundColor: '#B8505E',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '9999px',
              padding: '0.6rem 0.75rem',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: isAdding ? 'wait' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.45rem',
              boxShadow: '0 4px 14px rgba(184, 80, 94, 0.25)',
              transition: 'all 0.2s ease',
              opacity: isAdding ? 0.75 : 1,
            }}
            onMouseEnter={(e) => {
              if (!isAdding) e.currentTarget.style.backgroundColor = '#9E3E4B';
            }}
            onMouseLeave={(e) => {
              if (!isAdding) e.currentTarget.style.backgroundColor = '#B8505E';
            }}
          >
            <ShoppingBag size={15} />
            <span>{isAdding ? 'Adding...' : 'Add Outfit to Bag'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// OUTFIT DETAILS MODAL COMPONENT
// -------------------------------------------------------------
function OutfitDetailModal({ outfit, onClose, onAddOutfitToBag, isAdding, openProductDetail }) {
  if (!outfit) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(28, 24, 25, 0.65)',
        backdropFilter: 'blur(8px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '24px',
          maxWidth: '780px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          boxShadow: '0 24px 60px rgba(0, 0, 0, 0.25)',
          position: 'relative',
          padding: '2.25rem',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            backgroundColor: '#FAF7F5',
            border: 'none',
            borderRadius: '50%',
            width: '36px',
            height: '36px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            color: '#6E5D62',
          }}
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <span
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              backgroundColor: '#FDECEF',
              color: '#B8505E',
              padding: '0.2rem 0.65rem',
              borderRadius: '9999px',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
            }}
          >
            {outfit.fashion_direction} • Score: {outfit.score}/100
          </span>
          <h2
            style={{
              fontFamily: "'Playfair Display', serif",
              fontSize: '1.85rem',
              fontWeight: 700,
              color: '#1C1819',
              margin: '0.5rem 0 0.25rem 0',
            }}
          >
            {outfit.name}
          </h2>
          <p style={{ margin: 0, fontSize: '0.88rem', color: '#6E5D62' }}>
            {outfit.description}
          </p>
        </div>

        {/* Compatibility Breakdown Bars */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '1rem',
            backgroundColor: '#FAF7F5',
            padding: '1rem',
            borderRadius: '16px',
            marginBottom: '1.75rem',
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: '#8A7B80', textTransform: 'uppercase', fontWeight: 600 }}>
              Color Harmony
            </span>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#B8505E' }}>
              {outfit.color_score}%
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: '#8A7B80', textTransform: 'uppercase', fontWeight: 600 }}>
              Style Cohesion
            </span>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#B8505E' }}>
              {outfit.style_score}%
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.72rem', color: '#8A7B80', textTransform: 'uppercase', fontWeight: 600 }}>
              Occasion Match
            </span>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#B8505E' }}>
              {outfit.occasion_score}%
            </div>
          </div>
        </div>

        {/* Stylist Explanation */}
        <div
          style={{
            backgroundColor: '#FDF8F7',
            border: '1px solid rgba(216, 114, 126, 0.2)',
            borderRadius: '14px',
            padding: '1rem 1.25rem',
            marginBottom: '1.75rem',
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'flex-start',
          }}
        >
          <Info size={18} color="#B8505E" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#8E3642', marginBottom: '2px' }}>
              Why this look works:
            </div>
            <div style={{ fontSize: '0.82rem', color: '#5C4E52', lineHeight: 1.5 }}>
              {outfit.explanation}
            </div>
          </div>
        </div>

        {/* Itemized Products List */}
        <div style={{ marginBottom: '2rem' }}>
          <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#1C1819', margin: '0 0 0.85rem 0' }}>
            Complete Outfit Pieces ({outfit.items?.length || 0})
          </h4>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {outfit.items?.map((it) => (
              <div
                key={it.product_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.65rem 0.85rem',
                  backgroundColor: '#FAF7F5',
                  borderRadius: '12px',
                  border: '1px solid rgba(216, 114, 126, 0.12)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <img
                    src={it.image}
                    alt={it.product_name}
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '8px',
                      objectFit: 'cover',
                    }}
                  />
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#1C1819' }}>
                      {it.product_name}
                    </div>
                    <div style={{ fontSize: '0.74rem', color: '#8A7B80' }}>
                      {it.category_name} • {it.color}
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#B8505E' }}>
                      ₹{Number(it.selling_price).toLocaleString('en-IN')}
                    </div>
                    {it.base_price > it.selling_price && (
                      <div style={{ fontSize: '0.72rem', color: '#9E8F94', textDecoration: 'line-through' }}>
                        ₹{Number(it.base_price).toLocaleString('en-IN')}
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => openProductDetail(it)}
                    style={{
                      backgroundColor: '#FFFFFF',
                      border: '1px solid rgba(216, 114, 126, 0.25)',
                      borderRadius: '8px',
                      padding: '0.35rem 0.65rem',
                      fontSize: '0.75rem',
                      color: '#B8505E',
                      cursor: 'pointer',
                      fontWeight: 600,
                    }}
                  >
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Modal Bottom Actions & Price Summary */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderTop: '1px solid rgba(216, 114, 126, 0.18)',
            paddingTop: '1.25rem',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
            <div style={{ fontSize: '0.76rem', color: '#8A7B80' }}>Total Outfit Cost</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#B8505E' }}>
              ₹ {Number(outfit.total_price).toLocaleString('en-IN')}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#2F6B48', fontWeight: 600 }}>
              ₹ {Math.max(0, Number(outfit.remaining_budget)).toLocaleString('en-IN')} remaining within budget
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={onClose}
              style={{
                backgroundColor: '#FAF7F5',
                color: '#6E5D62',
                border: 'none',
                padding: '0.75rem 1.4rem',
                borderRadius: '9999px',
                fontSize: '0.86rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Close
            </button>

            <button
              disabled={isAdding}
              onClick={() => {
                onAddOutfitToBag();
                onClose();
              }}
              style={{
                backgroundColor: '#B8505E',
                color: '#FFFFFF',
                border: 'none',
                padding: '0.75rem 2rem',
                borderRadius: '9999px',
                fontSize: '0.86rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                boxShadow: '0 6px 18px rgba(184, 80, 94, 0.3)',
              }}
            >
              <ShoppingBag size={16} />
              <span>Add Complete Outfit to Bag</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// REUSABLE STYLES
// -------------------------------------------------------------
const featureBadgeStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.65rem',
  backgroundColor: 'rgba(255, 255, 255, 0.65)',
  border: '1px solid rgba(216, 114, 126, 0.2)',
  padding: '0.65rem 0.85rem',
  borderRadius: '12px',
  backdropFilter: 'blur(8px)',
};

const featureTitleStyle = {
  display: 'block',
  fontSize: '0.82rem',
  fontWeight: 700,
  color: '#1C1819',
  lineHeight: 1.2,
};

const featureSubStyle = {
  display: 'block',
  fontSize: '0.72rem',
  color: '#8A7B80',
  lineHeight: 1.2,
};

const controlColumnStyle = {
  display: 'flex',
  flexDirection: 'column',
};

const controlLabelStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  fontSize: '0.88rem',
  fontWeight: 700,
  color: '#1C1819',
  marginBottom: '0.85rem',
};
