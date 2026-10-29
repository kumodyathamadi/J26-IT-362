import React, { useState, useEffect, useRef } from 'react';
import { useOutletContext, useSearchParams, useParams, Link } from 'react-router-dom';
import { 
  Sliders, 
  RefreshCw, 
  ArrowRight, 
  ShieldAlert, 
  Sparkles, 
  RotateCcw, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  FileText,
  Check
} from 'lucide-react';
import { simulateBusinessScenario, applyScenarioToBusiness } from '../services/api';
import { FeasibilityBadge } from './common/Badge';
import { formatCurrency, formatCustomersPerDay } from '../utils/formatters';
import { useToast } from './common/Toast';

export default function WhatIfSimulator({ scenarioData: propScenario, currentInput: propInput, onScenarioSuccess }) {
  const ctx = useOutletContext();
  const [searchParams] = useSearchParams();
  const { id } = useParams();
  const profile = ctx?.profile;
  const scenarioData = propScenario || profile?.scenario_analysis;
  const currentInput = propInput || profile?.business_input;
  const baselineFeasibility = profile?.feasibility_analysis || {};

  // Preserve the true original baseline from initial intake if scenario was previously applied
  const originalBaseline = profile?.original_baseline;
  const initialInput = originalBaseline?.business_input || currentInput;
  const initialFeasibility = originalBaseline?.feasibility_analysis || baselineFeasibility;

  const baselineCapital = initialInput?.available_capital_lkr ?? (currentInput?.available_capital_lkr || 500000);
  const baselineBudget = initialInput?.monthly_budget_lkr ?? (currentInput?.monthly_budget_lkr || 150000);
  const baselineCustomers = initialInput?.expected_customers_per_day ?? (currentInput?.expected_customers_per_day || 40);
  const baselinePrice = initialInput?.expected_price_lkr ?? (currentInput?.expected_price_lkr || 350);
  const baselineScore = originalBaseline?.confidence_score ?? (initialFeasibility.confidence_score || initialFeasibility.probability_score || 0.5);
  const baselineLabel = originalBaseline?.feasibility_label ?? (initialFeasibility.predicted_label || 'Conditionally Feasible');

  const paramCapital = searchParams.get('capital');
  const paramBudget = searchParams.get('budget');
  const paramCustomers = searchParams.get('customers');
  const paramStrategyName = searchParams.get('strategyName') || searchParams.get('strategy');

  const parsedCapital = paramCapital ? parseFloat(paramCapital) : null;
  const initialCapital = parsedCapital && !isNaN(parsedCapital) ? parsedCapital : (currentInput?.available_capital_lkr || baselineCapital);

  const parsedBudget = paramBudget ? parseFloat(paramBudget) : null;
  const initialBudget = parsedBudget && !isNaN(parsedBudget) ? parsedBudget : (currentInput?.monthly_budget_lkr || baselineBudget);

  const parsedCustomers = paramCustomers ? parseInt(paramCustomers, 10) : null;
  const initialCustomers = parsedCustomers && !isNaN(parsedCustomers) ? parsedCustomers : (currentInput?.expected_customers_per_day || baselineCustomers);

  // Interactive Scenario State
  const [customCapital, setCustomCapital] = useState(initialCapital);
  const [customBudget, setCustomBudget] = useState(initialBudget);
  const [customCustomers, setCustomCustomers] = useState(initialCustomers);
  const [customPrice, setCustomPrice] = useState(currentInput?.expected_price_lkr || baselinePrice);
  
  const [liveScoring, setLiveScoring] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [activeCustomResult, setActiveCustomResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  
  const toast = useToast();
  const [isApplying, setIsApplying] = useState(false);
  const [applySuccess, setApplySuccess] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const isDifferentFromBaseline = 
    customCapital !== baselineCapital ||
    customBudget !== baselineBudget ||
    customCustomers !== baselineCustomers ||
    customPrice !== baselinePrice;

  const handleApplyScenario = async () => {
    if (!id) return;
    setIsApplying(true);
    setErrorMsg(null);
    try {
      const scenarioParams = {
        available_capital_lkr: parseFloat(customCapital),
        monthly_budget_lkr: parseFloat(customBudget),
        expected_customers_per_day: parseInt(customCustomers, 10),
        expected_price_lkr: parseFloat(customPrice),
      };
      const res = await applyScenarioToBusiness(id, scenarioParams);
      if (res?.structured_profile && ctx?.setProfile) {
        ctx.setProfile(res.structured_profile);
      } else if (ctx?.reloadRecord) {
        ctx.reloadRecord();
      }
      setApplySuccess({
        capital: customCapital,
        budget: customBudget,
        customers: customCustomers,
        price: customPrice
      });
      setActiveCustomResult(null);
      const msg = "Scenario successfully applied! Your Business Plan and financial runway have been regenerated.";
      if (toast?.success) toast.success(msg);
      else if (toast?.showToast) toast.showToast(msg, 'success');
      setShowConfirmModal(false);
    } catch (err) {
      console.error('Failed to apply scenario:', err);
      const errMsg = `Failed to apply scenario: ${err.message}`;
      setErrorMsg(errMsg);
      if (toast?.error) toast.error(errMsg);
      else if (toast?.showToast) toast.showToast(errMsg, 'error');
    } finally {
      setIsApplying(false);
    }
  };

  const debounceTimer = useRef(null);

  const runScenarioSimulation = async (capital, budget, customers, price) => {
    setSimulating(true);
    setErrorMsg(null);
    try {
      const modifiedInput = {
        ...currentInput,
        available_capital_lkr: parseFloat(capital),
        monthly_budget_lkr: parseFloat(budget),
        expected_customers_per_day: parseInt(customers, 10),
        expected_price_lkr: parseFloat(price),
      };
      
      const recordId = id || profile?.metadata?.record_id || null;
      // Dedicated non-persistent simulation endpoint - creates ZERO database records
      const newResult = await simulateBusinessScenario(modifiedInput, recordId);
      setActiveCustomResult(newResult);
      if (onScenarioSuccess) onScenarioSuccess(newResult);
    } catch (err) {
      console.error('Scenario simulation failed:', err);
      setErrorMsg(err.message);
    } finally {
      setSimulating(false);
    }
  };

  // Live Debounced Re-scoring
  useEffect(() => {
    if (!liveScoring) return;

    // Check if values have actually changed from baseline or previous
    const isDifferent = 
      customCapital !== baselineCapital ||
      customBudget !== baselineBudget ||
      customCustomers !== baselineCustomers ||
      customPrice !== baselinePrice;

    if (!isDifferent && !activeCustomResult) return;

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(() => {
      runScenarioSimulation(customCapital, customBudget, customCustomers, customPrice);
    }, 600);

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [customCapital, customBudget, customCustomers, customPrice, liveScoring]);

  const handleResetToBaseline = () => {
    setCustomCapital(baselineCapital);
    setCustomBudget(baselineBudget);
    setCustomCustomers(baselineCustomers);
    setCustomPrice(baselinePrice);
    setActiveCustomResult(null);
    setErrorMsg(null);
  };

  const handleApplyScenarioToSliders = (sim) => {
    const mods = sim.modifications || {};
    if (mods.available_capital_lkr !== undefined) {
      setCustomCapital(parseFloat(mods.available_capital_lkr));
    }
    if (mods.monthly_budget_lkr !== undefined) {
      setCustomBudget(parseFloat(mods.monthly_budget_lkr));
    }
    if (mods.expected_customers_per_day !== undefined) {
      setCustomCustomers(parseInt(mods.expected_customers_per_day, 10));
    }
    if (mods.expected_price_lkr !== undefined) {
      setCustomPrice(parseFloat(mods.expected_price_lkr));
    }
    const target = document.querySelector('.glass-card');
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const scenarioFeasibility = activeCustomResult?.feasibility_analysis || null;
  const scenarioLabel = scenarioFeasibility?.predicted_label || 
    (isDifferentFromBaseline ? baselineLabel : (profile?.feasibility_analysis?.predicted_label || baselineLabel));
  const scenarioScore = scenarioFeasibility 
    ? (scenarioFeasibility.confidence_score || scenarioFeasibility.probability_score || 0)
    : (isDifferentFromBaseline ? baselineScore : (profile?.feasibility_analysis?.confidence_score || baselineScore));

  // Viability Index delta represents true multi-class shift: P(Feas) + 0.5 * P(Cond)
  const viabilityDelta = isDifferentFromBaseline && activeCustomResult?.viability_delta !== undefined 
    ? activeCustomResult.viability_delta 
    : (isDifferentFromBaseline && scenarioFeasibility ? (scenarioScore - baselineScore) : 0);
  const viabilityDeltaPct = (viabilityDelta * 100).toFixed(1);
  const probDeltas = isDifferentFromBaseline ? (activeCustomResult?.probability_deltas || {}) : {};

  const what_if_simulations = scenarioData?.what_if_simulations || [];
  const counterfactual_boundary = scenarioData?.counterfactual_boundary || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Header */}
      <div>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          <Sliders size={22} style={{ color: '#60a5fa' }} />
          <span>Scenario Explorer & Live What-If Simulator</span>
          <span className="tab-pill-badge tab-pill-purple" style={{ fontSize: '0.72rem', padding: '0.2rem 0.55rem' }}>Interactive</span>
        </h3>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginTop: '0.25rem' }}>
          Adjust financial capital, unit pricing, and customer demand with live interactive sliders. Evaluate real-time ML re-scoring against {currentInput?.business_name ? currentInput.business_name : 'your baseline project'}.
        </p>
      </div>

      {/* Apply Success Banner */}
      {applySuccess && (
        <div 
          style={{
            background: 'linear-gradient(135deg, rgba(6, 78, 59, 0.65), rgba(15, 23, 42, 0.95))',
            border: '1.5px solid rgba(16, 185, 129, 0.7)',
            borderRadius: '12px',
            padding: '1rem 1.25rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
            boxShadow: '0 4px 20px rgba(16, 185, 129, 0.25)',
            animation: 'fadeIn 0.3s ease'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#34d399' }}>
              <CheckCircle2 size={22} />
            </div>
            <div>
              <div style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                Scenario Applied & Business Plan Regenerated!
              </div>
              <div style={{ fontSize: '0.78rem', color: '#cbd5e1', marginTop: '0.2rem' }}>
                Your baseline Available Capital is now updated to <strong style={{ color: '#34d399' }}>{formatCurrency(applySuccess.capital)}</strong>. Your 5-section Business Plan and financial runway have been re-synthesized.
              </div>
            </div>
          </div>

          <Link
            to={`/businesses/${id}/plan`}
            style={{
              background: 'linear-gradient(135deg, #059669, #10b981)',
              color: '#ffffff',
              padding: '0.55rem 1.2rem',
              borderRadius: '8px',
              fontSize: '0.82rem',
              fontWeight: 700,
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.45rem',
              boxShadow: '0 2px 10px rgba(16, 185, 129, 0.4)'
            }}
          >
            <FileText size={16} />
            <span>View Updated Business Plan</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      )}

      {/* Strategy Simulation Banner */}
      {paramStrategyName && (
        <div 
          className="glass-card"
          style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(30, 41, 59, 0.75))',
            border: '1px solid rgba(99, 102, 241, 0.5)',
            borderRadius: '10px',
            padding: '0.85rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <Sparkles size={20} style={{ color: '#c084fc' }} />
            <div>
              <span style={{ fontSize: '0.7rem', color: '#a5b4fc', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.5px' }}>
                Simulating Evaluated Strategy
              </span>
              <h4 style={{ fontSize: '0.98rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                {paramStrategyName}
              </h4>
            </div>
          </div>
          <span style={{ fontSize: '0.76rem', color: '#cbd5e1' }}>
            Sliders pre-filled from strategic recommendation. Move sliders below to test sensitivity.
          </span>
        </div>
      )}

      {/* Side-by-Side Change Versus Baseline Comparison Card */}
      <div 
        className="glass-card" 
        style={{ 
          border: '1px solid rgba(59, 130, 246, 0.4)', 
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95))', 
          padding: '1.5rem'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#60a5fa', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '1px' }}>
              Real-Time Model Comparison
            </span>
            <h4 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '0.15rem' }}>
              {currentInput?.business_name ? `${currentInput.business_name}: Baseline vs. Modified` : 'Baseline vs. Modified Scenario'}
            </h4>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {/* Live Re-scoring Toggle */}
            <button
              onClick={() => setLiveScoring(!liveScoring)}
              style={{
                background: liveScoring ? 'rgba(34, 197, 94, 0.15)' : 'rgba(100, 116, 139, 0.15)',
                border: `1px solid ${liveScoring ? 'rgba(34, 197, 94, 0.4)' : 'rgba(100, 116, 139, 0.3)'}`,
                color: liveScoring ? '#4ade80' : '#94a3b8',
                padding: '0.35rem 0.75rem',
                borderRadius: '20px',
                fontSize: '0.75rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                cursor: 'pointer'
              }}
            >
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: liveScoring ? '#22c55e' : '#64748b' }}></span>
              Live Auto-Score: {liveScoring ? 'ON' : 'OFF'}
            </button>

            {/* Reset to Baseline Button */}
            <button
              onClick={handleResetToBaseline}
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
              title="Reset all sliders back to baseline inputs"
            >
              <RotateCcw size={13} />
              Reset Baseline
            </button>
          </div>
        </div>

        {/* Comparison Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem', alignItems: 'center' }}>
          
          {/* Baseline Column */}
          <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px', padding: '1.1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase' }}>
                Original Baseline
              </span>
              <FeasibilityBadge label={baselineLabel} showScore={false} size="sm" />
            </div>

            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
              {(baselineScore * 100).toFixed(1)}% <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 500 }}>Confidence</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.78rem', color: '#cbd5e1', paddingTop: '0.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <div>Capital: <strong style={{ color: 'var(--text-primary)' }}>{formatCurrency(baselineCapital)}</strong></div>
              <div>Demand: <strong style={{ color: 'var(--text-primary)' }}>{formatCustomersPerDay(baselineCustomers)}</strong></div>
              <div>Unit Price: <strong style={{ color: 'var(--text-primary)' }}>LKR {baselinePrice}</strong></div>
            </div>
          </div>

          {/* Delta Shift Indicator */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '0.5rem' }}>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              gap: '0.35rem',
              background: viabilityDelta > 0.005 
                ? 'rgba(34, 197, 94, 0.15)' 
                : viabilityDelta < -0.005 
                  ? 'rgba(239, 68, 68, 0.15)' 
                  : 'rgba(59, 130, 246, 0.15)',
              border: `1px solid ${viabilityDelta > 0.005 ? 'rgba(34, 197, 94, 0.3)' : viabilityDelta < -0.005 ? 'rgba(239, 68, 68, 0.3)' : 'rgba(59, 130, 246, 0.3)'}`,
              padding: '0.75rem 1.15rem',
              borderRadius: '12px',
              minWidth: '155px'
            }}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                Viability Impact
              </div>
              <div style={{ 
                fontSize: '1.25rem', 
                fontWeight: 900, 
                display: 'flex', 
                alignItems: 'center', 
                gap: '0.35rem',
                color: viabilityDelta > 0.005 ? '#4ade80' : viabilityDelta < -0.005 ? '#fca5a5' : '#60a5fa'
              }}>
                {viabilityDelta > 0.005 && <TrendingUp size={18} />}
                {viabilityDelta < -0.005 && <TrendingDown size={18} />}
                {Math.abs(viabilityDelta) <= 0.005 && <Minus size={18} />}
                <span>{viabilityDelta > 0 ? `+${viabilityDeltaPct}%` : `${viabilityDeltaPct}%`}</span>
              </div>
              <span style={{ fontSize: '0.68rem', color: '#cbd5e1', textAlign: 'center' }}>
                {viabilityDelta > 0.005 ? 'Viability Enhanced' : viabilityDelta < -0.005 ? 'Risk Increased' : 'Unchanged'}
              </span>

              {/* Multi-Class Probability Shifts Breakdown */}
              {probDeltas && Object.keys(probDeltas).length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem', marginTop: '0.35rem', fontSize: '0.67rem', paddingTop: '0.35rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)', width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: (probDeltas.Feasible || 0) >= 0 ? '#4ade80' : '#fca5a5' }}>
                    <span>Feasible:</span>
                    <strong>{(probDeltas.Feasible || 0) >= 0 ? `+${((probDeltas.Feasible || 0) * 100).toFixed(1)}%` : `${((probDeltas.Feasible || 0) * 100).toFixed(1)}%`}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: (probDeltas['Conditionally Feasible'] || 0) >= 0 ? '#fde047' : '#fca5a5' }}>
                    <span>Conditional:</span>
                    <strong>{(probDeltas['Conditionally Feasible'] || 0) >= 0 ? `+${((probDeltas['Conditionally Feasible'] || 0) * 100).toFixed(1)}%` : `${((probDeltas['Conditionally Feasible'] || 0) * 100).toFixed(1)}%`}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: (probDeltas.Infeasible || 0) <= 0 ? '#4ade80' : '#fca5a5' }}>
                    <span>Infeasible:</span>
                    <strong>{(probDeltas.Infeasible || 0) >= 0 ? `+${((probDeltas.Infeasible || 0) * 100).toFixed(1)}%` : `${((probDeltas.Infeasible || 0) * 100).toFixed(1)}%`}</strong>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Modified Scenario Column */}
          <div style={{ 
            background: 'rgba(15, 23, 42, 0.9)', 
            border: `1px solid ${scenarioFeasibility ? 'rgba(59, 130, 246, 0.4)' : 'rgba(255, 255, 255, 0.08)'}`, 
            borderRadius: '10px', 
            padding: '1.1rem',
            position: 'relative'
          }}>
            {simulating && (
              <div style={{ position: 'absolute', top: '0.5rem', right: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.7rem', color: '#60a5fa' }}>
                <RefreshCw size={12} className="spin" /> Re-scoring...
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '0.75rem', color: '#60a5fa', fontWeight: 700, textTransform: 'uppercase' }}>
                Modified Scenario
              </span>
              <FeasibilityBadge label={scenarioLabel} showScore={false} size="sm" />
            </div>

            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
              {(scenarioScore * 100).toFixed(1)}% <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontWeight: 500 }}>Live Score</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.78rem', color: '#cbd5e1', paddingTop: '0.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Capital: <strong style={{ color: '#4ade80' }}>{formatCurrency(customCapital)}</strong></span>
                {customCapital !== baselineCapital && (
                  <span style={{ fontSize: '0.7rem', color: customCapital > baselineCapital ? '#4ade80' : '#fca5a5' }}>
                    {customCapital > baselineCapital ? `+${formatCurrency(customCapital - baselineCapital)}` : `-${formatCurrency(baselineCapital - customCapital)}`}
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Demand: <strong style={{ color: '#c084fc' }}>{formatCustomersPerDay(customCustomers)}</strong></span>
                {customCustomers !== baselineCustomers && (
                  <span style={{ fontSize: '0.7rem', color: customCustomers > baselineCustomers ? '#4ade80' : '#fca5a5' }}>
                    {customCustomers > baselineCustomers ? `+${customCustomers - baselineCustomers}/day` : `${customCustomers - baselineCustomers}/day`}
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Unit Price: <strong style={{ color: '#fde047' }}>LKR {customPrice}</strong></span>
                {customPrice !== baselinePrice && (
                  <span style={{ fontSize: '0.7rem', color: customPrice > baselinePrice ? '#4ade80' : '#fca5a5' }}>
                    {customPrice > baselinePrice ? `+LKR ${customPrice - baselinePrice}` : `-LKR ${baselinePrice - customPrice}`}
                  </span>
                )}
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Interactive Sliders Panel */}
      <div className="glass-card" style={{ border: '1px solid rgba(59, 130, 246, 0.35)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} style={{ color: '#60a5fa' }} />
            Dynamic Scenario Sliders
          </h4>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Move sliders to test resilience under different market conditions
          </span>
        </div>

        <div className="grid-2" style={{ gap: '1.25rem', marginBottom: '1.25rem' }}>
          
          {/* Slider 1: Capital */}
          <div className="form-group" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label" style={{ marginBottom: 0, fontWeight: 600 }}>
                Available Capital
              </label>
              <strong style={{ color: '#60a5fa', fontSize: '0.95rem' }}>{formatCurrency(customCapital)}</strong>
            </div>
            <input
              type="range"
              min="100000"
              max="5000000"
              step="50000"
              value={customCapital}
              onChange={(e) => setCustomCapital(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#3b82f6' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#64748b', marginTop: '0.25rem' }}>
              <span>LKR 100K</span>
              <span>Baseline: {formatCurrency(baselineCapital)}</span>
              <span>LKR 5.0M</span>
            </div>
          </div>

          {/* Slider 2: Customers */}
          <div className="form-group" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label" style={{ marginBottom: 0, fontWeight: 600 }}>
                Expected Customers / Day
              </label>
              <strong style={{ color: '#c084fc', fontSize: '0.95rem' }}>{customCustomers} customers/day</strong>
            </div>
            <input
              type="range"
              min="5"
              max="250"
              step="5"
              value={customCustomers}
              onChange={(e) => setCustomCustomers(parseInt(e.target.value, 10))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#a855f7' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#64748b', marginTop: '0.25rem' }}>
              <span>5 / day</span>
              <span>Baseline: {baselineCustomers} / day</span>
              <span>250 / day</span>
            </div>
          </div>

          {/* Slider 3: Price */}
          <div className="form-group" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label" style={{ marginBottom: 0, fontWeight: 600 }}>
                Expected Unit Price
              </label>
              <strong style={{ color: '#4ade80', fontSize: '0.95rem' }}>LKR {customPrice}</strong>
            </div>
            <input
              type="range"
              min="50"
              max="3500"
              step="25"
              value={customPrice}
              onChange={(e) => setCustomPrice(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#22c55e' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#64748b', marginTop: '0.25rem' }}>
              <span>LKR 50</span>
              <span>Baseline: LKR {baselinePrice}</span>
              <span>LKR 3,500</span>
            </div>
          </div>

          {/* Slider 4: Monthly Operating Budget */}
          <div className="form-group" style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label" style={{ marginBottom: 0, fontWeight: 600 }}>
                Monthly Operating Budget
              </label>
              <strong style={{ color: '#818cf8', fontSize: '0.95rem' }}>{formatCurrency(customBudget)}</strong>
            </div>
            <input
              type="range"
              min="30000"
              max="1500000"
              step="20000"
              value={customBudget}
              onChange={(e) => setCustomBudget(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#6366f1' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#64748b', marginTop: '0.25rem' }}>
              <span>LKR 30K</span>
              <span>Baseline: {formatCurrency(baselineBudget)}</span>
              <span>LKR 1.5M</span>
            </div>
          </div>

        </div>

        {/* Action & Manual Trigger Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.85rem', borderTop: '1px solid var(--border-color)', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
              * Evaluates updated inputs through trained Random Forest ML pipeline in real-time.
            </span>
            {isDifferentFromBaseline && (
              <button
                onClick={handleResetToBaseline}
                type="button"
                className="btn btn-secondary"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.78rem',
                  background: 'rgba(100, 116, 139, 0.2)',
                  border: '1px solid rgba(148, 163, 184, 0.3)',
                  color: '#cbd5e1',
                  borderRadius: '6px'
                }}
              >
                <RotateCcw size={13} />
                <span>Reset Sliders</span>
              </button>
            )}
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              onClick={() => runScenarioSimulation(customCapital, customBudget, customCustomers, customPrice)}
              disabled={simulating}
              className="btn btn-primary"
              style={{ padding: '0.55rem 1.15rem', fontSize: '0.825rem' }}
            >
              <RefreshCw size={15} className={simulating ? 'spin' : ''} />
              <span>{simulating ? 'Re-scoring Model...' : 'Calculate Scenario'}</span>
            </button>

            {isDifferentFromBaseline && (
              <button
                onClick={() => setShowConfirmModal(true)}
                disabled={simulating || isApplying}
                type="button"
                style={{
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  color: '#ffffff',
                  fontWeight: 700,
                  padding: '0.55rem 1.25rem',
                  fontSize: '0.825rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  borderRadius: '6px',
                  border: 'none',
                  cursor: isApplying ? 'not-allowed' : 'pointer',
                  boxShadow: '0 4px 14px rgba(16, 185, 129, 0.35)',
                  transition: 'all 0.2s ease'
                }}
              >
                <Check size={16} />
                <span>Apply This Scenario & Update Business Plan</span>
              </button>
            )}
          </div>
        </div>

        {errorMsg && (
          <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#fca5a5', fontSize: '0.8rem' }}>
            Simulation error: {errorMsg}
          </div>
        )}
      </div>

      {/* Alternative Business Scenarios */}
      {what_if_simulations.length > 0 && (
        <div>
          <div style={{ marginBottom: '1rem' }}>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={18} style={{ color: '#38bdf8' }} />
              <span>Alternative Business Scenarios</span>
            </h4>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', margin: '0.25rem 0 0 0' }}>
              See how common adjustments (like adding capital, taking a loan, or attracting more customers) would improve your business feasibility.
            </p>
          </div>

          <div className="grid-2" style={{ gap: '1rem' }}>
            {what_if_simulations.map((sim, idx) => {
              const deltas = sim.probability_deltas || {};
              const dInfeas = Math.round((deltas.Infeasible || 0) * 1000) / 10;
              const dFeas = Math.round((deltas.Feasible || 0) * 1000) / 10;
              const riskDrop = Math.abs(dInfeas);
              const isUpgraded = (baselineLabel === 'Infeasible' && sim.new_prediction !== 'Infeasible') ||
                                 (baselineLabel === 'Conditionally Feasible' && sim.new_prediction === 'Feasible');

              // Friendly explanation fallback if impact_summary contains raw statistical text
              let friendlyText = sim.impact_summary;
              if (!friendlyText || friendlyText.includes('Class probability shifts')) {
                if (sim.title?.includes('Capital')) {
                  friendlyText = `Adding 50% more capital extends your cash runway and buffers early operating expenses, reducing failure risk by ${riskDrop.toFixed(1)}%.`;
                } else if (sim.title?.includes('Loan')) {
                  friendlyText = `Securing an SME working loan provides immediate liquidity to purchase stock and manage daily cash flow, lowering risk by ${riskDrop.toFixed(1)}%.`;
                } else if (sim.title?.includes('Footfall') || sim.title?.includes('Customer')) {
                  friendlyText = `Attracting 30% more daily customers boosts daily sales revenue, trimming failure risk by ${riskDrop.toFixed(1)}%.`;
                } else if (sim.title?.includes('Operating Cost') || sim.title?.includes('Budget')) {
                  friendlyText = `Trimming monthly expenses by 20% lowers your daily break-even requirements, cutting risk by ${riskDrop.toFixed(1)}%.`;
                } else if (dInfeas <= -1.0) {
                  friendlyText = `This scenario reduces failure risk by ${riskDrop.toFixed(1)}% and improves overall business viability.`;
                } else {
                  friendlyText = `This adjustment helps stabilize operations, but additional capital or customer demand is recommended.`;
                }
              }

              // Determine badge text and color based on real impact
              let badgeText = 'Minimal Shift';
              let badgeBg = 'rgba(100, 116, 139, 0.15)';
              let badgeColor = '#94a3b8';
              let badgeBorder = 'rgba(100, 116, 139, 0.3)';

              if (dInfeas <= -1.0) {
                badgeText = `-${riskDrop.toFixed(1)}% Failure Risk`;
                badgeBg = 'rgba(34, 197, 94, 0.15)';
                badgeColor = '#4ade80';
                badgeBorder = 'rgba(34, 197, 94, 0.35)';
              } else if (dFeas >= 1.0) {
                badgeText = `+${dFeas.toFixed(1)}% Feasible`;
                badgeBg = 'rgba(56, 189, 248, 0.15)';
                badgeColor = '#38bdf8';
                badgeBorder = 'rgba(56, 189, 248, 0.35)';
              } else if (sim.viability_delta > 0.005) {
                badgeText = `+${(sim.viability_delta * 100).toFixed(1)}% Viability`;
                badgeBg = 'rgba(34, 197, 94, 0.15)';
                badgeColor = '#4ade80';
                badgeBorder = 'rgba(34, 197, 94, 0.35)';
              }

              return (
                <div key={idx} className="glass-card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '0.85rem' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.65rem' }}>
                      <span style={{ color: 'var(--text-primary)', fontSize: '0.92rem', fontWeight: 700, lineHeight: 1.3 }}>
                        {sim.title}
                      </span>
                      <span style={{ 
                        padding: '0.22rem 0.55rem', 
                        borderRadius: '6px', 
                        fontSize: '0.72rem', 
                        fontWeight: 700,
                        whiteSpace: 'nowrap',
                        background: badgeBg,
                        color: badgeColor,
                        border: `1px solid ${badgeBorder}`
                      }}>
                        {badgeText}
                      </span>
                    </div>

                    <p style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: 1.55, margin: 0 }}>
                      {friendlyText}
                    </p>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.78rem' }}>
                      <span style={{ color: '#94a3b8' }}>Expected Verdict:</span>
                      <span style={{ 
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        padding: '0.2rem 0.6rem',
                        borderRadius: '12px',
                        background: sim.new_prediction === 'Feasible' ? 'rgba(34, 197, 94, 0.15)' : sim.new_prediction === 'Conditionally Feasible' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        color: sim.new_prediction === 'Feasible' ? '#4ade80' : sim.new_prediction === 'Conditionally Feasible' ? '#fbbf24' : '#f87171',
                        border: `1px solid ${sim.new_prediction === 'Feasible' ? 'rgba(34, 197, 94, 0.3)' : sim.new_prediction === 'Conditionally Feasible' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
                      }}>
                        {isUpgraded ? `▲ Upgraded to ${sim.new_prediction}` : sim.new_prediction}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleApplyScenarioToSliders(sim)}
                      className="btn btn-secondary"
                      style={{ fontSize: '0.72rem', padding: '0.25rem 0.6rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                      title="Test this scenario in the interactive sliders above"
                    >
                      <Sliders size={12} />
                      <span>Test in Simulator</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Target Recommendation to Achieve Full Feasibility */}
      {counterfactual_boundary && counterfactual_boundary.recommendation && (
        <div className="glass-card" style={{ border: '1px solid rgba(99, 102, 241, 0.4)', background: 'rgba(49, 46, 129, 0.25)', padding: '1.25rem' }}>
          <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: '#a5b4fc', textTransform: 'uppercase', letterSpacing: '0.8px', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Sparkles size={16} style={{ color: '#818cf8' }} />
            Target Recommendation to Achieve Full Feasibility
          </h4>
          <p style={{ fontSize: '0.84rem', color: '#e2e8f0', lineHeight: '1.6', margin: 0 }}>
            {counterfactual_boundary.recommendation}
          </p>
        </div>
      )}

      {/* Confirmation Modal: Apply Scenario & Update Business Plan */}
      {showConfirmModal && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.78)',
            backdropFilter: 'blur(5px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1050,
            padding: '1rem'
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget && !isApplying) setShowConfirmModal(false);
          }}
        >
          <div 
            className="glass-card"
            style={{
              maxWidth: '540px',
              width: '100%',
              background: '#0f172a',
              border: '1.5px solid rgba(16, 185, 129, 0.5)',
              borderRadius: '16px',
              padding: '1.75rem',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
              animation: 'fadeIn 0.2s ease-out'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#34d399' }}>
                <Sparkles size={22} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                  Apply Scenario & Update Business Plan
                </h3>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  Component 1: Feasibility Analysis & Business Plan Generator
                </span>
              </div>
            </div>

            <p style={{ fontSize: '0.84rem', color: '#cbd5e1', lineHeight: '1.5', marginBottom: '1.25rem' }}>
              You are adopting this customized simulation scenario as your new business baseline. The system will permanently update your inputs, re-run the research pipeline, and regenerate your <strong>5-section Personalized Business Plan</strong>.
            </p>

            {/* Parameter Change Breakdown */}
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '10px', padding: '1rem', marginBottom: '1.25rem' }}>
              <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 700, letterSpacing: '0.5px', marginBottom: '0.75rem' }}>
                Baseline vs. New Scenario Parameters
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', fontSize: '0.82rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#94a3b8' }}>Available Capital:</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: '#64748b', textDecoration: customCapital !== baselineCapital ? 'line-through' : 'none' }}>
                      {formatCurrency(baselineCapital)}
                    </span>
                    {customCapital !== baselineCapital && (
                      <>
                        <ArrowRight size={12} style={{ color: '#10b981' }} />
                        <strong style={{ color: '#34d399' }}>{formatCurrency(customCapital)}</strong>
                      </>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#94a3b8' }}>Monthly Budget:</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: '#64748b', textDecoration: customBudget !== baselineBudget ? 'line-through' : 'none' }}>
                      {formatCurrency(baselineBudget)}
                    </span>
                    {customBudget !== baselineBudget && (
                      <>
                        <ArrowRight size={12} style={{ color: '#818cf8' }} />
                        <strong style={{ color: '#a5b4fc' }}>{formatCurrency(customBudget)}</strong>
                      </>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#94a3b8' }}>Daily Customers:</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: '#64748b', textDecoration: customCustomers !== baselineCustomers ? 'line-through' : 'none' }}>
                      {formatCustomersPerDay(baselineCustomers)}
                    </span>
                    {customCustomers !== baselineCustomers && (
                      <>
                        <ArrowRight size={12} style={{ color: '#38bdf8' }} />
                        <strong style={{ color: '#38bdf8' }}>{formatCustomersPerDay(customCustomers)}</strong>
                      </>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#94a3b8' }}>Expected Unit Price:</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ color: '#64748b', textDecoration: customPrice !== baselinePrice ? 'line-through' : 'none' }}>
                      LKR {baselinePrice}
                    </span>
                    {customPrice !== baselinePrice && (
                      <>
                        <ArrowRight size={12} style={{ color: '#4ade80' }} />
                        <strong style={{ color: '#4ade80' }}>LKR {customPrice}</strong>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                onClick={() => setShowConfirmModal(false)}
                disabled={isApplying}
                className="btn btn-secondary"
                type="button"
                style={{ padding: '0.6rem 1.25rem', fontSize: '0.85rem' }}
              >
                Cancel
              </button>
              <button
                onClick={handleApplyScenario}
                disabled={isApplying}
                type="button"
                style={{
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  color: '#ffffff',
                  fontWeight: 700,
                  border: 'none',
                  borderRadius: '6px',
                  padding: '0.6rem 1.4rem',
                  fontSize: '0.85rem',
                  cursor: isApplying ? 'not-allowed' : 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  boxShadow: '0 4px 15px rgba(16, 185, 129, 0.4)'
                }}
              >
                {isApplying ? (
                  <>
                    <RefreshCw size={15} className="spin" />
                    <span>Regenerating Business Plan...</span>
                  </>
                ) : (
                  <>
                    <Check size={16} />
                    <span>Confirm & Regenerate Business Plan</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
