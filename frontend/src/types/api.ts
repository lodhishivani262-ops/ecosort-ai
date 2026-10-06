/**
 * EcoSort AI - Frontend TypeScript API Contracts (Stage 6).
 * Strictly mirrors backend FastAPI & Pydantic models from Stages 2–5.
 */

export type WasteCategory =
  | 'ORGANIC / WET WASTE'
  | 'DRY WASTE'
  | 'RECYCLABLE'
  | 'E-WASTE'
  | 'HAZARDOUS / SPECIAL HANDLING'
  | 'GLASS'
  | 'SANITARY WASTE'
  | 'UNKNOWN / UNCLASSIFIED';

export type ConfidenceLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export type ContaminationLevel = 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'UNKNOWN';

export type InputType = 'IMAGE' | 'TEXT';

export interface WastePerception {
  item_name: string;
  material: string;
  condition: string;
  contamination: ContaminationLevel;
  visual_clues: string[];
  confidence: ConfidenceLevel;
  uncertainty_reason: string | null;
  is_safety_sensitive: boolean;
}

export interface WasteRecommendation {
  category: WasteCategory;
  preparation_steps: string[];
  disposal_guidance: string;
  warnings: string[];
  confidence: ConfidenceLevel;
  reason: string;
  uncertainty_reason: string | null;
}

export interface ClassificationResultResponse {
  request_id: string;
  input_type: InputType;
  perception: WastePerception;
  recommendation: WasteRecommendation;
  mock: boolean;
}

export type FeedbackType =
  | 'HELPFUL'
  | 'NOT_HELPFUL'
  | 'INCORRECT_CATEGORY'
  | 'INCORRECT_IDENTIFICATION'
  | 'UNCLEAR_GUIDANCE'
  | 'OTHER';

export interface FeedbackCreate {
  request_id: string;
  rating?: number | null;
  feedback_type: FeedbackType;
  comment?: string | null;
}

export interface FeedbackResponse {
  success: boolean;
  message: string;
  request_id: string;
  created_at: string;
}

export interface ClassificationHistoryItem {
  request_id: string;
  created_at: string;
  input_type: string;
  item_name: string;
  material: string;
  condition: string;
  contamination: string;
  ai_confidence: string;
  category: string;
  recommendation_confidence: string;
  warning_count: number;
  processing_time_ms: number;
  status: string;
}

export interface HistoryResponse {
  session_id: string | null;
  total: number;
  items: ClassificationHistoryItem[];
}

export interface CategoryBreakdown {
  category: string;
  count: number;
  percentage: number;
}

export interface FeedbackMetrics {
  total_feedback: number;
  helpful_count: number;
  not_helpful_count: number;
  helpful_percentage: number;
  average_rating: number | null;
  type_breakdown: Record<string, number>;
}

export interface MetricsResponse {
  total_classifications: number;
  successful_classifications: number;
  failed_classifications: number;
  average_processing_time_ms: number;
  low_confidence_percentage: number;
  categories: CategoryBreakdown[];
  feedback: FeedbackMetrics;
}

export interface ApiErrorDetail {
  code: string;
  message: string;
}

export interface ApiErrorResponse {
  error: ApiErrorDetail;
}
