/**
 * EcoSort AI - Navigation Types (Stage 6 Redesign).
 */

export type NavigationTab = 'dashboard' | 'analyze' | 'history' | 'insights' | 'settings';

export type AnalyzeMode = 'camera' | 'upload' | 'text';

export interface NavItem {
  id: NavigationTab;
  label: string;
  description: string;
}
