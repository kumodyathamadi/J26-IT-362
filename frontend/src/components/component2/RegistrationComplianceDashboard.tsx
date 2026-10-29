import React, { useState } from 'react';
import { COLOMBO_LEGAL_DATABASE } from './mockData';
import { SectorType, RAGLegalCitation, ComplianceRequirement } from './types';

export const RegistrationComplianceDashboard: React.FC = () => {
  const [selectedSector, setSelectedSector] = useState<SectorType>('food');
  const [activeTab, setActiveTab] = useState<'roadmap' | 'licenses' | 'tax' | 'checklist'>('roadmap');
  const [selectedCitationId, setSelectedCitationId] = useState<string>('cite-tin-ird');
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const evaluationData = COLOMBO_LEGAL_DATABASE[selectedSector];
  const { businessContext, ragCitations, requirements, summaryCounts } = evaluationData;

  const currentCitation: RAGLegalCitation = 
    ragCitations[selectedCitationId] || Object.values(ragCitations)[0];

  return (
    <div className="flex h-screen bg-slate-100 font-sans text-slate-800 antialiased overflow-hidden">
      
      {/* LEFT NAVIGATION SIDEBAR */}
      <aside class="w-64 flex-shrink-0 flex flex-col justify-between text-slate-300" style={{ backgroundColor: '#0d1629' }}>
        <div>
          {/* Brand Header */}
          <div className="px-6 py-5 flex items-center gap-3 border-b border-slate-800">
            <div className="w-9 h-9 rounded-lg bg-emerald-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
              <i className="fa-solid fa-compass text-lg"></i>
            </div>
            <div>
              <h1 className="font-bold text-white text-base tracking-tight leading-none">LifeCycle AI</h1>
              <span className="text-xs text-slate-400 font-medium">Business decision support</span>
            </div>
          </div>

          {/* Lifecycle Modules */}
          <div className="px-4 py-6">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-3">Lifecycle Modules</div>
            <nav className="space-y-1">
              <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                <i className="fa-regular fa-lightbulb w-4 text-center"></i>
                <div className="flex flex-col text-left">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Component 1</span>
                  <span class="text-xs font-medium text-slate-300">Idea & Feasibility</span>
                </div>
              </button>

              <button className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold text-white bg-slate-800 border-l-4 border-emerald-500 shadow-sm">
                <div className="flex items-center gap-3">
                  <i className="fa-solid fa-shield-halved w-4 text-center text-emerald-400"></i>
                  <div className="flex flex-col text-left">
                    <span className="text-[10px] text-emerald-400 uppercase tracking-wider font-semibold">Component 2</span>
                    <span className="text-xs font-semibold text-white">Registration & Compliance</span>
                  </div>
                </div>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              </button>

              <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                <i className="fa-solid fa-wallet w-4 text-center"></i>
                <div className="flex flex-col text-left">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Component 3</span>
                  <span className="text-xs font-medium text-slate-300">Financial Management</span>
                </div>
              </button>

              <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                <i className="fa-solid fa-chart-line w-4 text-center"></i>
                <div className="flex flex-col text-left">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Component 4</span>
                  <span className="text-xs font-medium text-slate-300">Growth & Advisory</span>
                </div>
              </button>
            </nav>
          </div>

          {/* Quick Sector Presets */}
          <div className="px-4 py-3 mx-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>Colombo District Presets</span>
              <i className="fa-solid fa-location-dot text-emerald-400 text-xs"></i>
            </div>
            <div className="grid grid-cols-2 gap-1.5 text-xs">
              {(['food', 'clothing', 'saloon', 'vehicle'] as SectorType[]).map((sec) => (
                <button
                  key={sec}
                  onClick={() => setSelectedSector(sec)}
                  className={`px-2 py-1.5 rounded text-left transition-all font-medium capitalize ${
                    selectedSector === sec
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                      : 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {sec === 'food' && '🍔 Food'}
                  {sec === 'clothing' && '👗 Clothing'}
                  {sec === 'saloon' && '💇 Saloon'}
                  {sec === 'vehicle' && '🚗 Vehicle'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 flex items-center gap-3 text-xs">
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-white font-bold text-xs border border-slate-600">
            LK
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-slate-200 font-medium truncate">Western Province Reg.</p>
            <p className="text-slate-400 text-[11px] truncate">Colombo District Engine</p>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT CANVAS */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-50">
        
        <!-- Header -->
        <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs text-slate-500 font-medium mb-1">
              <span>Component 2</span>
              <i className="fa-solid fa-chevron-right text-[10px]"></i>
              <span>AI decision support</span>
              <i className="fa-solid fa-chevron-right text-[10px]"></i>
              <span className="text-blue-600 font-semibold">Sri Lanka Compliance Engine</span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Business Registration & Regulatory Compliance</h2>
          </div>

          <div className="flex items-center gap-3">
            <button className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 shadow-sm">
              <i className="fa-solid fa-download text-slate-500"></i>
              Export report
            </button>
            <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 rounded-lg text-xs font-semibold text-white hover:bg-blue-700 shadow-md">
              <i className="fa-solid fa-rotate text-white"></i>
              Re-evaluate RAG Rules
            </button>
          </div>
        </header>

        <!-- Main Body -->
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          <!-- Context Banner -->
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
                <i className="fa-solid fa-file-invoice text-lg"></i>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-slate-900 text-base">{businessContext.name}</h3>
                  <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-medium capitalize">
                    {businessContext.sectorLabel}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-xs font-medium">
                    {businessContext.entityType}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-xs font-medium">
                    {businessContext.council}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-xs font-medium">
                    {businessContext.employeesCount} employees
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">{businessContext.description}</p>
              </div>
            </div>

            <button onClick={() => setIsModalOpen(true)} className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-blue-50">
              <i className="fa-solid fa-pen-to-square"></i> Edit context
            </button>
          </div>

          <!-- Cards Grid -->
          <div className="grid grid-cols-12 gap-5">
            <!-- Gauge Card -->
            <div className="col-span-12 lg:col-span-5 rounded-2xl p-6 text-white flex flex-col justify-between shadow-xl" style={{ background: 'linear-gradient(135deg, #09132b 0%, #111f42 100%)' }}>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-xs text-slate-400 font-medium uppercase tracking-wide">Compliance readiness</span>
                  <p className="text-[11px] text-slate-400 mt-0.5">{evaluationData.totalRulesEvaluated} rules evaluated · {evaluationData.applicableRulesCount} apply</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-emerald-400">
                  <i className="fa-solid fa-chart-pie text-xs"></i>
                </div>
              </div>

              <div className="my-3 flex items-baseline gap-3">
                <span className="text-5xl font-extrabold tracking-tight text-white">{evaluationData.readinessPercentage}%</span>
                <span className="text-xs font-medium text-emerald-400 flex items-center gap-1 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800">
                  <i className="fa-solid fa-arrow-trend-up text-[10px]"></i> Action required
                </span>
              </div>

              <div className="w-full bg-slate-800/90 rounded-full h-3 mb-4 p-0.5 border border-slate-700/60 overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-700" style={{ width: `${evaluationData.readinessPercentage}%` }}></div>
              </div>

              <div className="text-xs text-slate-400 pt-3 border-t border-slate-800 flex items-center justify-between">
                <span>{evaluationData.completedCount} of {evaluationData.applicableRulesCount} requirements completed</span>
              </div>
            </div>

            <!-- Next Best Action -->
            <div className="col-span-12 lg:col-span-4 bg-white border border-slate-200 rounded-2xl p-6 flex flex-col justify-between shadow-sm">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-blue-600 uppercase tracking-wider flex items-center gap-1.5">
                    <i className="fa-solid fa-wand-magic-sparkles text-amber-500"></i> Next best action
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">High Priority</span>
                </div>
                <h4 className="text-lg font-bold text-slate-900 leading-snug">{evaluationData.nextBestAction.title}</h4>
                <p className="text-xs font-semibold text-slate-500 mt-0.5">{evaluationData.nextBestAction.authority}</p>

                <div className="mt-4 p-3 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs">
                  <span className="font-bold block">Due in {evaluationData.nextBestAction.deadlineDays} days</span>
                  <span className="text-amber-800 text-[11px]">{evaluationData.nextBestAction.rationale}</span>
                </div>
              </div>
            </div>

            <!-- Summary Counts -->
            <div className="col-span-12 lg:col-span-3 bg-white border border-slate-200 rounded-2xl p-6 flex flex-col justify-between shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Identified by AI</span>
                <span className="text-[10px] text-blue-600 bg-blue-50 font-semibold px-2 py-0.5 rounded">Western Prov. RAG</span>
              </div>

              <div className="space-y-3 my-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Registrations</span>
                  <span className="font-bold text-slate-900">{summaryCounts.registrations}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Licenses & permits</span>
                  <span className="font-bold text-slate-900">{summaryCounts.licensesAndPermits}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Tax & regulatory</span>
                  <span className="font-bold text-slate-900">{summaryCounts.taxAndRegulatory}</span>
                </div>
                <div className="flex items-center justify-between text-amber-700 bg-amber-50/50 p-1 rounded">
                  <span>Due within 30 days</span>
                  <span className="font-bold">{summaryCounts.dueWithin30Days}</span>
                </div>
              </div>

              <div className="pt-2 text-[11px] text-emerald-600 font-semibold border-t border-slate-100">
                <i className="fa-solid fa-circle text-[6px] mr-1"></i> 99.2% Evidence-Grounded Match
              </div>
            </div>
          </div>

          <!-- Main Detailed Tabs & Citation Sidebar -->
          <div className="grid grid-cols-12 gap-6">
            <!-- Main Tabs Stack -->
            <div className="col-span-12 lg:col-span-7 space-y-4">
              <div className="bg-white border border-slate-200 rounded-xl px-4 pt-3 pb-0 shadow-sm flex items-center gap-6 text-xs font-semibold text-slate-500">
                <button onClick={() => setActiveTab('roadmap')} className={`pb-3 ${activeTab === 'roadmap' ? 'text-blue-600 border-b-2 border-blue-600 font-bold' : ''}`}>
                  Step-by-step roadmap
                </button>
                <button onClick={() => setActiveTab('licenses')} className={`pb-3 ${activeTab === 'licenses' ? 'text-blue-600 border-b-2 border-blue-600 font-bold' : ''}`}>
                  Licenses & permits
                </button>
                <button onClick={() => setActiveTab('tax')} className={`pb-3 ${activeTab === 'tax' ? 'text-blue-600 border-b-2 border-blue-600 font-bold' : ''}`}>
                  Tax & regulatory
                </button>
              </div>

              <!-- Requirements List -->
              {activeTab === 'roadmap' && (
                <div className="space-y-3">
                  {requirements.map((req) => (
                    <div
                      key={req.id}
                      onClick={() => setSelectedCitationId(req.citationId)}
                      className={`bg-white border rounded-xl p-4 shadow-sm cursor-pointer hover:border-blue-400 transition-all ${
                        selectedCitationId === req.citationId ? 'border-2 border-blue-500 bg-blue-50/20' : 'border-slate-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ${
                            req.status === 'Completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-800'
                          }`}>
                            {req.stepNumber}
                          </div>
                          <div>
                            <h5 className="text-sm font-bold text-slate-900">{req.title}</h5>
                            <p className="text-xs text-slate-500 mt-0.5">{req.authority}</p>
                            <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-2">
                              <span>Fee: LKR {req.estimatedFeeLkr.toLocaleString()}</span>
                              <span>Duration: {req.validityDuration}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <!-- Citation Drawer -->
            <div className="col-span-12 lg:col-span-5">
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div className="flex items-center gap-2">
                    <i className="fa-solid fa-book-bookmark text-blue-600"></i>
                    <h4 className="font-bold text-slate-900 text-sm">Evidence-Grounded RAG Citation</h4>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                    {(currentCitation.vectorSimilarityScore * 100).toFixed(1)}% Match
                  </span>
                </div>

                <div>
                  <h5 className="font-bold text-slate-900 text-sm">{currentCitation.actTitle}</h5>
                  <p className="text-xs text-slate-500 mt-0.5">{currentCitation.subTitle}</p>
                </div>

                <div className="p-3 bg-slate-900 text-slate-200 rounded-xl text-[11px] font-mono leading-relaxed">
                  {currentCitation.legalExcerpt}
                </div>

                <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs">
                  <span className="font-bold text-blue-900 block mb-1">AI Rationale:</span>
                  <p className="text-slate-700 text-[11px]">{currentCitation.explainabilityRationale}</p>
                </div>

                <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-900">
                  <span className="font-bold block">Penalty Risk:</span>
                  <p className="text-[11px]">{currentCitation.penaltyRiskText}</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </main>

    </div>
  );
};
