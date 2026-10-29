import React from 'react';
import { 
  LayoutDashboard, 
  Building2, 
  PlusCircle, 
  Briefcase, 
  ShieldCheck, 
  Lightbulb, 
  Sparkles, 
  Layers, 
  Sliders, 
  FileText, 
  UserCheck 
} from 'lucide-react';
import Logo from './Logo';

export default function Sidebar({ activeTab, setActiveTab, activeProfile }) {
  const hasProfile = Boolean(activeProfile);

  const mainNavItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'my_businesses', label: 'My Businesses', icon: Building2 },
    { id: 'new_analysis', label: 'New Analysis', icon: PlusCircle },
  ];

  const workspaceNavItems = [
    { id: 'overview', label: 'Overview', icon: Briefcase, enabled: hasProfile },
    { id: 'feasibility', label: 'Feasibility Assessment', icon: ShieldCheck, enabled: hasProfile },
    { id: 'insights', label: 'Key Insights', icon: Lightbulb, enabled: hasProfile },
    { id: 'recommendations', label: 'Recommendations', icon: Sparkles, enabled: hasProfile },
    { id: 'options', label: 'Explore Options', icon: Layers, enabled: hasProfile },
    { id: 'scenario', label: 'Scenario Explorer', icon: Sliders, enabled: hasProfile },
    { id: 'plan', label: 'Business Plan', icon: FileText, enabled: hasProfile },
    { id: 'profile', label: 'Business Profile', icon: UserCheck, enabled: hasProfile },
  ];

  return (
    <aside className="sidebar">
      
      {/* Brand Header */}
      <div 
        className="sidebar-brand-header" 
        onClick={() => setActiveTab('dashboard')}
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.65rem', 
          marginBottom: '1.25rem', 
          paddingBottom: '0.85rem', 
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          cursor: 'pointer'
        }}
      >
        <Logo variant="compact" height={34} />
        <div>
          <div style={{ fontWeight: 800, fontSize: '0.95rem', color: '#ffffff', letterSpacing: '-0.2px' }}>SME360 AI</div>
          <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Decision Support System</div>
        </div>
      </div>

      {/* Main SaaS Navigation */}
      <div className="sidebar-heading" style={{ color: '#64748b', fontSize: '0.68rem', uppercase: 'uppercase', letterSpacing: '0.8px', fontWeight: 700, marginBottom: '0.5rem' }}>
        NAVIGATION
      </div>
      <nav className="nav-list" style={{ marginBottom: '1.5rem' }}>
        {mainNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item-btn ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} style={{ color: isActive ? '#60a5fa' : '#94a3b8' }} />
              <span style={{ fontWeight: isActive ? 700 : 500 }}>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {activeTab === 'new_analysis' && (
        <div style={{ margin: '0 0 1.25rem', padding: '0.4rem 0 0' }}>
          <div style={{ color: '#64748b', fontSize: '0.62rem', letterSpacing: '0.8px', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.45rem', paddingLeft: '0.75rem' }}>
            New Analysis
          </div>
          <button
            type="button"
            className="nav-item-btn active"
            style={{
              width: '100%',
              background: 'rgba(96, 165, 250, 0.08)',
              borderLeft: '3px solid #60a5fa',
              paddingLeft: '0.85rem',
              justifyContent: 'flex-start'
            }}
          >
            <ShieldCheck size={18} style={{ color: '#60a5fa' }} />
            <span style={{ fontWeight: 700, color: '#e2e8f0' }}># Business Registration & Regulatory Compliance</span>
          </button>
        </div>
      )}

      {/* Active Business Workspace Navigation */}
      <div className="sidebar-heading" style={{ color: '#64748b', fontSize: '0.68rem', uppercase: 'uppercase', letterSpacing: '0.8px', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>BUSINESS WORKSPACE</span>
        {hasProfile && (
          <span style={{ fontSize: '0.6rem', background: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
            Active
          </span>
        )}
      </div>

      <nav className="nav-list">
        {workspaceNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const isDisabled = !item.enabled;

          return (
            <button
              key={item.id}
              disabled={isDisabled}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item-btn ${isActive ? 'active' : ''}`}
              style={{ opacity: isDisabled ? 0.4 : 1 }}
            >
              <Icon size={18} style={{ color: isActive ? '#60a5fa' : '#94a3b8' }} />
              <span style={{ fontWeight: isActive ? 700 : 400 }}>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {!hasProfile && (
        <div style={{ marginTop: '1.5rem', padding: '0.85rem', background: 'rgba(30, 58, 138, 0.25)', border: '1px solid rgba(59, 130, 246, 0.25)', borderRadius: '10px', fontSize: '0.725rem', color: '#93c5fd', lineHeight: '1.4' }}>
          💡 Click <strong>New Analysis</strong> to analyze a business and unlock workspace modules.
        </div>
      )}
    </aside>
  );
}
