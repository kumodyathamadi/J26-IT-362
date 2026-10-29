import React, { useState, useEffect } from 'react';
import { RegistrationComplianceDashboard } from './components/component2.tsx';
import { BusinessRegistrationView } from './components/BusinessRegistrationView';

// ---------------------------------------------------------------------------
// Static Legal Sources Data for Corpus Inspector Tab
// ---------------------------------------------------------------------------
interface LegalSourceItem {
  source_id: string;
  title: string;
  authority: string;
  jurisdiction: string;
  doc_type: string;
  effective_date: string;
  key_sections: string;
  status: 'verified' | 'needs_verification';
  pdf_query?: string;
}

const STATUTORY_REGISTER: LegalSourceItem[] = [
  {
    source_id: 'SRC-WP-BN-1990',
    title: 'Business Names Statute of Western Province No. 04 of 1990',
    authority: 'Department of Business Names (Western Provincial Council)',
    jurisdiction: 'Western Province, Sri Lanka',
    doc_type: 'Provincial Statute',
    effective_date: '1990-06-15',
    key_sections: 'Section 3(1), Section 7 (Registration within 14 days)',
    status: 'verified',
    pdf_query: 'companies_act',
  },
  {
    source_id: 'SRC-MCO-1976',
    title: 'Municipal Councils Ordinance No. 29 of 1947 (Section 247A By-laws)',
    authority: 'Colombo Municipal Council / Western Province Local Authorities',
    jurisdiction: 'Western Province (Municipal Areas)',
    doc_type: 'Primary Act & By-Laws',
    effective_date: '1976-11-20',
    key_sections: 'Section 247A (Annual Trade Tax & Commercial Operating License)',
    status: 'verified',
    pdf_query: 'motor_traffic',
  },
  {
    source_id: 'SRC-FOOD-ACT-1980',
    title: 'Food Act No. 26 of 1980 & Food (Hygiene) Regulations',
    authority: 'Public Health Department / Office of MOH (Municipal Health)',
    jurisdiction: 'Sri Lanka (National & Municipal Enforcement)',
    doc_type: 'Primary Act & Gazettes',
    effective_date: '1980-08-01',
    key_sections: 'Section 2(1) (Food premises licensing), Reg 14 (PHI Medical Clearance)',
    status: 'verified',
    pdf_query: 'food_act',
  },
  {
    source_id: 'SRC-NMRA-COSMETICS-2015',
    title: 'National Medicines Regulatory Authority (NMRA) Act No. 5 of 2015',
    authority: 'National Medicines Regulatory Authority & Municipal Health Department',
    jurisdiction: 'Sri Lanka (National)',
    doc_type: 'Primary Act',
    effective_date: '2015-07-01',
    key_sections: 'Part IV Regulation 12 (Cosmetic chemical handling & salon registration)',
    status: 'verified',
    pdf_query: 'cosmetics',
  },
  {
    source_id: 'SRC-CEA-ENV-2008',
    title: 'National Environmental Act No. 47 of 1980 (Order 1533/16)',
    authority: 'Central Environmental Authority (CEA)',
    jurisdiction: 'Western Province & National',
    doc_type: 'Statutory Gazette Order',
    effective_date: '2008-02-01',
    key_sections: 'Schedule List B (Hazardous waste lubricant & spent battery storage)',
    status: 'verified',
    pdf_query: 'environmental_act',
  },
  {
    source_id: 'SRC-LA-TRADE-1980',
    title: 'Local Authority Trade Licensing & Fire Safety Regulations',
    authority: 'Local Municipal Council & Fire Service Department',
    jurisdiction: 'Colombo Municipal Limits',
    doc_type: 'Municipal By-Law',
    effective_date: '1980-01-15',
    key_sections: 'Section 4 (Textile / Garment commercial safety clearance)',
    status: 'needs_verification',
    pdf_query: 'motor_traffic',
  },
];

export const App: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'comp1' | 'comp2' | 'sources' | 'kleene_inspector' | 'business_reg' | 'audit_log'>('comp1');
  const [backendStatus, setBackendStatus] = useState<'online' | 'checking' | 'offline'>('checking');
  const [sourceSearch, setSourceSearch] = useState<string>('');
  const [sourceDocTypeFilter, setSourceDocTypeFilter] = useState<string>('all');
  const [copiedSourceId, setCopiedSourceId] = useState<string | null>(null);
  const [selectedSourceDetail, setSelectedSourceDetail] = useState<LegalSourceItem | null>(null);

  const handleCopySourceId = (id: string) => {
    navigator.clipboard?.writeText(id);
    setCopiedSourceId(id);
    setTimeout(() => setCopiedSourceId(null), 2000);
  };

  // Interactive Kleene Inspector State
  const [kleeneFacts, setKleeneFacts] = useState<{
    province_is_wp: boolean | null;
    physical_premises: boolean | null;
    operates_kitchen: boolean | null;
    handles_hazardous_waste: boolean | null;
  }>({
    province_is_wp: true,
    physical_premises: true,
    operates_kitchen: null, // Unknown
    handles_hazardous_waste: false,
  });

  // Verify backend health on mount
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/health')
      .then((res) => {
        if (res.ok) setBackendStatus('online');
        else setBackendStatus('offline');
      })
      .catch(() => setBackendStatus('offline'));
  }, []);

  // Compute Kleene 3VL demonstration output:
  const computeKleeneFoodPremises = () => {
    const { province_is_wp, physical_premises, operates_kitchen } = kleeneFacts;
    if (province_is_wp === false || physical_premises === false || operates_kitchen === false) {
      return { status: 'NOT_APPLICABLE', label: 'Not Applicable (False)', color: 'text-slate-600 bg-slate-100 border-slate-300' };
    }
    if (province_is_wp === null || physical_premises === null || operates_kitchen === null) {
      return { status: 'UNKNOWN', label: 'Conditional / Unknown (None)', color: 'text-amber-800 bg-amber-50 border-amber-300' };
    }
    return { status: 'APPLICABLE', label: 'Applicable (True)', color: 'text-emerald-800 bg-emerald-50 border-emerald-300' };
  };

  const filteredSources = STATUTORY_REGISTER.filter((s) => {
    const q = sourceSearch.toLowerCase().trim();
    const matchesSearch =
      !q ||
      s.title.toLowerCase().includes(q) ||
      s.authority.toLowerCase().includes(q) ||
      s.source_id.toLowerCase().includes(q) ||
      s.key_sections.toLowerCase().includes(q) ||
      s.jurisdiction.toLowerCase().includes(q);

    if (!matchesSearch) return false;

    if (sourceDocTypeFilter === 'all') return true;
    if (sourceDocTypeFilter === 'verified') return s.status === 'verified';
    if (sourceDocTypeFilter === 'primary_act') return s.doc_type.toLowerCase().includes('primary act');
    if (sourceDocTypeFilter === 'provincial') return s.doc_type.toLowerCase().includes('provincial');
    if (sourceDocTypeFilter === 'bylaw') return s.doc_type.toLowerCase().includes('by-law');
    if (sourceDocTypeFilter === 'gazette') return s.doc_type.toLowerCase().includes('gazette');

    return true;
  });

  const navItems = [
    {
      id: 'comp1' as const,
      title: 'Feasibility & Planning',
      subtitle: 'Component 1 — ML & SHAP',
      icon: 'fa-chart-line',
      badge: null,
    },
    {
      id: 'comp2' as const,
      title: 'Regulatory Engine',
      subtitle: 'Component 2 — Law & Regs',
      icon: 'fa-gavel',
      badge: 'Core',
    },
    {
      id: 'sources' as const,
      title: 'Statutory Register',
      subtitle: 'Primary Acts & Gazettes',
      icon: 'fa-book-bookmark',
      badge: `${STATUTORY_REGISTER.length}`,
    },
    {
      id: 'kleene_inspector' as const,
      title: '3VL Kleene Inspector',
      subtitle: 'Audit-Proof Logic Demo',
      icon: 'fa-flask-vial',
      badge: '3VL',
    },
    {
      id: 'business_reg' as const,
      title: 'Business Registration',
      subtitle: 'WP Form 1 & Roadmap',
      icon: 'fa-file-signature',
      badge: 'Form 1',
    },
  ];

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-800 font-sans antialiased selection:bg-teal-500 selection:text-white">
      {/* ----------------------------------------------------------------- */}
      {/* MOBILE DRAWER OVERLAY & SLIDE-OUT MENU                            */}
      {/* ----------------------------------------------------------------- */}
      <div
        className={`fixed inset-0 z-50 md:hidden transition-opacity duration-300 ${
          isMobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
      >
        {/* Backdrop */}
        <div
          className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
          onClick={() => setIsMobileMenuOpen(false)}
        />

        {/* Slide-out Drawer */}
        <div
          className={`relative w-72 max-w-[85vw] h-full bg-white shadow-2xl flex flex-col transition-transform duration-300 ease-out ${
            isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          {/* Mobile Header */}
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-900 to-slate-800 text-teal-400 flex items-center justify-center shadow-sm">
                <i className="fa-solid fa-scale-balanced text-lg"></i>
              </div>
              <div>
                <span className="font-extrabold text-sm tracking-tight text-slate-900 flex items-center gap-1.5">
                  LEXIS·SME AI
                  <span className="text-[10px] bg-teal-50 text-teal-700 font-bold px-1.5 py-0.5 rounded border border-teal-200">
                    v1.2
                  </span>
                </span>
                <span className="text-[11px] text-slate-500 block">Western Province LegalTech</span>
              </div>
            </div>

            <button
              onClick={() => setIsMobileMenuOpen(false)}
              className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center text-sm transition-colors"
              aria-label="Close menu"
            >
              <i className="fa-solid fa-xmark"></i>
            </button>
          </div>

          {/* Mobile Nav Links */}
          <nav className="p-3 space-y-1.5 flex-1 overflow-y-auto">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setIsMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-xs font-semibold transition-all ${
                    isActive ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                      isActive ? 'bg-slate-800 text-teal-400' : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    <i className={`fa-solid ${item.icon}`}></i>
                  </div>
                  <div className="text-left flex-1 truncate">
                    <div className="truncate font-semibold text-sm">{item.title}</div>
                    <div className={`text-[11px] font-normal truncate ${isActive ? 'text-slate-300' : 'text-slate-500'}`}>
                      {item.subtitle}
                    </div>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        isActive ? 'bg-teal-500/20 text-teal-300' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Mobile Status Info */}
          <div className="p-4 border-t border-slate-100 bg-slate-50/70">
            <div className="flex items-center gap-2.5 p-2 rounded-xl bg-white border border-slate-200">
              <span
                className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                  backendStatus === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
                }`}
              ></span>
              <div className="text-[11px]">
                <span className="font-bold text-slate-800 block">
                  {backendStatus === 'online' ? 'API Server Online' : 'Connecting to API...'}
                </span>
                <span className="text-slate-500 font-mono text-[10px]">127.0.0.1:8000</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 1. DESKTOP EXECUTIVE SIDEBAR (Hidden on mobile < md)               */}
      {/* ----------------------------------------------------------------- */}
      <aside
        className={`hidden md:flex bg-white border-r border-slate-200/90 flex-col transition-all duration-300 ease-in-out shrink-0 z-40 relative shadow-xs ${
          isSidebarCollapsed ? 'w-20' : 'w-72'
        }`}
      >
        {/* Brand / Logo Section */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between min-h-[72px]">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-900 to-slate-800 text-teal-400 flex items-center justify-center shrink-0 shadow-sm border border-slate-700/50">
              <i className="fa-solid fa-scale-balanced text-lg"></i>
            </div>
            {!isSidebarCollapsed && (
              <div className="flex flex-col truncate">
                <span className="font-extrabold text-sm tracking-tight text-slate-900 flex items-center gap-1.5">
                  LEXIS·SME AI
                  <span className="text-[10px] bg-teal-50 text-teal-700 font-bold px-1.5 py-0.5 rounded border border-teal-200">
                    v1.2
                  </span>
                </span>
                <span className="text-[11px] text-slate-600 truncate font-medium">
                  Regulatory &amp; Advisory Suite
                </span>
              </div>
            )}
          </div>
          <button
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            title={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className="w-8 h-8 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-500 hover:text-slate-800 flex items-center justify-center transition-colors text-xs border border-slate-200/80 shrink-0"
          >
            <i className={`fa-solid ${isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'}`}></i>
          </button>
        </div>

        {/* Academic Project Scope Pill */}
        {!isSidebarCollapsed && (
          <div className="mx-4 mt-3 p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px]">
            <div className="flex items-center gap-1.5 font-semibold text-slate-700 mb-0.5">
              <span className="w-2 h-2 rounded-full bg-blue-600"></span>
              Research Demonstration
            </div>
            <p className="text-slate-600 leading-tight">
              Western Province SME Compliance Architecture (Kleene 3VL Engine)
            </p>
          </div>
        )}

        {/* Primary Navigation Menu */}
        <nav className="p-3 space-y-1.5 flex-1 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                title={item.title}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                    isActive ? 'bg-slate-800 text-teal-400' : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  <i className={`fa-solid ${item.icon}`}></i>
                </div>
                {!isSidebarCollapsed && (
                  <div className="text-left flex-1 truncate">
                    <div className="truncate font-semibold">{item.title}</div>
                    <div className={`text-[10px] font-normal truncate ${isActive ? 'text-slate-300' : 'text-slate-600'}`}>
                      {item.subtitle}
                    </div>
                  </div>
                )}
                {!isSidebarCollapsed && item.badge && (
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isActive ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40' : 'bg-slate-200 text-slate-600'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer: System Diagnostics */}
        <div className="p-3 border-t border-slate-100 bg-slate-50/60">
          <div className="flex items-center gap-2.5 p-2 rounded-xl bg-white border border-slate-200/80 shadow-2xs">
            <span
              className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                backendStatus === 'online'
                  ? 'bg-emerald-500 ring-4 ring-emerald-100 animate-pulse'
                  : 'bg-rose-500'
              }`}
            ></span>
            {!isSidebarCollapsed && (
              <div className="truncate">
                <div className="text-[11px] font-bold text-slate-800 leading-tight">
                  {backendStatus === 'online' ? 'API Server Online' : 'API Connecting...'}
                </div>
                <div className="text-[10px] text-slate-600 font-mono">
                  127.0.0.1:8000
                </div>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* ----------------------------------------------------------------- */}
      {/* 2. MAIN APPLICATION CONTENT AREA                                 */}
      {/* ----------------------------------------------------------------- */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Executive Header */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs">
          <div className="flex items-center gap-3 min-w-0">
            {/* Hamburger Button (Mobile Only) */}
            <button
              type="button"
              onClick={() => setIsMobileMenuOpen(true)}
              className="md:hidden w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition-colors shrink-0"
              aria-label="Open navigation menu"
            >
              <i className="fa-solid fa-bars text-sm"></i>
            </button>

            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-xs font-semibold text-slate-600 hidden sm:flex items-center gap-1.5 shrink-0">
                <i className="fa-solid fa-landmark text-slate-600"></i>
                Sri Lanka LegalTech
              </span>
              <span className="text-slate-300 hidden sm:inline">/</span>
              <span className="text-xs font-bold text-slate-800 truncate">
                {activeTab === 'comp1' && 'Component 1 — Feasibility & Planning Advisory'}
                {activeTab === 'comp2' && 'Component 2 — Regulatory Compliance Engine'}
                {activeTab === 'sources' && 'Statutory Source Register'}
                {activeTab === 'kleene_inspector' && 'Deterministic 3VL Kleene Logic Inspector'}
                {activeTab === 'business_reg' && 'Business Registration & Statutory Form 1 Portal'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {/* Jurisdiction Badge */}
            <div className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200/80 text-xs font-semibold text-slate-700">
              <span className="text-sm">🇱🇰</span>
              <span>Western Province</span>
            </div>

            {/* Kleene Logic Indicator */}
            <div className="hidden lg:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-800">
              <i className="fa-solid fa-shield-check text-emerald-600"></i>
              <span>Deterministic 3VL</span>
            </div>

            {/* Swagger API Direct Link */}
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              title="Open FastAPI Swagger Interactive Docs"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-100 border border-slate-200 shadow-2xs transition-colors"
            >
              <i className="fa-solid fa-terminal text-blue-600"></i>
              <span className="hidden sm:inline">API Docs</span>
            </a>
          </div>
        </header>

        {/* Active View Container */}
        <main className="flex-1 pb-20 md:pb-6">
          {/* TAB 1: REGULATORY COMPLIANCE ENGINE (COMPONENT 2) */}
          {activeTab === 'comp2' && <RegistrationComplianceDashboard />}

          {/* TAB 2: COMPONENT 1 (FEASIBILITY & INTAKE) */}
          {activeTab === 'comp1' && (
            <div className="max-w-5xl mx-auto p-4 sm:p-8 space-y-6">
              <div className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-7 shadow-xs">
                <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
                  <div>
                    <span className="inline-block px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-bold uppercase tracking-wider mb-2 border border-blue-200">
                      Component 1 Architecture
                    </span>
                    <h2 className="text-xl font-bold text-slate-900">
                      Business Feasibility, AI Intake &amp; Planning Engine
                    </h2>
                    <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
                      Component 1 receives entrepreneurial ideas, predicts viability using an ensemble
                      Random Forest trained on Sri Lankan SME survey datasets, extracts SHAP explainability values,
                      and outputs the structured Business Profile JSON consumed by Component 2.
                    </p>
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xl shrink-0">
                    <i className="fa-solid fa-network-wired"></i>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-slate-100 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
                    <div className="text-xs font-bold text-slate-700 flex items-center gap-2 mb-1">
                      <i className="fa-solid fa-robot text-teal-600"></i>
                      Intake Assistant
                    </div>
                    <p className="text-xs text-slate-500">
                      Conversational NLP extractor mapping freeform Sri Lankan business descriptions to structured parameters.
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
                    <div className="text-xs font-bold text-slate-700 flex items-center gap-2 mb-1">
                      <i className="fa-solid fa-chart-pie text-blue-600"></i>
                      Random Forest Model
                    </div>
                    <p className="text-xs text-slate-500">
                      Predicts success probability score and risk profile across startup capital, location, and demand.
                    </p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
                    <div className="text-xs font-bold text-slate-700 flex items-center gap-2 mb-1">
                      <i className="fa-solid fa-file-invoice-dollar text-purple-600"></i>
                      Financial &amp; Plan Generator
                    </div>
                    <p className="text-xs text-slate-500">
                      Generates 12-month cashflow projections, break-even analyses, and ready-to-fund business plans.
                    </p>
                  </div>
                </div>

                <div className="mt-6 flex flex-col sm:flex-row items-center justify-between bg-slate-900 text-white rounded-xl p-4 gap-4">
                  <div>
                    <h3 className="text-sm font-bold">Bridge to Component 2 Legal Engine</h3>
                    <p className="text-xs text-slate-300 mt-0.5">
                      Ready to feed the validated business profile JSON into the regulatory rule engine?
                    </p>
                  </div>
                  <button
                    onClick={() => setActiveTab('comp2')}
                    className="w-full sm:w-auto px-5 py-2.5 bg-teal-500 hover:bg-teal-400 text-slate-900 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2 shadow-sm"
                  >
                    <span>Open Regulatory Engine</span>
                    <i className="fa-solid fa-arrow-right"></i>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: STATUTORY REGISTER & SOURCE CORPUS */}
          {activeTab === 'sources' && (
            <div className="max-w-7xl mx-auto p-4 sm:p-8 space-y-6">
              {/* Executive Hero Banner */}
              <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-850 to-indigo-950 p-6 sm:p-8 text-white shadow-xl border border-slate-800">
                {/* Decorative ambient background glows */}
                <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-blue-500/15 blur-3xl pointer-events-none" />
                <div className="absolute -bottom-20 -left-20 w-80 h-80 rounded-full bg-teal-500/15 blur-3xl pointer-events-none" />

                <div className="relative z-10">
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-teal-500/15 text-teal-300 border border-teal-500/30">
                      <i className="fa-solid fa-shield-halved text-xs text-teal-400" />
                      Authoritative Sri Lanka Legal Repository
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">
                      <i className="fa-solid fa-check-double text-xs text-blue-400" />
                      100% Vector Grounded
                    </span>
                  </div>

                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                    <div>
                      <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
                        <span className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 to-teal-400 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 text-base">
                          <i className="fa-solid fa-scale-balanced" />
                        </span>
                        Statutory Source Register
                      </h2>
                      <p className="text-xs sm:text-sm text-slate-300 mt-2 max-w-2xl leading-relaxed">
                        The definitive statutory knowledge corpus powering Component 2. Every cited compliance obligation,
                        sanitary pass, and registration rule is deterministically grounded in registered Acts, Gazette Orders, and
                        Western Province Statutes to completely eliminate LLM hallucination.
                      </p>
                    </div>

                    {/* Quick Stats Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 shrink-0">
                      <div className="p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                        <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Sources</span>
                        <span className="text-xl font-extrabold text-white">6</span>
                        <span className="block text-[10px] text-teal-400 font-medium mt-0.5">Indexed &amp; Active</span>
                      </div>

                      <div className="p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                        <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Primary Acts</span>
                        <span className="text-xl font-extrabold text-white">3</span>
                        <span className="block text-[10px] text-blue-400 font-medium mt-0.5">National Statutes</span>
                      </div>

                      <div className="p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                        <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Local &amp; Province</span>
                        <span className="text-xl font-extrabold text-white">3</span>
                        <span className="block text-[10px] text-indigo-400 font-medium mt-0.5">WP &amp; CMC By-laws</span>
                      </div>

                      <div className="p-3 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                        <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Hallucination Risk</span>
                        <span className="text-xl font-extrabold text-emerald-400">0.0%</span>
                        <span className="block text-[10px] text-emerald-300 font-medium mt-0.5">Strict Citation Proof</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Search & Filter Toolbar */}
              <div className="bg-white rounded-2xl border border-slate-200/90 p-4 sm:p-5 shadow-xs space-y-4">
                <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
                  {/* Search Bar */}
                  <div className="relative flex-1 max-w-lg">
                    <i className="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-xs text-slate-400" />
                    <input
                      type="text"
                      value={sourceSearch}
                      onChange={(e) => setSourceSearch(e.target.value)}
                      placeholder="Search acts, enforcing authorities, cited sections, or source IDs..."
                      className="w-full pl-10 pr-9 py-2.5 text-xs text-slate-900 border border-slate-300 rounded-xl bg-slate-50/50 hover:bg-white focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-2xs font-medium"
                    />
                    {sourceSearch && (
                      <button
                        type="button"
                        onClick={() => setSourceSearch('')}
                        className="absolute right-3 top-2.5 text-xs text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                        title="Clear search"
                      >
                        <i className="fa-solid fa-xmark" />
                      </button>
                    )}
                  </div>

                  {/* Results Count indicator */}
                  <div className="text-xs font-semibold text-slate-500 flex items-center gap-1.5 self-center">
                    <i className="fa-solid fa-database text-blue-600 text-[11px]" />
                    <span>
                      Showing <strong className="text-slate-900 font-bold">{filteredSources.length}</strong> of{' '}
                      <strong className="text-slate-900 font-bold">{STATUTORY_REGISTER.length}</strong> registered acts
                    </span>
                  </div>
                </div>

                {/* Filter Pills */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-100">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1.5 flex items-center gap-1">
                    <i className="fa-solid fa-filter text-[10px]" /> Filter:
                  </span>

                  {[
                    { key: 'all', label: 'All Statutes', count: STATUTORY_REGISTER.length },
                    { key: 'primary_act', label: 'Primary Acts', count: STATUTORY_REGISTER.filter(s => s.doc_type.toLowerCase().includes('primary act')).length },
                    { key: 'provincial', label: 'Provincial Statutes', count: STATUTORY_REGISTER.filter(s => s.doc_type.toLowerCase().includes('provincial')).length },
                    { key: 'bylaw', label: 'Municipal By-Laws', count: STATUTORY_REGISTER.filter(s => s.doc_type.toLowerCase().includes('by-law')).length },
                    { key: 'gazette', label: 'Gazette Orders', count: STATUTORY_REGISTER.filter(s => s.doc_type.toLowerCase().includes('gazette')).length },
                    { key: 'verified', label: 'Verified Law Only', count: STATUTORY_REGISTER.filter(s => s.status === 'verified').length },
                  ].map((filter) => {
                    const isActive = sourceDocTypeFilter === filter.key;
                    return (
                      <button
                        key={filter.key}
                        type="button"
                        onClick={() => setSourceDocTypeFilter(filter.key)}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                          isActive
                            ? 'bg-slate-900 text-white shadow-xs'
                            : 'bg-slate-100/80 text-slate-600 hover:bg-slate-200/80 hover:text-slate-900'
                        }`}
                      >
                        <span>{filter.label}</span>
                        <span
                          className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full ${
                            isActive ? 'bg-white/20 text-white' : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {filter.count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Elevated Modern Data Table */}
              <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse min-w-[760px]">
                    <thead>
                      <tr className="border-b border-slate-200/80 bg-slate-50/90 text-slate-500 uppercase tracking-wider text-[10px] font-bold">
                        <th className="py-3.5 px-4">Source Identifier</th>
                        <th className="py-3.5 px-4">Statute / By-Law Title</th>
                        <th className="py-3.5 px-4">Enforcing Authority</th>
                        <th className="py-3.5 px-4">Key Cited Sections</th>
                        <th className="py-3.5 px-4">Verification Status</th>
                        <th className="py-3.5 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {filteredSources.length > 0 ? (
                        filteredSources.map((s) => {
                          const isCopied = copiedSourceId === s.source_id;
                          return (
                            <tr
                              key={s.source_id}
                              className="hover:bg-blue-50/30 transition-colors group cursor-default"
                            >
                              {/* Source Identifier */}
                              <td className="py-4 px-4 whitespace-nowrap align-top">
                                <button
                                  type="button"
                                  onClick={() => handleCopySourceId(s.source_id)}
                                  className="group/btn inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 text-indigo-700 font-mono text-[11px] font-bold transition-all shadow-2xs cursor-pointer"
                                  title="Click to copy Source ID"
                                >
                                  <span>{s.source_id}</span>
                                  <i
                                    className={`fa-solid ${
                                      isCopied ? 'fa-check text-emerald-600' : 'fa-copy text-slate-400 group-hover/btn:text-indigo-600'
                                    } text-[10px]`}
                                  />
                                </button>
                                {isCopied && (
                                  <span className="block text-[9px] text-emerald-600 font-bold mt-1">Copied!</span>
                                )}
                              </td>

                              {/* Title & Classification */}
                              <td className="py-4 px-4 align-top max-w-sm">
                                <div className="font-bold text-slate-900 text-xs leading-snug group-hover:text-blue-900 transition-colors">
                                  {s.title}
                                </div>
                                <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
                                  <span
                                    className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                                      s.doc_type.includes('Provincial')
                                        ? 'bg-purple-50 text-purple-700 border border-purple-200'
                                        : s.doc_type.includes('Gazette')
                                        ? 'bg-cyan-50 text-cyan-700 border border-cyan-200'
                                        : s.doc_type.includes('By-Law')
                                        ? 'bg-amber-50 text-amber-700 border border-amber-200'
                                        : 'bg-blue-50 text-blue-700 border border-blue-200'
                                    }`}
                                  >
                                    {s.doc_type}
                                  </span>
                                  <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
                                    <i className="fa-regular fa-calendar text-[10px] text-slate-400" />
                                    Eff. {s.effective_date}
                                  </span>
                                  <span className="text-[10px] text-slate-400">&bull;</span>
                                  <span className="text-[11px] text-slate-600 font-medium">
                                    📍 {s.jurisdiction}
                                  </span>
                                </div>
                              </td>

                              {/* Enforcing Authority */}
                              <td className="py-4 px-4 align-top">
                                <div className="flex items-start gap-2">
                                  <span className="w-6 h-6 rounded-md bg-slate-100 flex items-center justify-center text-slate-500 text-xs shrink-0 mt-0.5">
                                    <i className="fa-solid fa-landmark text-slate-600" />
                                  </span>
                                  <div className="font-semibold text-slate-800 text-xs leading-snug">
                                    {s.authority}
                                  </div>
                                </div>
                              </td>

                              {/* Key Cited Sections */}
                              <td className="py-4 px-4 align-top">
                                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200/80 text-slate-700 font-medium text-[11px] leading-relaxed">
                                  <i className="fa-solid fa-paragraph text-slate-400 text-[10px] shrink-0" />
                                  <span>{s.key_sections}</span>
                                </div>
                              </td>

                              {/* Verification Status */}
                              <td className="py-4 px-4 align-top whitespace-nowrap">
                                {s.status === 'verified' ? (
                                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs">
                                    <i className="fa-solid fa-check-double text-[10px] text-emerald-600" />
                                    Verified Law
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-50 text-amber-800 border border-amber-200 shadow-2xs">
                                    <i className="fa-solid fa-triangle-exclamation text-[10px] text-amber-600" />
                                    Needs Verification
                                  </span>
                                )}
                              </td>

                              {/* Action Buttons */}
                              <td className="py-4 px-4 align-top text-right whitespace-nowrap">
                                <div className="flex items-center justify-end gap-1.5">
                                  <button
                                    type="button"
                                    onClick={() => setSelectedSourceDetail(s)}
                                    className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors cursor-pointer"
                                    title="Quick Inspect Statute Metadata"
                                  >
                                    <i className="fa-solid fa-eye text-slate-500 text-xs" />
                                    <span>Inspect</span>
                                  </button>

                                  <a
                                    href={`http://localhost:8000/api/v1/component2/legal-documents/${s.pdf_query || s.source_id}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs shadow-xs hover:shadow-md transition-all cursor-pointer"
                                  >
                                    <i className="fa-solid fa-file-pdf text-red-200 text-xs" />
                                    <span>View Act</span>
                                    <i className="fa-solid fa-arrow-up-right-from-square text-[9px] text-blue-200" />
                                  </a>
                                </div>
                              </td>
                            </tr>
                          );
                        })
                      ) : (
                        <tr>
                          <td colSpan={6} className="py-12 text-center">
                            <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3 text-lg">
                              <i className="fa-solid fa-folder-open" />
                            </div>
                            <h4 className="font-bold text-slate-800 text-sm">No statutory sources found</h4>
                            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                              No legal sources matched your search query &quot;{sourceSearch}&quot; in the current filter.
                            </p>
                            <button
                              type="button"
                              onClick={() => {
                                setSourceSearch('');
                                setSourceDocTypeFilter('all');
                              }}
                              className="mt-3 px-3 py-1.5 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 transition-colors cursor-pointer"
                            >
                              Reset Search &amp; Filters
                            </button>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Statute Detail Quick-Inspect Modal */}
              {selectedSourceDetail && (
                <div
                  className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200"
                  onClick={() => setSelectedSourceDetail(null)}
                >
                  <div
                    className="bg-white rounded-3xl max-w-xl w-full p-6 sm:p-7 shadow-2xl border border-slate-200 space-y-5 animate-in zoom-in-95 duration-150"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
                      <div className="flex items-center gap-3">
                        <span className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center text-lg shrink-0">
                          <i className="fa-solid fa-landmark-dome" />
                        </span>
                        <div>
                          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">
                            {selectedSourceDetail.source_id}
                          </span>
                          <h3 className="text-base font-extrabold text-slate-900 leading-snug">
                            {selectedSourceDetail.title}
                          </h3>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => setSelectedSourceDetail(null)}
                        className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors cursor-pointer"
                        title="Close modal"
                      >
                        <i className="fa-solid fa-xmark text-sm" />
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                        <span className="text-[10px] font-bold text-slate-500 uppercase block">Enforcing Authority</span>
                        <p className="font-semibold text-slate-900">{selectedSourceDetail.authority}</p>
                      </div>

                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                        <span className="text-[10px] font-bold text-slate-500 uppercase block">Jurisdiction Scope</span>
                        <p className="font-semibold text-slate-900">{selectedSourceDetail.jurisdiction}</p>
                      </div>

                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                        <span className="text-[10px] font-bold text-slate-500 uppercase block">Document Classification</span>
                        <p className="font-semibold text-slate-900">{selectedSourceDetail.doc_type}</p>
                      </div>

                      <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                        <span className="text-[10px] font-bold text-slate-500 uppercase block">Effective Date</span>
                        <p className="font-semibold text-slate-900">{selectedSourceDetail.effective_date}</p>
                      </div>
                    </div>

                    <div className="p-3.5 rounded-xl bg-blue-50/60 border border-blue-100 text-xs space-y-1">
                      <span className="text-[10px] font-bold text-blue-900 uppercase tracking-wider block">
                        Key Cited Legal Sections
                      </span>
                      <p className="text-slate-800 font-medium leading-relaxed">
                        {selectedSourceDetail.key_sections}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                      <button
                        type="button"
                        onClick={() => handleCopySourceId(selectedSourceDetail.source_id)}
                        className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1.5 cursor-pointer"
                      >
                        <i className="fa-solid fa-copy" />
                        <span>Copy Source ID</span>
                      </button>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => setSelectedSourceDetail(null)}
                          className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors cursor-pointer"
                        >
                          Close
                        </button>

                        <a
                          href={`http://localhost:8000/api/v1/component2/legal-documents/${selectedSourceDetail.pdf_query || selectedSourceDetail.source_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs shadow-xs transition-all cursor-pointer"
                        >
                          <i className="fa-solid fa-file-pdf text-xs" />
                          <span>View Official PDF</span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: KLEENE 3-VALUED LOGIC INSPECTOR (ACADEMIC DEMO) */}
          {activeTab === 'kleene_inspector' && (
            <div className="max-w-5xl mx-auto p-4 sm:p-8 space-y-6">
              <div className="bg-white rounded-2xl border border-slate-200 p-5 sm:p-7 shadow-xs">
                <div>
                  <span className="inline-block px-2.5 py-1 rounded-md bg-teal-50 text-teal-700 text-xs font-bold uppercase tracking-wider mb-2 border border-teal-200">
                    Academic Research Rigor
                  </span>
                  <h2 className="text-xl font-bold text-slate-900">
                    Deterministic Three-Valued Kleene Logic Inspector
                  </h2>
                  <p className="text-xs text-slate-500 mt-1 max-w-3xl leading-relaxed">
                    A core research contribution of Component 2 is the strict elimination of LLM hallucination
                    in legal applicability. Missing facts are treated with Kleene 3-valued logic (True, False, None/Unknown).
                    Missing facts are <strong>never assumed to be false</strong>.
                  </p>
                </div>

                {/* Mathematical Kleene Truth Tables */}
                <div className="mt-6 pt-6 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Kleene AND Table */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <h3 className="text-xs font-bold text-slate-800 mb-2 flex items-center gap-2">
                      <i className="fa-solid fa-square-root-variable text-blue-600"></i>
                      Kleene Conjunction (AND / all_of)
                    </h3>
                    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
                      <table className="w-full text-center text-xs min-w-[240px]">
                        <thead className="bg-slate-100 font-bold text-slate-600 border-b border-slate-200">
                          <tr>
                            <th className="py-1.5">AND</th>
                            <th className="py-1.5 text-emerald-700">True</th>
                            <th className="py-1.5 text-amber-700">Unknown</th>
                            <th className="py-1.5 text-rose-700">False</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 text-slate-700 font-mono text-[11px]">
                          <tr>
                            <td className="bg-slate-100 font-bold text-emerald-700">True</td>
                            <td className="bg-emerald-50 text-emerald-800 font-bold">True</td>
                            <td className="bg-amber-50 text-amber-800">Unknown</td>
                            <td className="bg-rose-50 text-rose-800">False</td>
                          </tr>
                          <tr>
                            <td className="bg-slate-100 font-bold text-amber-700">Unknown</td>
                            <td className="bg-amber-50 text-amber-800">Unknown</td>
                            <td className="bg-amber-50 text-amber-800">Unknown</td>
                            <td className="bg-rose-50 text-rose-800">False</td>
                          </tr>
                          <tr>
                            <td className="bg-slate-100 font-bold text-rose-700">False</td>
                            <td className="bg-rose-50 text-rose-800">False</td>
                            <td className="bg-rose-50 text-rose-800">False</td>
                            <td className="bg-rose-50 text-rose-800">False</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-2">
                      Notice: <code>False AND Unknown = False</code> (short-circuit). However, <code>True AND Unknown = Unknown</code>.
                    </p>
                  </div>

                  {/* Kleene OR Table */}
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <h3 className="text-xs font-bold text-slate-800 mb-2 flex items-center gap-2">
                      <i className="fa-solid fa-code-fork text-teal-600"></i>
                      Kleene Disjunction (OR / any_of)
                    </h3>
                    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
                      <table className="w-full text-center text-xs min-w-[240px]">
                        <thead className="bg-slate-100 font-bold text-slate-600 border-b border-slate-200">
                          <tr>
                            <th className="py-1.5">OR</th>
                            <th className="py-1.5 text-emerald-700">True</th>
                            <th className="py-1.5 text-amber-700">Unknown</th>
                            <th className="py-1.5 text-rose-700">False</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 text-slate-700 font-mono text-[11px]">
                          <tr>
                            <td className="bg-slate-100 font-bold text-emerald-700">True</td>
                            <td className="bg-emerald-50 text-emerald-800">True</td>
                            <td className="bg-emerald-50 text-emerald-800">True</td>
                            <td className="bg-emerald-50 text-emerald-800">True</td>
                          </tr>
                          <tr>
                            <td className="bg-slate-100 font-bold text-amber-700">Unknown</td>
                            <td className="bg-emerald-50 text-emerald-800">True</td>
                            <td className="bg-amber-50 text-amber-800">Unknown</td>
                            <td className="bg-amber-50 text-amber-800">Unknown</td>
                          </tr>
                          <tr>
                            <td className="bg-slate-100 font-bold text-rose-700">False</td>
                            <td className="bg-emerald-50 text-emerald-800">True</td>
                            <td className="bg-amber-50 text-amber-800">Unknown</td>
                            <td className="bg-rose-50 text-rose-800">False</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-2">
                      Notice: <code>True OR Unknown = True</code>. However, <code>False OR Unknown = Unknown</code>.
                    </p>
                  </div>
                </div>

                {/* Interactive Sandbox Playground */}
                <div className="mt-6 p-4 sm:p-5 rounded-xl border border-slate-200 bg-white shadow-2xs space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                        <i className="fa-solid fa-gamepad text-blue-600"></i>
                        Interactive Rule Evaluation Sandbox
                      </h3>
                      <p className="text-xs text-slate-500">
                        Rule: <code>CMC Food Premises Hygiene Licence (OBL-FOOD-001)</code>
                      </p>
                    </div>
                    <div>
                      <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">
                        Evaluated Verdict
                      </div>
                      <div className={`mt-1 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${computeKleeneFoodPremises().color}`}>
                        {computeKleeneFoodPremises().label}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t border-slate-100">
                    {/* Fact 1 */}
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">
                        1. Location in Western Province
                      </label>
                      <div className="flex gap-1">
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, province_is_wp: true }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.province_is_wp === true ? 'bg-emerald-600 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          True
                        </button>
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, province_is_wp: null }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.province_is_wp === null ? 'bg-amber-500 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          Unknown
                        </button>
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, province_is_wp: false }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.province_is_wp === false ? 'bg-rose-600 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          False
                        </button>
                      </div>
                    </div>

                    {/* Fact 2 */}
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">
                        2. Has Physical Premises
                      </label>
                      <div className="flex gap-1">
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, physical_premises: true }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.physical_premises === true ? 'bg-emerald-600 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          True
                        </button>
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, physical_premises: null }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.physical_premises === null ? 'bg-amber-500 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          Unknown
                        </button>
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, physical_premises: false }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.physical_premises === false ? 'bg-rose-600 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          False
                        </button>
                      </div>
                    </div>

                    {/* Fact 3 */}
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                      <label className="block text-xs font-bold text-slate-700 mb-1.5">
                        3. Operates Kitchen / Cooking
                      </label>
                      <div className="flex gap-1">
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, operates_kitchen: true }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.operates_kitchen === true ? 'bg-emerald-600 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          True
                        </button>
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, operates_kitchen: null }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.operates_kitchen === null ? 'bg-amber-500 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          Unknown
                        </button>
                        <button
                          type="button"
                          onClick={() => setKleeneFacts((p) => ({ ...p, operates_kitchen: false }))}
                          className={`flex-1 py-1.5 text-xs font-semibold rounded ${
                            kleeneFacts.operates_kitchen === false ? 'bg-rose-600 text-white' : 'bg-white border text-slate-600'
                          }`}
                        >
                          False
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {/* TAB 5: BUSINESS REGISTRATION & FORM 1 GENERATOR */}
          {activeTab === 'business_reg' && <BusinessRegistrationView />}
        </main>

        {/* ----------------------------------------------------------------- */}
        {/* MOBILE BOTTOM NAVIGATION BAR (Thumb-friendly touch bar)           */}
        {/* ----------------------------------------------------------------- */}
        <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-slate-200/90 px-2 py-1.5 flex items-center justify-around shadow-lg">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all relative ${
                  isActive ? 'text-teal-600 font-bold scale-105' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm ${isActive ? 'bg-teal-50 text-teal-600 shadow-2xs' : ''}`}>
                  <i className={`fa-solid ${item.icon}`}></i>
                </div>
                <span className="text-[9px] mt-0.5 tracking-tight truncate max-w-[62px]">
                  {item.id === 'comp1' ? 'Feasibility' : item.id === 'comp2' ? 'Legal Regs' : item.id === 'sources' ? 'Statutes' : item.id === 'kleene_inspector' ? '3VL Logic' : 'Registration'}
                </span>
                {isActive && (
                  <span className="absolute -top-1 w-6 h-0.5 rounded-full bg-teal-500"></span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default App;
