import React, { useState } from 'react';
import './compliance.css';

// ---------------------------------------------------------------------------
// Types & Data Contracts
// ---------------------------------------------------------------------------

export type ApplicabilityStatus =
  | 'APPLICABLE'
  | 'UNKNOWN'
  | 'NOT_APPLICABLE'
  | 'NEEDS_VERIFICATION';

export interface ObligationResult {
  obligation_id: string;
  title: string;
  status: ApplicabilityStatus;
  classification: 'Mandatory' | 'Conditional' | 'Not Applicable' | 'Needs Verification';
  priority: 'high' | 'review' | 'none';
  triggering_facts: Record<string, unknown>;
  missing_facts: string[];
  applicability_conditions: Record<string, unknown>;
  exceptions: Array<{ description: string; source_id: string; confirmed: boolean }>;
  authority: string;
  explanation: string;
  action: string;
  registration_steps: string[];
  next_action: string;
  source_id: string;
  source_paragraph: string;
  source_text: string;
  documents_needed: string[];
  documents_notice: string;
  has_verified_source: boolean;
  evidence_quality?: string;
}

export interface FollowUpQuestion {
  fact: string;
  question_en: string;
  question_si: string;
  type: 'boolean' | 'select' | 'number' | 'text';
  options: (string | boolean | number)[];
}

export interface AnalysisSummary {
  total: number;
  applicable: number;
  not_applicable: number;
  unknown: number;
  needs_verification: number;
}

export interface LegalSourceExcerpt {
  source_id: string;
  title: string;
  authority: string | null;
  excerpt: string;
  url: string | null;
  page: number | null;
  retrieval_score: number;
  verification_status: string;
  title_is_filename_guess: boolean;
  section_reference?: string | null;
  paragraph_number?: number | null;
  file_type?: 'pdf' | 'txt' | null;
  action_guidance?: {
    rule_title: string;
    category: string;
    predicted_action_type: string;
    rule_purpose: string;
    where_to_go: string;
    office_location: string;
    action_needed: string;
    action_urgency: string;
    required_documents: string[];
    procedural_steps: string[];
  } | null;
}

export interface RegistrationStageItem {
  stage_number: number;
  title: string;
  title_si: string;
  authority: string;
  action: string;
  duration: string;
  statutory_fee: string;
}

export interface RegistrationDocumentItem {
  document_id: string;
  name: string;
  name_si: string;
  is_mandatory: boolean;
  purpose: string;
  status: 'READY' | 'ACTION_REQUIRED';
}

export interface FormFieldGuideItem {
  field_label: string;
  description: string;
  suggested_value: string;
}

export interface RegistrationGuidanceData {
  recommended_legal_form: string;
  pathway_key: 'sole_proprietorship' | 'partnership' | 'private_limited';
  legal_basis: string;
  governing_body: string;
  target_office: string;
  district: string;
  reasoning: string;
  official_form_name: string;
  estimated_fees: string;
  estimated_timeline: string;
  stages: RegistrationStageItem[];
  document_checklist: RegistrationDocumentItem[];
  form_fields_guide: FormFieldGuideItem[];
}

export interface ComplianceAnalysisResponse {
  summary: AnalysisSummary;
  obligations: ObligationResult[];
  follow_up_questions: FollowUpQuestion[];
  source_discovery: LegalSourceExcerpt[];
  action_roadmap?: {
    model_status: string;
    predicted_action_type: string;
    category: string;
    target_authority: string;
    office_location: string;
    required_action_name: string;
    action_urgency: string;
    required_documents: string[];
    procedural_steps: string[];
    governing_laws: string[];
    estimated_cost_lkr?: number;
    estimated_timeline_days?: number;
  } | null;
  registration_guidance?: RegistrationGuidanceData | null;
  evaluation_id: string;
  retrieval_mode: string;
  business_context: Record<string, unknown>;
  profile_validation: {
    complete: boolean;
    missing_required_fields: string[];
    note: string;
  };
  disclaimer: string;
}

export interface BusinessProfileForm {
  business_type?: 'food' | 'clothing' | 'salon' | 'vehicle_parts' | null;
  local_authority?: string | null;
  legal_form?: 'sole_proprietorship' | 'partnership' | 'private_limited' | 'other' | null;
  number_of_employees?: number | null;
  province?: string | null;
  district?: string | null;
  handles_food?: boolean | null;
  has_physical_premises?: boolean | null;
  is_manufacturing?: boolean | null;
  is_importing?: boolean | null;
  // Conditional fields
  serves_cooked_food?: boolean | null;
  sells_alcohol?: boolean | null;
  uses_chemicals_or_cosmetics?: boolean | null;
  handles_waste_oil_or_batteries?: boolean | null;
  turnover_band?: string | null;
  location?: string | null;
  products_services?: string[];
  business_size?: string | null;
}

// ---------------------------------------------------------------------------
// Constants & Metadata
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const STATUS_CONFIG: Record<
  ApplicabilityStatus,
  { label: string; color: string; bg: string; border: string; icon: string; badge: string }
> = {
  APPLICABLE: {
    label: 'Applicable',
    color: 'text-emerald-800',
    bg: 'bg-emerald-50/80',
    border: 'border-emerald-200',
    badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    icon: 'fa-circle-check',
  },
  UNKNOWN: {
    label: 'Conditional / Needs Review',
    color: 'text-amber-800',
    bg: 'bg-amber-50/70',
    border: 'border-amber-200',
    badge: 'bg-amber-100 text-amber-800 border-amber-300',
    icon: 'fa-circle-question',
  },
  NOT_APPLICABLE: {
    label: 'Not Applicable',
    color: 'text-slate-600',
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    badge: 'bg-slate-100 text-slate-700 border-slate-300',
    icon: 'fa-circle-minus',
  },
  NEEDS_VERIFICATION: {
    label: 'Needs Verification',
    color: 'text-amber-900',
    bg: 'bg-amber-50',
    border: 'border-amber-300',
    badge: 'bg-amber-100 text-amber-900 border-amber-400',
    icon: 'fa-triangle-exclamation',
  },
};

const FACT_DISPLAY_LABELS: Record<string, string> = {
  province: 'Province',
  district: 'District',
  business_type: 'Business Type',
  local_authority: 'Local Authority',
  legal_form: 'Legal Form',
  number_of_employees: 'Number of Employees',
  employee_band: 'Number of Employees',
  has_physical_premises: 'Physical Premises',
  handles_food: 'Handles Food',
  is_manufacturing: 'Manufacturing Operations',
  is_importing: 'Importing Goods',
  serves_cooked_food: 'Serves Cooked Food',
  sells_alcohol: 'Sells Alcohol',
  uses_chemicals_or_cosmetics: 'Uses Cosmetics/Chemicals',
  handles_waste_oil_or_batteries: 'Handles Waste Oil/Batteries',
  turnover_band: 'Turnover Band',
};

// Real sample profiles matching the 4 business types in Western Province
const SAMPLE_PROFILES: Record<string, BusinessProfileForm> = {
  clear_case: {
    business_type: 'food',
    province: 'Western Province',
    district: 'Colombo',
    local_authority: 'Colombo Municipal Council',
    legal_form: 'sole_proprietorship',
    number_of_employees: 4,
    has_physical_premises: true,
    handles_food: true,
    serves_cooked_food: true,
    sells_alcohol: false,
    is_manufacturing: false,
    is_importing: false,
    turnover_band: '1m_10m',
    location: 'Colombo',
    products_services: ['Prepared food', 'Bakery products'],
    business_size: 'small',
  },
  conditional_case: {
    business_type: 'vehicle_parts',
    province: 'Western Province',
    district: 'Colombo',
    local_authority: 'Colombo Municipal Council',
    legal_form: 'partnership',
    number_of_employees: 6,
    has_physical_premises: true,
    handles_food: false,
    is_manufacturing: false,
    is_importing: false,
    handles_waste_oil_or_batteries: true,
    turnover_band: '10m_50m',
    location: 'Colombo',
    products_services: ['Vehicle parts retail'],
    business_size: 'small',
  },
  missing_info_case: {
    business_type: 'food',
    province: 'Western Province',
    district: 'Colombo',
    local_authority: 'Colombo Municipal Council',
    legal_form: null,
    number_of_employees: null,
    has_physical_premises: null,
    handles_food: null,
    serves_cooked_food: null,
    sells_alcohol: null,
    is_manufacturing: null,
    is_importing: null,
    turnover_band: null,
    location: null,
    products_services: [],
    business_size: null,
  },
};

// ---------------------------------------------------------------------------
// API Helper
// ---------------------------------------------------------------------------

async function analyseComplianceAPI(profile: BusinessProfileForm): Promise<ComplianceAnalysisResponse> {
  const payload = Object.fromEntries(
    Object.entries(profile).map(([k, v]) => [k, v === undefined ? null : v])
  );

  const res = await fetch(`${API_BASE}/api/v1/component2/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to analyze compliance profile');
  }

  return res.json();
}

export interface ExtractedPlanResponse {
  success: boolean;
  filename: string;
  pages_count: number;
  is_scanned: boolean;
  ocr_used: boolean;
  character_count: number;
  extracted_profile: Record<string, any>;
  metadata: Record<string, any>;
  raw_text_preview: string;
}

export interface SamplePlanItem {
  id: string;
  title: string;
  category: string;
  sector: string;
  stage: string;
  location: string;
  strategy: string;
  filename: string;
  description: string;
}

async function uploadAndExtractPlanPDF(file: File): Promise<ExtractedPlanResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/v1/component2/extract-plan-pdf`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to extract business plan PDF');
  }

  return res.json();
}

async function extractSamplePlanAPI(sampleId: string): Promise<ExtractedPlanResponse> {
  const res = await fetch(`${API_BASE}/api/v1/component2/sample-plans/${sampleId}/extract`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to extract sample plan');
  }
  return res.json();
}

async function fetchSamplePlansListAPI(): Promise<SamplePlanItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/component2/sample-plans`);
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Bilingual Translation Dictionaries & Helpers for 5-Stage Roadmap
// ---------------------------------------------------------------------------

function stripSinhalaText(text?: string | null): string {
  if (!text) return '';
  return text.replace(/\s*\([\u0D80-\u0DFF\s\d\-./,]+\)/g, '').replace(/[\u0D80-\u0DFF]/g, '').trim();
}

function stripEnglishText(text?: string | null): string {
  if (!text) return '';
  return text.replace(/\s*\([a-zA-Z0-9\s\-./,]+\)/g, '').trim();
}

function getDistrictSinhala(dist?: string | null): string {
  if (!dist) return 'කොළඹ';
  const d = dist.toLowerCase();
  if (d.includes('colombo')) return 'කොළඹ';
  if (d.includes('gampaha')) return 'ගම්පහ';
  if (d.includes('kalutara')) return 'කළුතර';
  return 'බස්නාහිර පළාත';
}

interface StageTranslation {
  title_en: string;
  title_si: string;
  action_en: string;
  action_si: string;
  duration_en: string;
  duration_si: string;
  fee_en: string;
  fee_si: string;
}

const STAGE_TRANSLATIONS: Record<number, StageTranslation> = {
  1: {
    title_en: 'Business Name Availability & Scope Check',
    title_si: 'ව්‍යාපාර නාමය තහවුරු කරගැනීම (නම පරීක්ෂාව)',
    action_en: 'Verify that the proposed name does not conflict with existing registered businesses in the province and avoids restricted words.',
    action_si: 'යෝජිත ව්‍යාපාර නාමය පළාත තුළ දැනට ලියාපදිංචි කර ඇති වෙනත් ව්‍යාපාර සමඟ නොගැටෙන බව සහ රජයේ හෝ තහනම් වචන අඩංගු නොවන බව තහවුරු කර ගැනීම.',
    duration_en: '1 day',
    duration_si: 'දින 1',
    fee_en: 'Free / Stamp duty approx. LKR 100',
    fee_si: 'නොමිලේ / මුද්දර ගාස්තු රු. 100 පමණ',
  },
  2: {
    title_en: 'Grama Niladhari Verification & Proof of Premises',
    title_si: 'ග්‍රාම නිලධාරී වාර්තාව සහ පරිශ්‍රය තහවුරු කිරීම',
    action_en: 'Obtain Grama Niladhari residence & commercial operation report; compile title deed or valid lease agreement.',
    action_si: 'ව්‍යාපාරික ස්ථානයට අදාළ ග්‍රාම නිලධාරී පදිංචිය සහ ව්‍යාපාර වාර්තාව ලබාගැනීම; පරිශ්‍රයේ ඔප්පුව, වලංගු බදු ගිවිසුම හෝ විරෝධතාවක් නොමැති ලිපිය සූදානම් කරගැනීම.',
    duration_en: '1 - 2 days',
    duration_si: 'දින 1 - 2',
    fee_en: 'Nominal stamp duty',
    fee_si: 'නාමික මුද්දර ගාස්තු පමණි',
  },
  3: {
    title_en: 'Form 1 Application Lodgement',
    title_si: '1 වන ආකෘති පත්‍රය (Form 1) ඉදිරිපත් කිරීම',
    action_en: 'Submit completed Form 1 signed by owner/partners together with NIC copies and premises evidence.',
    action_si: 'හිමිකරු අත්සන් කළ සම්පූර්ණ කරන ලද 1 වන ආකෘති පත්‍රය, ජාතික හැඳුනුම්පත් පිටපත් සහ පරිශ්‍රයට අදාළ ලියකියවිලි සමඟ ප්‍රාදේශීය ලේකම් කාර්යාලයට භාරදීම.',
    duration_en: '1 day',
    duration_si: 'දින 1',
    fee_en: 'LKR 250 - 2,500 (depending on initial capital)',
    fee_si: 'රු. 250 - රු. 2,500 (මූලික ප්‍රාග්ධනය අනුව)',
  },
  4: {
    title_en: 'Issuance of Business Registration (BR) Certificate',
    title_si: 'ව්‍යාපාර ලියාපදිංචි සහතිකය (BR) නිකුත් කිරීම',
    action_en: 'Subject to officer verification, the official Business Registration Certificate under Statute No. 04 of 1990 is issued.',
    action_si: 'ලේඛන නිලධාරියා විසින් පරීක්ෂා කර තහවුරු කිරීමෙන් පසු, 1990 අංක 04 දරන බස්නාහිර පළාත් ප්‍රඥප්තිය යටතේ නිල ව්‍යාපාර ලියාපදිංචි සහතිකය නිකුත් කරනු ලැබේ.',
    duration_en: '1 - 3 business days',
    duration_si: 'වැඩකරන දින 1 - 3',
    fee_en: 'Included in initial payment',
    fee_si: 'මූලික ගෙවීමට ඇතුළත් කර ඇත',
  },
  5: {
    title_en: 'Post-Registration Mandatory Compliance',
    title_si: 'ලියාපදිංචියෙන් පසු අනිවාර්ය නීතිමය පියවර',
    action_en: 'Obtain business TIN from IRD, pay municipal trade tax / trade license, register employees with EPF/ETF within 14 days of hiring.',
    action_si: 'දේශීය ආදායම් දෙපාර්තමේන්තුවෙන් (IRD) ව්‍යාපාරික TIN අංකය ලබාගැනීම, පළාත් පාලන ආයතනයට වෙළඳ බද්ද ගෙවීම සහ සේවකයින් සිටී නම් දින 14ක් ඇතුළත EPF/ETF ලියාපදිංචි කිරීම.',
    duration_en: 'Within 14 - 30 days',
    duration_si: 'දින 14 - 30ක් ඇතුළත',
    fee_en: 'Varies by local authority trade tax schedule',
    fee_si: 'පළාත් පාලන ආයතනයේ වෙළඳ බදු ගාස්තු අනුව',
  },
};

const DOC_PURPOSE_SINHALA: Record<string, string> = {
  doc_nic: 'ශ්‍රී ලාංකික පුරවැසිභාවය සහ වයස අවුරුදු 18 සම්පූර්ණ බව තහවුරු කිරීමට.',
  doc_premises: 'බස්නාහිර පළාතේ දක්වා ඇති ලිපිනයේ නීත්‍යානුකූලව ව්‍යාපාරය පවත්වාගෙන යාමට ඇති අයිතිය තහවුරු කිරීමට.',
  doc_gn: '1990 අංක 04 දරන බස්නාහිර පළාත් ප්‍රඥප්තිය යටතේ අනන්‍යතාවය සහ ප්‍රදේශයේ නීත්‍යානුකූලභාවය තහවුරු කිරීමට අවශ්‍ය වේ.',
  doc_form1: 'ව්‍යාපාරය ලියාපදිංචි කිරීම සඳහා ඉදිරිපත් කරන ප්‍රධාන නිල ප්‍රකාශන අයදුම්පත.',
  doc_partnership_deed: 'හවුල්කරුවන් අතර ලාභ බෙදීයාම, ප්‍රාග්ධනය සහ වගකීම් පාලනය කරන ගිවිසුම.',
};

const FORM_GUIDE_SINHALA: Record<number, { label: string; desc: string }> = {
  0: {
    label: '1. යෝජිත ව්‍යාපාර නාමය',
    desc: 'නිවැරදි ව්‍යාපාර නාමය ඇතුළත් කරන්න. රැවටිලිසහගත හෝ රජයේ තහනම් වචන නොතිබිය යුතුය.',
  },
  1: {
    label: '2. ව්‍යාපාරයේ සාමාන්‍ය ස්වභාවය',
    desc: 'ප්‍රධාන වාණිජ කටයුතු පැහැදිලිව සඳහන් කරන්න (උදා. ආහාර හා බීම සිල්ලර වෙළඳාම, නිෂ්පාදනය, මෝටර් රථ සේවා).',
  },
  2: {
    label: '3. ප්‍රධාන ව්‍යාපාරික ස්ථානයේ ලිපිනය',
    desc: 'බස්නාහිර පළාත තුළ ව්‍යාපාරික මෙහෙයුම් සහ පොත්පත් තබන නිවැරදි භෞතික ලිපිනය.',
  },
  3: {
    label: '4. ව්‍යාපාරය ආරම්භ කළ හෝ ආරම්භ කරන දිනය',
    desc: '1990 අංක 04 දරන ප්‍රඥප්තියේ 7 වන වගන්තිය යටතේ ලියාපදිංචියට දින 14කට පෙර හෝ ලියාපදිංචි වන අවස්ථාව විය යුතුය.',
  },
  4: {
    label: '5. යොදවන ලද ආරම්භක ප්‍රාග්ධනය',
    desc: 'ශ්‍රී ලංකා රුපියල් වලින් මුළු ආරම්භක ප්‍රාග්ධනය (පළාත් මුද්දර ගාස්තු තීරණය වන්නේ මෙම අගය මතය).',
  },
};

// ---------------------------------------------------------------------------
// Bilingual Translation Dictionaries & Helpers for Rules & Institutional Actions
// ---------------------------------------------------------------------------

const RULE_PURPOSE_SINHALA: Record<string, string> = {
  food_business:
    'ආහාර සකස් කිරීම, පරිහරණය හෝ මහජනතාවට අලෙවි කිරීමට පෙර පරිශ්‍රයේ සනීපාරක්ෂාව, සෞඛ්‍ය ප්‍රමිතීන් සහ ආහාර හසුරුවන්නන්ගේ වෛද්‍ය යෝග්‍යතාව නියාමනය කිරීම.',
  environmental_waste:
    'මධ්‍යම පරිසර අධිකාරිය යටතේ පරිසර දූෂණය වැළැක්වීම සඳහා කාර්මික විමෝචන, අපද්‍රව්‍ය බැහැර කිරීම, අපජල පිරිපහදු කිරීම සහ පාරිසරික අනුමැතීන් නියාමනය කිරීම.',
  business_registration:
    'තනි පුද්ගල ව්‍යාපාර, හවුල් ව්‍යාපාර හෝ සමාගම් සඳහා නීතිමය අනන්‍යතාවය තහවුරු කිරීම සහ බැංකු ගිණුම් විවෘත කිරීමට හා වාණිජ බිල්පත් නිකුත් කිරීමට අවශ්‍ය ලියාපදිංචිය ලබාදීම.',
  vehicle_repair_motor_trade:
    'මෝටර් රථ ගරාජ් මෙහෙයුම්, අමතර කොටස් අලෙවිය සහ අපද්‍රව්‍ය තෙල් බැහැර කිරීම පළාත් පාලන අතුරු ව්‍යවස්ථා සහ මෝටර් රථ ප්‍රවාහන මාර්ගෝපදේශ යටතේ නියාමනය කිරීම.',
  cosmetics_salon:
    'රූපලාවන්‍ය රසායනික භාවිතය, සම/කොණ්ඩය ආශ්‍රිත ආරක්ෂාව සහ උපකරණ විෂබීජහරණය කිරීම NMRA සහ මහ නගර සභා සෞඛ්‍ය අතුරු ව්‍යවස්ථා යටතේ නියාමනය කිරීම.',
  data_protection_digital:
    '2022 අංක 09 දරන පුද්ගලික දත්ත ආරක්ෂණ පනත යටතේ පාරිභෝගික පුද්ගලික දත්ත, මාර්ගගත ඇණවුම් සහ සේවක තොරතුරු නීත්‍යානුකූලව සැකසීම හා සුරක්ෂිත කිරීම.',
};

function getRulePurposeText(purpose: string, category?: string, isSi?: boolean): string {
  if (!isSi) return purpose;
  if (category && RULE_PURPOSE_SINHALA[category]) {
    return RULE_PURPOSE_SINHALA[category];
  }
  return purpose;
}

function getWhereToGoText(targetAuth: string, isSi?: boolean): string {
  if (!isSi) return targetAuth;
  const s = targetAuth.toLowerCase();
  if (s.includes('public health') || s.includes('phi') || s.includes('health department')) {
    return 'මහජන සෞඛ්‍ය දෙපාර්තමේන්තුව / මහජන සෞඛ්‍ය පරීක්ෂක (PHI) කාර්යාලය / සෞඛ්‍ය වෛද්‍ය නිලධාරී (MOH) කාර්යාලය';
  }
  if (s.includes('central environmental') || s.includes('cea')) {
    return 'මධ්‍යම පරිසර අධිකාරිය (CEA) / පළාත් පාලන ආයතනයේ පාරිසරික අංශය';
  }
  if (s.includes('divisional secretariat') || s.includes('registrar of companies') || s.includes('eroc')) {
    return 'ප්‍රාදේශීය ලේකම් කාර්යාලය / සමාගම් රෙජිස්ට්‍රාර් දෙපාර්තමේන්තුව (eROC)';
  }
  if (s.includes('motor traffic') || s.includes('dmt')) {
    return 'මෝටර් රථ ප්‍රවාහන දෙපාර්තමේන්තුව (DMT) / ප්‍රාදේශීය සභා වෙළඳ අංශය';
  }
  if (s.includes('medicines') || s.includes('nmra')) {
    return 'ජාතික ඖෂධ නියාමන අධිකාරිය (NMRA) / නගර සභා සෞඛ්‍ය අංශය';
  }
  if (s.includes('data protection') || s.includes('dpa')) {
    return 'ශ්‍රී ලංකා දත්ත ආරක්ෂණ අධිකාරිය (DPA SL)';
  }
  return targetAuth;
}

function getOfficeLocationText(officeLoc: string, isSi?: boolean): string {
  if (!isSi || !officeLoc) return officeLoc;
  return officeLoc
    .replace(/Divisional Secretariat/gi, 'ප්‍රාදේශීය ලේකම් කාර්යාලය')
    .replace(/Registrar of Companies \(eROC\), Colombo 10/gi, 'සමාගම් රෙජිස්ට්‍රාර් දෙපාර්තමේන්තුව (eROC), කොළඹ 10')
    .replace(/Central Environmental Authority/gi, 'මධ්‍යම පරිසර අධිකාරිය')
    .replace(/Head Office Battaramulla/gi, 'ප්‍රධාන කාර්යාලය බත්තරමුල්ල')
    .replace(/District Office/gi, 'දිස්ත්‍රික් කාර්යාලය')
    .replace(/Department of Motor Traffic/gi, 'මෝටර් රථ ප්‍රවාහන දෙපාර්තමේන්තුව')
    .replace(/Local Council Trade Unit/gi, 'ප්‍රාදේශීය සභා වෙළඳ අංශය')
    .replace(/National Medicines Regulatory Authority/gi, 'ජාතික ඖෂධ නියාමන අධිකාරිය')
    .replace(/Local Council Health Dept/gi, 'පළාත් පාලන සෞඛ්‍ය අංශය')
    .replace(/Colombo/gi, 'කොළඹ')
    .replace(/Gampaha/gi, 'ගම්පහ')
    .replace(/Kalutara/gi, 'කළුතර');
}

function getActionNeededText(action: string, isSi?: boolean): string {
  if (!isSi) return action;
  const s = action.toLowerCase();
  if (s.includes('food premises') || s.includes('food-safety')) {
    return 'ආහාර පරිශ්‍ර ලියාපදිංචිය / වෙළඳ බලපත්‍ර අනුමැතිය සහ සෞඛ්‍ය නිෂ්කාශනය';
  }
  if (s.includes('environmental protection licence') || s.includes('epl')) {
    return 'පාරිසරික ආරක්ෂණ බලපත්‍රය (EPL) හෝ අදාළ පාරිසරික නිෂ්කාශන අනුමැතිය';
  }
  if (s.includes('business registration') || s.includes('company incorporation')) {
    return 'ව්‍යාපාර නාම ලියාපදිංචිය හෝ සමාගම් සංස්ථාගත කිරීමේ ලේඛන';
  }
  if (s.includes('motor trade') || s.includes('garage')) {
    return 'මෝටර් රථ අලුත්වැඩියා / ගරාජ් වෙළඳ බලපත්‍රය සහ පාරිසරික අනුමැතිය';
  }
  if (s.includes('salon') || s.includes('cosmetic')) {
    return 'රූපලාවන්‍යාගාර සෞඛ්‍ය ලියාපදිංචිය සහ NMRA නිෂ්පාදන අනුකූලතාව';
  }
  if (s.includes('data protection')) {
    return 'පාරිභෝගික දත්ත ආරක්ෂණ ක්‍රමවේද සහ ප්‍රතිපත්ති අනුකූලතාව';
  }
  return action;
}

const DOCUMENT_TRANSLATIONS: Record<string, string> = {
  'Business and premises details': 'ව්‍යාපාරය සහ පරිශ්‍රය පිළිබඳ මූලික තොරතුරු',
  'Description of food preparation, storage and sale activities': 'ආහාර පිළියෙල කිරීම, ගබඩා කිරීම සහ අලෙවි කිරීම පිළිබඳ විස්තර',
  'Premises/layout information if requested by the official checklist': 'පරිශ්‍රයේ බිම් සැලැස්ම (Floor / Layout Plan)',
  'Food-handler or hygiene evidence only if required by current rules': 'ආහාර හසුරුවන්නන්ගේ වෛද්‍ය යෝග්‍යතා වාර්තා / සෞඛ්‍ය සහතික',
  'Current official application form': 'නියමිත නිල අයදුම්පත',
  'Exact activity/process description and scale': 'නිශ්චිත කාර්මික ක්‍රියාවලිය සහ පරිමාණය පිළිබඳ විස්තරය',
  'Premises location and site information': 'ස්ථානය සහ පරිශ්‍රයට අදාළ පිහිටුම් විස්තර',
  'Wastewater, emissions, noise and waste-handling details where relevant': 'අපජලය, ශබ්ද විමෝචන සහ අපද්‍රව්‍ය කළමනාකරණ සැලැස්ම',
  'Current official application/checklist only after confirming the applicable pathway': 'අදාළ මාර්ගය තහවුරු කරගත් පසු නිල අයදුම්පත සහ ලේඛන ලැයිස්තුව',
  'National Identity Card (NIC) / Business Registration Certificate': 'ජාතික හැඳුනුම්පත (NIC) හෝ ව්‍යාපාර ලියාපදිංචි සහතිකයේ පිටපතක්',
  'Proof of premises (Lease Agreement or Title Deed)': 'පරිශ්‍රය තහවුරු කිරීමේ ලියකියවිලි (බදු ගිවිසුම හෝ ඔප්පුව)',
  'Official Application Form with prescribed processing fee': 'නියමිත ගාස්තුව සමඟ සම්පූර්ණ කරන ලද නිල අයදුම්පත',
};

function getDocumentText(doc: string, isSi?: boolean): string {
  if (!isSi) return doc;
  return DOCUMENT_TRANSLATIONS[doc] || doc;
}

const STEP_TRANSLATIONS: Record<string, string> = {
  'Describe the food activities and premises accurately.': 'ආහාර මෙහෙයුම් සහ පරිශ්‍රය නිවැරදිව වාර්තා කරන්න.',
  'Obtain the current food-premises checklist from the competent local authority/public-health office.': 'අදාළ පළාත් පාලන ආයතනයෙන් හෝ මහජන සෞඛ්‍ය පරීක්ෂක කාර්යාලයෙන් වත්මන් ලේඛන ලැයිස්තුව ලබාගන්න.',
  'Confirm required inspections, food-handler conditions and forms.': 'අවශ්‍ය පරික්ෂණ, සෞඛ්‍ය වාර්තා සහ අයදුම්පත් තහවුරු කරගන්න.',
  'Prepare only the documents listed in the verified checklist.': 'තහවුරු කරන ලද ලැයිස්තුවේ ඇති ලියකියවිලි පමණක් සම්පූර්ණ කරන්න.',
  'Submit the application and follow inspection or correction instructions.': 'අයදුම්පත භාරදී පරීක්ෂණ නිලධාරියාගේ උපදෙස් අනුගමනය කරන්න.',
  'Record the exact activity, process, scale and premises.': 'නිශ්චිත ක්‍රියාවලිය, පරිමාණය සහ පරිශ්‍රයේ තොරතුරු සටහන් කරන්න.',
  'Compare the activity with the current official prescribed-activity list and applicable regulations.': 'ක්‍රියාවලිය නිල නියමිත ක්‍රියාකාරකම් ලැයිස්තුව සමඟ සසඳන්න.',
  'Confirm the competent authority and licence/approval category.': 'බලධාරී ආයතනය සහ අවශ්‍ය බලපත්‍ර කාණ්ඩය තහවුරු කරගන්න.',
  'Obtain the current application and document checklist.': 'වත්මන් අයදුම්පත සහ ලේඛන පිරික්සුම් ලැයිස්තුව ලබාගන්න.',
  'Submit only if the verified rules require it and retain the decision/evidence.': 'නීත්‍යානුකූලව අවශ්‍ය නම් පමණක් අයදුම්පත යොමු කර තීරණය සුරක්ෂිතව තබාගන්න.',
  'Step 1: Obtain official prescribed application form from the responsible office.': 'පියවර 1: අදාළ කාර්යාලයෙන් නියමිත නිල අයදුම්පත ලබාගන්න.',
  'Step 2: Compile necessary premises proofs, layout sketch, and identification.': 'පියවර 2: අවශ්‍ය පරිශ්‍ර සාක්ෂි, බිම් සැලැස්ම සහ හැඳුනුම්පත් සූදානම් කරන්න.',
  'Step 3: Submit application for officer inspection / clearance.': 'පියවර 3: නිලධාරී පරීක්ෂාව සහ නිෂ්කාශනය සඳහා අයදුම්පත ඉදිරිපත් කරන්න.',
  'Step 4: Pay regulatory inspection fees and collect official licence / certificate.': 'පියවර 4: නියමිත ගාස්තු ගෙවා නිල බලපත්‍රය හෝ සහතිකය ලබාගන්න.',
};

function getStepText(step: string, isSi?: boolean): string {
  if (!isSi) return step;
  return STEP_TRANSLATIONS[step] || step;
}

// ---------------------------------------------------------------------------
// Sub-components: Badges, Controls, Cards
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: ApplicabilityStatus }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.UNKNOWN;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${cfg.badge}`}
    >
      <i className={`fa-solid ${cfg.icon} text-xs`} />
      {cfg.label}
    </span>
  );
}

function InlineAnswerControl({
  factKey,
  onAnswer,
}: {
  factKey: string;
  onAnswer: (key: keyof BusinessProfileForm, value: unknown) => void;
}) {
  const label = FACT_DISPLAY_LABELS[factKey] || factKey;

  // Decide if boolean or selection
  const isSelect = factKey === 'turnover_band' || factKey === 'legal_form' || factKey === 'local_authority' || factKey === 'business_type';

  return (
    <div className="bg-amber-100/60 border border-amber-300/80 rounded-lg p-2.5 flex flex-wrap items-center justify-between gap-2 text-xs">
      <span className="font-semibold text-amber-900 flex items-center gap-1.5">
        <i className="fa-solid fa-circle-question text-amber-600" />
        {label}?
      </span>

      {!isSelect && factKey !== 'number_of_employees' && factKey !== 'employee_band' ? (
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => onAnswer(factKey as keyof BusinessProfileForm, true)}
            className="px-2.5 py-1 bg-white hover:bg-emerald-50 text-emerald-700 font-semibold border border-emerald-300 rounded shadow-xs transition-colors"
          >
            Yes
          </button>
          <button
            type="button"
            onClick={() => onAnswer(factKey as keyof BusinessProfileForm, false)}
            className="px-2.5 py-1 bg-white hover:bg-rose-50 text-rose-700 font-semibold border border-rose-300 rounded shadow-xs transition-colors"
          >
            No
          </button>
          <button
            type="button"
            onClick={() => onAnswer(factKey as keyof BusinessProfileForm, null)}
            className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-600 font-semibold border border-slate-300 rounded transition-colors"
          >
            Not sure
          </button>
        </div>
      ) : factKey === 'number_of_employees' || factKey === 'employee_band' ? (
        <input
          type="number"
          min="0"
          placeholder="Enter number..."
          onBlur={(e) => {
            if (e.target.value !== '') onAnswer('number_of_employees', Number(e.target.value));
          }}
          className="w-32 border border-amber-300 bg-white rounded px-2 py-1 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-amber-500"
        />
      ) : factKey === 'turnover_band' ? (
        <select
          onChange={(e) => onAnswer('turnover_band', e.target.value)}
          defaultValue=""
          className="border border-amber-300 bg-white rounded px-2 py-1 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-amber-500"
        >
          <option value="">Not sure (keep unknown)</option>
          <option value="under_1m">Under LKR 1 Million</option>
          <option value="1m_10m">LKR 1M – 10M</option>
          <option value="10m_50m">LKR 10M – 50M</option>
          <option value="over_50m">Over LKR 50 Million</option>
        </select>
      ) : factKey === 'legal_form' ? (
        <select
          onChange={(e) => onAnswer('legal_form', e.target.value)}
          defaultValue=""
          className="border border-amber-300 bg-white rounded px-2 py-1 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-amber-500"
        >
          <option value="">Not sure (keep unknown)</option>
          <option value="sole_proprietorship">Sole Proprietorship</option>
          <option value="partnership">Partnership</option>
          <option value="private_limited">Private Limited</option>
        </select>
      ) : factKey === 'local_authority' ? (
        <select
          onChange={(e) => onAnswer('local_authority', e.target.value || null)}
          defaultValue=""
          className="border border-amber-300 bg-white rounded px-2 py-1 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-amber-500"
        >
          <option value="">Not sure (keep unknown)</option>
          <option value="Colombo Municipal Council">Colombo Municipal Council</option>
          <option value="Sri Jayawardenepura Kotte Municipal Council">Kotte Municipal Council</option>
          <option value="Dehiwala-Mount Lavinia Municipal Council">Dehiwala-Mount Lavinia Municipal Council</option>
          <option value="Moratuwa Municipal Council">Moratuwa Municipal Council</option>
        </select>
      ) : factKey === 'business_type' ? (
        <select
          onChange={(e) => onAnswer('business_type', e.target.value || null)}
          defaultValue=""
          className="border border-amber-300 bg-white rounded px-2 py-1 text-xs text-slate-700 focus:outline-none focus:ring-1 focus:ring-amber-500"
        >
          <option value="">Not sure (keep unknown)</option>
          <option value="food">Food</option>
          <option value="clothing">Clothing</option>
          <option value="salon">Salon</option>
          <option value="vehicle_parts">Vehicle parts</option>
        </select>
      ) : null}
    </div>
  );
}

function ObligationCard({
  obl,
  onAnswerMissingFact,
  onOpenEvidence,
}: {
  obl: ObligationResult;
  onAnswerMissingFact: (key: keyof BusinessProfileForm, value: unknown) => void;
  onOpenEvidence: (obligationId: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const cfg = STATUS_CONFIG[obl.status] || STATUS_CONFIG.UNKNOWN;

  return (
    <div className={`border ${cfg.border} rounded-2xl overflow-hidden bg-white shadow-xs transition-all`}>
      {/* Header */}
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className={`w-full flex items-center gap-3 px-5 py-4 ${cfg.bg} text-left hover:brightness-95 transition-all`}
      >
        <i className={`fa-solid ${cfg.icon} ${cfg.color} text-lg`} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-bold text-slate-900 truncate">{obl.title}</p>
          <p className="text-xs text-slate-500 mt-0.5">
            <span className="font-semibold text-slate-700">{obl.authority}</span> &middot; ID: <span className="font-mono">{obl.obligation_id}</span>
          </p>
          <p className="text-[11px] text-slate-500 mt-1">
            Classification: <span className="font-semibold">{obl.classification}</span>
            {' · '}Priority: <span className="font-semibold">{obl.priority}</span>
          </p>
        </div>
        <StatusBadge status={obl.status} />
        <i
          className={`fa-solid ${expanded ? 'fa-chevron-up' : 'fa-chevron-down'} text-slate-400 text-xs ml-2`}
        />
      </button>

      {/* Expanded details */}
      {expanded && (
        <div className="px-5 py-4 bg-white space-y-4 text-xs border-t border-slate-100">
          {/* Why it applies / Triggering facts */}
          <div>
            <p className="font-semibold text-slate-500 uppercase tracking-wide text-[11px] mb-1.5">
              {obl.status === 'APPLICABLE' ? 'Why It Applies (Triggering Facts)' : 'Evaluated Facts'}
            </p>
            {Object.keys(obl.triggering_facts).length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(obl.triggering_facts).map(([k, v]) => (
                  <span
                    key={k}
                    className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-100 text-slate-800 border border-slate-200"
                  >
                    <strong>{FACT_DISPLAY_LABELS[k] || k}:</strong> {String(v)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 italic">No positive triggering facts evaluated.</p>
            )}
          </div>

          {/* Missing Facts & Inline Controls */}
          {obl.missing_facts.length > 0 && (
            <div className="p-3.5 bg-amber-50/60 rounded-xl border border-amber-200 space-y-2">
              <p className="font-semibold text-amber-900 text-xs flex items-center gap-1.5">
                <i className="fa-solid fa-bolt text-amber-600" />
                Missing Facts &mdash; Answer inline to re-evaluate:
              </p>
              <div className="space-y-1.5">
                {obl.missing_facts.map((factKey) => (
                  <InlineAnswerControl
                    key={factKey}
                    factKey={factKey}
                    onAnswer={onAnswerMissingFact}
                  />
                ))}
              </div>
            </div>
          )}

          {(Object.keys(obl.applicability_conditions).length > 0 || obl.exceptions.length > 0) && (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 space-y-2">
              {Object.keys(obl.applicability_conditions).length > 0 && (
                <div>
                  <p className="font-semibold text-slate-600 uppercase tracking-wide text-[11px] mb-1">
                    Rulebook applicability conditions
                  </p>
                  <ul className="list-disc pl-5 space-y-1 text-slate-700">
                    {Object.entries(obl.applicability_conditions).map(([key, value]) => (
                      <li key={key}><strong>{FACT_DISPLAY_LABELS[key] || key}:</strong> {String(value)}</li>
                    ))}
                  </ul>
                </div>
              )}
              {obl.exceptions.length > 0 && (
                <div>
                  <p className="font-semibold text-slate-600 uppercase tracking-wide text-[11px] mb-1">
                    Recorded exceptions
                  </p>
                  <ul className="list-disc pl-5 space-y-1 text-slate-700">
                    {obl.exceptions.map((exception, index) => (
                      <li key={`${exception.source_id}-${index}`}>
                        {exception.description} — {exception.confirmed ? 'reviewed' : 'not verified'}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <p className="text-[11px] text-slate-500">
                These are rulebook records and are not legal determinations unless their source is verified.
              </p>
            </div>
          )}

          {/* Required Action */}
          <div>
            <p className="font-semibold text-slate-500 uppercase tracking-wide text-[11px]">
              {obl.status === 'NEEDS_VERIFICATION' ? 'Verification Required' : 'Rulebook Action'}
            </p>
            <p className="text-xs text-slate-800 mt-1 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              {obl.action || (
                obl.status === 'NEEDS_VERIFICATION'
                  ? 'No compliance action is recommended until the source and requirement are verified.'
                  : 'Confirm the current procedure with the responsible authority.'
              )}
            </p>
            <p className="text-xs text-slate-600 mt-2">{obl.explanation}</p>
            <p className="text-xs font-semibold text-blue-800 mt-2">Next action: {obl.next_action}</p>
          </div>

          {obl.registration_steps.length > 0 && (
            <div>
              <p className="font-semibold text-slate-500 uppercase tracking-wide text-[11px] mb-1.5">
                {obl.status === 'NEEDS_VERIFICATION' ? 'Verification step' : 'Registration Guidance'}
              </p>
              <ol className="list-decimal pl-5 space-y-1 text-slate-700">
                {obl.registration_steps.map((step, index) => <li key={index}>{step}</li>)}
              </ol>
            </div>
          )}

          {/* Documents Needed */}
          {obl.documents_needed && obl.documents_needed.length > 0 && (
            <div>
              <p className="font-semibold text-slate-500 uppercase tracking-wide text-[11px] mb-1.5">
                Required Application Documents
              </p>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                {obl.documents_needed.map((doc, i) => (
                  <li
                    key={i}
                    className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg border border-slate-100 text-slate-700"
                  >
                    <i className="fa-solid fa-file-lines text-blue-500 text-xs shrink-0" />
                    <span>{doc}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {obl.documents_notice && (
            <p className="text-xs text-amber-800 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
              {obl.documents_notice}
            </p>
          )}

          {/* Statutory Source Citation & Excerpt */}
          <div className="border-t border-slate-100 pt-3 space-y-1.5">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-slate-500 uppercase tracking-wide text-[11px]">
                Rulebook Source Reference
              </p>
              <span className="font-mono text-[11px] text-slate-500">
                {obl.source_id} &middot; {obl.source_paragraph}
              </span>
            </div>
            <p className="text-[11px] text-amber-800">
              Evidence status: {obl.has_verified_source ? 'verified' : 'draft / not independently verified'}
            </p>
            {obl.source_text ? (
              <blockquote className="border-l-2 border-blue-500 bg-blue-50/40 p-2.5 rounded-r-lg text-slate-700 italic leading-relaxed text-xs">
                &ldquo;{obl.source_text}&rdquo;
              </blockquote>
            ) : (
              <p className="text-xs text-slate-500">
                No matching source excerpt is available in the local corpus.
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={() => onOpenEvidence(obl.obligation_id)}
            className="w-full rounded-lg border border-blue-200 bg-blue-50 px-3 py-2.5 text-left text-xs font-semibold text-blue-800 transition hover:border-blue-300 hover:bg-blue-100"
          >
            <i className="fa-solid fa-book-open mr-2" />
            Open evidence details
            <i className="fa-solid fa-arrow-right float-right mt-0.5" />
          </button>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Dashboard Component
// ---------------------------------------------------------------------------

export const RegistrationComplianceDashboard: React.FC = () => {
  // Every field defaults to null/undefined (Unknown)
  const [profile, setProfile] = useState<BusinessProfileForm>({
    business_type: null,
    local_authority: null,
    legal_form: null,
    number_of_employees: null,
    province: 'Western Province', // Fixed scope
    district: null,
    handles_food: null,
    has_physical_premises: null,
    is_manufacturing: null,
    is_importing: null,
    serves_cooked_food: null,
    sells_alcohol: null,
    uses_chemicals_or_cosmetics: null,
    handles_waste_oil_or_batteries: null,
    turnover_band: null,
    location: null,
    products_services: [],
    business_size: null,
  });

  const [result, setResult] = useState<ComplianceAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<'profile' | 'results' | 'evidence'>('profile');
  const [selectedObligationId, setSelectedObligationId] = useState('');
  const [resultFilter, setResultFilter] = useState<'all' | ApplicabilityStatus>('all');
  const [showManualForm, setShowManualForm] = useState(false);
  const [guidanceLanguage, setGuidanceLanguage] = useState<'en' | 'si'>('en');
  const [rulesLanguage, setRulesLanguage] = useState<'en' | 'si'>('en');
  const [resultsSubTab, setResultsSubTab] = useState<'roadmap' | 'registration' | 'legal_rules'>('roadmap');

  // PDF Business / Growth Plan Ingestion State
  const [pdfUploading, setPdfUploading] = useState(false);
  const [pdfExtractResult, setPdfExtractResult] = useState<ExtractedPlanResponse | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const [samplePlans, setSamplePlans] = useState<SamplePlanItem[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [extractedProfileEdit, setExtractedProfileEdit] = useState<any | null>(null);
  const [newProductTag, setNewProductTag] = useState('');
  const [isDownloadingDossier, setIsDownloadingDossier] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  // Load available sample business plans on mount
  React.useEffect(() => {
    fetchSamplePlansListAPI().then(setSamplePlans);
  }, []);

  const handleDownloadDossier = async () => {
    if (!result) return;
    setIsDownloadingDossier(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/component2/download-compliance-dossier`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result),
      });
      if (!res.ok) throw new Error('Failed to generate compliance dossier');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `SME_Compliance_Registration_Dossier_${result.registration_guidance?.district || 'WP'}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('Failed to download compliance dossier PDF');
    } finally {
      setIsDownloadingDossier(false);
    }
  };



  const handlePdfFile = async (file: File) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setPdfError('Please upload a valid PDF document (.pdf).');
      return;
    }
    setPdfUploading(true);
    setPdfError(null);
    try {
      const data = await uploadAndExtractPlanPDF(file);
      const cleanProducts = (data.extracted_profile?.products_services || []).filter(
        (p: string) => p && !/page break|filing date|\bdate\b|---|\d{4,}/i.test(p) && p.trim().length >= 3
      );
      setPdfExtractResult(data);
      setExtractedProfileEdit({ ...data.extracted_profile, products_services: cleanProducts });
    } catch (err: any) {
      setPdfError(err.message || 'Failed to process business plan PDF');
    } finally {
      setPdfUploading(false);
    }
  };

  const handleSelectSamplePlan = async (sampleId: string) => {
    setPdfUploading(true);
    setPdfError(null);
    try {
      const data = await extractSamplePlanAPI(sampleId);
      const cleanProducts = (data.extracted_profile?.products_services || []).filter(
        (p: string) => p && !/page break|filing date|\bdate\b|---|\d{4,}/i.test(p) && p.trim().length >= 3
      );
      setPdfExtractResult(data);
      setExtractedProfileEdit({ ...data.extracted_profile, products_services: cleanProducts });
    } catch (err: any) {
      setPdfError(err.message || 'Failed to load sample business plan');
    } finally {
      setPdfUploading(false);
    }
  };

  const handleConfirmExtractedProfile = () => {
    if (!extractedProfileEdit) return;

    const confirmed: BusinessProfileForm = {
      business_type: extractedProfileEdit.business_type || 'food',
      province: extractedProfileEdit.province || 'Western Province',
      district: extractedProfileEdit.district || 'Colombo',
      local_authority: extractedProfileEdit.local_authority || 'Colombo Municipal Council',
      legal_form: extractedProfileEdit.legal_form || 'sole_proprietorship',
      number_of_employees: extractedProfileEdit.number_of_employees ?? 2,
      has_physical_premises: extractedProfileEdit.has_physical_premises ?? true,
      handles_food: extractedProfileEdit.handles_food ?? (extractedProfileEdit.business_type === 'food'),
      serves_cooked_food: extractedProfileEdit.serves_cooked_food ?? false,
      sells_alcohol: extractedProfileEdit.sells_alcohol ?? false,
      uses_chemicals_or_cosmetics: extractedProfileEdit.uses_chemicals_or_cosmetics ?? (extractedProfileEdit.business_type === 'salon'),
      handles_waste_oil_or_batteries: extractedProfileEdit.handles_waste_oil_or_batteries ?? (extractedProfileEdit.business_type === 'vehicle_parts'),
      is_manufacturing: extractedProfileEdit.is_manufacturing ?? false,
      is_importing: extractedProfileEdit.is_importing ?? false,
      turnover_band: extractedProfileEdit.turnover_band || '1m_10m',
      location: extractedProfileEdit.location || 'Colombo',
      products_services: extractedProfileEdit.products_services || [],
      business_size: (extractedProfileEdit.number_of_employees ?? 2) > 10 ? 'medium' : 'small',
    };

    setProfile(confirmed);
    runAnalysis(confirmed);
  };

  const handleEditInManualForm = () => {
    if (!extractedProfileEdit) return;
    setProfile((prev) => ({
      ...prev,
      business_type: extractedProfileEdit.business_type || prev.business_type,
      province: extractedProfileEdit.province || prev.province,
      district: extractedProfileEdit.district || prev.district,
      local_authority: extractedProfileEdit.local_authority || prev.local_authority,
      legal_form: extractedProfileEdit.legal_form || prev.legal_form,
      number_of_employees: extractedProfileEdit.number_of_employees ?? prev.number_of_employees,
      has_physical_premises: extractedProfileEdit.has_physical_premises ?? prev.has_physical_premises,
      handles_food: extractedProfileEdit.handles_food ?? prev.handles_food,
      serves_cooked_food: extractedProfileEdit.serves_cooked_food ?? prev.serves_cooked_food,
      sells_alcohol: extractedProfileEdit.sells_alcohol ?? prev.sells_alcohol,
      uses_chemicals_or_cosmetics: extractedProfileEdit.uses_chemicals_or_cosmetics ?? prev.uses_chemicals_or_cosmetics,
      handles_waste_oil_or_batteries: extractedProfileEdit.handles_waste_oil_or_batteries ?? prev.handles_waste_oil_or_batteries,
      is_manufacturing: extractedProfileEdit.is_manufacturing ?? prev.is_manufacturing,
      is_importing: extractedProfileEdit.is_importing ?? prev.is_importing,
      turnover_band: extractedProfileEdit.turnover_band || prev.turnover_band,
      location: extractedProfileEdit.location || prev.location,
      products_services: extractedProfileEdit.products_services || prev.products_services,
    }));
    setPdfExtractResult(null);
    setShowManualForm(true);
  };

  const setField = (key: keyof BusinessProfileForm, value: unknown) => {
    setProfile((prev) => ({
      ...prev,
      [key]: value === '' || value === 'unknown' ? null : value,
    }));
  };

  const runAnalysis = async (profToAnalyze: BusinessProfileForm = profile) => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyseComplianceAPI(profToAnalyze);
      setResult(data);
      setResultsSubTab('roadmap');
      setSelectedObligationId((current) =>
        data.obligations.some((obligation) => obligation.obligation_id === current)
          ? current
          : data.obligations[0]?.obligation_id || ''
      );
      setActiveStep('results');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error evaluating compliance');
    } finally {
      setLoading(false);
    }
  };

  const handleInlineAnswer = (key: keyof BusinessProfileForm, value: unknown) => {
    const updated = { ...profile, [key]: value };
    setProfile(updated);
    runAnalysis(updated);
  };

  const handleLoadSample = (sampleId: 'clear_case' | 'conditional_case' | 'missing_info_case') => {
    const sample = SAMPLE_PROFILES[sampleId];
    if (sample) {
      setProfile(sample);
      runAnalysis(sample);
    }
  };

  // Group obligations
  const unknownList = result?.obligations.filter(
    (o) => o.status === 'UNKNOWN' || o.status === 'NEEDS_VERIFICATION'
  ) || [];
  const selectedObligation = result?.obligations.find(
    (obligation) => obligation.obligation_id === selectedObligationId
  ) || result?.obligations[0];
  const profileFactKeys = [
    'business_type',
    'legal_form',
    'local_authority',
    'district',
    'province',
    'products_services',
    'business_size',
    'number_of_employees',
    'has_physical_premises',
    'handles_food',
    'is_manufacturing',
    'is_importing',
    'turnover_band',
    ...(profile.business_type === 'food' ? ['serves_cooked_food', 'sells_alcohol'] : []),
    ...(profile.business_type === 'salon' ? ['uses_chemicals_or_cosmetics'] : []),
    ...(profile.business_type === 'vehicle_parts' ? ['handles_waste_oil_or_batteries'] : []),
  ];
  const knownProfileFacts = profileFactKeys.filter((key) => {
    const value = profile[key as keyof BusinessProfileForm];
    if (Array.isArray(value)) return value.length > 0;
    return value !== null && value !== undefined && value !== '';
  }).length;
  const profileCompleteness = Math.round((knownProfileFacts / profileFactKeys.length) * 100);
  const followUpFacts = Array.from(
    new Set(unknownList.flatMap((obligation) => obligation.missing_facts))
  );
  const filteredObligations = (result?.obligations || []).filter(
    (obligation) => resultFilter === 'all' || obligation.status === resultFilter
  );

  return (
    <div className="compliance-app min-h-screen flex-1 font-sans bg-slate-50">
      {/* Sleek Sub-Header & Stage Navigation Bar */}
      <div className="bg-white/95 backdrop-blur-md border-b border-slate-200/90 px-4 sm:px-8 py-3.5 shadow-2xs">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-slate-900 via-indigo-950 to-slate-900 text-teal-400 flex items-center justify-center font-extrabold text-sm shadow-md border border-slate-700/80">
              C2
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm sm:text-base font-extrabold text-slate-900 tracking-tight">Compliance Navigator</h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
                  Western Province SME Scope
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">
                Deterministic Three-Valued Kleene Logic Regulatory Engine
              </p>
            </div>
          </div>

          {/* Stepper Navigation Pills */}
          <nav className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-2xl border border-slate-200 self-stretch sm:self-auto overflow-x-auto">
            {([
              { id: 'profile', label: '1 · Business Profile', icon: 'fa-id-card' },
              { id: 'results', label: '2 · Regulatory Results', icon: 'fa-scale-balanced', count: result ? result.obligations.length : null },
              { id: 'evidence', label: '3 · Evidence & Sources', icon: 'fa-book-bookmark' },
            ] as const).map((step) => {
              const isAvailable = step.id === 'profile' || Boolean(result);
              const isActive = activeStep === step.id;
              return (
                <button
                  key={step.id}
                  type="button"
                  disabled={!isAvailable}
                  onClick={() => isAvailable && setActiveStep(step.id)}
                  className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                    isActive
                      ? 'bg-white text-slate-900 shadow-xs border border-slate-200/90'
                      : isAvailable
                      ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                      : 'text-slate-400 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <i className={`fa-solid ${step.icon} text-[11px] ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  <span>{step.label}</span>
                  {step.count !== null && (
                    <span className="px-1.5 py-0.2 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-800">
                      {step.count}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      <main className="max-w-7xl mx-auto p-4 sm:p-8 space-y-6">
        {/* Component 2 Executive Introduction & Capabilities Banner */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-teal-50/90 via-emerald-50/70 to-blue-50/80 border border-teal-200/90 p-5 sm:p-6 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <span className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-teal-600 to-emerald-500 text-white flex items-center justify-center text-xl shadow-md shadow-teal-600/20 shrink-0 mt-0.5">
                <i className="fa-solid fa-scale-balanced" />
              </span>
              <div className="space-y-1.5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-teal-600 text-white shadow-2xs">
                    Component 2
                  </span>
                  <span className="text-xs font-bold text-slate-900 tracking-tight">
                    AI-Driven Regulatory Compliance &amp; Business Registration System
                  </span>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-white text-emerald-800 border border-emerald-200 shadow-2xs">
                    <i className="fa-solid fa-circle-check text-emerald-600 text-[9px]" /> Verified Legal Framework
                  </span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed max-w-4xl">
                  Intelligent decision support for Sri Lankan SMEs across the Western Province (Colombo, Gampaha, Kalutara).
                  Evaluates your business characteristics against registered Parliamentary Acts, Provincial Statutes, and Municipal By-laws
                  to identify required trade permits, health clearances, and statutory registration filings with zero legal hallucination.
                </p>
                <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] font-semibold text-slate-600">
                  <span className="inline-flex items-center gap-1 bg-white/80 px-2.5 py-1 rounded-lg border border-slate-200/80">
                    📍 Western Province &amp; Colombo MC
                  </span>
                  <span className="inline-flex items-center gap-1 bg-white/80 px-2.5 py-1 rounded-lg border border-slate-200/80">
                    📜 Food Act, WP Statute 04/1990 &amp; By-Laws
                  </span>
                  <span className="inline-flex items-center gap-1 bg-white/80 px-2.5 py-1 rounded-lg border border-slate-200/80">
                    🛡️ Three-Valued Logic (Missing facts never assumed false)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {activeStep === 'profile' && (
          <div className="compliance-layout">
            <section className="compliance-panel space-y-5">
              {/* ------------------------------------------------------------- */}
              {/* ------------------------------------------------------------- */}
              {/* COMPONENT 1 ➔ COMPONENT 2 INTEGRATION: PDF INGESTION & EXTRACTION */}
              {/* ------------------------------------------------------------- */}
              <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-[#0d1627] to-indigo-950 p-6 sm:p-7 text-white shadow-xl border border-slate-800">
                {/* Decorative ambient background glows */}
                <div className="absolute -top-20 -right-20 w-72 h-72 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
                <div className="absolute -bottom-20 -left-20 w-72 h-72 rounded-full bg-teal-500/10 blur-3xl pointer-events-none" />

                <div className="relative z-10">
                  {/* Header & Steps Indicator */}
                  <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-700/60 pb-5">
                    <div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/15 text-blue-300 text-[11px] font-bold border border-blue-400/30 mb-2.5">
                        <i className="fa-solid fa-network-wired text-blue-400" />
                        Component 1 ➔ Component 2 AI Pipeline Bridge
                      </div>
                      <h2 className="text-xl font-extrabold text-white flex items-center gap-2.5 tracking-tight">
                        <span className="w-8 h-8 rounded-xl bg-red-500/20 text-red-400 flex items-center justify-center text-sm border border-red-500/30">
                          <i className="fa-solid fa-file-pdf" />
                        </span>
                        Upload Business / Growth Plan (PDF)
                      </h2>
                      <p className="text-xs text-slate-300 mt-1.5 max-w-2xl leading-relaxed">
                        Upload the PDF plan generated from Component 1 or any external SME business plan.
                        The system automatically parses text (or performs OCR on scanned PDFs), extracts a comprehensive
                        business profile, and lets you confirm it before displaying applicable Sri Lankan legal &amp; regulatory requirements.
                      </p>
                    </div>

                    {/* Step badges */}
                    <div className="flex flex-wrap sm:flex-nowrap items-center gap-1.5 text-[11px] font-bold bg-slate-800/80 p-2 rounded-2xl border border-slate-700/80 shadow-inner">
                      <span className="px-2.5 py-1 rounded-lg bg-blue-500/25 text-blue-300 whitespace-nowrap">1. Download Plan</span>
                      <i className="fa-solid fa-chevron-right text-[9px] text-slate-500 shrink-0" />
                      <span className="px-2.5 py-1 rounded-lg bg-teal-500/25 text-teal-300 whitespace-nowrap">2. Upload PDF</span>
                      <i className="fa-solid fa-chevron-right text-[9px] text-slate-500 shrink-0" />
                      <span className="px-2.5 py-1 rounded-lg bg-amber-500/25 text-amber-300 whitespace-nowrap">3. Extract &amp; Confirm</span>
                      <i className="fa-solid fa-chevron-right text-[9px] text-slate-500 shrink-0" />
                      <span className="px-2.5 py-1 rounded-lg bg-emerald-500/25 text-emerald-300 whitespace-nowrap">4. Legal Guidance</span>
                    </div>
                  </div>

                  {/* Upload Error Banner */}
                  {pdfError && (
                    <div className="mt-4 p-3.5 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-200 text-xs flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <i className="fa-solid fa-circle-exclamation text-rose-400" />
                        {pdfError}
                      </span>
                      <button
                        type="button"
                        onClick={() => setPdfError(null)}
                        className="text-rose-300 hover:text-white text-xs ml-3 font-semibold cursor-pointer"
                      >
                        Dismiss
                      </button>
                    </div>
                  )}

                  {/* Main Ingestion & Upload Section (Shown when no extracted profile is awaiting confirmation) */}
                  {!pdfExtractResult && (
                    <div className="mt-5 space-y-4">
                      {/* Drag and Drop Zone */}
                      <div
                        onDragOver={(e) => {
                          e.preventDefault();
                          setIsDragOver(true);
                        }}
                        onDragLeave={() => setIsDragOver(false)}
                        onDrop={(e) => {
                          e.preventDefault();
                          setIsDragOver(false);
                          const file = e.dataTransfer.files?.[0];
                          if (file) handlePdfFile(file);
                        }}
                        onClick={() => fileInputRef.current?.click()}
                        className={`group relative border-2 border-dashed rounded-2xl p-7 text-center cursor-pointer transition-all duration-200 ${
                          isDragOver
                            ? 'border-teal-400 bg-teal-500/15 scale-[1.01] shadow-lg shadow-teal-500/10'
                            : 'border-slate-700 hover:border-teal-500/50 bg-slate-800/40 hover:bg-slate-800/70'
                        }`}
                      >
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="application/pdf"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handlePdfFile(file);
                          }}
                        />

                        {pdfUploading ? (
                          <div className="py-6 space-y-3">
                            <i className="fa-solid fa-circle-notch fa-spin text-4xl text-teal-400" />
                            <div className="text-sm font-bold text-teal-300">
                              Analyzing &amp; Extracting Business Profile from PDF...
                            </div>
                            <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
                              Running PyMuPDF text extractor · Scanning for OCR text · Identifying category, location &amp; commercial offerings
                            </p>
                          </div>
                        ) : (
                          <div className="space-y-3">
                            <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-slate-800 to-slate-700 flex items-center justify-center text-teal-400 text-2xl shadow-inner group-hover:scale-105 transition-transform border border-slate-600/50">
                              <i className="fa-solid fa-cloud-arrow-up" />
                            </div>
                            <div className="text-sm font-bold text-slate-100">
                              Drop your Business Plan PDF here, or <span className="text-teal-400 underline underline-offset-4 decoration-teal-400/50 group-hover:decoration-teal-400">browse file</span>
                            </div>
                            <p className="text-[11px] text-slate-400 max-w-lg mx-auto leading-relaxed">
                              Supports Component 1 SME360 AI Reports, Strategic Growth Plans, or Scanned SME Business Plans (.pdf)
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                {/* ------------------------------------------------------------- */}
                {/* STEP 3 & 4: EXTRACTED PROFILE CONFIRMATION & REVIEW CARD     */}
                {/* ------------------------------------------------------------- */}
                {pdfExtractResult && extractedProfileEdit && (
                  <div className="mt-5 bg-white text-slate-900 rounded-xl p-5 shadow-lg border border-slate-200 space-y-4">
                    {/* Header verification tag */}
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                      <div>
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold mb-1">
                          <i className="fa-solid fa-circle-check text-emerald-600" />
                          Step 3 Complete: Business Profile Extracted
                        </div>
                        <h3 className="text-base font-bold text-slate-900">
                          Step 4: Confirm &amp; Adjust Extracted Business Profile
                        </h3>
                        <p className="text-xs text-slate-500">
                          Extracted from <span className="font-semibold text-slate-700">{pdfExtractResult.filename}</span> ({pdfExtractResult.pages_count} Pages · {pdfExtractResult.is_scanned ? 'OCR Processed' : 'Digital Text Extracted'})
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => {
                            setPdfExtractResult(null);
                            setExtractedProfileEdit(null);
                          }}
                          className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                        >
                          <i className="fa-solid fa-arrow-rotate-left mr-1" />
                          Upload Different PDF
                        </button>
                      </div>
                    </div>

                    {/* Editable Fields Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5 text-xs">
                      {/* Business Name */}
                      <div>
                        <label className="block font-bold text-slate-700 mb-1">Business Name</label>
                        <input
                          type="text"
                          value={extractedProfileEdit.business_name || ''}
                          onChange={(e) =>
                            setExtractedProfileEdit({ ...extractedProfileEdit, business_name: e.target.value })
                          }
                          className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none font-semibold text-slate-800"
                        />
                      </div>

                      {/* Business Category & Mapped Sector */}
                      <div>
                        <label className="block font-bold text-slate-700 mb-1">
                          Category &amp; Mapped Legal Sector
                        </label>
                        <select
                          value={extractedProfileEdit.business_type || 'food'}
                          onChange={(e) => {
                            const bt = e.target.value;
                            setExtractedProfileEdit({
                              ...extractedProfileEdit,
                              business_type: bt,
                              sector: bt,
                              handles_food: bt === 'food',
                              uses_chemicals_or_cosmetics: bt === 'salon',
                              handles_waste_oil_or_batteries: bt === 'vehicle_parts',
                            });
                          }}
                          className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none bg-slate-50 font-semibold"
                        >
                          <option value="food">Grocery / Mini-Mart / Food Business</option>
                          <option value="clothing">Clothing / Garment Retail</option>
                          <option value="salon">Beauty Salon / Grooming</option>
                          <option value="vehicle_parts">Vehicle Parts &amp; Auto Accessories</option>
                        </select>
                      </div>

                      {/* Business Stage */}
                      <div>
                        <label className="block font-bold text-slate-700 mb-1">Business Stage</label>
                        <select
                          value={extractedProfileEdit.business_stage || 'New Startup'}
                          onChange={(e) =>
                            setExtractedProfileEdit({ ...extractedProfileEdit, business_stage: e.target.value })
                          }
                          className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                          <option value="New Startup">New Startup</option>
                          <option value="Existing Business">Existing Business (Expansion)</option>
                        </select>
                      </div>

                      {/* Province & District */}
                      <div>
                        <label className="block font-bold text-slate-700 mb-1">Province &amp; District</label>
                        <div className="flex gap-1.5">
                          <input
                            type="text"
                            readOnly
                            value={extractedProfileEdit.province || 'Western Province'}
                            className="w-1/2 bg-slate-100 border border-slate-300 rounded-lg px-2 py-1.5 text-xs text-slate-600"
                          />
                          <input
                            type="text"
                            value={extractedProfileEdit.district || 'Colombo'}
                            onChange={(e) =>
                              setExtractedProfileEdit({ ...extractedProfileEdit, district: e.target.value })
                            }
                            className="w-1/2 border border-slate-300 rounded-lg px-2 py-1.5 text-xs"
                          />
                        </div>
                      </div>

                      {/* Local Authority */}
                      <div>
                        <label className="block font-bold text-slate-700 mb-1">Local Authority</label>
                        <select
                          value={extractedProfileEdit.local_authority || 'Colombo Municipal Council'}
                          onChange={(e) =>
                            setExtractedProfileEdit({ ...extractedProfileEdit, local_authority: e.target.value })
                          }
                          className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        >
                          <option value="Colombo Municipal Council">Colombo Municipal Council</option>
                          <option value="Kotte Municipal Council">Kotte Municipal Council</option>
                          <option value="Dehiwala-Mount Lavinia Municipal Council">Dehiwala-Mount Lavinia Municipal Council</option>
                          <option value="Gampaha Municipal Council">Gampaha Municipal Council</option>
                          <option value="Negombo Municipal Council">Negombo Municipal Council</option>
                          <option value="Kalutara Urban Council">Kalutara Urban Council</option>
                        </select>
                      </div>

                      {/* Number of Staff */}
                      <div>
                        <label className="block font-bold text-slate-700 mb-1">Hired Staff / Employees</label>
                        <input
                          type="number"
                          min="0"
                          value={extractedProfileEdit.number_of_employees ?? 1}
                          onChange={(e) =>
                            setExtractedProfileEdit({
                              ...extractedProfileEdit,
                              number_of_employees: parseInt(e.target.value, 10) || 0,
                            })
                          }
                          className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none font-semibold"
                        />
                      </div>
                    </div>

                    {/* Proposed Activity / Concept */}
                    <div>
                      <label className="block font-bold text-slate-700 mb-1">
                        Proposed Activity / Business Concept (Identified from PDF)
                      </label>
                      <textarea
                        rows={2}
                        value={extractedProfileEdit.proposed_activity || ''}
                        onChange={(e) =>
                          setExtractedProfileEdit({ ...extractedProfileEdit, proposed_activity: e.target.value })
                        }
                        className="w-full border border-slate-300 rounded-lg p-2 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none leading-relaxed text-slate-700"
                      />
                    </div>

                    {/* Products & Services Tag Cloud */}
                    <div>
                      <label className="block font-bold text-slate-700 mb-1">
                        Products &amp; Commercial Offerings
                      </label>
                      <div className="flex flex-wrap items-center gap-1.5 p-2 bg-slate-50 border border-slate-200 rounded-lg min-h-[38px]">
                        {(extractedProfileEdit.products_services || []).map((prod: string, idx: number) => (
                          <span
                            key={idx}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-100 text-blue-800 text-[11px] font-medium"
                          >
                            {prod}
                            <button
                              type="button"
                              onClick={() => {
                                const updated = extractedProfileEdit.products_services.filter(
                                  (_: any, i: number) => i !== idx
                                );
                                setExtractedProfileEdit({ ...extractedProfileEdit, products_services: updated });
                              }}
                              className="text-blue-500 hover:text-blue-900 ml-0.5 text-[10px]"
                            >
                              ✕
                            </button>
                          </span>
                        ))}

                        <div className="inline-flex items-center gap-1 ml-1">
                          <input
                            type="text"
                            placeholder="+ Add product"
                            value={newProductTag}
                            onChange={(e) => setNewProductTag(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && newProductTag.trim()) {
                                e.preventDefault();
                                const updated = [
                                  ...(extractedProfileEdit.products_services || []),
                                  newProductTag.trim(),
                                ];
                                setExtractedProfileEdit({ ...extractedProfileEdit, products_services: updated });
                                setNewProductTag('');
                              }
                            }}
                            className="text-[11px] border border-slate-300 rounded px-1.5 py-0.5 w-24 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Operational Checkbox Flags */}
                    <div className="pt-2 border-t border-slate-100">
                      <span className="block font-bold text-slate-700 mb-2">
                        Operational Attributes for Regulatory Rulebook:
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-[11px]">
                        <label className="flex items-center gap-2 cursor-pointer bg-slate-50 p-2 rounded-lg border border-slate-200">
                          <input
                            type="checkbox"
                            checked={Boolean(extractedProfileEdit.has_physical_premises)}
                            onChange={(e) =>
                              setExtractedProfileEdit({
                                ...extractedProfileEdit,
                                has_physical_premises: e.target.checked,
                              })
                            }
                            className="rounded text-blue-600"
                          />
                          <span>Physical Premises</span>
                        </label>

                        <label className="flex items-center gap-2 cursor-pointer bg-slate-50 p-2 rounded-lg border border-slate-200">
                          <input
                            type="checkbox"
                            checked={Boolean(extractedProfileEdit.handles_food)}
                            onChange={(e) =>
                              setExtractedProfileEdit({
                                ...extractedProfileEdit,
                                handles_food: e.target.checked,
                              })
                            }
                            className="rounded text-blue-600"
                          />
                          <span>Handles Food / Grocery</span>
                        </label>

                        <label className="flex items-center gap-2 cursor-pointer bg-slate-50 p-2 rounded-lg border border-slate-200">
                          <input
                            type="checkbox"
                            checked={Boolean(extractedProfileEdit.uses_chemicals_or_cosmetics)}
                            onChange={(e) =>
                              setExtractedProfileEdit({
                                ...extractedProfileEdit,
                                uses_chemicals_or_cosmetics: e.target.checked,
                              })
                            }
                            className="rounded text-blue-600"
                          />
                          <span>Uses Cosmetics/Chemicals</span>
                        </label>

                        <label className="flex items-center gap-2 cursor-pointer bg-slate-50 p-2 rounded-lg border border-slate-200">
                          <input
                            type="checkbox"
                            checked={Boolean(extractedProfileEdit.handles_waste_oil_or_batteries)}
                            onChange={(e) =>
                              setExtractedProfileEdit({
                                ...extractedProfileEdit,
                                handles_waste_oil_or_batteries: e.target.checked,
                              })
                            }
                            className="rounded text-blue-600"
                          />
                          <span>Waste Oil / Batteries</span>
                        </label>
                      </div>
                    </div>

                    {/* Bottom Confirmation Bar */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
                      <div className="text-[11px] text-slate-500">
                        {extractedProfileEdit.selected_strategy && (
                          <span>
                            Active Strategy: <strong className="text-slate-700">{extractedProfileEdit.selected_strategy}</strong>
                          </span>
                        )}
                        {extractedProfileEdit.available_capital_lkr && (
                          <span className="ml-2 font-mono">
                            · Capital: LKR {extractedProfileEdit.available_capital_lkr.toLocaleString()}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={handleEditInManualForm}
                          className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs transition-colors"
                        >
                          Edit in Form Below
                        </button>
                        <button
                          type="button"
                          onClick={handleConfirmExtractedProfile}
                          disabled={loading}
                          className="px-5 py-2.5 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-bold rounded-xl text-xs transition-all shadow-md flex items-center gap-2"
                        >
                          {loading ? (
                            <>
                              <i className="fa-solid fa-circle-notch fa-spin text-xs" />
                              <span>Evaluating Statutory Obligations...</span>
                            </>
                          ) : (
                            <>
                              <i className="fa-solid fa-check text-xs" />
                              <span>Confirm Profile &amp; View Legal Guidance ➔</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
                </div>
              </div>

              {/* Form Container */}
              <div className="compliance-form-card bg-white rounded-2xl shadow-sm border border-slate-200 p-5 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <i className="fa-solid fa-sliders text-blue-600" />
                Business Intake Profile
              </h2>
              <p className="text-xs text-slate-500">
                {profile.business_type
                  ? `Active Profile: ${profile.business_type.toUpperCase()} · ${profile.district || profile.location || 'Western Province'} · ${profile.legal_form || 'Sole Proprietorship'}`
                  : 'Upload a plan PDF above or choose a preset to evaluate regulatory compliance.'}
              </p>
            </div>

            {/* Real Sample Profile Buttons */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500">Presets:</span>
              <button
                type="button"
                onClick={() => handleLoadSample('clear_case')}
                className="px-2.5 py-1.5 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 transition-colors cursor-pointer"
              >
                Clear Case
              </button>
              <button
                type="button"
                onClick={() => handleLoadSample('conditional_case')}
                className="px-2.5 py-1.5 bg-slate-100 hover:bg-amber-50 hover:text-amber-700 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 transition-colors cursor-pointer"
              >
                Conditional Case
              </button>
              <button
                type="button"
                onClick={() => handleLoadSample('missing_info_case')}
                className="px-2.5 py-1.5 bg-slate-100 hover:bg-purple-50 hover:text-purple-700 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 transition-colors cursor-pointer"
              >
                Missing Info
              </button>
            </div>
          </div>

          {/* Quick Profile Summary & Optional Manual Toggle */}
          <div className="flex items-center justify-between py-1">
            <div className="text-xs text-slate-600 flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${profile.business_type ? 'bg-emerald-500' : 'bg-slate-400'}`} />
              <span>
                Status:{' '}
                <strong className="text-slate-800">
                  {profile.business_type ? `${profile.business_type.replace('_', ' ')} (${knownProfileFacts} facts captured)` : 'No profile loaded (Defaults to Unknown)'}
                </strong>
              </span>
            </div>
            <button
              type="button"
              onClick={() => setShowManualForm(!showManualForm)}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1.5 py-1 px-2.5 rounded-lg hover:bg-blue-50 transition-colors cursor-pointer"
            >
              <i className={`fa-solid ${showManualForm ? 'fa-chevron-up' : 'fa-pen-to-square'}`} />
              {showManualForm ? 'Hide manual form fields' : 'Edit fields manually (Optional)'}
            </button>
          </div>

          {showManualForm && (
            <div className="pt-3 border-t border-slate-100 space-y-4">
              {/* Form Fields Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Business Type (Scope: 4 types) */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Business Type (Sector)
                  </label>
                  <select
                value={profile.business_type || ''}
                onChange={(e) => setField('business_type', e.target.value || null)}
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Unknown (null) --</option>
                <option value="food">Food &amp; Catering (Bakery / Restaurant / Sweets)</option>
                <option value="clothing">Clothing &amp; Textile Retail</option>
                <option value="salon">Beauty Salon &amp; Hair Care</option>
                <option value="vehicle_parts">Vehicle Spare Parts Retail</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Business Location</label>
              <input
                type="text"
                value={profile.location || ''}
                onChange={(e) => setField('location', e.target.value || null)}
                placeholder="Town or business area"
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">District</label>
              <input
                type="text"
                value={profile.district || ''}
                onChange={(e) => setField('district', e.target.value || null)}
                placeholder="Colombo"
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Products / Services</label>
              <input
                type="text"
                value={(profile.products_services || []).join(', ')}
                onChange={(e) =>
                  setField(
                    'products_services',
                    e.target.value.split(',').map((value) => value.trim()).filter(Boolean)
                  )
                }
                placeholder="Comma-separated products or services"
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Business Size</label>
              <select
                value={profile.business_size || ''}
                onChange={(e) => setField('business_size', e.target.value || null)}
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Unknown --</option>
                <option value="micro">Micro</option>
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </div>

            {/* Local Authority */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Local Authority</label>
              <select
                value={profile.local_authority || ''}
                onChange={(e) => setField('local_authority', e.target.value || null)}
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Unknown (null) --</option>
                <option value="Colombo Municipal Council">Colombo Municipal Council</option>
                <option value="Sri Jayawardenepura Kotte Municipal Council">Kotte Municipal Council</option>
                <option value="Dehiwala-Mount Lavinia Municipal Council">Dehiwala-Mount Lavinia MC</option>
                <option value="Moratuwa Municipal Council">Moratuwa Municipal Council</option>
              </select>
            </div>

            {/* Legal Form */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Legal Form</label>
              <select
                value={profile.legal_form || ''}
                onChange={(e) => setField('legal_form', e.target.value || null)}
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Unknown (null) --</option>
                <option value="sole_proprietorship">Sole Proprietorship</option>
                <option value="partnership">Partnership</option>
                <option value="private_limited">Private Limited Company</option>
                <option value="other">Other Legal Form</option>
              </select>
            </div>

            {/* Number of Employees */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Number of Employees (Staff)
              </label>
              <input
                type="number"
                min="0"
                placeholder="-- Unknown (null) --"
                value={profile.number_of_employees !== null && profile.number_of_employees !== undefined ? profile.number_of_employees : ''}
                onChange={(e) => setField('number_of_employees', e.target.value === '' ? null : parseInt(e.target.value, 10))}
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Province (Fixed Scope: Western Province) */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-bold text-slate-700">Province (Scope)</label>
                <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  Western Province Only
                </span>
              </div>
              <select
                value={profile.province || 'Western Province'}
                onChange={(e) => setField('province', e.target.value)}
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm font-medium text-slate-800 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-default"
              >
                <option value="Western Province">Western Province</option>
              </select>
            </div>

            {/* Turnover Band (All business types) */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Annual Turnover Band (All Businesses)
              </label>
              <select
                value={profile.turnover_band || ''}
                onChange={(e) => setField('turnover_band', e.target.value || null)}
                className="w-full border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Unknown (null) --</option>
                <option value="under_1m">Under LKR 1 Million</option>
                <option value="1m_10m">LKR 1M – 10M</option>
                <option value="10m_50m">LKR 10M – 50M</option>
                <option value="over_50m">Over LKR 50 Million</option>
              </select>
            </div>
          </div>

          {/* Standard Yes/No Toggles */}
          <div>
            <p className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">
              Operational Attributes (Defaults to Unknown / null)
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {([
                { key: 'handles_food', label: 'Handles Food' },
                { key: 'has_physical_premises', label: 'Physical Premises' },
                { key: 'is_manufacturing', label: 'Manufacturing' },
                { key: 'is_importing', label: 'Importing Goods' },
              ] as const).map(({ key, label }) => {
                const val = profile[key];
                return (
                  <div key={key} className="border border-slate-200 rounded-xl p-2.5 bg-slate-50/50">
                    <p className="text-xs font-semibold text-slate-700 mb-1.5">{label}</p>
                    <div className="flex gap-1.5">
                      <button
                        type="button"
                        onClick={() => setField(key, val === true ? null : true)}
                        className={`flex-1 text-xs py-1 rounded-lg font-semibold border transition-all ${
                          val === true
                            ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                            : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        type="button"
                        onClick={() => setField(key, val === false ? null : false)}
                        className={`flex-1 text-xs py-1 rounded-lg font-semibold border transition-all ${
                          val === false
                            ? 'bg-rose-600 text-white border-rose-600 shadow-xs'
                            : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Conditional Fields depending on business_type */}
          {profile.business_type === 'food' && (
            <div className="p-3.5 bg-blue-50/70 border border-blue-200 rounded-xl space-y-2">
              <p className="text-xs font-bold text-blue-900 flex items-center gap-1.5">
                <i className="fa-solid fa-utensils text-blue-600" />
                Extra Questions for Food Businesses:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="border border-blue-200 bg-white rounded-lg p-2.5">
                  <p className="text-xs font-semibold text-slate-700 mb-1.5">Serves Cooked Food on Premises?</p>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setField('serves_cooked_food', profile.serves_cooked_food === true ? null : true)}
                      className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.serves_cooked_food === true ? 'bg-emerald-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => setField('serves_cooked_food', profile.serves_cooked_food === false ? null : false)}
                      className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.serves_cooked_food === false ? 'bg-rose-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                    >
                      No
                    </button>
                  </div>
                </div>

                <div className="border border-blue-200 bg-white rounded-lg p-2.5">
                  <p className="text-xs font-semibold text-slate-700 mb-1.5">Sells / Serves Alcohol?</p>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setField('sells_alcohol', profile.sells_alcohol === true ? null : true)}
                      className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.sells_alcohol === true ? 'bg-emerald-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => setField('sells_alcohol', profile.sells_alcohol === false ? null : false)}
                      className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.sells_alcohol === false ? 'bg-rose-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                    >
                      No
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {profile.business_type === 'salon' && (
            <div className="p-3.5 bg-purple-50/70 border border-purple-200 rounded-xl space-y-2">
              <p className="text-xs font-bold text-purple-900 flex items-center gap-1.5">
                <i className="fa-solid fa-scissors text-purple-600" />
                Extra Questions for Beauty Salon Businesses:
              </p>
              <div className="border border-purple-200 bg-white rounded-lg p-2.5 max-w-md">
                <p className="text-xs font-semibold text-slate-700 mb-1.5">Uses Chemical Cosmetics / Dyes / Bleaches?</p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setField('uses_chemicals_or_cosmetics', profile.uses_chemicals_or_cosmetics === true ? null : true)}
                    className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.uses_chemicals_or_cosmetics === true ? 'bg-emerald-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                  >
                    Yes
                  </button>
                  <button
                    type="button"
                    onClick={() => setField('uses_chemicals_or_cosmetics', profile.uses_chemicals_or_cosmetics === false ? null : false)}
                    className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.uses_chemicals_or_cosmetics === false ? 'bg-rose-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                  >
                    No
                  </button>
                </div>
              </div>
            </div>
          )}

          {profile.business_type === 'vehicle_parts' && (
            <div className="p-3.5 bg-amber-50/70 border border-amber-200 rounded-xl space-y-2">
              <p className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                <i className="fa-solid fa-wrench text-amber-600" />
                Extra Questions for Vehicle Parts Businesses:
              </p>
              <div className="border border-amber-200 bg-white rounded-lg p-2.5 max-w-md">
                <p className="text-xs font-semibold text-slate-700 mb-1.5">Handles Waste Mineral Oil or Used Lead Batteries?</p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setField('handles_waste_oil_or_batteries', profile.handles_waste_oil_or_batteries === true ? null : true)}
                    className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.handles_waste_oil_or_batteries === true ? 'bg-emerald-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                  >
                    Yes
                  </button>
                  <button
                    type="button"
                    onClick={() => setField('handles_waste_oil_or_batteries', profile.handles_waste_oil_or_batteries === false ? null : false)}
                    className={`flex-1 text-xs py-1 rounded font-semibold border ${profile.handles_waste_oil_or_batteries === false ? 'bg-rose-600 text-white' : 'bg-slate-50 text-slate-600'}`}
                  >
                    No
                  </button>
                </div>
              </div>
            </div>
          )}

            </div>
          )}

          {/* Action Button */}
          <button
            type="button"
            onClick={() => runAnalysis(profile)}
            disabled={loading}
            className="compliance-primary-button w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-sm font-bold rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <i className="fa-solid fa-spinner fa-spin" />
                Evaluating Deterministic Rules&hellip;
              </>
            ) : (
              <>
                <i className="fa-solid fa-bolt" />
                Analyze requirements
                <i className="fa-solid fa-arrow-right ml-1" />
              </>
            )}
          </button>
        </div>
            </section>

            <aside className="compliance-side-panel space-y-4">
              {/* Profile Completeness Widget */}
              <section className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-xs space-y-3.5 hover:shadow-md transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <i className="fa-solid fa-chart-pie text-teal-600" />
                    Profile Completeness
                  </span>
                  <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-mono">
                    {knownProfileFacts} / {profileFactKeys.length} Facts
                  </span>
                </div>

                <div className="flex items-baseline justify-between">
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-extrabold text-slate-900 tracking-tight">{profileCompleteness}%</span>
                    <span className="text-xs text-slate-500 font-medium">captured</span>
                  </div>
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                    profileFactKeys.length - knownProfileFacts === 0
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-800 border border-amber-200'
                  }`}>
                    {profileFactKeys.length - knownProfileFacts} facts unknown
                  </span>
                </div>

                {/* Modern Progress Bar */}
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden p-0.5 border border-slate-200/80">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-teal-500 to-emerald-500 shadow-sm transition-all duration-500"
                    style={{ width: `${profileCompleteness}%` }}
                  />
                </div>

                <p className="text-xs text-slate-500 leading-relaxed pt-1 border-t border-slate-100">
                  {profileFactKeys.length - knownProfileFacts === 0
                    ? 'Your business profile is 100% complete. Kleene logic can evaluate all regulatory mandates deterministically.'
                    : 'Missing facts remain strictly Unknown in 3-valued logic. Adding more details narrows down conditional permits.'}
                </p>
              </section>

              {/* Kleene Three-Valued Logic Key */}
              <section className="bg-gradient-to-br from-slate-900 via-[#0d1627] to-indigo-950 text-white rounded-3xl p-5 shadow-sm border border-slate-800 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="w-7 h-7 rounded-xl bg-teal-500/20 text-teal-300 flex items-center justify-center text-xs">
                    <i className="fa-solid fa-microchip" />
                  </span>
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">3VL Kleene Logic Engine</h4>
                    <span className="text-[10px] text-teal-400 font-mono">No Hallucination · Strict Determinism</span>
                  </div>
                </div>

                <div className="space-y-1.5 pt-1 text-xs">
                  <div className="flex items-center justify-between p-2 rounded-xl bg-white/5 border border-white/10">
                    <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" /> True (Applicable)
                    </span>
                    <span className="text-[10px] text-slate-400">All conditions satisfied</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-xl bg-white/5 border border-white/10">
                    <span className="text-[11px] font-bold text-amber-400 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400" /> Unknown (Conditional)
                    </span>
                    <span className="text-[10px] text-slate-400">Missing facts needed</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-xl bg-white/5 border border-white/10">
                    <span className="text-[11px] font-bold text-slate-400 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-slate-500" /> False (Not Applicable)
                    </span>
                    <span className="text-[10px] text-slate-400">Condition violated</span>
                  </div>
                </div>
              </section>

              {/* How It Works List */}
              <section className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-xs space-y-3 hover:shadow-md transition-all">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                  <i className="fa-solid fa-list-check text-blue-600" />
                  How Evaluation Works
                </span>
                <ol className="space-y-3 pt-1">
                  <li className="flex items-start gap-3">
                    <span className="w-6 h-6 rounded-lg bg-blue-50 text-blue-700 font-extrabold text-xs flex items-center justify-center shrink-0 border border-blue-200">
                      1
                    </span>
                    <div>
                      <p className="text-xs font-bold text-slate-900">Sri Lankan Rulebook Check</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">Profile facts are evaluated against Western Province and National statutes.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="w-6 h-6 rounded-lg bg-teal-50 text-teal-700 font-extrabold text-xs flex items-center justify-center shrink-0 border border-teal-200">
                      2
                    </span>
                    <div>
                      <p className="text-xs font-bold text-slate-900">Kleene 3VL Logic Verdict</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">Every rule produces an exact mathematical classification without AI guesswork.</p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="w-6 h-6 rounded-lg bg-purple-50 text-purple-700 font-extrabold text-xs flex items-center justify-center shrink-0 border border-purple-200">
                      3
                    </span>
                    <div>
                      <p className="text-xs font-bold text-slate-900">Official Evidence &amp; Form 1</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">Results map to verified legal clauses and pre-fill statutory Form 1 for registration.</p>
                    </div>
                  </li>
                </ol>
              </section>
            </aside>
          </div>
        )}

        {/* Error Notification */}
        {error && (
          <div className="compliance-error p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center gap-2">
            <i className="fa-solid fa-triangle-exclamation text-red-500" />
            <span>{error}</span>
          </div>
        )}

        {activeStep === 'results' && result && (
          <div className={resultsSubTab === "legal_rules" ? "compliance-results-layout" : "w-full space-y-4"}>
            <section className="compliance-results-main">
              <div className="compliance-result-meta">
                <div>
                  <p className="compliance-eyebrow">Analysis results</p>
                  <h2>Requirements for this business</h2>
                </div>
                <span>Evaluation {result.evaluation_id}</span>
              </div>

              {/* Page Sub-Tabs: 3-Page Flow (1. Roadmap -> 2. Registration -> 3. Legal Rules) */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-3 mb-1">
                <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-2xl border border-slate-200">
                  <button
                    type="button"
                    onClick={() => {
                      setResultsSubTab('roadmap');
                      window.scrollTo(0, 0);
                    }}
                    className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      resultsSubTab === 'roadmap'
                        ? 'bg-white text-emerald-800 shadow-xs border border-slate-200'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-[10px] font-extrabold">1</span>
                    <span>{guidanceLanguage === 'si' ? 'ක්‍රියාකාරී මාර්ග සිතියම' : 'Actionable Roadmap'}</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setResultsSubTab('registration');
                      window.scrollTo(0, 0);
                    }}
                    className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      resultsSubTab === 'registration'
                        ? 'bg-white text-blue-800 shadow-xs border border-slate-200'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center text-[10px] font-extrabold">2</span>
                    <span>{guidanceLanguage === 'si' ? 'ව්‍යාපාර ලියාපදිංචිය (Form 1)' : 'Business Registration'}</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setResultsSubTab('legal_rules');
                      window.scrollTo(0, 0);
                    }}
                    className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      resultsSubTab === 'legal_rules'
                        ? 'bg-white text-amber-800 shadow-xs border border-slate-200'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center text-[10px] font-extrabold">3</span>
                    <span>{guidanceLanguage === 'si' ? 'අදාළ නීති සහ අවශ්‍යතා' : 'Legal Rules & Actions'}</span>
                  </button>
                </div>

                <span className="text-[11px] font-semibold text-slate-500 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-200">
                  {resultsSubTab === 'roadmap'
                    ? (guidanceLanguage === 'si' ? 'පිටුව 1/3' : 'Page 1 of 3')
                    : resultsSubTab === 'registration'
                    ? (guidanceLanguage === 'si' ? 'පිටුව 2/3' : 'Page 2 of 3')
                    : (guidanceLanguage === 'si' ? 'පිටුව 3/3' : 'Page 3 of 3')}
                </span>
              </div>

              {!result.profile_validation.complete && (
                <div className="compliance-incomplete">
                  <i className="fa-solid fa-circle-info" />
                  <span>Some profile details are still unknown. You can answer questions on the right or edit the profile.</span>
                </div>
              )}

              {/* ============================================================= */}
              {/* PAGE 1: ACTIONABLE COMPLIANCE ROADMAP & STATUTORY RULES       */}
              {/* ============================================================= */}
              {resultsSubTab === 'roadmap' && (
                <>
              {result.action_roadmap && (
                <section className="rounded-2xl border-2 border-emerald-500/30 bg-gradient-to-br from-emerald-50/90 via-white to-teal-50/70 p-5 shadow-sm space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-200/60 pb-3">
                    <div className="flex items-center gap-2">
                      <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-sm text-xs">
                        <i className="fa-solid fa-route" />
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-emerald-950">
                            Actionable Compliance Roadmap
                          </h4>
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                            <i className="fa-solid fa-microchip text-[9px]" /> AI Model Recommended
                          </span>
                        </div>
                        <p className="text-[11px] text-emerald-800">
                          Specific institutional destination, licence name, documents, and procedure for this business.
                        </p>
                      </div>
                    </div>

                    <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-100/80 px-2.5 py-1 rounded-full border border-emerald-300/40">
                      Target: {result.action_roadmap.predicted_action_type.replace(/_/g, ' ')}
                    </span>
                  </div>

                  {/* Target Authority & Required License Banner */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="bg-white p-3.5 rounded-xl border border-emerald-100 shadow-xs">
                      <span className="block font-bold text-slate-500 uppercase tracking-wider text-[10px] mb-1">
                        <i className="fa-solid fa-building-columns text-emerald-600 mr-1.5" />
                        Where to Go (Target Authority)
                      </span>
                      <p className="font-semibold text-slate-900 leading-snug">
                        {result.action_roadmap.target_authority}
                      </p>
                      {result.action_roadmap.office_location && result.action_roadmap.office_location !== 'nan' && (
                        <p className="text-[11px] text-slate-500 mt-1">
                          <i className="fa-solid fa-location-dot text-red-500 mr-1" />
                          {result.action_roadmap.office_location}
                        </p>
                      )}
                    </div>

                    <div className="bg-white p-3.5 rounded-xl border border-emerald-100 shadow-xs">
                      <span className="block font-bold text-slate-500 uppercase tracking-wider text-[10px] mb-1">
                        <i className="fa-solid fa-certificate text-amber-500 mr-1.5" />
                        Required Approval / Licence Name
                      </span>
                      <p className="font-semibold text-slate-900 leading-snug">
                        {result.action_roadmap.required_action_name}
                      </p>
                      <p className="text-[11px] text-amber-700 mt-1">
                        <i className="fa-solid fa-clock text-amber-500 mr-1" />
                        {result.action_roadmap.action_urgency}
                      </p>
                    </div>
                  </div>

                  {/* Documents & Step-by-Step Procedure Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs pt-1">
                    {/* Left: Required Documents Checklist */}
                    <div className="bg-white p-4 rounded-xl border border-emerald-100 shadow-xs">
                      <h5 className="font-bold text-slate-800 text-xs flex items-center gap-2 mb-2.5">
                        <i className="fa-solid fa-folder-open text-blue-600" />
                        Mandatory Document Package Checklist:
                      </h5>
                      <ul className="space-y-1.5">
                        {(result.action_roadmap.required_documents || []).map((doc, i) => (
                          <li key={i} className="flex items-start gap-2 text-slate-700 text-[11px] bg-slate-50 p-2 rounded-lg border border-slate-100">
                            <i className="fa-solid fa-circle-check text-emerald-500 mt-0.5 text-xs shrink-0" />
                            <span>{doc}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Right: Procedural Workflow Steps */}
                    <div className="bg-white p-4 rounded-xl border border-emerald-100 shadow-xs">
                      <h5 className="font-bold text-slate-800 text-xs flex items-center gap-2 mb-2.5">
                        <i className="fa-solid fa-list-check text-teal-600" />
                        Step-by-Step Submission Procedure:
                      </h5>
                      <ol className="space-y-2">
                        {(result.action_roadmap.procedural_steps || []).map((step, idx) => (
                          <li key={idx} className="flex items-start gap-2.5 text-slate-700 text-[11px]">
                            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                              {idx + 1}
                            </span>
                            <span className="leading-relaxed pt-0.5">{step}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  </div>

                  {/* Next Button: Proceed to Business Registration Guidance Page (Page 2) */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-3.5 border-t border-emerald-200/60">
                    <span className="text-[11px] text-emerald-800 font-medium flex items-center gap-1.5">
                      <i className="fa-solid fa-circle-check text-emerald-600" />
                      {guidanceLanguage === 'si'
                        ? 'ක්‍රියාකාරී මාර්ග සිතියම සමාලෝචනය කර ඊළඟ පිටුවෙහි ඇති ලියාපදිංචි මාර්ග සිතියම වෙත පිවිසෙන්න:'
                        : 'Review this actionable roadmap, then proceed to the official registration page:'}
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setResultsSubTab('registration');
                        window.scrollTo(0, 0);
                      }}
                      className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-bold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer group ml-auto"
                    >
                      <span>
                        {guidanceLanguage === 'si'
                          ? 'ඊළඟ පිටුව: AI ව්‍යාපාර ලියාපදිංචි මාර්ග සිතියම (Page 2) →'
                          : 'Next Page: Business Registration Guidance (Page 2) →'}
                      </span>
                      <i className="fa-solid fa-arrow-right text-xs transition-transform group-hover:translate-x-1" />
                    </button>
                  </div>
                </section>
              )}
            </>
          )}

          {/* ============================================================= */}
          {/* PAGE 3: APPLICABLE LEGAL RULES & INSTITUTIONAL ACTIONS        */}
          {/* ============================================================= */}
          {resultsSubTab === 'legal_rules' && (
            <div className="space-y-4 animate-fade-in">
              {/* Page 3 Top Navigation Bar with Back Button & Language Switcher */}
              <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3.5 rounded-2xl border border-amber-200 shadow-xs">
                <button
                  type="button"
                  onClick={() => {
                    setResultsSubTab('registration');
                    window.scrollTo(0, 0);
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-slate-900 font-bold text-xs transition-all cursor-pointer border border-slate-200 shadow-2xs"
                >
                  <i className="fa-solid fa-arrow-left text-xs" />
                  <span>
                    {guidanceLanguage === 'si'
                      ? '← ආපසු: ව්‍යාපාර ලියාපදිංචි මාර්ගෝපදේශය (Page 2)'
                      : '← Back to Registration Guidance (Page 2)'}
                  </span>
                </button>

                <div className="flex items-center gap-2.5">
                  <span className="text-[11px] font-semibold text-amber-900 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
                    {rulesLanguage === 'si'
                      ? `හඳුනාගත් නීති සහ ප්‍රතිපත්ති ${result.source_discovery.length} කි`
                      : `${result.source_discovery.length} Identified Rules & Policies`}
                  </span>

                  {/* Language Switcher for Rules */}
                  <div className="inline-flex rounded-xl bg-amber-100/80 p-0.5 border border-amber-300">
                    <button
                      type="button"
                      onClick={() => setRulesLanguage('en')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        rulesLanguage === 'en'
                          ? 'bg-amber-600 text-white shadow-xs'
                          : 'text-amber-950 hover:text-amber-700 hover:bg-amber-50'
                      }`}
                    >
                      🇬🇧 English
                    </button>
                    <button
                      type="button"
                      onClick={() => setRulesLanguage('si')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        rulesLanguage === 'si'
                          ? 'bg-amber-600 text-white shadow-xs'
                          : 'text-amber-950 hover:text-amber-700 hover:bg-amber-50'
                      }`}
                    >
                      🇱🇰 සිංහල
                    </button>
                  </div>
                </div>
              </div>

              {result.source_discovery.length > 0 && (
                <section className="rounded-2xl border border-amber-300/80 bg-gradient-to-br from-amber-50/50 via-white to-amber-50/30 p-5 shadow-xs space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200/80 pb-3">
                    <div>
                      <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                        <i className="fa-solid fa-scale-balanced text-amber-600" />
                        {rulesLanguage === 'si'
                          ? 'අදාළ නීතිමය රීති සහ ආයතනික ක්‍රියාමාර්ග'
                          : 'Applicable Legal Rules & Institutional Actions'}
                      </h4>
                      <p className="mt-0.5 text-xs text-slate-600">
                        {rulesLanguage === 'si' ? (
                          <>
                            AI මඟින් පුරෝකථනය කළ ආයතනික මගපෙන්වීම:{' '}
                            <em>මෙම නීතියෙන් කුමක් සිදුවේද? ඔබ යා යුත්තේ කොතැනටද? ගත යුතු ක්‍රියාමාර්ගය කුමක්ද?</em>
                          </>
                        ) : (
                          <>
                            AI-predicted institutional guidance answering:{' '}
                            <em>What does this rule do? Where should you go? What action is required?</em>
                          </>
                        )}
                      </p>
                    </div>

                    <div className="flex flex-wrap items-center gap-2.5">
                      {/* Language Switcher for Rules & Institutional Actions */}
                      <div className="inline-flex rounded-xl bg-amber-100/80 p-0.5 border border-amber-300">
                        <button
                          type="button"
                          onClick={() => setRulesLanguage('en')}
                          className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                            rulesLanguage === 'en'
                              ? 'bg-amber-600 text-white shadow-xs'
                              : 'text-amber-950 hover:text-amber-700 hover:bg-amber-50'
                          }`}
                        >
                          🇬🇧 English
                        </button>
                        <button
                          type="button"
                          onClick={() => setRulesLanguage('si')}
                          className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                            rulesLanguage === 'si'
                              ? 'bg-amber-600 text-white shadow-xs'
                              : 'text-amber-950 hover:text-amber-700 hover:bg-amber-50'
                          }`}
                        >
                          🇱🇰 සිංහල
                        </button>
                      </div>

                      <span className="text-[11px] font-semibold text-amber-900 bg-amber-100 px-2.5 py-1 rounded-full border border-amber-200">
                        {rulesLanguage === 'si'
                          ? `හඳුනාගත් නීති සහ ප්‍රතිපත්ති ${result.source_discovery.length} කි`
                          : `${result.source_discovery.length} Identified Rules & Policies`}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {result.source_discovery.map((source, index) => {
                      const isSi = rulesLanguage === 'si';
                      return (
                      <article
                        key={`${source.source_id}-${source.page}-${index}`}
                        className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm space-y-3 transition-all hover:border-slate-300"
                      >
                        {/* Title and Identification Header */}
                        <div className="flex flex-wrap items-start justify-between gap-2 border-b border-slate-100 pb-2.5">
                          <div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200/60 mb-1 inline-block">
                              {isSi ? `නීතිමය මූලාශ්‍රය #${index + 1}` : `Statutory Source #${index + 1}`}
                            </span>
                            <h5 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                              <i className="fa-solid fa-book-bookmark text-slate-500 text-xs" />
                              {source.title}
                            </h5>
                            <p className="mt-0.5 text-[11px] text-slate-500">
                              {source.source_id}
                              {source.page
                                ? isSi
                                  ? ` · පිටුව ${source.page}`
                                  : ` · Page ${source.page}`
                                : source.section_reference
                                  ? ` · ${source.section_reference}`
                                  : ''}
                              {source.authority
                                ? isSi
                                  ? ` · බලධාරී ආයතනය: ${source.authority}`
                                  : ` · Authority: ${source.authority}`
                                : ''}
                            </p>
                          </div>

                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-[10px] font-semibold text-amber-800 bg-amber-50 px-2.5 py-1 rounded-full border border-amber-200">
                              {isSi
                                ? `තහවුරු කිරීම: ${
                                    source.verification_status === 'needs_verification'
                                      ? 'තහවුරු කරගත යුතුය'
                                      : source.verification_status === 'verified'
                                        ? 'තහවුරු කර ඇත'
                                        : 'කෙටුම්පත'
                                  }`
                                : `Verification: ${source.verification_status || 'Draft Template'}`}
                            </span>
                            <a
                              href={`${API_BASE}/api/v1/component2/legal-documents/${encodeURIComponent(source.source_file || source.source_id || source.title)}`}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 hover:text-blue-800 border border-blue-200 transition-colors shadow-xs"
                              title="View and download official Sri Lankan Act / Gazette / By-law (PDF)"
                            >
                              <i className="fa-solid fa-file-pdf text-red-500 text-xs" />
                              <span>{isSi ? 'නිල PDF ලේඛනය බලන්න' : 'View Official PDF'}</span>
                            </a>
                          </div>
                        </div>

                        {/* ML Action Guidance (Where to go, what it does, what to do) */}
                        {source.action_guidance && (
                          <div className="rounded-xl bg-slate-50/90 border border-slate-200 p-3.5 space-y-3 text-xs">
                            {/* 1. What this rule does */}
                            <div className="flex items-start gap-2.5">
                              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-amber-100 text-amber-800 text-xs shadow-xs mt-0.5">
                                <i className="fa-solid fa-lightbulb" />
                              </span>
                              <div>
                                <span className="font-bold text-slate-800 text-[11px] uppercase tracking-wide block">
                                  {isSi
                                    ? '1. මේ නීතියෙන් වෙන්නේ කුමක්ද? (නීතිමය අවශ්‍යතාව):'
                                    : '1. What This Rule Mandates:'}
                                </span>
                                <p className="text-slate-700 mt-0.5 leading-relaxed font-medium">
                                  {getRulePurposeText(
                                    source.action_guidance.rule_purpose,
                                    source.action_guidance.category,
                                    isSi
                                  )}
                                </p>
                              </div>
                            </div>

                            {/* 2. Where to Go */}
                            <div className="flex items-start gap-2.5">
                              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-800 text-xs shadow-xs mt-0.5">
                                <i className="fa-solid fa-building-columns" />
                              </span>
                              <div>
                                <span className="font-bold text-slate-800 text-[11px] uppercase tracking-wide block">
                                  {isSi
                                    ? '2. යන්න ඕනෙ ස්ථානය / කාර්යාලය කොහෙද? (අදාළ ආයතනය):'
                                    : '2. Where to Go / Target Office:'}
                                </span>
                                <p className="text-blue-900 font-bold mt-0.5">
                                  {getWhereToGoText(source.action_guidance.where_to_go, isSi)}
                                </p>
                                {source.action_guidance.office_location && source.action_guidance.office_location !== 'nan' && (
                                  <p className="text-slate-600 text-[11px] mt-0.5 flex items-center gap-1">
                                    <i className="fa-solid fa-location-dot text-red-500 text-[10px]" />
                                    {getOfficeLocationText(source.action_guidance.office_location, isSi)}
                                  </p>
                                )}
                              </div>
                            </div>

                            {/* 3. Action Needed */}
                            <div className="flex items-start gap-2.5">
                              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-800 text-xs shadow-xs mt-0.5">
                                <i className="fa-solid fa-file-circle-check" />
                              </span>
                              <div>
                                <span className="font-bold text-slate-800 text-[11px] uppercase tracking-wide block">
                                  {isSi
                                    ? '3. ගත යුතු ක්‍රියාමාර්ගය (අවශ්‍ය බලපත්‍රය / ලියාපදිංචිය):'
                                    : '3. Action Needed / Required Licence:'}
                                </span>
                                <p className="text-emerald-900 font-bold mt-0.5">
                                  {getActionNeededText(source.action_guidance.action_needed, isSi)}
                                </p>
                              </div>
                            </div>

                            {/* 4. Documents & Steps Sub-grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 pt-1 text-[11px]">
                              {/* Documents */}
                              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                                <span className="font-bold text-slate-700 block mb-1">
                                  <i className="fa-solid fa-folder-closed text-slate-500 mr-1" />
                                  {isSi
                                    ? 'ගෙනියන්න ඕනෙ ලියකියවිලි (Documents Checklist):'
                                    : 'Documents Checklist:'}
                                </span>
                                <ul className="space-y-1 text-slate-600">
                                  {source.action_guidance.required_documents.slice(0, 4).map((doc, dIdx) => (
                                    <li key={dIdx} className="flex items-start gap-1.5">
                                      <i className="fa-solid fa-check text-emerald-600 text-[10px] mt-0.5" />
                                      <span>{getDocumentText(doc, isSi)}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>

                              {/* Steps */}
                              <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                                <span className="font-bold text-slate-700 block mb-1">
                                  <i className="fa-solid fa-list-ol text-slate-500 mr-1" />
                                  {isSi
                                    ? 'පියවරෙන් පියවර (Procedural Steps):'
                                    : 'Procedural Steps:'}
                                </span>
                                <ol className="space-y-1 text-slate-600 list-decimal pl-3.5">
                                  {source.action_guidance.procedural_steps.slice(0, 3).map((st, sIdx) => (
                                    <li key={sIdx}>{getStepText(st, isSi)}</li>
                                  ))}
                                </ol>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Raw statutory excerpt (as secondary evidence quote) */}
                        <details className="text-[11px] text-slate-500">
                          <summary className="cursor-pointer hover:text-slate-800 font-medium">
                            <i className="fa-solid fa-quote-left text-slate-400 mr-1" />
                            {isSi
                              ? 'මූලාශ්‍ර ලේඛනයෙන් උපුටාගත් මුල් නීතිමය පාඨය බලන්න'
                              : 'View Raw Statutory Quote Excerpt from Source Document'}
                          </summary>
                          <blockquote className="mt-2 border-l-2 border-amber-300 pl-3 leading-relaxed text-slate-700 bg-amber-50/40 p-2 rounded-r-lg">
                            {source.excerpt}
                          </blockquote>
                        </details>
                      </article>
                      );
                    })}
                  </div>
                </section>
              )}

              <div className="compliance-summary-grid">
                <div className="compliance-summary-card applicable">
                  <strong>{result.summary.applicable}</strong><span>Applicable</span>
                </div>
                <div className="compliance-summary-card conditional">
                  <strong>{result.summary.unknown}</strong><span>Conditional / unknown</span>
                </div>
                <div className="compliance-summary-card needs-verification">
                  <strong>{result.summary.needs_verification}</strong><span>Needs verification</span>
                </div>
                <div className="compliance-summary-card not-applicable">
                  <strong>{result.summary.not_applicable}</strong><span>Not applicable</span>
                </div>
                <div className="compliance-summary-card total">
                  <strong>{result.summary.total}</strong><span>Reviewed</span>
                </div>
              </div>

              <div className="compliance-filter-row" aria-label="Filter requirements">
                {([
                  { id: 'all', label: 'All', count: result.summary.total },
                  { id: 'APPLICABLE', label: 'Applicable', count: result.summary.applicable },
                  { id: 'UNKNOWN', label: 'Unknown', count: result.summary.unknown },
                  { id: 'NEEDS_VERIFICATION', label: 'Needs verification', count: result.summary.needs_verification },
                  { id: 'NOT_APPLICABLE', label: 'Not applicable', count: result.summary.not_applicable },
                ] as const).map((filter) => (
                  <button
                    key={filter.id}
                    type="button"
                    className={`compliance-filter ${resultFilter === filter.id ? 'is-active' : ''}`}
                    onClick={() => setResultFilter(filter.id)}
                  >
                    {filter.label}<span>{filter.count}</span>
                  </button>
                ))}
              </div>

              <div className="space-y-3">
                {filteredObligations.map((obligation) => (
                  <ObligationCard
                    key={obligation.obligation_id}
                    obl={obligation}
                    onAnswerMissingFact={handleInlineAnswer}
                    onOpenEvidence={(id) => {
                      setSelectedObligationId(id);
                      setActiveStep('evidence');
                    }}
                  />
                ))}
                {filteredObligations.length === 0 && (
                  <div className="compliance-empty-state">No requirements match this filter.</div>
                )}
              </div>

              {/* Bottom Navigation on Page 3 */}
              <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-slate-200 shadow-xs mt-4">
                <button
                  type="button"
                  onClick={() => {
                    setResultsSubTab('registration');
                    window.scrollTo(0, 0);
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs transition-all cursor-pointer border border-slate-200"
                >
                  <i className="fa-solid fa-arrow-left text-xs" />
                  <span>
                    {guidanceLanguage === 'si'
                      ? '← ආපසු: ව්‍යාපාර ලියාපදිංචි මාර්ගෝපදේශය (Page 2)'
                      : '← Back to Registration Guidance (Page 2)'}
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveStep('profile')}
                  className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-xs border border-blue-200 transition-all cursor-pointer"
                >
                  <i className="fa-solid fa-pen-to-square text-xs" />
                  <span>{guidanceLanguage === 'si' ? 'ව්‍යාපාර පැතිකඩ සංස්කරණය' : 'Edit Business Profile'}</span>
                </button>
              </div>
            </div>
          )}

          {/* ============================================================= */}
          {/* PAGE 2: DEDICATED BUSINESS REGISTRATION GUIDANCE PAGE         */}
          {/* ============================================================= */}
          {resultsSubTab === 'registration' && result.registration_guidance && (
            <div className="space-y-4 animate-fade-in">
              {/* Page 2 Top Header Bar with Back Button */}
              <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3.5 rounded-2xl border border-blue-200 shadow-xs">
                <button
                  type="button"
                  onClick={() => {
                    setResultsSubTab('roadmap');
                    window.scrollTo(0, 0);
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 hover:text-slate-900 font-bold text-xs transition-all cursor-pointer border border-slate-200 shadow-2xs"
                >
                  <i className="fa-solid fa-arrow-left text-xs" />
                  <span>
                    {guidanceLanguage === 'si'
                      ? '← ආපසු: ක්‍රියාකාරී මාර්ග සිතියම (Back to Page 1)'
                      : '← Back to Compliance Roadmap (Page 1)'}
                  </span>
                </button>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-semibold text-blue-900 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                    📍 {guidanceLanguage === 'si'
                      ? `${getDistrictSinhala(result.registration_guidance.district)} දිස්ත්‍රික් බලප්‍රදේශය`
                      : `${result.registration_guidance.district} District Jurisdiction`}
                  </span>

                  {/* Language Switcher Toggle */}
                  <div className="inline-flex items-center bg-white p-0.5 rounded-xl border border-blue-300 shadow-2xs">
                    <button
                      type="button"
                      onClick={() => setGuidanceLanguage('en')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        guidanceLanguage === 'en'
                          ? 'bg-blue-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-blue-700 hover:bg-blue-50'
                      }`}
                    >
                      🇬🇧 English
                    </button>
                    <button
                      type="button"
                      onClick={() => setGuidanceLanguage('si')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                        guidanceLanguage === 'si'
                          ? 'bg-blue-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-blue-700 hover:bg-blue-50'
                      }`}
                    >
                      🇱🇰 සිංහල
                    </button>
                  </div>
                </div>
              </div>

              {/* Business Registration Guidance Card Content */}
              <section className="rounded-2xl border border-blue-200/90 bg-gradient-to-br from-blue-50/50 via-white to-indigo-50/30 p-5 shadow-xs space-y-5">
                {/* Header with Title and Registration Engine Badge */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-blue-200/70 pb-3.5">
                  <div className="flex items-center gap-2.5">
                    <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm text-sm">
                      <i className="fa-solid fa-landmark" />
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-sm font-bold text-slate-900">
                          {guidanceLanguage === 'si'
                            ? 'AI-මඟපෙන්වීම සහිත ව්‍යාපාර ලියාපදිංචි මාර්ග සිතියම සහ ආයතනික ක්‍රියාවලිය'
                            : 'AI-Assisted Business Registration Guidance & Institutional Roadmap'}
                        </h4>
                        <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-bold text-blue-800">
                          <i className="fa-solid fa-brain text-[9px]" /> {guidanceLanguage === 'si' ? 'ලියාපදිංචි පද්ධතිය' : 'Registration Engine'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600">
                        {guidanceLanguage === 'si'
                          ? 'බස්නාහිර පළාත් නීති රාමුව (1990 අංක 04 දරන ප්‍රඥප්තිය සහ 2007 අංක 07 දරන සමාගම් පනත)'
                          : 'Western Province Legal Framework (Statute No. 04 of 1990 & Companies Act No. 07 of 2007)'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Official Export & PDF Generation Banner */}
                <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-blue-200 shadow-xs">
                  <div className="flex items-center gap-3">
                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs">
                      <i className="fa-solid fa-file-pdf text-base text-red-500" />
                    </span>
                    <div>
                      <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                        {guidanceLanguage === 'si' ? 'නිල නීතිමය ලියකියවිලි කට්ටලය' : 'Official Regulatory Documentation Packages'}
                        <span className="text-[9px] uppercase font-extrabold bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded border border-emerald-200">
                          {guidanceLanguage === 'si' ? 'මුද්‍රණයට සූදානම්' : 'Print-Ready'}
                        </span>
                      </span>
                      <p className="text-[11px] text-slate-500">
                        {guidanceLanguage === 'si'
                          ? 'ලියාපදිංචිය සඳහා අවශ්‍ය නිල අනුකූලතා ලේඛන සහ නියමිත අයදුම්පත් සම්පූර්ණ කර බාගත කරන්න.'
                          : 'Generate formal, submission-ready compliance documentation and official application forms.'}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={handleDownloadDossier}
                      disabled={isDownloadingDossier}
                      className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs shadow-xs transition-all disabled:opacity-50 cursor-pointer"
                    >
                      <i className={`fa-solid ${isDownloadingDossier ? 'fa-spinner fa-spin' : 'fa-file-shield'}`} />
                      <span>
                        {isDownloadingDossier
                          ? (guidanceLanguage === 'si' ? 'සකස් කරමින් පවතී...' : 'Generating Dossier...')
                          : (guidanceLanguage === 'si' ? 'අනුකූලතා ලියකියවිලි (PDF) බාගත කරන්න' : 'Download Compliance Dossier (PDF)')}
                      </span>
                    </button>
                  </div>
                </div>

                {/* 1. Legal Form Recommendation & Office Routing Banner */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 text-xs">
                  {/* Legal Form */}
                  <div className="bg-white p-3.5 rounded-xl border border-blue-100 shadow-xs space-y-1.5">
                    <span className="block font-bold text-slate-500 uppercase tracking-wider text-[10px]">
                      <i className="fa-solid fa-scale-balanced text-blue-600 mr-1" />
                      {guidanceLanguage === 'si' ? 'නිර්දේශිත නීතිමය ස්වරූපය' : 'Recommended Legal Form'}
                    </span>
                    <p className="font-bold text-blue-950 text-xs">
                      {guidanceLanguage === 'si'
                        ? (result.registration_guidance.pathway_key === 'partnership'
                            ? 'හවුල් ව්‍යාපාරය (Partnership)'
                            : result.registration_guidance.pathway_key === 'private_limited'
                            ? 'පුද්ගලික සීමිත සමාගම (Pvt Ltd)'
                            : 'තනි පුද්ගල ව්‍යාපාරය (Sole Proprietorship)')
                        : stripSinhalaText(result.registration_guidance.recommended_legal_form)}
                    </p>
                    <p className="text-[10px] text-slate-500 font-medium">
                      {guidanceLanguage === 'si'
                        ? (result.registration_guidance.pathway_key === 'private_limited'
                            ? '2007 අංක 07 දරන සමාගම් පනත (eROC ඔස්සේ)'
                            : '1990 අංක 04 දරන බස්නාහිර පළාත් ව්‍යාපාර නාම ප්‍රඥප්තිය (3 වන වගන්තිය)')
                        : result.registration_guidance.legal_basis}
                    </p>
                    <p className="text-[11px] text-slate-700 leading-relaxed bg-blue-50/50 p-2 rounded-lg border border-blue-100/60 mt-1">
                      {guidanceLanguage === 'si'
                        ? (result.registration_guidance.pathway_key === 'partnership'
                            ? 'සහභාගී වන හවුල්කරුවන්ගේ නම් සහ වගකීම් සහිතව පළාත් සභා ප්‍රඥප්තිය යටතේ ලියාපදිංචිය හිමිවේ.'
                            : result.registration_guidance.pathway_key === 'private_limited'
                            ? 'සීමිත වගකීම් සහ අධ්‍යක්ෂ මණ්ඩල ව්‍යුහය සහිතව කොළඹ සමාගම් රෙජිස්ට්‍රාර් වෙතින් සංස්ථාගත කිරීම නිර්දේශ කෙරේ.'
                            : 'තනි හිමිකරු යටතේ සරල නීතිමය වගකීම් සහිතව ප්‍රාදේශීය ලේකම් කාර්යාලය හරහා ලියාපදිංචි සහතිකය ලබාගත හැක.')
                        : result.registration_guidance.recommendation_reason}
                    </p>
                  </div>

                  {/* Competent Office */}
                  <div className="bg-white p-3.5 rounded-xl border border-blue-100 shadow-xs space-y-1.5">
                    <span className="block font-bold text-slate-500 uppercase tracking-wider text-[10px]">
                      <i className="fa-solid fa-building-columns text-blue-600 mr-1" />
                      {guidanceLanguage === 'si' ? 'අයදුම්පත් භාරදෙන නිල කාර්යාලය' : 'Competent Lodgement Office'}
                    </span>
                    <p className="font-bold text-blue-950 text-xs">
                      {guidanceLanguage === 'si'
                        ? (result.registration_guidance.pathway_key === 'private_limited'
                            ? 'සමාගම් රෙජිස්ට්‍රාර් දෙපාර්තමේන්තුව (eROC, කොළඹ 10)'
                            : `${getDistrictSinhala(result.registration_guidance.district)} ප්‍රාදේශීය ලේකම් කාර්යාලය (ව්‍යාපාර නාම අංශය)`)
                        : stripSinhalaText(result.registration_guidance.competent_office)}
                    </p>
                    <p className="text-[11px] text-slate-600 leading-relaxed bg-slate-50 p-2 rounded-lg border border-slate-100 mt-1">
                      {guidanceLanguage === 'si'
                        ? `${getDistrictSinhala(result.registration_guidance.district)} දිස්ත්‍රික්කයේ ව්‍යාපාරික පරිශ්‍රය පිහිටි ප්‍රාදේශීය ලේකම් කොට්ඨාස කාර්යාලයට හෝ eROC පද්ධතියට ලේඛන යොමු කරන්න.`
                        : result.registration_guidance.office_address}
                    </p>
                  </div>

                  {/* Timeline & Statutory Fee */}
                  <div className="bg-white p-3.5 rounded-xl border border-blue-100 shadow-xs space-y-1.5">
                    <span className="block font-bold text-slate-500 uppercase tracking-wider text-[10px]">
                      <i className="fa-solid fa-clock text-blue-600 mr-1" />
                      {guidanceLanguage === 'si' ? 'ඇස්තමේන්තුගත කාලය සහ ගාස්තු' : 'Timeline & Estimated Fees'}
                    </span>
                    <p className="font-bold text-blue-950 text-xs">
                      {guidanceLanguage === 'si' ? 'වැඩකරන දින 1 - 3 ඇතුළත' : result.registration_guidance.timeline_estimate}
                    </p>
                    <p className="text-[10px] text-slate-500">
                      {guidanceLanguage === 'si'
                        ? (result.registration_guidance.pathway_key === 'private_limited'
                            ? 'eROC නාම අනුමැතිය සහ සංස්ථාගත කිරීමේ රජයේ ගාස්තු අදාළ වේ.'
                            : '1990 අංක 04 දරන බස්නාහිර පළාත් සභා ප්‍රඥප්තිය යටතේ නියමිත මුද්දර ගාස්තු.')
                        : result.registration_guidance.statutory_fee_estimate}
                    </p>
                    <div className="p-2 bg-emerald-50 rounded-lg border border-emerald-100 text-[11px] text-emerald-900 font-semibold mt-1 flex items-center gap-1.5">
                      <i className="fa-solid fa-circle-check text-emerald-600 text-xs" />
                      <span>{guidanceLanguage === 'si' ? 'පූර්ව පරීක්ෂාව සාර්ථකයි' : 'Prerequisites Verified'}</span>
                    </div>
                  </div>
                </div>

                {/* 2. 5-Stage Chronological Roadmap */}
                <div className="space-y-2.5 pt-1">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-slate-900 flex items-center gap-2">
                      <i className="fa-solid fa-list-ol text-blue-600" />
                      {guidanceLanguage === 'si'
                        ? 'පියවරෙන් පියවර නිල ලියාපදිංචි කිරීමේ ක්‍රියාවලිය'
                        : '5-Stage Official Registration Procedure'}
                    </h5>
                    <span className="text-[10px] font-medium text-slate-500">
                      {guidanceLanguage === 'si' ? 'කාලානුක්‍රමික පියවර 5' : 'Chronological Flow'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5">
                    {result.registration_guidance.stages.map((stg) => {
                      const tr = STAGE_TRANSLATIONS[stg.stage_number];
                      const isSi = guidanceLanguage === 'si';
                      const stageTitle = isSi ? (tr?.title_si || stg.title_si || stg.title) : (tr?.title_en || stripSinhalaText(stg.title));
                      const stageAction = isSi ? (tr?.action_si || stg.action) : (tr?.action_en || stg.action);
                      const stageDuration = isSi ? (tr?.duration_si || stg.duration) : (tr?.duration_en || stg.duration);
                      const stageFee = isSi ? (tr?.fee_si || stg.statutory_fee) : (tr?.fee_en || stg.statutory_fee);

                      return (
                        <div
                          key={stg.stage_number}
                          className="bg-white rounded-xl border border-slate-200 p-3 shadow-2xs space-y-2 flex flex-col justify-between hover:border-blue-300 transition-all"
                        >
                          <div className="space-y-1.5">
                            <div className="flex items-center justify-between">
                              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-blue-800 font-extrabold text-[10px]">
                                {stg.stage_number}
                              </span>
                              <span className="text-[9px] font-semibold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                                {stageDuration}
                              </span>
                            </div>

                            <h6 className="font-bold text-slate-900 text-[11px] leading-tight">
                              {stageTitle}
                            </h6>
                            <p className="text-[10px] text-slate-600 leading-relaxed pt-1">
                              {stageAction}
                            </p>
                          </div>

                          <div className="pt-2 border-t border-slate-100 text-[9px] text-slate-500">
                            <span className="block font-semibold text-slate-700">
                              {isSi ? `ගාස්තුව: ${stageFee}` : `Fee: ${stageFee}`}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* 3. Document Readiness Audit & Form 1 Completion Assistant Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-1">
                  {/* Document Readiness Checklist */}
                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                      <h5 className="font-bold text-slate-900 text-xs flex items-center gap-2">
                        <i className="fa-solid fa-folder-closed text-blue-600" />
                        {guidanceLanguage === 'si' ? 'ලියාපදිංචියට පෙර ලියකියවිලි සූදානම පරීක්ෂාව' : 'Pre-Filing Document Readiness Audit'}
                      </h5>
                      <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {guidanceLanguage === 'si'
                          ? `${getDistrictSinhala(result.registration_guidance.district)} දිස්ත්‍රික්කය සඳහා තහවුරු කරන ලදී`
                          : `Verified for ${result.registration_guidance.district}`}
                      </span>
                    </div>

                    <div className="space-y-2">
                      {result.registration_guidance.document_checklist.map((doc) => {
                        const isSi = guidanceLanguage === 'si';
                        const docName = isSi ? (doc.name_si || doc.name) : stripSinhalaText(doc.name);
                        const docPurpose = isSi ? (DOC_PURPOSE_SINHALA[doc.document_id] || doc.purpose) : doc.purpose;

                        return (
                          <div
                            key={doc.document_id}
                            className="p-2.5 rounded-lg border border-slate-100 bg-slate-50/70 flex items-start justify-between gap-2.5 text-xs"
                          >
                            <div className="flex items-start gap-2.5">
                              <i className="fa-solid fa-file-lines text-blue-600 text-xs mt-0.5" />
                              <div>
                                <p className="font-bold text-slate-800 text-xs">{docName}</p>
                                <p className="text-[11px] text-slate-500 mt-0.5">{docPurpose}</p>
                              </div>
                            </div>
                            <span
                              className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded shrink-0 ${
                                doc.is_mandatory
                                  ? 'bg-rose-50 text-rose-700 border border-rose-200'
                                  : 'bg-slate-100 text-slate-600'
                              }`}
                            >
                              {isSi ? (doc.is_mandatory ? 'අනිවාර්යයි' : 'විකල්ප') : (doc.is_mandatory ? 'Mandatory' : 'Optional')}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Pre-fill Form 1 Assistant */}
                  <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                      <h5 className="font-bold text-slate-900 text-xs flex items-center gap-2">
                        <i className="fa-solid fa-pen-to-square text-teal-600" />
                        {guidanceLanguage === 'si' ? 'ආකෘති පත්‍රය සම්පූර්ණ කිරීමේ මඟපෙන්වීම' : 'Application Completion Assistant'}
                      </h5>
                      <span className="text-[10px] font-semibold text-slate-500">
                        {guidanceLanguage === 'si'
                          ? 'බස්නාහිර පළාත් සභා ආකෘති පත්‍රය'
                          : stripSinhalaText(result.registration_guidance.official_form_name.split('(')[0])}
                      </span>
                    </div>

                    <div className="space-y-2 text-xs">
                      {result.registration_guidance.form_fields_guide.map((field, fIdx) => {
                        const isSi = guidanceLanguage === 'si';
                        const guideSi = FORM_GUIDE_SINHALA[fIdx];
                        const fieldLabel = isSi ? (guideSi?.label || field.field_label) : stripSinhalaText(field.field_label);
                        const fieldDesc = isSi ? (guideSi?.desc || field.description) : field.description;

                        return (
                          <div key={fIdx} className="bg-slate-50/80 p-2.5 rounded-lg border border-slate-100 space-y-0.5">
                            <span className="font-bold text-slate-800 text-[11px] block">
                              {fieldLabel}
                            </span>
                            <p className="text-[10px] text-slate-500">
                              {fieldDesc}
                            </p>
                            <div className="mt-1 flex items-center gap-1.5 bg-white px-2 py-1 rounded border border-slate-200 text-[11px] text-slate-700 font-medium">
                              <span className="text-[9px] uppercase font-bold text-teal-700 bg-teal-50 px-1 py-0.5 rounded border border-teal-200">
                                {isSi ? 'යෝජිත අගය' : 'Suggested Value'}
                              </span>
                              <span className="truncate">{field.suggested_value}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </section>

              {/* Bottom Navigation on the Registration Page */}
              <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                <button
                  type="button"
                  onClick={() => {
                    setResultsSubTab('roadmap');
                    window.scrollTo(0, 0);
                  }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs transition-all cursor-pointer border border-slate-200"
                >
                  <i className="fa-solid fa-arrow-left text-xs" />
                  <span>
                    {guidanceLanguage === 'si'
                      ? '← ආපසු: ක්‍රියාකාරී මාර්ග සිතියම (Back)'
                      : 'Back to Compliance Roadmap'}
                  </span>
                </button>

                {/* Next Button: Proceed to Applicable Legal Rules & Institutional Actions (Page 3) */}
                <button
                  type="button"
                  onClick={() => {
                    setResultsSubTab('legal_rules');
                    window.scrollTo(0, 0);
                  }}
                  className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 active:scale-95 text-white font-bold text-xs shadow-md hover:shadow-lg transition-all cursor-pointer group"
                >
                  <span>
                    {guidanceLanguage === 'si'
                      ? 'ඊළඟ පිටුව: අදාළ නීතිමය රීති සහ ආයතනික ක්‍රියාමාර්ග (Page 3) →'
                      : 'Next: Applicable Legal Rules & Institutional Actions (Page 3) →'}
                  </span>
                  <i className="fa-solid fa-arrow-right text-xs transition-transform group-hover:translate-x-1" />
                </button>
              </div>
            </div>
          )}
            </section>

            {resultsSubTab === "legal_rules" && (
            <aside className="compliance-side-panel">
              <section className="compliance-side-card">
                <p className="compliance-eyebrow">Answers to resolve</p>
                {followUpFacts.length > 0 ? (
                  <div className="compliance-followups">
                    {followUpFacts.map((factKey) => {
                      const obligationCount = unknownList.filter((obligation) =>
                        obligation.missing_facts.includes(factKey)
                      ).length;
                      return (
                        <div className="compliance-followup" key={factKey}>
                          <InlineAnswerControl factKey={factKey} onAnswer={handleInlineAnswer} />
                          <small>May clarify {obligationCount} {obligationCount === 1 ? 'requirement' : 'requirements'}</small>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="compliance-side-copy">No unanswered facts are currently blocking a decision.</p>
                )}
                <p className="compliance-side-copy">Questions are based on missing facts in the rule results. “Not sure” keeps a fact unknown.</p>
                <button type="button" className="compliance-secondary-button" onClick={() => setActiveStep('profile')}>
                  <i className="fa-solid fa-arrow-left mr-2" />Edit profile
                </button>
              </section>
            </aside>
            )}
          </div>
        )}

        {activeStep === 'evidence' && result && selectedObligation && (
          <div className="compliance-evidence-layout">
            <section className="compliance-evidence-main">
              <button type="button" className="compliance-back-link" onClick={() => setActiveStep('results')}>
                <i className="fa-solid fa-arrow-left mr-2" />Back to results
              </button>
              <div className="compliance-evidence-heading">
                <div>
                  <p className="compliance-eyebrow">Requirement evidence</p>
                  <h2>{selectedObligation.title}</h2>
                </div>
                <StatusBadge status={selectedObligation.status} />
              </div>

              <div className="compliance-fact-table">
                {Object.entries(selectedObligation.triggering_facts).map(([fact, value]) => (
                  <div key={fact}><span>{FACT_DISPLAY_LABELS[fact] || fact}</span><strong>{String(value)}</strong></div>
                ))}
                {selectedObligation.missing_facts.map((fact) => (
                  <div key={fact}><span>{FACT_DISPLAY_LABELS[fact] || fact}</span><strong className="is-unknown">Unknown</strong></div>
                ))}
                {Object.keys(selectedObligation.triggering_facts).length === 0 && selectedObligation.missing_facts.length === 0 && (
                  <div><span>Evaluation</span><strong>No triggering or missing facts were returned.</strong></div>
                )}
              </div>

              <section className="compliance-evidence-section">
                  <p className="compliance-eyebrow">
                    {selectedObligation.status === 'NEEDS_VERIFICATION' ? 'Verification required' : 'What to do'}
                  </p>
                  <p>{selectedObligation.action || (
                    selectedObligation.status === 'NEEDS_VERIFICATION'
                      ? 'No compliance action is recommended until the source and requirement are verified.'
                      : 'Confirm the process with the relevant authority.'
                  )}</p>
                <p className="compliance-next-action"><strong>Next action:</strong> {selectedObligation.next_action}</p>
                {selectedObligation.registration_steps.length > 0 && (
                  <ol>
                    {selectedObligation.registration_steps.map((step, index) => <li key={index}>{step}</li>)}
                  </ol>
                )}
                {selectedObligation.documents_needed.length > 0 && (
                  <div className="compliance-documents">
                    <p className="compliance-eyebrow">Documents noted by the rulebook</p>
                    <ul>{selectedObligation.documents_needed.map((document, index) => <li key={index}>{document}</li>)}</ul>
                    {selectedObligation.documents_notice && <small>{selectedObligation.documents_notice}</small>}
                  </div>
                )}
              </section>

              <section className="compliance-quote-card">
                <div className="compliance-quote-meta">
                  <span>{selectedObligation.source_id} · {selectedObligation.source_paragraph}</span>
                  <span className={selectedObligation.has_verified_source ? 'is-verified' : 'is-draft'}>
                    <i className={`fa-solid ${selectedObligation.has_verified_source ? 'fa-circle-check' : 'fa-triangle-exclamation'} mr-1`} />
                    {selectedObligation.has_verified_source ? 'Citation verified' : 'Draft · expert review pending'}
                  </span>
                </div>
                {selectedObligation.source_text ? (
                  <blockquote>“{selectedObligation.source_text}”</blockquote>
                ) : (
                  <p className="compliance-side-copy">No matching source excerpt is available in the local corpus.</p>
                )}
              </section>
            </section>

            <aside className="compliance-side-panel">
              <section className="compliance-side-card">
                <p className="compliance-eyebrow">
                  {selectedObligation.status === 'NEEDS_VERIFICATION' ? 'Potential authority — unverified' : 'Authority'}
                </p>
                <p className="compliance-authority">{selectedObligation.authority || 'Relevant local authority'}</p>
                <p className="compliance-eyebrow">Status</p>
                <StatusBadge status={selectedObligation.status} />
                <p className="compliance-side-copy">
                  {selectedObligation.has_verified_source
                    ? 'This evidence is marked as verified in the local source register.'
                    : 'This source reference is not independently verified. Confirm details with the relevant authority.'}
                </p>
                <div className="compliance-source-id">
                  <span>Obligation</span><strong>{selectedObligation.obligation_id}</strong>
                  <span>Source reference</span><strong>{selectedObligation.source_id} · {selectedObligation.source_paragraph}</strong>
                  <span>Rule priority</span><strong>{selectedObligation.priority}</strong>
                </div>
              </section>
            </aside>
          </div>
        )}

        {result && (
          <div className="compliance-disclaimer">
            <i className="fa-solid fa-scale-balanced" />
            <span>{result.disclaimer}</span>
          </div>
        )}
      </main>
    </div>
  );
};

export default RegistrationComplianceDashboard;
