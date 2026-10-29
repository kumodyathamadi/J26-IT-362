/**
 * Component 2: AI-Based Business Registration & Regulatory Compliance
 * Scope: Sri Lanka - Western Province (Colombo District)
 * Research Topic: AI-Driven Business Lifecycle Decision Support System
 */

export type SectorType = 'food' | 'clothing' | 'saloon' | 'vehicle';

export type EntityType = 'Sole proprietorship' | 'Partnership' | 'Private Limited (Pvt Ltd)';

export type MunicipalCouncil = 
  | 'Colombo Municipal Council'
  | 'Sri Jayawardenepura Kotte MC'
  | 'Dehiwala-Mount Lavinia MC'
  | 'Kaduwela Municipal Council';

export interface BusinessContext {
  id: string;
  name: string;
  sector: SectorType;
  sectorLabel: string;
  entityType: EntityType;
  council: MunicipalCouncil;
  province: 'Western Province';
  district: 'Colombo District';
  employeesCount: number;
  annualRevenueLkr: number;
  description: string;
  activities: string[];
}

export interface ComplianceRequirement {
  id: string;
  stepNumber: number;
  title: string;
  authority: string;
  category: 'Registration' | 'License' | 'Tax' | 'Environmental' | 'Labour';
  status: 'Completed' | 'In Progress' | 'Action Required' | 'Pending Prerequisites';
  dueDate?: string;
  estimatedFeeLkr: number;
  validityDuration: string;
  documentsRequired: string[];
  citationId: string;
}

export interface RAGLegalCitation {
  id: string;
  actTitle: string;
  subTitle: string;
  jurisdiction: string;
  enforcingAuthority: string;
  vectorSimilarityScore: number; // e.g. 0.984
  legalExcerpt: string;
  explainabilityRationale: string;
  penaltyRiskText: string;
  requiredArtifacts: string[];
}

export interface ComplianceEvaluationResult {
  businessContext: BusinessContext;
  readinessPercentage: number;
  totalRulesEvaluated: number;
  applicableRulesCount: number;
  completedCount: number;
  inProgressCount: number;
  nextBestAction: {
    title: string;
    authority: string;
    deadlineDays: number;
    rationale: string;
    stepId: string;
  };
  summaryCounts: {
    registrations: number;
    licensesAndPermits: number;
    taxAndRegulatory: number;
    dueWithin30Days: number;
    overdue: number;
  };
  requirements: ComplianceRequirement[];
  ragCitations: Record<string, RAGLegalCitation>;
}
