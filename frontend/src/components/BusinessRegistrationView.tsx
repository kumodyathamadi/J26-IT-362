import React, { useState } from 'react';

export interface BrFormData {
  business_name: string;
  legal_form: 'sole_proprietorship' | 'partnership' | 'private_limited';
  sector: string;
  district: string;
  province: string;
  local_authority: string;
  divisional_secretariat: string;
  grama_niladhari: string;
  address: string;
  activities: string[];
  products_services: string[];
  employee_count: number;
  revenue: number;
  initial_capital: number;
  owner_name: string;
  owner_nic: string;
  phone: string;
  email: string;
  residence_address: string;
  commencement_date: string;
}

const EMPTY_FORM_DATA: BrFormData = {
  business_name: '',
  legal_form: 'sole_proprietorship',
  sector: '',
  district: 'Colombo',
  province: 'Western Province',
  local_authority: 'Colombo Municipal Council',
  divisional_secretariat: 'Thimbirigasyaya Divisional Secretariat',
  grama_niladhari: '',
  address: '',
  activities: [],
  products_services: [],
  employee_count: 0,
  revenue: 0,
  initial_capital: 0,
  owner_name: '',
  owner_nic: '',
  phone: '',
  email: '',
  residence_address: '',
  commencement_date: '',
};

const EMPTY_STAGE_1 = {
  alt_name_1: '',
  alt_name_2: '',
  name_meaning: '',
  language_scripts: 'English & Sinhala',
  search_date: new Date().toISOString().split('T')[0],
  reservation_period: '3 Months (Statutory Validity under WP Statute Sec. 4)',
};

const EMPTY_STAGE_2 = {
  ownership_type: 'commercial_lease',
  landlord_name: '',
  landlord_phone: '',
  deed_lease_no: '',
  electoral_no: '',
  house_no: '',
  residence_duration: '',
  inspection_readiness: '',
};

const EMPTY_STAGE_4 = {
  assessment_no: '',
  trade_category: '',
  floor_area: '',
  fire_safety: '',
  phi_division: '',
  food_handlers_certified: 0,
  waste_disposal: '',
  license_year: '2026 / 2027',
  br_certificate_no: '',
};

const EMPTY_STAGE_5 = {
  taxpayer_type: 'Sole Proprietorship Enterprise',
  ird_unit: '',
  tin_status: 'New RAMIS TIN Application Required',
  labour_office: '',
  monthly_payroll: 0,
  epf_status: 'Mandatory Form D Employer Registration (12% + 8%)',
  etf_status: 'Mandatory 3% Employer Contribution',
  bank_name: '',
  bank_branch: '',
  bank_account: '',
};

const EMPTY_CHECKLISTS: Record<number, Record<string, boolean>> = {
  1: { s1_form: false, s1_nic: false, s1_meaning: false, s1_fee: false },
  2: { s2_deed: false, s2_consent: false, s2_utility: false, s2_electoral: false, s2_nic: false },
  3: { s3_form1: false, s3_gn_rep: false, s3_nic: false, s3_deed: false, s3_duty: false },
  4: { s4_br: false, s4_rates: false, s4_phi: false, s4_plan: false, s4_fire: false },
  5: { s5_br_copy: false, s5_tin_slip: false, s5_labour_d: false, s5_staff_list: false, s5_bank: false },
};

const SAMPLE_PRESETS: Record<string, BrFormData> = {
  bakery: {
    business_name: 'CEYLON ARTISAN BAKEHOUSE',
    legal_form: 'sole_proprietorship',
    sector: 'Food Manufacturing & Bakery Products',
    district: 'Colombo',
    province: 'Western Province',
    local_authority: 'Colombo Municipal Council',
    divisional_secretariat: 'Thimbirigasyaya Divisional Secretariat',
    grama_niladhari: 'Havelock Town (GN Division 512)',
    address: 'No. 45, Galle Road, Colombo 04',
    activities: ['Baking bread and pastries', 'Cooked meals preparation', 'Retail sales'],
    products_services: ['Artisan Sourdough', 'Cakes & Pastries', 'Cooked Breakfast Snacks', 'Tea & Coffee'],
    employee_count: 5,
    revenue: 4200000,
    initial_capital: 1500000,
    owner_name: 'Dhananjaya Bandara',
    owner_nic: '199415802345',
    phone: '+94 77 123 4567',
    email: 'dhananjaya.bakes@sme.lk',
    residence_address: 'No. 12/B, Flower Road, Colombo 07',
    commencement_date: '2026-11-01',
  },
  clothing: {
    business_name: 'URBAN THREAD BOUTIQUE',
    legal_form: 'sole_proprietorship',
    sector: 'Textile & Garment Retail',
    district: 'Colombo',
    province: 'Western Province',
    local_authority: 'Colombo Municipal Council',
    divisional_secretariat: 'Colombo Divisional Secretariat',
    grama_niladhari: 'Kollupitiya (GN Division 504)',
    address: 'No. 88, Dharmapala Mawatha, Colombo 03',
    activities: ['Ready-made garment retail', 'Custom tailoring', 'Online fashion orders'],
    products_services: ['Casual Wear', 'Office Trousers', 'Dresses & Sarees', 'Bespoke Tailoring'],
    employee_count: 3,
    revenue: 3500000,
    initial_capital: 1200000,
    owner_name: 'Anoma Senanayake',
    owner_nic: '198965401234',
    phone: '+94 71 987 6543',
    email: 'anoma.threads@fashion.lk',
    residence_address: 'No. 24, Station Road, Dehiwala',
    commencement_date: '2026-11-15',
  },
  salon: {
    business_name: 'GLAMOUR & GLOW UNISEX SALON',
    legal_form: 'partnership',
    sector: 'Personal Care & Beauty Services',
    district: 'Colombo',
    province: 'Western Province',
    local_authority: 'Kotte Municipal Council',
    divisional_secretariat: 'Sri Jayawardenepura Kotte DS',
    grama_niladhari: 'Rajagiriya North (GN Division 518)',
    address: 'No. 112, Kotte Road, Rajagiriya',
    activities: ['Hair cutting and styling', 'Cosmetic chemical treatments', 'Skin care & bridal dressing'],
    products_services: ['Hair Styling', 'Facials & Skin Care', 'Bridal Dressing Packages', 'Nail Art'],
    employee_count: 4,
    revenue: 3800000,
    initial_capital: 1800000,
    owner_name: 'Kavindi Perera & Partners',
    owner_nic: '199587402198',
    phone: '+94 77 456 7890',
    email: 'kavindi.glamour@gmail.com',
    residence_address: 'No. 78, Nawala Road, Rajagiriya',
    commencement_date: '2026-12-01',
  },
  vehicle: {
    business_name: 'LANKA AUTO GEAR & REPAIRS',
    legal_form: 'sole_proprietorship',
    sector: 'Vehicle Parts & Repair Workshop',
    district: 'Gampaha',
    province: 'Western Province',
    local_authority: 'Gampaha Municipal Council',
    divisional_secretariat: 'Gampaha Divisional Secretariat',
    grama_niladhari: 'Yakkala South (GN Division 204)',
    address: 'No. 15, Kandy Road, Yakkala, Gampaha',
    activities: ['Auto mechanical repair', 'Spare parts retail', 'Spent lubricant & battery handling'],
    products_services: ['Brake Pads & Belts', 'Motor Lubricants', 'Engine Diagnostics', 'Battery Replacements'],
    employee_count: 6,
    revenue: 5500000,
    initial_capital: 2500000,
    owner_name: 'Sunil Weerasinghe',
    owner_nic: '198212304567',
    phone: '+94 70 333 4455',
    email: 'sunil.autogear@sme.lk',
    residence_address: 'No. 5, Temple Road, Yakkala',
    commencement_date: '2026-11-10',
  },
};

interface RoadmapStep {
  step: number;
  title: string;
  title_si: string;
  auth: string;
  time: string;
  fee: string;
  icon: string;
  desc: string;
  mandatory_docs: string[];
  statutory_form: string;
  official_portal?: string;
  pro_tip: string;
}

interface EntityRoadmapConfig {
  entity_label: string;
  entity_label_si: string;
  badge: string;
  badge_color: string;
  statute: string;
  governing_body: string;
  filing_portal: string;
  est_timeline: string;
  est_cost: string;
  description: string;
  steps: RoadmapStep[];
}

const ROADMAP_DATA_BY_ENTITY: Record<'sole_proprietorship' | 'partnership' | 'private_limited', EntityRoadmapConfig> = {
  sole_proprietorship: {
    entity_label: 'Sole Proprietorship',
    entity_label_si: 'තනි පුද්ගල ව්‍යාපාරය',
    badge: 'Western Province Individual Enterprise',
    badge_color: 'bg-teal-100 text-teal-800 border-teal-200',
    statute: 'Western Province Business Names Statute No. 04 of 1990',
    governing_body: 'Divisional Secretariat (Business Names Division)',
    filing_portal: 'Divisional Secretariat Office (Based on business location)',
    est_timeline: '4 - 8 Days',
    est_cost: 'LKR 5,750 - 11,000 (Govt Duty + Municipal)',
    description: 'Direct individual owner liability and sole authority. Registration is completed directly through the local Divisional Secretariat and local municipal council.',
    steps: [
      {
        step: 1,
        title: 'Name Search & Clearance',
        title_si: 'ව්‍යාපාර නාමය සෙවීම සහ අනුමැතිය',
        auth: 'Divisional Secretariat',
        time: '1 Day',
        fee: 'LKR 250 - 500',
        icon: 'fa-magnifying-glass',
        desc: 'Submit the proposed trading name at the Divisional Secretariat to confirm that the name is not identical, deceptively similar, or legally restricted under WP Business Names Statute Section 4.',
        mandatory_docs: [
          'Proposed Business Name Query Form (WP/BN/01)',
          'Applicant National Identity Card (NIC) Photocopy',
        ],
        statutory_form: 'Business Name Inquiry Slip',
        official_portal: 'Divisional Secretariat — Business Names Counter',
        pro_tip: 'Avoid prohibited words such as "State", "President", or single generic dictionary words without distinguishing prefixes.',
      },
      {
        step: 2,
        title: 'Grama Niladhari Report',
        title_si: 'ග්‍රාම නිලධාරී පරීක්ෂාව සහ වාර්තාව',
        auth: 'Grama Niladhari Officer',
        time: '1 - 2 Days',
        fee: 'Free (Statutory Duty)',
        icon: 'fa-user-check',
        desc: 'The GN Officer visits and inspects the physical business premises, confirms applicant residence within the division, and verifies property ownership or commercial lease deed.',
        mandatory_docs: [
          'Deed of Ownership or Stamped Commercial Lease Agreement',
          'Electoral Register confirmation or recent Utility Bill',
          'Applicant Certified NIC copy',
        ],
        statutory_form: 'GN Residence & Premises Assessment Report (වසමේ වාර්තාව)',
        official_portal: 'Local Grama Niladhari Office (අදාළ ග්‍රාම නිලධාරී වසම)',
        pro_tip: 'If operating from a rented building, ensure the property owner signs a written consent letter or tenancy contract with valid revenue stamps.',
      },
      {
        step: 3,
        title: 'Statutory Form 1 Filing',
        title_si: 'Form 1 අයදුම්පත භාරදීම සහ BR සහතිකය',
        auth: 'Department of Business Names',
        time: '1 - 3 Days',
        fee: 'LKR 2,500',
        icon: 'fa-file-signature',
        desc: 'Submit the completed Form 1 Statement of Particulars to the Divisional Secretary. Upon inspection of submitted documents, the official Business Registration Certificate (BR) is issued.',
        mandatory_docs: [
          'Completed & Signed Form 1 Statement of Particulars',
          'Original GN Inspection Assessment Report',
          'Certified copy of Applicant NIC (certified by JP / Attorney)',
          'Registered Deed / Tenancy Agreement copy',
        ],
        statutory_form: 'Form 1 (Statement of Particulars - Individual)',
        official_portal: 'Divisional Secretariat — Business Registration Unit',
        pro_tip: 'Display the original laminated Business Registration certificate visibly inside your retail premises for local authority inspections.',
      },
      {
        step: 4,
        title: 'Municipal Trade Tax & Health Clearance',
        title_si: 'නගර සභා වෙළඳ බද්ද සහ සෞඛ්‍ය බලපත්‍රය',
        auth: 'Municipal / Urban Council (e.g., CMC, KMC)',
        time: '2 - 5 Days',
        fee: 'LKR 3,000 - 8,000',
        icon: 'fa-city',
        desc: 'Register under Municipal Council By-Laws to obtain commercial trade tax clearance and public health inspection pass (PHI food hygiene pass for food establishments or salons).',
        mandatory_docs: [
          'Certified copy of Business Registration (BR) Certificate',
          'Municipal Assessment Rates payment receipt',
          'Store floor plan / Layout sketch',
        ],
        statutory_form: 'Municipal Trade Tax & Licence Application',
        official_portal: 'Relevant Municipal Council / Urban Council Office',
        pro_tip: 'Food businesses must coordinate with the local Public Health Inspector (PHI) for kitchen hygiene and medical fitness passes for handlers.',
      },
      {
        step: 5,
        title: 'RAMIS TIN & Labour EPF/ETF',
        title_si: 'TIN අංකය සහ සේවක ලියාපදිංචිය',
        auth: 'Inland Revenue & Labour Dept',
        time: '1 - 3 Days',
        fee: 'Free Registration',
        icon: 'fa-receipt',
        desc: 'Obtain mandatory individual Taxpayer Identification Number (TIN) via IRD RAMIS portal. If hiring one or more employees, register with Department of Labour for EPF/ETF contributions.',
        mandatory_docs: [
          'Individual NIC & BR Certificate copy',
          'RAMIS Online Registration submission',
          'Employee list with NICs and wage schedule (if hiring)',
        ],
        statutory_form: 'RAMIS Taxpayer Registration & Labour Form D',
        official_portal: 'Inland Revenue RAMIS (www.ird.gov.lk) & Labour Dept',
        pro_tip: 'Opening a commercial business current bank account in Sri Lanka now strictly requires the mandatory RAMIS TIN document.',
      },
    ],
  },
  partnership: {
    entity_label: 'Partnership',
    entity_label_si: 'හවුල් ව්‍යාපාරය',
    badge: 'Co-Founder Model (2 - 20 Partners)',
    badge_color: 'bg-blue-100 text-blue-800 border-blue-200',
    statute: 'Partnership Ordinance No. 22 of 1890 & WP Statute No. 04 of 1990',
    governing_body: 'Divisional Secretariat & Notarial Legal Execution',
    filing_portal: 'Divisional Secretariat (Department of Business Names)',
    est_timeline: '7 - 14 Days',
    est_cost: 'LKR 11,750 - 27,000 (Deed + Govt Duty)',
    description: 'Shared capital and joint liability among co-founders. Governed by a legally executed Partnership Agreement drafted by an Attorney-at-Law and filed at the Divisional Secretariat.',
    steps: [
      {
        step: 1,
        title: 'Partnership Name Verification',
        title_si: 'හවුල් ව්‍යාපාර නාමය සෙවීම සහ වෙන්කිරීම',
        auth: 'Divisional Secretariat',
        time: '1 Day',
        fee: 'LKR 250 - 500',
        icon: 'fa-magnifying-glass',
        desc: 'Check availability of the proposed firm name across the Western Province business register to ensure it is distinct and does not mislead the public.',
        mandatory_docs: [
          'Partnership Name Reservation Application',
          'Primary Partner NIC copy',
        ],
        statutory_form: 'WP Partnership Name Inquiry Form',
        official_portal: 'Divisional Secretariat — Business Registration Unit',
        pro_tip: 'Firm names cannot include words like "Limited" or "Incorporated" which imply limited liability.',
      },
      {
        step: 2,
        title: 'Partnership Agreement / Deed Drafting',
        title_si: 'හවුල් ගිවිසුම සකස් කිරීම සහ නොතාරිස් සහතිකය',
        auth: 'Attorney-at-Law & Notary Public',
        time: '2 - 4 Days',
        fee: 'LKR 6,000 - 15,000 (Legal Drafting)',
        icon: 'fa-handshake',
        desc: 'Draft and execute a legally binding Partnership Deed specifying capital contribution ratios, profit/loss sharing percentages, partner duties, signing mandates, and dissolution rules.',
        mandatory_docs: [
          'Agreed Commercial Partnership Terms',
          'NIC copies of all participating partners',
          'Capital contribution breakdown & bank operating instructions',
        ],
        statutory_form: 'Notarized Deed of Partnership (හවුල් ගිවිසුම් පත්‍රය)',
        official_portal: 'Office of an Attorney-at-Law / Notary Public',
        pro_tip: 'Under the Prevention of Frauds Ordinance, any partnership with capital exceeding LKR 1,000 must be in writing and notarized to be legally enforceable.',
      },
      {
        step: 3,
        title: 'Multi-Partner Grama Niladhari Clearances',
        title_si: 'සියලු හවුල්කරුවන්ගේ පදිංචිය හා පරිශ්‍රය තහවුරු කිරීම',
        auth: 'Local Grama Niladhari Officers',
        time: '1 - 2 Days',
        fee: 'Free (Statutory Duty)',
        icon: 'fa-users',
        desc: 'Premises inspection by the GN officer where the business is situated, along with individual residence verification reports for all resident partners in Sri Lanka.',
        mandatory_docs: [
          'Premises Lease Deed signed with the Partnership',
          'Residence verification extracts for all partners',
          'Certified NIC copies for each partner',
        ],
        statutory_form: 'GN Premises Report & Partner Residence Certificates',
        official_portal: 'Respective Grama Niladhari Divisions for each partner',
        pro_tip: 'All partner names, initials, and addresses on the statutory Form 1 must match their GN certificates and NICs exactly.',
      },
      {
        step: 4,
        title: 'Statutory Form 1 Partnership Filing',
        title_si: 'හවුල් ව්‍යාපාර Form 1 ලියාපදිංචිය සහ සහතිකය',
        auth: 'Divisional Secretariat (Business Names)',
        time: '1 - 3 Days',
        fee: 'LKR 3,500',
        icon: 'fa-file-signature',
        desc: 'Submit Form 1 (Statement of Particulars for Partnership) signed by ALL partners, along with the certified Deed of Partnership to obtain the Partnership BR Certificate.',
        mandatory_docs: [
          'Form 1 Statement of Particulars signed by ALL partners',
          'Certified copy of the Notarized Deed of Partnership',
          'Certified copies of NICs of all partners',
          'Original GN reports and premises tenancy agreement',
        ],
        statutory_form: 'Form 1 (Statement of Particulars - Partnership)',
        official_portal: 'Divisional Secretariat — Business Registration Unit',
        pro_tip: 'Every single partner must sign Form 1 personally in blue ink, or submit a registered Power of Attorney if overseas.',
      },
      {
        step: 5,
        title: 'Partnership RAMIS TIN & Joint Bank Account',
        title_si: 'හවුල් TIN අංකය, බැංකු ගිණුම සහ සේවක EPF',
        auth: 'Inland Revenue & Commercial Bank',
        time: '2 - 4 Days',
        fee: 'LKR 3,000 - 8,000 (Municipal Trade Tax)',
        icon: 'fa-building-columns',
        desc: 'Register a dedicated Partnership TIN with the IRD, open a joint commercial bank account in the firm name, and pay municipal council trade tax.',
        mandatory_docs: [
          'Partnership BR Certificate Copy',
          'Certified Partnership Deed copy',
          'Partnership IRD TIN Certificate',
          'KYC documents of all signing partners',
        ],
        statutory_form: 'RAMIS Partnership TIN Registration & Bank Mandate',
        official_portal: 'Inland Revenue RAMIS Portal & Commercial Bank Branch',
        pro_tip: 'Ensure the bank mandate clearly specifies whether cheques and transfers require all partners to sign or any single partner to sign.',
      },
    ],
  },
  private_limited: {
    entity_label: 'Private Limited Company (Pvt Ltd)',
    entity_label_si: 'සීමාසහිත පුද්ගලික සමාගම',
    badge: 'Statutory Corporate Entity (Separate Legal Personality)',
    badge_color: 'bg-purple-100 text-purple-800 border-purple-200',
    statute: 'Companies Act No. 07 of 2007 (Section 4)',
    governing_body: 'Department of the Registrar of Companies (eROC — Samagam Medura)',
    filing_portal: 'eROC Online Portal (eroc.drc.gov.lk) / Samagam Medura, Battaramulla',
    est_timeline: '5 - 10 Days',
    est_cost: 'LKR 18,500 - 32,000 (Statutory Filing + Secretarial)',
    description: 'Incorporation as an independent corporate legal entity with limited liability for shareholders. Registration is governed nationally by the Registrar of Companies (eROC), NOT the Divisional Secretariat.',
    steps: [
      {
        step: 1,
        title: 'eROC Online Name Reservation',
        title_si: 'eROC හරහා සමාගම් නාමය වෙන්කරවා ගැනීම',
        auth: 'Registrar of Companies (eROC)',
        time: '1 - 2 Days',
        fee: 'LKR 1,000 + Taxes (~LKR 1,180)',
        icon: 'fa-globe',
        desc: 'Submit the proposed corporate name ending in "(Private) Limited" or "(Pvt) Ltd" via the official eROC online portal (eroc.drc.gov.lk). Once approved, the name is reserved for 3 months.',
        mandatory_docs: [
          'Proposed Company Name in English & Sinhala/Tamil script',
          'Main commercial business object description',
          'Applicant NIC / Passport details on eROC account',
        ],
        statutory_form: 'eROC Name Reservation Application (Online)',
        official_portal: 'eROC System (https://eroc.drc.gov.lk)',
        pro_tip: 'Perform a name search on the eROC portal beforehand to ensure your proposed corporate name does not phonetically conflict with an active company.',
      },
      {
        step: 2,
        title: 'Articles of Association & Secretarial Appointment',
        title_si: 'සමාගම් ව්‍යවස්ථාව සහ සමාගම් ලේකම් පත්කිරීම',
        auth: 'Certified Company Secretary & Legal Counsel',
        time: '2 - 3 Days',
        fee: 'LKR 10,000 - 18,000 (Secretarial Retainer)',
        icon: 'fa-file-shield',
        desc: 'Adopt Model Articles under First Schedule or draft custom Articles of Association. Under Section 221 of Companies Act, appoint a licensed Company Secretary to handle statutory compliances.',
        mandatory_docs: [
          'Articles of Association (Drafted or Model Articles)',
          'Consent of Secretary (Form 19) signed by licensed secretary',
          'Company Secretary professional registration license copy',
        ],
        statutory_form: 'Articles of Association & Statutory Form 19',
        official_portal: 'Department of the Registrar of Companies (Samagam Medura)',
        pro_tip: 'Every Sri Lankan Pvt Ltd company is required by law to have a qualified Company Secretary to file annual returns and board resolutions.',
      },
      {
        step: 3,
        title: 'Statutory Incorporation Filing & Certificate (PV Number)',
        title_si: 'eROC Form 1, 18, 19 සහ සංස්ථාගත සහතිකය ලබාගැනීම',
        auth: 'Registrar General of Companies',
        time: '2 - 4 Days',
        fee: 'LKR 18,500 (Form 1: 15,000 + Form 18: 2,000 + Form 19: 1,500)',
        icon: 'fa-certificate',
        desc: 'Electronically upload Form 1 (Application for Registration of a Company), Form 18 (Consent of Directors), and Form 19 (Consent of Secretary). Upon approval, receive the Certificate of Incorporation with official PV number.',
        mandatory_docs: [
          'Form 1 (Application for Incorporation of a Company)',
          'Form 18 signed by each appointed director',
          'Form 19 signed by the licensed company secretary',
          'Signed Articles of Association',
        ],
        statutory_form: 'Companies Act Statutory Forms 1, 18 & 19',
        official_portal: 'eROC Portal & Samagam Medura, Battaramulla',
        pro_tip: 'The issued Certificate of Incorporation containing your unique "PV" number establishes your company as a distinct legal person separate from owners.',
      },
      {
        step: 4,
        title: 'Company Seal, Bank Account & Share Capital',
        title_si: 'සමාගම් මුද්‍රාව, බැංකු ගිණුම සහ කොටස් නිකුතුව',
        auth: 'Commercial Corporate Bank & Secretary',
        time: '1 - 2 Days',
        fee: 'LKR 2,000 - 4,000 (Seal fabrication & documentation)',
        icon: 'fa-stamp',
        desc: 'Fabricate the official embossed Company Seal, adopt an initial Board resolution to open a corporate bank account, and formally issue share certificates to initial subscribers.',
        mandatory_docs: [
          'Original Certificate of Incorporation (PV Certificate)',
          'Certified true copies of Form 1, 18, 19 and Articles of Association',
          'Board of Directors Resolution authorizing bank account opening',
          'Directors and Secretary KYC documents',
        ],
        statutory_form: 'Company Share Certificates & Corporate Bank Mandate',
        official_portal: 'Corporate Commercial Bank Branch',
        pro_tip: 'Stated initial share capital should be deposited directly into the newly opened corporate bank account to satisfy company capitalization records.',
      },
      {
        step: 5,
        title: 'Corporate RAMIS TIN, Gazette Notice & EPF/ETF',
        title_si: 'ආයතනික TIN අංකය, ගැසට් නිවේදනය සහ සේවක අර්ථසාධක',
        auth: 'Inland Revenue Dept, Government Press & Labour Dept',
        time: '2 - 4 Days',
        fee: 'LKR 3,500 - 7,000 (Gazette Notice & Municipal License)',
        icon: 'fa-newspaper',
        desc: 'Publish statutory public notice of incorporation in daily newspapers and the Government Gazette within 30 days. Obtain Corporate TIN from IRD and register company as an employer for EPF/ETF.',
        mandatory_docs: [
          'Certificate of Incorporation copy',
          'Certified Director List (Form 18)',
          'Government Gazette notice publication receipt',
          'Municipal Council Trade Tax registration',
        ],
        statutory_form: 'RAMIS Corporate TIN Registration & Gazette Notice',
        official_portal: 'Inland Revenue Department (RAMIS) & Dept of Government Printing',
        pro_tip: 'Failing to publish the incorporation notice in the Government Gazette within 30 days of registration incurs statutory penalties under Section 9 of the Companies Act.',
      },
    ],
  },
};

export const BusinessRegistrationView: React.FC = () => {
  // Empty clean default state - no auto-fill
  const [formData, setFormData] = useState<BrFormData>(EMPTY_FORM_DATA);
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadSuccess, setDownloadSuccess] = useState(false);
  const [downloadMessage, setDownloadMessage] = useState<string>('');
  const [activeRoadmapStage, setActiveRoadmapStage] = useState<number>(1);

  // Stage 1 Extra Data: Name Search & Clearance (WP/BN/01) - Clean / Empty by default
  const [stage1Data, setStage1Data] = useState(EMPTY_STAGE_1);

  // Stage 2 Extra Data: Grama Niladhari Report - Clean / Empty by default
  const [stage2Data, setStage2Data] = useState(EMPTY_STAGE_2);

  // Stage 4 Extra Data: Municipal Council Trade Tax & Health - Clean / Empty by default
  const [stage4Data, setStage4Data] = useState(EMPTY_STAGE_4);

  // Stage 5 Extra Data: RAMIS TIN & Labour EPF/ETF - Clean / Empty by default
  const [stage5Data, setStage5Data] = useState(EMPTY_STAGE_5);

  // Dynamic Checklists per Stage - Unchecked by default
  const [stageChecklists, setStageChecklists] = useState<Record<number, Record<string, boolean>>>(EMPTY_CHECKLISTS);

  const handleSelectPreset = (key: string) => {
    const preset = SAMPLE_PRESETS[key];
    if (!preset) return;
    setFormData(preset);
    if (key === 'bakery') {
      setStage1Data({
        alt_name_1: 'CEYLON HERITAGE BAKERY',
        alt_name_2: 'ISLAND ARTISAN BAKES',
        name_meaning: 'Artisan Sri Lankan traditional bakes with modern quality standards and natural ingredients',
        language_scripts: 'English & Sinhala',
        search_date: new Date().toISOString().split('T')[0],
        reservation_period: '3 Months (Statutory Validity under WP Statute Sec. 4)',
      });
      setStage2Data({
        ownership_type: 'commercial_lease',
        landlord_name: 'Mr. K. A. Perera',
        landlord_phone: '+94 77 345 6789',
        deed_lease_no: 'Lease Agreement No. 2024/481',
        electoral_no: 'EL/COL/512/048',
        house_no: 'No. 12/B',
        residence_duration: '6 Years',
        inspection_readiness: 'Premises ready for on-site officer inspection',
      });
      setStage4Data({
        assessment_no: 'CMC/WR/2026/8941',
        trade_category: 'Food Manufacturing & Bakery Products',
        floor_area: '1,250 Sq. Ft.',
        fire_safety: 'Fire Extinguishers Installed (CO2 + Foam)',
        phi_division: 'PHI Range 03 - Thimbirigasyaya Division',
        food_handlers_certified: 5,
        waste_disposal: 'Municipal Council Daily Collection & Sealed Grease Trap',
        license_year: '2026 / 2027',
        br_certificate_no: 'WP/COL/2026/10492',
      });
      setStage5Data({
        taxpayer_type: 'Sole Proprietorship Enterprise',
        ird_unit: 'Colombo South Metropolitan Unit (Chitampalam Gardiner Mw)',
        tin_status: 'New RAMIS TIN Application Required',
        labour_office: 'Colombo South Labour Office (Narahenpita)',
        monthly_payroll: 350000,
        epf_status: 'Mandatory Form D Employer Registration (12% + 8%)',
        etf_status: 'Mandatory 3% Employer Contribution',
        bank_name: 'Commercial Bank of Ceylon',
        bank_branch: 'Bambalapitiya Branch',
        bank_account: '1000849201',
      });
      setStageChecklists({
        1: { s1_form: true, s1_nic: true, s1_meaning: true, s1_fee: false },
        2: { s2_deed: true, s2_consent: true, s2_utility: true, s2_electoral: false, s2_nic: true },
        3: { s3_form1: true, s3_gn_rep: true, s3_nic: true, s3_deed: true, s3_duty: false },
        4: { s4_br: true, s4_rates: false, s4_phi: true, s4_plan: true, s4_fire: true },
        5: { s5_br_copy: true, s5_tin_slip: true, s5_labour_d: false, s5_staff_list: true, s5_bank: true },
      });
    } else {
      setStage1Data({
        alt_name_1: `${preset.business_name} VENTURES`,
        alt_name_2: `${preset.business_name} LANKA`,
        name_meaning: `${preset.sector} commercial trade activities`,
        language_scripts: 'English & Sinhala',
        search_date: new Date().toISOString().split('T')[0],
        reservation_period: '3 Months (Statutory Validity under WP Statute Sec. 4)',
      });
    }
  };

  const handleClearAll = () => {
    setFormData(EMPTY_FORM_DATA);
    setStage1Data(EMPTY_STAGE_1);
    setStage2Data(EMPTY_STAGE_2);
    setStage4Data(EMPTY_STAGE_4);
    setStage5Data(EMPTY_STAGE_5);
    setStageChecklists(EMPTY_CHECKLISTS);
  };

  const STAGE_CHECKLIST_CONFIG: Record<number, { key: string; label: string; desc: string }[]> = {
    1: [
      { key: 's1_form', label: 'Proposed Name Inquiry Form (WP/BN/01)', desc: 'Official inquiry slip filled in duplicate' },
      { key: 's1_nic', label: 'Applicant Certified NIC Copy', desc: 'Certified photocopy of National Identity Card' },
      { key: 's1_meaning', label: 'Name Meaning & Origin Brief', desc: 'Explanation if using specialized or transliterated words' },
      { key: 's1_fee', label: 'Statutory Search Duty Receipt (LKR 250 - 500)', desc: 'Divisional Secretariat cashier receipt' },
    ],
    2: [
      { key: 's2_deed', label: 'Deed or Stamped Commercial Lease', desc: 'Premises lease agreement or proof of property ownership' },
      { key: 's2_consent', label: 'Property Owner Consent Letter', desc: 'Signed declaration permitting commercial operation' },
      { key: 's2_utility', label: 'Recent Premises Utility Bill', desc: 'Electricity or water bill within last 3 months' },
      { key: 's2_electoral', label: 'Electoral Register Residence Confirmation', desc: 'Proof of applicant residence in GN division' },
      { key: 's2_nic', label: 'Certified NIC Copy of Applicant', desc: 'Certified by Justice of the Peace (JP)' },
    ],
    3: [
      { key: 's3_form1', label: 'Signed Form 1 (Statement of Particulars)', desc: 'Completed statutory registration application form' },
      { key: 's3_gn_rep', label: 'Original Grama Niladhari Assessment Report', desc: 'Signed inspection report from GN Officer' },
      { key: 's3_nic', label: 'Certified Applicant NIC / Passport', desc: 'Certified copy verified against original document' },
      { key: 's3_deed', label: 'Registered Premises Lease / Deed Copy', desc: 'Valid commercial tenancy contract' },
      { key: 's3_duty', label: 'Statutory Registration Fee Receipt (LKR 2,500)', desc: 'Divisional Secretariat cashier payment' },
    ],
    4: [
      { key: 's4_br', label: 'Certified BR Certificate Copy', desc: 'Copy of issued Form 1 Business Registration' },
      { key: 's4_rates', label: 'Municipal Assessment Rates Receipt', desc: 'Latest municipal council property tax receipt' },
      { key: 's4_phi', label: 'PHI Cleanliness & Hygiene Pass', desc: 'Public Health Inspector clearance pass for premises' },
      { key: 's4_plan', label: 'Premises Floor Plan / Layout Sketch', desc: 'Dimensional sketch of trade space and equipment' },
      { key: 's4_fire', label: 'Fire Extinguisher Certification', desc: 'Inspected and certified fire extinguisher equipment' },
    ],
    5: [
      { key: 's5_br_copy', label: 'Business Registration (BR) Copy', desc: 'Proof of registered business enterprise' },
      { key: 's5_tin_slip', label: 'RAMIS Online Registration Slip', desc: 'Inland Revenue system confirmation printout' },
      { key: 's5_labour_d', label: 'Labour Dept Form D (Employer Reg)', desc: 'Registration of establishment under EPF Act' },
      { key: 's5_staff_list', label: 'Employee Schedule & NIC Copies', desc: 'Staff wage roster and National ID copies' },
      { key: 's5_bank', label: 'Commercial Bank Account Mandate', desc: 'Bank letter verifying operational business account' },
    ],
  };

  const STAGE_SUBMISSION_INFO: Record<number, { title: string; subtitle: string; desc: string; hours: string; time: string; fee: string }> = {
    1: {
      title: 'Business Names Inquiry Counter',
      subtitle: 'WP Business Names Division',
      desc: `Submit your Proposed Business Name Inquiry Form (WP/BN/01) in person at ${formData.divisional_secretariat} (Business Names Counter) to verify name uniqueness.`,
      hours: 'Mon - Fri (8:30 AM - 3:00 PM)',
      time: '1 Day (Same-day clearance)',
      fee: 'LKR 250 - 500',
    },
    2: {
      title: 'Local Grama Niladhari Office',
      subtitle: `${formData.grama_niladhari}`,
      desc: `Meet your local Grama Niladhari officer at the division office with ownership/lease documents to schedule the physical premises inspection.`,
      hours: 'Tue & Thu: 9:00 AM - 12:30 PM (or by appointment)',
      time: '1 - 2 Days',
      fee: 'Free (Statutory Public Duty)',
    },
    3: {
      title: 'Business Registration Unit',
      subtitle: 'Divisional Secretariat Office',
      desc: `Submit your completed and signed Form 1 package along with the GN report to the Business Names Registrar at ${formData.divisional_secretariat}.`,
      hours: 'Mon - Fri (8:30 AM - 4:15 PM)',
      time: '1 - 3 Business Days',
      fee: 'LKR 2,500',
    },
    4: {
      title: 'Municipal / Urban Council Health & Revenue Dept',
      subtitle: `${formData.local_authority}`,
      desc: `Present your BR certificate at ${formData.local_authority} to obtain commercial trade tax clearance and arrange PHI hygiene inspection.`,
      hours: 'Mon - Fri (9:00 AM - 3:30 PM)',
      time: '2 - 5 Days',
      fee: 'LKR 3,000 - 8,000',
    },
    5: {
      title: 'Inland Revenue Dept (RAMIS) & Dept of Labour',
      subtitle: 'Taxpayer & Social Security Services',
      desc: `Submit mandatory TIN registration on the IRD RAMIS portal (www.ird.gov.lk) and file Form D with the Department of Labour if hiring employees.`,
      hours: 'Online 24/7 (RAMIS) | Dept: 8:30 AM - 4:15 PM',
      time: '1 - 3 Days',
      fee: 'Free Registration',
    },
  };

  const STAGE_META: Record<number, {
    badge: string;
    badge_color: string;
    title: string;
    title_si: string;
    icon: string;
    icon_color: string;
    desc: string;
    btn_label: string;
    btn_icon: string;
  }> = {
    1: {
      badge: 'Official Statutory Form (WP/BN/01)',
      badge_color: 'bg-blue-100 text-blue-800 border-blue-200',
      title: '3. Business Name Search & Clearance Application',
      title_si: 'ව්‍යාපාර නාමය සෙවීම සහ වෙන්කිරීමේ අයදුම්පත (WP/BN/01)',
      icon: 'fa-magnifying-glass',
      icon_color: 'text-blue-600',
      desc: 'Prescribed form under Western Province Business Names Statute Section 4 to verify uniqueness and secure name reservation.',
      btn_label: 'Download Name Search Form (PDF)',
      btn_icon: 'fa-file-pdf',
    },
    2: {
      badge: 'Grama Niladhari Assessment Form',
      badge_color: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      title: '3. Grama Niladhari Assessment & Residence Verification Report',
      title_si: 'ග්‍රාම නිලධාරී පරීක්ෂාව සහ පදිංචි සහතික වාර්තාව (වසමේ වාර්තාව)',
      icon: 'fa-user-check',
      icon_color: 'text-indigo-600',
      desc: 'Official inspection dossier for the Grama Niladhari officer to certify physical premises legality, tenancy rights, and applicant residence.',
      btn_label: 'Download GN Assessment Report (PDF)',
      btn_icon: 'fa-file-signature',
    },
    3: {
      badge: 'Official Statutory Form 1',
      badge_color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      title: '3. Statement of Particulars (Form 1) Particulars',
      title_si: 'ව්‍යවස්ථාපිත Form 1 අයදුම්පත (Statement of Particulars)',
      icon: 'fa-pen-to-square',
      icon_color: 'text-emerald-600',
      desc: 'Data entered below is mapped directly to the official Sri Lanka Business Registration PDF filed at the Divisional Secretariat.',
      btn_label: 'Download Form 1 (PDF)',
      btn_icon: 'fa-file-pdf',
    },
    4: {
      badge: 'Municipal Trade Tax & Health Form',
      badge_color: 'bg-amber-100 text-amber-800 border-amber-200',
      title: '3. Municipal Trade Tax & Health License Application',
      title_si: 'නගර සභා වෙළඳ බද්ද සහ සෞඛ්‍ය බලපත්‍ර අයදුම්පත',
      icon: 'fa-city',
      icon_color: 'text-amber-600',
      desc: 'Application for Local Authority Trade Tax registration, municipal rates assessment, and Public Health Inspector (PHI) food hygiene certification.',
      btn_label: 'Download Municipal License Form (PDF)',
      btn_icon: 'fa-file-invoice',
    },
    5: {
      badge: 'RAMIS TIN & Labour Form D',
      badge_color: 'bg-purple-100 text-purple-800 border-purple-200',
      title: '3. RAMIS TIN & Labour EPF/ETF Registration Form',
      title_si: 'TIN අංකය සහ සේවක අර්ථසාධක (EPF/ETF) ලියාපදිංචි අයදුම්පත',
      icon: 'fa-receipt',
      icon_color: 'text-purple-600',
      desc: 'Mandatory statutory registration with Inland Revenue Department (RAMIS) for TIN and Department of Labour for EPF/ETF compliance.',
      btn_label: 'Download TIN & EPF Dossier (PDF)',
      btn_icon: 'fa-file-shield',
    },
  };

  const currentRoadmap = ROADMAP_DATA_BY_ENTITY[formData.legal_form] || ROADMAP_DATA_BY_ENTITY.sole_proprietorship;
  const activeStepData = currentRoadmap.steps.find((s) => s.step === activeRoadmapStage) || currentRoadmap.steps[0];

  const currentChecklistState = stageChecklists[activeRoadmapStage] || {};
  const currentChecklistItems = STAGE_CHECKLIST_CONFIG[activeRoadmapStage] || [];

  const toggleChecklist = (key: string) => {
    setStageChecklists((prev) => ({
      ...prev,
      [activeRoadmapStage]: {
        ...prev[activeRoadmapStage],
        [key]: !prev[activeRoadmapStage]?.[key],
      },
    }));
  };

  const checklistScore = Math.round(
    currentChecklistItems.length > 0
      ? (currentChecklistItems.filter((item) => currentChecklistState[item.key]).length / currentChecklistItems.length) * 100
      : 100
  );

  const triggerDownload = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleDownloadStageForm = async () => {
    setIsGenerating(true);
    setDownloadSuccess(false);

    try {
      const stagePayload = {
        stage: activeRoadmapStage,
        ...formData,
        ...stage1Data,
        ...stage2Data,
        ...stage4Data,
        ...stage5Data,
      };

      const safeName = (formData.business_name || 'Business').replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_-]/g, '');
      const filenameMap: Record<number, string> = {
        1: `WP_BN_01_Name_Search_Clearance_${safeName}.pdf`,
        2: `Grama_Niladhari_Report_${safeName}.pdf`,
        3: `BR_Application_Form1_${safeName}.pdf`,
        4: `Municipal_Trade_License_Application_${safeName}.pdf`,
        5: `RAMIS_TIN_Labour_FormD_${safeName}.pdf`,
      };
      const targetFilename = filenameMap[activeRoadmapStage] || `Stage_${activeRoadmapStage}_Application_${safeName}.pdf`;

      // 1. Primary: Request genuine binary PDF from FastAPI backend
      let pdfDownloaded = false;
      try {
        const endpoint = activeRoadmapStage === 3
          ? 'http://127.0.0.1:8000/api/v1/component2/generate-br-form'
          : 'http://127.0.0.1:8000/api/v1/component2/generate-stage-form';

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(stagePayload),
        });

        if (response.ok) {
          const blob = await response.blob();
          triggerDownload(blob, targetFilename);
          setDownloadMessage(`Official ${STAGE_META[activeRoadmapStage].title.split('.')[1]?.trim()} (PDF) downloaded successfully!`);
          pdfDownloaded = true;
        }
      } catch (backendErr) {
        console.warn('Backend PDF endpoint unreachable, opening browser print-to-PDF...', backendErr);
      }

      // 2. Fallback: If backend was not reached, launch browser print dialog (Save as PDF)
      if (!pdfDownloaded) {
        const stageMeta = STAGE_META[activeRoadmapStage];
        const printWindow = window.open('', '_blank');
        if (printWindow) {
          printWindow.document.write(`<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>${stageMeta.title} - ${formData.business_name}</title>
  <style>
    @page { size: A4 portrait; margin: 15mm; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; padding: 20px; color: #0f172a; line-height: 1.5; font-size: 12px; }
    .header { text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 18px; }
    .emblem { font-size: 15px; font-weight: 800; color: #0f172a; letter-spacing: 0.5px; }
    .statute { font-size: 11px; color: #475569; font-weight: 700; text-transform: uppercase; margin-top: 3px; }
    h1 { font-size: 16px; margin: 10px 0 3px; color: #0f172a; font-weight: 800; }
    h2 { font-size: 12px; font-weight: 600; color: #334155; margin: 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 11.5px; }
    th, td { border: 1px solid #cbd5e1; padding: 7px 10px; text-align: left; }
    th { background: #f8fafc; font-weight: 700; width: 34%; color: #334155; }
    td { background: #ffffff; color: #0f172a; font-weight: 500; }
    .section-title { background: #e2e8f0; font-weight: 800; font-size: 12px; color: #0f172a; }
    .checklist { margin-top: 18px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; font-size: 11px; }
    .checklist-title { font-weight: 800; font-size: 11.5px; color: #0f172a; margin-bottom: 6px; }
    .footer { margin-top: 25px; display: flex; justify-content: space-between; font-size: 10.5px; border-top: 1px dashed #cbd5e1; padding-top: 12px; }
    .sign-box { width: 200px; border-top: 1px solid #0f172a; text-align: center; padding-top: 6px; margin-top: 35px; font-weight: 700; }
  </style>
</head>
<body>
  <div class="header">
    <div class="emblem">DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA</div>
    <div class="statute">WESTERN PROVINCIAL COUNCIL — DEPARTMENT OF BUSINESS NAMES</div>
    <h1>${stageMeta.title}</h1>
    <h2>${stageMeta.title_si}</h2>
  </div>

  <table>
    <tr class="section-title"><td colspan="2">1. GENERAL BUSINESS &amp; JURISDICTION PROFILE</td></tr>
    <tr><th>Proposed Trading Name</th><td><strong>${formData.business_name}</strong></td></tr>
    <tr><th>Legal Structure</th><td>${formData.legal_form.replace(/_/g, ' ').toUpperCase()}</td></tr>
    <tr><th>Target Divisional Secretariat</th><td>${formData.divisional_secretariat}</td></tr>
    <tr><th>Grama Niladhari Division</th><td>${formData.grama_niladhari}</td></tr>
    <tr><th>Local Municipal / Urban Council</th><td>${formData.local_authority}</td></tr>
    <tr><th>Principal Business Address</th><td>${formData.address}</td></tr>
    <tr><th>Applicant / Owner Name</th><td>${formData.owner_name}</td></tr>
    <tr><th>National Identity Card (NIC)</th><td>${formData.owner_nic}</td></tr>
    <tr><th>Contact Phone &amp; Email</th><td>${formData.phone} | ${formData.email}</td></tr>

    <tr class="section-title"><td colspan="2">2. STAGE ${activeRoadmapStage} SPECIFIC PARTICULARS</td></tr>
    ${
      activeRoadmapStage === 1
        ? `<tr><th>Alternative Name Choice 1</th><td>${stage1Data.alt_name_1}</td></tr>
           <tr><th>Alternative Name Choice 2</th><td>${stage1Data.alt_name_2}</td></tr>
           <tr><th>Name Meaning &amp; Origin</th><td>${stage1Data.name_meaning}</td></tr>
           <tr><th>Language Scripts</th><td>${stage1Data.language_scripts}</td></tr>
           <tr><th>Search Date &amp; Validity</th><td>${stage1Data.search_date} (${stage1Data.reservation_period})</td></tr>
           <tr><th>Statutory Duty Fee</th><td>LKR 250 - 500 (Payable at DS Cashier)</td></tr>`
        : activeRoadmapStage === 2
        ? `<tr><th>Premises Legal Tenancy Title</th><td>${stage2Data.ownership_type.replace(/_/g, ' ').toUpperCase()}</td></tr>
           <tr><th>Property Owner / Landlord</th><td>${stage2Data.landlord_name} (${stage2Data.landlord_phone})</td></tr>
           <tr><th>Deed / Stamped Lease Ref</th><td>${stage2Data.deed_lease_no}</td></tr>
           <tr><th>Electoral Register Serial No</th><td>${stage2Data.electoral_no} (House: ${stage2Data.house_no})</td></tr>
           <tr><th>Residence Duration in Division</th><td>${stage2Data.residence_duration}</td></tr>
           <tr><th>Inspection Status</th><td>${stage2Data.inspection_readiness}</td></tr>`
        : activeRoadmapStage === 4
        ? `<tr><th>Assessment Account Number</th><td>${stage4Data.assessment_no}</td></tr>
           <tr><th>Trade License Classification</th><td>${stage4Data.trade_category}</td></tr>
           <tr><th>Total Usable Floor Area</th><td>${stage4Data.floor_area}</td></tr>
           <tr><th>Public Health Inspector (PHI)</th><td>${stage4Data.phi_division}</td></tr>
           <tr><th>Food Handlers Medical Certified</th><td>${stage4Data.food_handlers_certified} Personnel</td></tr>
           <tr><th>Fire Safety Equipment</th><td>${stage4Data.fire_safety}</td></tr>
           <tr><th>Waste &amp; Drainage Arrangement</th><td>${stage4Data.waste_disposal}</td></tr>
           <tr><th>BR Certificate Reference</th><td>${stage4Data.br_certificate_no} (${stage4Data.license_year})</td></tr>`
        : `<tr><th>Taxpayer Classification</th><td>${stage5Data.taxpayer_type}</td></tr>
           <tr><th>Inland Revenue Regional Unit</th><td>${stage5Data.ird_unit}</td></tr>
           <tr><th>RAMIS TIN Application Status</th><td>${stage5Data.tin_status}</td></tr>
           <tr><th>Labour Department Office</th><td>${stage5Data.labour_office}</td></tr>
           <tr><th>Total Employees / Headcount</th><td>${formData.employee_count} Persons</td></tr>
           <tr><th>Estimated Monthly Payroll</th><td>LKR ${stage5Data.monthly_payroll.toLocaleString()}</td></tr>
           <tr><th>Statutory Social Security</th><td>EPF: 12% + 8% | ETF: 3% Employer</td></tr>
           <tr><th>Designated Remittance Bank</th><td>${stage5Data.bank_name} (${stage5Data.bank_branch}) - A/C: ${stage5Data.bank_account}</td></tr>`
    }
  </table>

  <div class="checklist">
    <div class="checklist-title">MANDATORY STATUTORY DOCUMENTS CHECKLIST</div>
    <ul>
      ${(STAGE_CHECKLIST_CONFIG[activeRoadmapStage] || [])
        .map((c) => `<li><strong>${c.label}</strong> — ${c.desc}</li>`)
        .join('')}
    </ul>
  </div>

  <div class="footer">
    <div>
      <p>Prepared for: <strong>${STAGE_SUBMISSION_INFO[activeRoadmapStage]?.title}</strong></p>
      <p>Office: ${STAGE_SUBMISSION_INFO[activeRoadmapStage]?.subtitle}</p>
      <p>Date: ${new Date().toLocaleDateString('en-GB')}</p>
    </div>
    <div class="sign-box">
      Applicant / Declarant Signature
    </div>
  </div>
  <script>
    window.onload = function() { window.print(); }
  </script>
</body>
</html>`);
          printWindow.document.close();
          setDownloadMessage(`Official Stage ${activeRoadmapStage} PDF print dialog opened. Select "Save as PDF" to save!`);
        }
      }

      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 6000);
    } catch (err) {
      console.error(err);
      alert('Could not download form. Please verify connection to server.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-8 space-y-7 font-sans">
      {/* ----------------------------------------------------------------- */}
      {/* 1. HERO HEADER BANNER                                             */}
      {/* ----------------------------------------------------------------- */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-[#0d1627] to-indigo-950 p-6 sm:p-8 text-white shadow-xl border border-slate-800">
        <div className="absolute -top-24 -right-24 w-80 h-80 rounded-full bg-teal-500/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-teal-500/15 text-teal-300 border border-teal-500/30">
                <i className="fa-solid fa-landmark text-teal-400" />
                Western Province Business Registration Portal
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">
                <i className="fa-solid fa-file-signature text-blue-400" />
                Statute No. 04 of 1990
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
              <span className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center text-slate-950 text-base shadow-lg shadow-teal-500/20">
                <i className="fa-solid fa-file-contract" />
              </span>
              Business Registration &amp; Form 1 Generator
            </h2>

            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Official institutional registration system for Sri Lankan SMEs in Western Province (Colombo, Gampaha, Kalutara).
              Pre-populates statutory <strong>Form 1 (Statement of Particulars)</strong> for Divisional Secretariat filing,
              guides your Grama Niladhari assessment, and calculates municipal fees.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 shrink-0">
            <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
              <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Statutory Filing</span>
              <span className="text-lg font-extrabold text-white">
                {formData.legal_form === 'private_limited' ? 'eROC Forms 1, 18, 19' : formData.legal_form === 'partnership' ? 'Form 1 (Partnership)' : 'Form 1 (Individual)'}
              </span>
              <span className="block text-[10px] text-teal-400 font-medium mt-0.5">
                {formData.legal_form === 'private_limited' ? 'eROC — Samagam Medura' : 'Divisional Secretariat'}
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
              <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Est. Timeline</span>
              <span className="text-lg font-extrabold text-white">{currentRoadmap.est_timeline}</span>
              <span className="block text-[10px] text-blue-400 font-medium mt-0.5">Full Roadmap Cycle</span>
            </div>

            <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md col-span-2 sm:col-span-1">
              <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Est. Budget</span>
              <span className="text-lg font-extrabold text-emerald-400">
                {formData.legal_form === 'private_limited' ? 'LKR 18,500+' : formData.legal_form === 'partnership' ? 'LKR 3,500+' : 'LKR 2,500'}
              </span>
              <span className="block text-[10px] text-emerald-300 font-medium mt-0.5">Statutory Filing Duty</span>
            </div>
          </div>
        </div>
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 2. LEGAL ENTITY SELECTOR & SECTOR PRESETS                         */}
      {/* ----------------------------------------------------------------- */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-5 sm:p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <i className="fa-solid fa-scale-balanced text-teal-600" />
              1. Choose Legal Structure &amp; Sector Preset
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Select your intended commercial classification under Western Province legislation.
            </p>
          </div>

          {/* Preset Buttons */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-semibold text-slate-500 mr-1">Sample Presets:</span>
            {[
              { key: 'bakery', label: 'Bakery SME', icon: 'fa-bread-slice' },
              { key: 'clothing', label: 'Clothing Boutique', icon: 'fa-shirt' },
              { key: 'salon', label: 'Beauty Salon', icon: 'fa-scissors' },
              { key: 'vehicle', label: 'Auto Parts / Garage', icon: 'fa-wrench' },
            ].map((preset) => (
              <button
                key={preset.key}
                type="button"
                onClick={() => handleSelectPreset(preset.key)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-teal-50 hover:text-teal-800 text-slate-700 border border-slate-200 transition-colors cursor-pointer"
              >
                <i className={`fa-solid ${preset.icon} text-slate-500`} />
                <span>{preset.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 3 Entity Types Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {/* Sole Proprietorship */}
          <div
            onClick={() => {
              setFormData({ ...formData, legal_form: 'sole_proprietorship' });
              setActiveRoadmapStage(1);
            }}
            className={`p-4 rounded-2xl border-2 transition-all cursor-pointer space-y-2 relative ${
              formData.legal_form === 'sole_proprietorship'
                ? 'border-teal-500 bg-teal-50/40 shadow-xs'
                : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
            }`}
          >
            {formData.legal_form === 'sole_proprietorship' && (
              <span className="absolute top-3 right-3 text-teal-600 font-bold text-xs">
                <i className="fa-solid fa-circle-check" /> Selected
              </span>
            )}
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-teal-800 bg-teal-100/80 px-2 py-0.5 rounded-md">
              Most Popular for SMEs
            </span>
            <h4 className="font-bold text-slate-900 text-sm">Sole Proprietorship (තනි පුද්ගල)</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Statutory Form 1 filed at the local Divisional Secretariat. Minimal compliance burden, direct owner authority.
            </p>
            <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] font-semibold text-slate-600">
              <span>Authority: Divisional Secretariat</span>
              <span className="text-teal-700 font-bold">~LKR 2,500</span>
            </div>
          </div>

          {/* Partnership */}
          <div
            onClick={() => {
              setFormData({ ...formData, legal_form: 'partnership' });
              setActiveRoadmapStage(1);
            }}
            className={`p-4 rounded-2xl border-2 transition-all cursor-pointer space-y-2 relative ${
              formData.legal_form === 'partnership'
                ? 'border-teal-500 bg-teal-50/40 shadow-xs'
                : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
            }`}
          >
            {formData.legal_form === 'partnership' && (
              <span className="absolute top-3 right-3 text-teal-600 font-bold text-xs">
                <i className="fa-solid fa-circle-check" /> Selected
              </span>
            )}
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-blue-800 bg-blue-100/80 px-2 py-0.5 rounded-md">
              Co-Founder Model
            </span>
            <h4 className="font-bold text-slate-900 text-sm">Partnership (හවුල් ව්‍යාපාරය)</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Governed by WP Statute No. 04 of 1990 &amp; Partnership Ordinance 1890. 2 to 20 partners with shared capital.
            </p>
            <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] font-semibold text-slate-600">
              <span>Authority: Divisional Secretariat</span>
              <span className="text-blue-700 font-bold">~LKR 3,500</span>
            </div>
          </div>

          {/* Private Limited Company */}
          <div
            onClick={() => {
              setFormData({ ...formData, legal_form: 'private_limited' });
              setActiveRoadmapStage(1);
            }}
            className={`p-4 rounded-2xl border-2 transition-all cursor-pointer space-y-2 relative ${
              formData.legal_form === 'private_limited'
                ? 'border-teal-500 bg-teal-50/40 shadow-xs'
                : 'border-slate-200 hover:border-slate-300 bg-slate-50/50'
            }`}
          >
            {formData.legal_form === 'private_limited' && (
              <span className="absolute top-3 right-3 text-teal-600 font-bold text-xs">
                <i className="fa-solid fa-circle-check" /> Selected
              </span>
            )}
            <span className="text-[10px] font-extrabold uppercase tracking-wider text-purple-800 bg-purple-100/80 px-2 py-0.5 rounded-md">
              Corporate Entity
            </span>
            <h4 className="font-bold text-slate-900 text-sm">Private Limited (Pvt Ltd)</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Companies Act No. 07 of 2007 through eROC (Samagam Medura). Provides limited liability for shareholders.
            </p>
            <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] font-semibold text-slate-600">
              <span>Authority: Registrar of Companies</span>
              <span className="text-purple-700 font-bold">~LKR 18,000+</span>
            </div>
          </div>
        </div>
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 3. 5-STAGE INSTITUTIONAL ROADMAP STEPPER (DYNAMIC PER ENTITY)     */}
      {/* ----------------------------------------------------------------- */}
      <div className="bg-white rounded-3xl border border-slate-200/90 p-5 sm:p-6 shadow-xs space-y-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-slate-100 pb-4">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-sm sm:text-base font-extrabold text-slate-900 flex items-center gap-2">
                <i className="fa-solid fa-route text-blue-600" />
                2. 5-Stage Institutional Registration Roadmap (පියවරෙන් පියවර මඟපෙන්වීම)
              </h3>
              <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border ${currentRoadmap.badge_color}`}>
                <i className="fa-solid fa-shield-halved text-[10px]" />
                {currentRoadmap.entity_label} ({currentRoadmap.entity_label_si})
              </span>
            </div>
            <p className="text-xs text-slate-500 max-w-3xl leading-relaxed">
              {currentRoadmap.description}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs shrink-0">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 font-semibold">
              <i className="fa-solid fa-clock text-blue-500" />
              Total Time: <strong className="text-slate-900">{currentRoadmap.est_timeline}</strong>
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 font-semibold">
              <i className="fa-solid fa-coins text-emerald-600" />
              Est. Cost: <strong className="text-slate-900">{currentRoadmap.est_cost}</strong>
            </span>
          </div>
        </div>

        {/* 5 Dynamic Stepper Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {currentRoadmap.steps.map((stg) => {
            const isSelected = activeRoadmapStage === stg.step;
            return (
              <div
                key={stg.step}
                onClick={() => setActiveRoadmapStage(stg.step)}
                className={`p-3.5 rounded-2xl border-2 transition-all cursor-pointer flex flex-col justify-between space-y-2 relative group ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/60 shadow-md ring-2 ring-blue-500/20'
                    : 'border-slate-200 hover:border-blue-300 hover:bg-slate-50/80 bg-slate-50/40'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span
                      className={`w-7 h-7 rounded-xl text-xs font-extrabold flex items-center justify-center transition-colors ${
                        isSelected ? 'bg-blue-600 text-white shadow-sm' : 'bg-slate-200 group-hover:bg-blue-100 text-slate-700'
                      }`}
                    >
                      {stg.step}
                    </span>
                    <span className="text-[10px] font-bold text-slate-500 font-mono bg-white px-2 py-0.5 rounded-md border border-slate-200/80">
                      {stg.time}
                    </span>
                  </div>

                  <div className="pt-1">
                    <h4 className="font-bold text-slate-900 text-xs leading-snug line-clamp-2">
                      <i className={`fa-solid ${stg.icon} text-blue-500 mr-1.5 text-[11px]`} />
                      {stg.title}
                    </h4>
                    <p className="text-[10.5px] text-slate-500 font-medium mt-0.5 line-clamp-1">{stg.title_si}</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-200/70 text-[10px] space-y-1">
                  <span className="text-slate-600 block truncate font-medium">📍 {stg.auth}</span>
                  <span className="text-blue-700 font-bold block">{stg.fee}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Stage Interactive Execution Details Drawer / Panel */}
        {activeStepData && (
          <div className="rounded-2xl border border-blue-200/80 bg-gradient-to-br from-blue-50/40 via-white to-slate-50/50 p-4 sm:p-6 space-y-4 shadow-xs transition-all">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200/70 pb-3.5">
              <div className="flex items-center gap-3">
                <span className="w-10 h-10 rounded-2xl bg-blue-600 text-white flex items-center justify-center text-base font-extrabold shadow-sm">
                  {activeStepData.step}
                </span>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h4 className="text-sm sm:text-base font-extrabold text-slate-900">
                      Stage {activeStepData.step}: {activeStepData.title}
                    </h4>
                    <span className="text-xs text-blue-800 font-semibold bg-blue-100/70 px-2.5 py-0.5 rounded-full">
                      {activeStepData.title_si}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Authority: <strong className="text-slate-800">{activeStepData.auth}</strong> | Standard Time: <strong className="text-slate-800">{activeStepData.time}</strong> | Govt Duty: <strong className="text-emerald-700">{activeStepData.fee}</strong>
                  </p>
                </div>
              </div>

              {/* Next/Prev Navigation */}
              <div className="flex items-center gap-2 self-end sm:self-auto">
                <button
                  type="button"
                  disabled={activeRoadmapStage <= 1}
                  onClick={() => setActiveRoadmapStage((prev) => Math.max(1, prev - 1))}
                  className="px-2.5 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors"
                >
                  <i className="fa-solid fa-arrow-left mr-1" /> Prev
                </button>
                <button
                  type="button"
                  disabled={activeRoadmapStage >= 5}
                  onClick={() => setActiveRoadmapStage((prev) => Math.min(5, prev + 1))}
                  className="px-2.5 py-1.5 rounded-xl border border-blue-600 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer transition-colors shadow-xs"
                >
                  Next Stage <i className="fa-solid fa-arrow-right ml-1" />
                </button>
              </div>
            </div>

            {/* Description & Execution Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                    Execution Procedure &amp; Guidance
                  </span>
                  <p className="text-xs sm:text-sm text-slate-700 leading-relaxed bg-white/80 p-3.5 rounded-xl border border-slate-200/70">
                    {activeStepData.desc}
                  </p>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                    Official Statutory Form &amp; Portal
                  </span>
                  <div className="p-3 bg-white/80 rounded-xl border border-slate-200/70 text-xs space-y-1.5">
                    <div className="flex items-center gap-2 text-slate-800">
                      <i className="fa-solid fa-file-lines text-teal-600" />
                      <span>Form: <strong>{activeStepData.statutory_form}</strong></span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <i className="fa-solid fa-building-columns text-blue-600" />
                      <span>Portal / Office: <strong>{activeStepData.official_portal}</strong></span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="space-y-1.5">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                    Mandatory Dossier Documents Checklist
                  </span>
                  <div className="p-3 bg-white/80 rounded-xl border border-slate-200/70 space-y-1.5">
                    {activeStepData.mandatory_docs.map((doc, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-slate-700">
                        <i className="fa-solid fa-circle-check text-emerald-600 mt-0.5 shrink-0" />
                        <span>{doc}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Legal Pro-Tip */}
                <div className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200/80 text-xs text-amber-900 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-amber-800">
                    <i className="fa-solid fa-lightbulb text-amber-600" />
                    <span>Statutory Compliance Pro-Tip:</span>
                  </div>
                  <p className="leading-relaxed text-amber-950/90 pl-5">
                    {activeStepData.pro_tip}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 4. INTERACTIVE FORM 1 AUTO-FILLER & GENERATION SECTION           */}
      {/* ----------------------------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Inputs (2 Cols) */}
        <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200/90 p-5 sm:p-7 shadow-xs space-y-5">
          {/* Stage Fast-Navigation Tab Bar */}
          <div className="flex items-center gap-1.5 p-1.5 bg-slate-100/90 rounded-2xl overflow-x-auto border border-slate-200/70">
            {[1, 2, 3, 4, 5].map((stgNum) => {
              const meta = STAGE_META[stgNum];
              const isCurrent = activeRoadmapStage === stgNum;
              return (
                <button
                  key={stgNum}
                  type="button"
                  onClick={() => setActiveRoadmapStage(stgNum)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all shrink-0 cursor-pointer ${
                    isCurrent
                      ? 'bg-white text-slate-900 shadow-sm border border-slate-200/80 ring-1 ring-slate-900/5'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-lg flex items-center justify-center text-[10px] font-extrabold ${
                      isCurrent ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-700'
                    }`}
                  >
                    {stgNum}
                  </span>
                  <span className="hidden sm:inline">{meta.title.split('.')[1]?.trim().split(' ')[0] || `Stage ${stgNum}`}</span>
                  <span className="sm:hidden">Stage {stgNum}</span>
                </button>
              );
            })}
          </div>

          {/* Dynamic Stage Header */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border mb-1 ${STAGE_META[activeRoadmapStage].badge_color}`}>
                {STAGE_META[activeRoadmapStage].badge}
              </span>
              <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <i className={`fa-solid ${STAGE_META[activeRoadmapStage].icon} ${STAGE_META[activeRoadmapStage].icon_color}`} />
                {STAGE_META[activeRoadmapStage].title}
              </h3>
              <p className="text-xs text-blue-800 font-semibold mt-0.5">
                {STAGE_META[activeRoadmapStage].title_si}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {STAGE_META[activeRoadmapStage].desc}
              </p>
            </div>

            <button
              type="button"
              onClick={handleDownloadStageForm}
              disabled={isGenerating}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-extrabold text-xs shadow-md transition-all cursor-pointer disabled:opacity-50"
            >
              <i className={`fa-solid ${isGenerating ? 'fa-spinner fa-spin' : STAGE_META[activeRoadmapStage].btn_icon}`} />
              <span>{isGenerating ? 'Generating Official Form...' : STAGE_META[activeRoadmapStage].btn_label}</span>
            </button>
          </div>

          {/* Success Banner */}
          {downloadSuccess && (
            <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between">
              <span className="flex items-center gap-2 font-semibold">
                <i className="fa-solid fa-circle-check text-emerald-600 text-sm" />
                {downloadMessage}
              </span>
              <button
                type="button"
                onClick={() => setDownloadSuccess(false)}
                className="text-emerald-700 hover:text-emerald-900 text-xs font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>
          )}

          {/* ------------------------------------------------------------- */}
          {/* STAGE 1: NAME SEARCH & CLEARANCE (WP/BN/01) FORM PARTICULARS  */}
          {/* ------------------------------------------------------------- */}
          {activeRoadmapStage === 1 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs animate-fadeIn">
              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  1st Choice: Proposed Business Name (ප්‍රමුඛ ව්‍යාපාරික නාමය)
                </label>
                <input
                  type="text"
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  placeholder="e.g. CEYLON ARTISAN BAKEHOUSE"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  2nd Choice: Alternative Name (විකල්ප නාමය 1)
                </label>
                <input
                  type="text"
                  value={stage1Data.alt_name_1}
                  onChange={(e) => setStage1Data({ ...stage1Data, alt_name_1: e.target.value })}
                  placeholder="e.g. CEYLON HERITAGE BAKERY"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  3rd Choice: Alternative Name (විකල්ප නාමය 2)
                </label>
                <input
                  type="text"
                  value={stage1Data.alt_name_2}
                  onChange={(e) => setStage1Data({ ...stage1Data, alt_name_2: e.target.value })}
                  placeholder="e.g. ISLAND ARTISAN BAKES"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Target Divisional Secretariat (ප්‍රාදේශීය ලේකම් කාර්යාලය)
                </label>
                <select
                  value={formData.divisional_secretariat}
                  onChange={(e) => setFormData({ ...formData, divisional_secretariat: e.target.value })}
                  placeholder="e.g. Thimbirigasyaya Divisional Secretariat"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                >
                  <option value="Thimbirigasyaya Divisional Secretariat">Thimbirigasyaya DS (Colombo Central)</option>
                  <option value="Colombo Divisional Secretariat">Colombo DS (Fort / Pettah)</option>
                  <option value="Sri Jayawardenepura Kotte DS">Kotte DS (Rajagiriya / Nugegoda)</option>
                  <option value="Kaduwela Divisional Secretariat">Kaduwela DS (Malabe / Battaramulla)</option>
                  <option value="Dehiwala-Mount Lavinia DS">Dehiwala DS (Mount Lavinia)</option>
                  <option value="Gampaha Divisional Secretariat">Gampaha DS</option>
                  <option value="Negombo Divisional Secretariat">Negombo DS</option>
                  <option value="Kalutara Divisional Secretariat">Kalutara DS</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Commercial Sector &amp; Trade Line
                </label>
                <input
                  type="text"
                  value={formData.sector}
                  onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
                  placeholder="e.g. Food Manufacturing & Bakery Products"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Meaning &amp; Justification of Name (නාමයේ අර්ථය හෝ විශේෂත්වය)
                </label>
                <input
                  type="text"
                  value={stage1Data.name_meaning}
                  onChange={(e) => setStage1Data({ ...stage1Data, name_meaning: e.target.value })}
                  placeholder="e.g. Meaning and commercial origin of the proposed name"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Language Scripts</label>
                <input
                  type="text"
                  value={stage1Data.language_scripts}
                  onChange={(e) => setStage1Data({ ...stage1Data, language_scripts: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Statutory Reservation Validity</label>
                <input
                  type="text"
                  value={stage1Data.reservation_period}
                  readOnly
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Applicant Full Name (අයදුම්කරුගේ නම)</label>
                <input
                  type="text"
                  value={formData.owner_name}
                  onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
                  placeholder="e.g. Dhananjaya Bandara"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Applicant National ID (NIC)</label>
                <input
                  type="text"
                  value={formData.owner_nic}
                  onChange={(e) => setFormData({ ...formData, owner_nic: e.target.value })}
                  placeholder="e.g. 199415802345 or 851234567V"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-mono font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Contact Phone</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="e.g. +94 77 123 4567"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Inquiry Filing Date</label>
                <input
                  type="date"
                  value={stage1Data.search_date}
                  onChange={(e) => setStage1Data({ ...stage1Data, search_date: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>
            </div>
          )}

          {/* ------------------------------------------------------------- */}
          {/* STAGE 2: GRAMA NILADHARI ASSESSMENT REPORT PARTICULARS         */}
          {/* ------------------------------------------------------------- */}
          {activeRoadmapStage === 2 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs animate-fadeIn">
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Grama Niladhari Division (ග්‍රාම නිලධාරී වසම සහ අංකය)
                </label>
                <input
                  type="text"
                  value={formData.grama_niladhari}
                  onChange={(e) => setFormData({ ...formData, grama_niladhari: e.target.value })}
                  placeholder="e.g. Havelock Town (GN Division 512)"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Divisional Secretariat Division (ප්‍රාදේශීය ලේකම් කොට්ඨාසය)
                </label>
                <input
                  type="text"
                  value={formData.divisional_secretariat}
                  onChange={(e) => setFormData({ ...formData, divisional_secretariat: e.target.value })}
                  placeholder="e.g. Thimbirigasyaya Divisional Secretariat"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Physical Business Premises Address (ව්‍යාපාරික ස්ථානයේ ලිපිනය)
                </label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="e.g. No. 45, Galle Road, Colombo 04"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Premises Ownership Rights (පරිශ්‍රයේ නෛතික අයිතිය)
                </label>
                <select
                  value={stage2Data.ownership_type}
                  onChange={(e) => setStage2Data({ ...stage2Data, ownership_type: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                >
                  <option value="commercial_lease">Commercial Lease Deed (බදු ගිවිසුම මත)</option>
                  <option value="sole_owner">Sole Legal Owner (නිරවුල් අයිතිකරු - සින්නක්කර)</option>
                  <option value="tenancy">Monthly Tenancy with Consent (කුලී පදනම)</option>
                  <option value="family_consent">Family Property with Written Consent (පවුලේ දේපළක්)</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Deed / Stamped Lease Ref No. (ඔප්පු හෝ බදු ගිවිසුම් අංකය)
                </label>
                <input
                  type="text"
                  value={stage2Data.deed_lease_no}
                  onChange={(e) => setStage2Data({ ...stage2Data, deed_lease_no: e.target.value })}
                  placeholder="e.g. Lease Agreement No. 2024/481"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Property Owner / Landlord Name (දේපළ හිමිකරුගේ නම)
                </label>
                <input
                  type="text"
                  value={stage2Data.landlord_name}
                  onChange={(e) => setStage2Data({ ...stage2Data, landlord_name: e.target.value })}
                  placeholder="e.g. Mr. K. A. Perera"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Landlord Contact Phone</label>
                <input
                  type="text"
                  value={stage2Data.landlord_phone}
                  onChange={(e) => setStage2Data({ ...stage2Data, landlord_phone: e.target.value })}
                  placeholder="e.g. +94 77 345 6789"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Electoral Register Serial No. (ඡන්ද හිමි නාමලේඛන අංකය)
                </label>
                <input
                  type="text"
                  value={stage2Data.electoral_no}
                  onChange={(e) => setStage2Data({ ...stage2Data, electoral_no: e.target.value })}
                  placeholder="e.g. EL/COL/512/048"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-mono font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Assessment House No. (නිවාස හෝ තක්සේරු අංකය)
                </label>
                <input
                  type="text"
                  value={stage2Data.house_no}
                  onChange={(e) => setStage2Data({ ...stage2Data, house_no: e.target.value })}
                  placeholder="e.g. No. 12/B"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Applicant Permanent Residence Address (අයදුම්කරුගේ ස්ථිර පදිංචි ලිපිනය)
                </label>
                <input
                  type="text"
                  value={formData.residence_address}
                  onChange={(e) => setFormData({ ...formData, residence_address: e.target.value })}
                  placeholder="e.g. No. 12/B, Flower Road, Colombo 07"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Continuous Residence Period</label>
                <input
                  type="text"
                  value={stage2Data.residence_duration}
                  onChange={(e) => setStage2Data({ ...stage2Data, residence_duration: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Premises Inspection Readiness</label>
                <input
                  type="text"
                  value={stage2Data.inspection_readiness}
                  onChange={(e) => setStage2Data({ ...stage2Data, inspection_readiness: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>
            </div>
          )}

          {/* ------------------------------------------------------------- */}
          {/* STAGE 3: OFFICIAL STATUTORY FORM 1 STATEMENT OF PARTICULARS   */}
          {/* ------------------------------------------------------------- */}
          {activeRoadmapStage === 3 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs animate-fadeIn">
              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Proposed Business Name (ව්‍යාපාරික නාමය)
                </label>
                <input
                  type="text"
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Target Divisional Secretariat (ප්‍රාදේශීය ලේකම් කාර්යාලය)
                </label>
                <select
                  value={formData.divisional_secretariat}
                  onChange={(e) => setFormData({ ...formData, divisional_secretariat: e.target.value })}
                  placeholder="e.g. Thimbirigasyaya Divisional Secretariat"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                >
                  <option value="Thimbirigasyaya Divisional Secretariat">Thimbirigasyaya DS (Colombo Central)</option>
                  <option value="Colombo Divisional Secretariat">Colombo DS (Fort / Pettah)</option>
                  <option value="Sri Jayawardenepura Kotte DS">Kotte DS (Rajagiriya / Nugegoda)</option>
                  <option value="Kaduwela Divisional Secretariat">Kaduwela DS (Malabe / Battaramulla)</option>
                  <option value="Dehiwala-Mount Lavinia DS">Dehiwala DS (Mount Lavinia)</option>
                  <option value="Gampaha Divisional Secretariat">Gampaha DS</option>
                  <option value="Negombo Divisional Secretariat">Negombo DS</option>
                  <option value="Kalutara Divisional Secretariat">Kalutara DS</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Local Municipal / Urban Council (පළාත් පාලන ආයතනය)
                </label>
                <input
                  type="text"
                  value={formData.local_authority}
                  onChange={(e) => setFormData({ ...formData, local_authority: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Grama Niladhari Division (ග්‍රාම නිලධාරී වසම)
                </label>
                <input
                  type="text"
                  value={formData.grama_niladhari}
                  onChange={(e) => setFormData({ ...formData, grama_niladhari: e.target.value })}
                  placeholder="e.g. Havelock Town (GN Division 512)"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Commercial Sector &amp; Activities
                </label>
                <input
                  type="text"
                  value={formData.sector}
                  onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
                  placeholder="e.g. Food Manufacturing & Bakery Products"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Principal Place of Business (ව්‍යාපාරය පවත්වාගෙන යන ස්ථානය)
                </label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="e.g. No. 45, Galle Road, Colombo 04"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Applicant / Owner Full Name (අයදුම්කරුගේ සම්පූර්ණ නම)
                </label>
                <input
                  type="text"
                  value={formData.owner_name}
                  onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
                  placeholder="e.g. Dhananjaya Bandara"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  National Identity Card (NIC) (ජාතික හැඳුනුම්පත් අංකය)
                </label>
                <input
                  type="text"
                  value={formData.owner_nic}
                  onChange={(e) => setFormData({ ...formData, owner_nic: e.target.value })}
                  placeholder="e.g. 199415802345 or 851234567V"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-mono font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Contact Phone</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="e.g. +94 77 123 4567"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Contact Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Permanent Residential Address (ස්ථිර පදිංචි ලිපිනය)
                </label>
                <input
                  type="text"
                  value={formData.residence_address}
                  onChange={(e) => setFormData({ ...formData, residence_address: e.target.value })}
                  placeholder="e.g. No. 12/B, Flower Road, Colombo 07"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Commencement Date</label>
                <input
                  type="date"
                  value={formData.commencement_date}
                  onChange={(e) => setFormData({ ...formData, commencement_date: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Initial Capital (LKR)</label>
                <input
                  type="number"
                  value={formData.initial_capital}
                  onChange={(e) => setFormData({ ...formData, initial_capital: parseFloat(e.target.value) || 0 })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>
            </div>
          )}

          {/* ------------------------------------------------------------- */}
          {/* STAGE 4: MUNICIPAL COUNCIL TRADE TAX & HEALTH LICENSE FORM    */}
          {/* ------------------------------------------------------------- */}
          {activeRoadmapStage === 4 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs animate-fadeIn">
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Local Municipal / Urban Council (පළාත් පාලන ආයතනය)
                </label>
                <input
                  type="text"
                  value={formData.local_authority}
                  onChange={(e) => setFormData({ ...formData, local_authority: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Assessment Rates Account No. (තක්සේරු අංකය)
                </label>
                <input
                  type="text"
                  value={stage4Data.assessment_no}
                  onChange={(e) => setStage4Data({ ...stage4Data, assessment_no: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-mono font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Registered Business Name (ලියාපදිංචි ව්‍යාපාර නාමය)
                </label>
                <input
                  type="text"
                  value={formData.business_name}
                  onChange={(e) => setFormData({ ...formData, business_name: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  BR Certificate Reference No. (BR අංකය)
                </label>
                <input
                  type="text"
                  value={stage4Data.br_certificate_no}
                  onChange={(e) => setStage4Data({ ...stage4Data, br_certificate_no: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-mono font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Trade Classification (වෙළඳ වර්ගීකරණය)
                </label>
                <input
                  type="text"
                  value={stage4Data.trade_category}
                  onChange={(e) => setStage4Data({ ...stage4Data, trade_category: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Covered Premises Floor Area (වර්ග අඩි ප්‍රමාණය)
                </label>
                <input
                  type="text"
                  value={stage4Data.floor_area}
                  onChange={(e) => setStage4Data({ ...stage4Data, floor_area: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Public Health Inspector (PHI) Division (අදාළ PHI කොට්ඨාසය)
                </label>
                <input
                  type="text"
                  value={stage4Data.phi_division}
                  onChange={(e) => setStage4Data({ ...stage4Data, phi_division: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Medical Certified Food Handlers Count
                </label>
                <input
                  type="number"
                  value={stage4Data.food_handlers_certified}
                  onChange={(e) => setStage4Data({ ...stage4Data, food_handlers_certified: parseInt(e.target.value) || 0 })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Fire Protection Equipment (ගිනි නිවීමේ පහසුකම්)
                </label>
                <input
                  type="text"
                  value={stage4Data.fire_safety}
                  onChange={(e) => setStage4Data({ ...stage4Data, fire_safety: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block font-bold text-slate-700 mb-1">
                  Solid Waste &amp; Effluent Drainage Arrangement
                </label>
                <input
                  type="text"
                  value={stage4Data.waste_disposal}
                  onChange={(e) => setStage4Data({ ...stage4Data, waste_disposal: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>
            </div>
          )}

          {/* ------------------------------------------------------------- */}
          {/* STAGE 5: IRD RAMIS TIN & LABOUR EPF/ETF FORM D PARTICULARS    */}
          {/* ------------------------------------------------------------- */}
          {activeRoadmapStage === 5 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs animate-fadeIn">
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Taxpayer Classification (බදු ගෙවන්නාගේ වර්ගීකරණය)
                </label>
                <input
                  type="text"
                  value={stage5Data.taxpayer_type}
                  onChange={(e) => setStage5Data({ ...stage5Data, taxpayer_type: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  RAMIS TIN Application Status (TIN තත්ත්වය)
                </label>
                <select
                  value={stage5Data.tin_status}
                  onChange={(e) => setStage5Data({ ...stage5Data, tin_status: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                >
                  <option value="New RAMIS TIN Application Required">New RAMIS TIN Application Required</option>
                  <option value="Existing Individual TIN Registered">Existing Individual TIN Registered</option>
                  <option value="TIN Linked to Commercial Bank Mandate">TIN Linked to Commercial Bank Mandate</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Designated IRD Regional Unit (දේශීය ආදායම් ඒකකය)
                </label>
                <input
                  type="text"
                  value={stage5Data.ird_unit}
                  onChange={(e) => setStage5Data({ ...stage5Data, ird_unit: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Department of Labour District Office (කම්කරු කාර්යාලය)
                </label>
                <input
                  type="text"
                  value={stage5Data.labour_office}
                  onChange={(e) => setStage5Data({ ...stage5Data, labour_office: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Total Active Employees Count (සේවක සංඛ්‍යාව)
                </label>
                <input
                  type="number"
                  value={formData.employee_count}
                  onChange={(e) => setFormData({ ...formData, employee_count: parseInt(e.target.value) || 0 })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Estimated Monthly Wage Payroll (LKR)
                </label>
                <input
                  type="number"
                  value={stage5Data.monthly_payroll}
                  onChange={(e) => setStage5Data({ ...stage5Data, monthly_payroll: parseFloat(e.target.value) || 0 })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Statutory EPF Contribution (12% + 8%)
                </label>
                <input
                  type="text"
                  value={stage5Data.epf_status}
                  readOnly
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Statutory ETF Contribution (3% Employer)
                </label>
                <input
                  type="text"
                  value={stage5Data.etf_status}
                  readOnly
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Commercial Bank for Tax / EPF Remittance
                </label>
                <input
                  type="text"
                  value={stage5Data.bank_name}
                  onChange={(e) => setStage5Data({ ...stage5Data, bank_name: e.target.value })}
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Bank Branch &amp; Account Number
                </label>
                <input
                  type="text"
                  value={stage5Data.bank_account}
                  onChange={(e) => setStage5Data({ ...stage5Data, bank_account: e.target.value })}
                  placeholder="e.g. 1000849201"
                  className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs font-mono font-medium focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
                />
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar: Dynamic Stage Document Checklist & Submission Office */}
        <div className="space-y-5">
          {/* Stage-Specific Document Checklist Card */}
          <div className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <i className="fa-solid fa-list-check text-teal-600" />
                Stage {activeRoadmapStage} Documents Checklist
              </h4>
              <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
                {checklistScore}% Ready
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-teal-500 to-emerald-500 rounded-full transition-all duration-300"
                style={{ width: `${checklistScore}%` }}
              />
            </div>

            <p className="text-[11px] text-slate-500 leading-relaxed">
              Check off documents you have prepared for <strong>Stage {activeRoadmapStage} ({STAGE_META[activeRoadmapStage].title.split('.')[1]?.trim()})</strong>:
            </p>

            <div className="space-y-2 text-xs">
              {currentChecklistItems.map((doc) => {
                const isChecked = !!currentChecklistState[doc.key];
                return (
                  <label
                    key={doc.key}
                    onClick={() => toggleChecklist(doc.key)}
                    className={`flex items-start gap-2.5 p-2.5 rounded-xl border transition-all cursor-pointer ${
                      isChecked ? 'bg-teal-50/60 border-teal-200' : 'bg-slate-50/50 border-slate-200/80 hover:bg-slate-100'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => {}}
                      className="mt-0.5 rounded text-teal-600 focus:ring-teal-500"
                    />
                    <div>
                      <span className={`block font-bold text-xs ${isChecked ? 'text-teal-950' : 'text-slate-700'}`}>
                        {doc.label}
                      </span>
                      <span className="text-[10px] text-slate-500 leading-tight block">{doc.desc}</span>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Dynamic Stage-Specific Submission Guidance Card */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-3xl p-5 shadow-xs border border-slate-700 space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-8 h-8 rounded-xl bg-teal-500/20 text-teal-400 flex items-center justify-center text-sm">
                <i className="fa-solid fa-building-columns" />
              </span>
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                  {STAGE_SUBMISSION_INFO[activeRoadmapStage]?.title || 'Submission Office'}
                </h4>
                <p className="text-[10px] text-teal-300 font-mono">
                  {STAGE_SUBMISSION_INFO[activeRoadmapStage]?.subtitle}
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {STAGE_SUBMISSION_INFO[activeRoadmapStage]?.desc}
            </p>

            <div className="pt-2 border-t border-slate-700/80 space-y-1.5 text-[11px] text-slate-300">
              <div className="flex items-center justify-between">
                <span>Working Hours:</span>
                <span className="text-white font-semibold">
                  {STAGE_SUBMISSION_INFO[activeRoadmapStage]?.hours}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Processing Time:</span>
                <span className="text-teal-400 font-bold">
                  {STAGE_SUBMISSION_INFO[activeRoadmapStage]?.time}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Statutory Duty:</span>
                <span className="text-emerald-400 font-bold">
                  {STAGE_SUBMISSION_INFO[activeRoadmapStage]?.fee}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessRegistrationView;
