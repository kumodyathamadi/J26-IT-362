import { ComplianceEvaluationResult, SectorType } from './types';

export const COLOMBO_LEGAL_DATABASE: Record<SectorType, ComplianceEvaluationResult> = {
  food: {
    businessContext: {
      id: 'biz-food-01',
      name: 'Lanka Spice Kitchen',
      sector: 'food',
      sectorLabel: 'Food & Beverage',
      entityType: 'Sole proprietorship',
      council: 'Colombo Municipal Council',
      province: 'Western Province',
      district: 'Colombo District',
      employeesCount: 6,
      annualRevenueLkr: 45000000,
      description: 'Commercial eatery & spice processing unit operating in Colombo 03, Western Province.',
      activities: ['Food preparation', 'Spice grinding & packaging', 'Retail sales']
    },
    readinessPercentage: 14,
    totalRulesEvaluated: 17,
    applicableRulesCount: 11,
    completedCount: 1,
    inProgressCount: 1,
    nextBestAction: {
      title: 'Taxpayer Identification Number (TIN)',
      authority: 'Inland Revenue Department (RAMIS)',
      deadlineDays: 16,
      rationale: 'Mandatory before opening a business bank account in Sri Lanka (LKR 2024 IRD directive).',
      stepId: 'tin'
    },
    summaryCounts: {
      registrations: 3,
      licensesAndPermits: 4,
      taxAndRegulatory: 4,
      dueWithin30Days: 9,
      overdue: 0
    },
    requirements: [
      {
        id: 'bizname',
        stepNumber: 1,
        title: 'Establish Legal Identity & Business Name Registration',
        authority: 'Dept. of Business Names (Western Province Provincial Council)',
        category: 'Registration',
        status: 'Completed',
        estimatedFeeLkr: 2500,
        validityDuration: 'Permanent',
        documentsRequired: ['Form A', 'Grama Niladhari Certificate', 'NIC Copy', 'Assessment Tax Receipt'],
        citationId: 'cite-bizname-wp'
      },
      {
        id: 'tin',
        stepNumber: 2,
        title: 'Taxpayer Identification Number (TIN) & RAMIS Registration',
        authority: 'Inland Revenue Department (IRD)',
        category: 'Tax',
        status: 'In Progress',
        dueDate: 'Due in 16 days',
        estimatedFeeLkr: 0,
        validityDuration: 'Permanent',
        documentsRequired: ['Form A Business Certificate', 'NIC', 'Bank Account Request Letter'],
        citationId: 'cite-tin-ird'
      },
      {
        id: 'cmc-trade',
        stepNumber: 3,
        title: 'Colombo Municipal Council Trade License & Assessment Tax Clearance',
        authority: 'Colombo Municipal Council (CMC)',
        category: 'License',
        status: 'Action Required',
        dueDate: 'Due in 30 days',
        estimatedFeeLkr: 12500,
        validityDuration: 'Annual (Dec 31)',
        documentsRequired: ['Building Plan / Assessment Receipt', 'PHI Inspection Pass', 'Business Name Cert'],
        citationId: 'cite-cmc-trade-by-law'
      },
      {
        id: 'phi-food',
        stepNumber: 4,
        title: 'Public Health Inspector (PHI) & Food Safety Permit',
        authority: 'Ministry of Health / CMC Health Department',
        category: 'License',
        status: 'Pending Prerequisites',
        estimatedFeeLkr: 5000,
        validityDuration: 'Annual',
        documentsRequired: ['Staff Medical Examination Cards (Form H-12)', 'Water Quality Test', 'Kitchen Blueprint'],
        citationId: 'cite-food-act-1980'
      },
      {
        id: 'epf-etf',
        stepNumber: 5,
        title: 'EPF & ETF Employer Registration (Form D)',
        authority: 'Department of Labour Sri Lanka',
        category: 'Labour',
        status: 'Pending Prerequisites',
        estimatedFeeLkr: 0,
        validityDuration: 'Permanent',
        documentsRequired: ['Form D', 'Form H', 'Business Registration', 'Staff NIC Copies'],
        citationId: 'cite-epf-act-1958'
      }
    ],
    ragCitations: {
      'cite-tin-ird': {
        id: 'cite-tin-ird',
        actTitle: 'Inland Revenue Act No. 24 of 2017 & RAMIS Gazette 2024',
        subTitle: 'Mandatory RAMIS Tax Registration for Sri Lankan Commercial Entities',
        jurisdiction: 'National / Western Prov.',
        enforcingAuthority: 'Inland Revenue Department (RAMIS)',
        vectorSimilarityScore: 0.994,
        legalExcerpt: '"Section 102: Every entity engaging in trade, business, or vocation in Sri Lanka must register with the Commissioner General of Inland Revenue to obtain a Taxpayer Identification Number (TIN)..."',
        explainabilityRationale: 'Operating a commercial food business generating gross receipts requires a mandatory TIN before bank account creation and local trade licensing in Colombo District.',
        penaltyRiskText: 'Penalty of LKR 50,000 for non-registration plus inability to obtain municipal trade clearance.',
        requiredArtifacts: ['Form A / Certificate of Business Name', 'National Identity Card (NIC)', 'Bank Account Request Letter', 'Proof of Business Location']
      },
      'cite-bizname-wp': {
        id: 'cite-bizname-wp',
        actTitle: 'Business Names Statute No. 6 of 1990 (Western Province)',
        subTitle: 'Registration of business names in Colombo District',
        jurisdiction: 'Western Province',
        enforcingAuthority: 'Dept of Business Names (WP)',
        vectorSimilarityScore: 0.984,
        legalExcerpt: '"Every person or firm carrying on business under a business name in the Western Province must register it under this Statute within 14 days of establishment..."',
        explainabilityRationale: 'Because your business "Lanka Spice Kitchen" is operated as a Sole Proprietorship under a trade name, mandatory WP registration applies.',
        penaltyRiskText: 'Fines up to LKR 50,000 under WP Provincial Council regulations and contract invalidation.',
        requiredArtifacts: ['Form A (Application)', 'Grama Niladhari Certificate', 'NIC Copy', 'Assessment Tax Receipt']
      },
      'cite-cmc-trade-by-law': {
        id: 'cite-cmc-trade-by-law',
        actTitle: 'Colombo Municipal Council Ordinance (Cap 252) & By-Laws',
        subTitle: 'Local Authority Trade Licensing for Food Establishments',
        jurisdiction: 'Colombo Municipal Council',
        enforcingAuthority: 'CMC Health & Licensing Dept',
        vectorSimilarityScore: 0.988,
        legalExcerpt: '"No person shall maintain a food outlet, bakery, or spice processing unit within the Colombo Municipal Council limits without an annual trade license issued under Section 14..."',
        explainabilityRationale: 'Physical establishment located in Ward 3 (Colombo 03) falls under Colombo Municipal Council jurisdiction requiring local council trade assessment.',
        penaltyRiskText: 'Sealing of commercial premises and daily compounding fines under Municipal Council bylaws.',
        requiredArtifacts: ['Approved Building Plan / Assessment Tax Receipt', 'PHI Inspection Certificate', 'NIC Copy', 'Business Name Registration']
      },
      'cite-food-act-1980': {
        id: 'cite-food-act-1980',
        actTitle: 'Food Act No. 26 of 1980 & Food Hygiene Regulations 2011',
        subTitle: 'Public Health Inspector Sanitary Clearance for Food Handlers',
        jurisdiction: 'Western Province MOH',
        enforcingAuthority: 'Chief Medical Officer / PHI',
        vectorSimilarityScore: 0.979,
        legalExcerpt: '"Part II Section 4: Food processing premises must maintain potable water testing, pest control, medical certificates for all kitchen staff, and grease trap installation..."',
        explainabilityRationale: 'Preparation and sale of cooked spice products requires PHI site inspection and staff health clearance.',
        penaltyRiskText: 'Confiscation of food items, immediate suspension of trade, and prosecution in Magistrate Court.',
        requiredArtifacts: ['Staff Medical Examination Cards (Form H-12)', 'Water Quality Test Report', 'Kitchen Blueprint Layout', 'Grease Trap Specs']
      },
      'cite-epf-act-1958': {
        id: 'cite-epf-act-1958',
        actTitle: 'Employees Provident Fund Act No. 15 of 1958 & ETF Act',
        subTitle: 'Statutory Employee Provident & Trust Fund Registration',
        jurisdiction: 'Department of Labour',
        enforcingAuthority: 'Labour Secretariat, Narahenpita',
        vectorSimilarityScore: 0.991,
        legalExcerpt: '"Every employer employing one or more employees in any undertaking shall register as an employer with the Labour Department within 14 days of employment..."',
        explainabilityRationale: 'With 6 active employees, Lanka Spice Kitchen is legally mandated to remit 12% EPF + 3% ETF monthly.',
        penaltyRiskText: 'Surcharges up to 50% on unpaid contributions and prosecution of business owner.',
        requiredArtifacts: ['Form D (Employer Registration)', 'Form H (Member Details)', 'Copy of Business Name Certificate', 'NIC copies of employees']
      }
    }
  },

  clothing: {
    businessContext: {
      id: 'biz-clothing-01',
      name: 'Urban Thread Boutique Pvt Ltd',
      sector: 'clothing',
      sectorLabel: 'Clothing & Apparel Retail',
      entityType: 'Private Limited (Pvt Ltd)',
      council: 'Colombo Municipal Council',
      province: 'Western Province',
      district: 'Colombo District',
      employeesCount: 12,
      annualRevenueLkr: 85000000,
      description: 'Fashion retail boutique & apparel warehouse in Bambalapitiya, Colombo 04.',
      activities: ['Textile retail', 'Apparel storage', 'Online garment sales']
    },
    readinessPercentage: 35,
    totalRulesEvaluated: 15,
    applicableRulesCount: 10,
    completedCount: 3,
    inProgressCount: 2,
    nextBestAction: {
      title: 'Fire & Safety Service Certificate',
      authority: 'Colombo Fire Service Department',
      deadlineDays: 10,
      rationale: 'Commercial retail outlet > 1,500 sq.ft requires Fire Safety Clearance before CMC Trade License renewal.',
      stepId: 'fire-safety'
    },
    summaryCounts: {
      registrations: 4,
      licensesAndPermits: 3,
      taxAndRegulatory: 5,
      dueWithin30Days: 5,
      overdue: 0
    },
    requirements: [
      {
        id: 'company-roc',
        stepNumber: 1,
        title: 'Form 1 (ROC Company Incorporation)',
        authority: 'Registrar of Companies (Department of Registrar of Companies)',
        category: 'Registration',
        status: 'Completed',
        estimatedFeeLkr: 35000,
        validityDuration: 'Permanent',
        documentsRequired: ['Form 1', 'Form 18', 'Form 20', 'Articles of Association'],
        citationId: 'cite-roc-companies-act'
      },
      {
        id: 'fire-safety',
        stepNumber: 2,
        title: 'Fire & Safety Clearance Certificate',
        authority: 'Colombo Fire Brigade',
        category: 'License',
        status: 'In Progress',
        dueDate: 'Due in 10 days',
        estimatedFeeLkr: 15000,
        validityDuration: 'Annual',
        documentsRequired: ['Floor Plan', 'Fire Extinguisher Test Receipt', 'Inspection Application'],
        citationId: 'cite-fire-safety-cmc'
      }
    ],
    ragCitations: {
      'cite-roc-companies-act': {
        id: 'cite-roc-companies-act',
        actTitle: 'Companies Act No. 07 of 2007',
        subTitle: 'Incorporation of Private Limited Liability Companies',
        jurisdiction: 'National',
        enforcingAuthority: 'Registrar of Companies (ROC Sri Lanka)',
        vectorSimilarityScore: 0.998,
        legalExcerpt: '"Section 4: Any two or more persons may form an incorporated company by subscribing to the articles of association..."',
        explainabilityRationale: 'Entity registered as Private Limited structure requiring mandatory ROC registration.',
        penaltyRiskText: 'Failure to file annual returns results in strike-off from the corporate register.',
        requiredArtifacts: ['Form 1', 'Form 18', 'Form 20', 'Articles of Association']
      },
      'cite-fire-safety-cmc': {
        id: 'cite-fire-safety-cmc',
        actTitle: 'CMC Fire Prevention & Commercial Establishment By-Laws',
        subTitle: 'Fire Clearance for Textile & High Storage Outlets',
        jurisdiction: 'Colombo Municipal Council',
        enforcingAuthority: 'Fire Service Department',
        vectorSimilarityScore: 0.982,
        legalExcerpt: '"Retail stores stocking combustible fabric textiles exceeding 100 sq.meters must install certified smoke detectors and fire extinguishers..."',
        explainabilityRationale: 'Textile retail inventory carries fire load ratings requiring mandatory inspection from Colombo Fire Department at T.B. Jaya Mawatha.',
        penaltyRiskText: 'Immediate closure of retail premises by Municipal Commissioner.',
        requiredArtifacts: ['Floor Plan Diagram', 'Fire Extinguisher Maintenance Receipt', 'Building Inspection Fee Slip']
      }
    }
  },

  saloon: {
    businessContext: {
      id: 'biz-saloon-01',
      name: 'Glamour & Glow Beauty Saloon',
      sector: 'saloon',
      sectorLabel: 'Saloon & Personal Care',
      entityType: 'Sole proprietorship',
      council: 'Sri Jayawardenepura Kotte MC',
      province: 'Western Province',
      district: 'Colombo District',
      employeesCount: 4,
      annualRevenueLkr: 18000000,
      description: 'Hair styling, cosmetics & wellness salon in Rajagiriya, Sri Jayawardenepura Kotte.',
      activities: ['Hair styling', 'Skin treatments', 'Cosmetic application']
    },
    readinessPercentage: 20,
    totalRulesEvaluated: 14,
    applicableRulesCount: 9,
    completedCount: 1,
    inProgressCount: 2,
    nextBestAction: {
      title: 'Kotte MC Health & Sanitation Clearance',
      authority: 'Sri Jayawardenepura Kotte Municipal Health Dept',
      deadlineDays: 7,
      rationale: 'Mandatory sanitary inspection for hair dressing, chemical treatment, and sterilizing equipment.',
      stepId: 'kotte-health'
    },
    summaryCounts: {
      registrations: 2,
      licensesAndPermits: 3,
      taxAndRegulatory: 3,
      dueWithin30Days: 4,
      overdue: 0
    },
    requirements: [
      {
        id: 'kotte-health',
        stepNumber: 1,
        title: 'Sanitary & Health Permit for Personal Care Parlours',
        authority: 'Sri Jayawardenepura Kotte MC',
        category: 'License',
        status: 'Action Required',
        dueDate: 'Due in 7 days',
        estimatedFeeLkr: 6500,
        validityDuration: 'Annual',
        documentsRequired: ['PHI Sanitary Pass', 'Autoclave Invoice', 'Cosmetology License'],
        citationId: 'cite-saloon-health-kotte'
      }
    ],
    ragCitations: {
      'cite-saloon-health-kotte': {
        id: 'cite-saloon-health-kotte',
        actTitle: 'Provincial Health & Beauty Parlour Guidelines 2022',
        subTitle: 'Sterilization & Public Health Standards for Salons',
        jurisdiction: 'Western Province Health Directorate',
        enforcingAuthority: 'PHI Officer Kotte',
        vectorSimilarityScore: 0.985,
        legalExcerpt: '"Salons using chemical hair dyes, skin treatment agents, and sharp tools must utilize UV sterilizers and autoclaves with proper hazardous waste management..."',
        explainabilityRationale: 'Personal care services involving skin & hair chemical applications fall under localized sanitary regulations.',
        penaltyRiskText: 'Revocation of business name clearance and cancellation of trade permit.',
        requiredArtifacts: ['Autoclave Purchase Invoice', 'Chemical Product NMRA Registration Copies', 'Staff Cosmetology Certificates']
      }
    }
  },

  vehicle: {
    businessContext: {
      id: 'biz-vehicle-01',
      name: 'Lanka Auto Gear & Spares',
      sector: 'vehicle',
      sectorLabel: 'Vehicle Parts, Repair & Resell',
      entityType: 'Partnership',
      council: 'Dehiwala-Mount Lavinia MC',
      province: 'Western Province',
      district: 'Colombo District',
      employeesCount: 15,
      annualRevenueLkr: 120000000,
      description: 'Auto spare parts importer, repair workshop & component reselling in Mount Lavinia.',
      activities: ['Vehicle repair workshop', 'Spare parts import & resale', 'Used parts reselling']
    },
    readinessPercentage: 40,
    totalRulesEvaluated: 22,
    applicableRulesCount: 14,
    completedCount: 4,
    inProgressCount: 3,
    nextBestAction: {
      title: 'Central Environmental Authority (CEA) EPL Clearance',
      authority: 'Central Environmental Authority (CEA Sri Lanka)',
      deadlineDays: 21,
      rationale: 'Waste oil management & noise level compliance mandatory for vehicle repair garages.',
      stepId: 'cea-epl'
    },
    summaryCounts: {
      registrations: 4,
      licensesAndPermits: 5,
      taxAndRegulatory: 5,
      dueWithin30Days: 8,
      overdue: 0
    },
    requirements: [
      {
        id: 'cea-epl',
        stepNumber: 1,
        title: 'Environmental Protection License (EPL Class B-12)',
        authority: 'Central Environmental Authority (CEA)',
        category: 'Environmental',
        status: 'Action Required',
        dueDate: 'Due in 21 days',
        estimatedFeeLkr: 15000,
        validityDuration: '3 Years',
        documentsRequired: ['Oil Trap Sump Plan', 'Waste Oil Vendor Agreement', 'Noise Control Specs'],
        citationId: 'cite-cea-epl-garage'
      }
    ],
    ragCitations: {
      'cite-cea-epl-garage': {
        id: 'cite-cea-epl-garage',
        actTitle: 'National Environmental Act No. 47 of 1980 (EPL Schedule Order)',
        subTitle: 'Prescribed Activities List for Vehicle Service Garages & Spares',
        jurisdiction: 'Central Environmental Authority (CEA)',
        enforcingAuthority: 'CEA Western Province Office',
        vectorSimilarityScore: 0.997,
        legalExcerpt: '"Prescribed Activity Class B-12: Garages engaging in engine overhaul, spray painting, or bulk storage of waste mineral oils require a valid Environmental Protection License..."',
        explainabilityRationale: 'Automotive repair activities emit effluent waste oil and noise requiring CEA environmental clearance prior to local council renewal.',
        penaltyRiskText: 'Court injunction closing workshop and fines up to LKR 100,000 per day of default.',
        requiredArtifacts: ['Oil Separator Sump Plan', 'Waste Management Agreement with Licensed Disposal Vendor', 'Site Plan Layout']
      }
    }
  }
};
