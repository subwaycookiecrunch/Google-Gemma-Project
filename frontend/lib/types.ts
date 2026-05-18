export interface FeedingPoint {
  node_id: string;
  name: string;
  file: string;
  line: number;
  blast_radius_score: number;
  stealth_score: number;
  persistence_score: number;
  final_score: number;
  danger_level: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  explanation: string;
  attack_surfaces: string[];
  attack_approach: string;
}

export interface MutationRecord {
  mutation_id: string;
  generation: number;
  approach: string;
  code_generated: string;
  fitness_before: number;
  fitness_after: number;
  survived: boolean;
  reasoning: string;
}

export interface Strain {
  strain_id: string;
  generation: number;
  status: 'alive' | 'dead' | 'dominant' | 'mutating';
  fitness_score: number;
  stealth_score: number;
  blast_radius_score: number;
  persistence_score: number;
  attack_approach: string;
  camouflage_code: string;
  mutation_history: MutationRecord[];
  personality_notes: string;
  target_feeding_point: FeedingPoint;
  last_mutated_at?: string;
  created_at?: string;
}

export interface AttackStep {
  step_number: number;
  action: string;
  target_node: string;
  technique: string;
  code_involved: string;
  detection_risk: string;
  impact: string;
  stealth_note: string;
}

export interface AttackPath {
  path_id: string;
  name: string;
  attack_type: string;
  entry_point: string;
  steps: AttackStep[];
  total_steps: number;
  detection_probability: number;
  time_to_execute: string;
  damage_description: string;
  blast_radius: string;
  final_impact: string;
}

export interface KillEvent {
  timestamp: string;
  event_type: string;
  description: string;
  affected_component: string;
  severity: string;
  stealth_level: 'VISIBLE' | 'HIDDEN' | 'GHOST';
  would_trigger_alert: boolean;
  alert_system?: string;
}

export interface KillSimulation {
  simulation_id: string;
  attack_path_name: string;
  attack_path_type: string;
  events: KillEvent[];
  total_duration: string;
  was_detected: boolean;
  detection_point?: string;
  survival_rate: number;
  final_state: string;
  damage_summary: string;
}

export interface TimeToImpact {
  days_until_natural_discovery: number;
  minutes_to_complete_attack: number;
  hours_until_irreversible: number;
  opportunity_window_days: number;
  urgency_rating: string;
  prediction_confidence: number;
  survival_curve_data: { day: number; survival: number }[];
  key_insight: string;
}

export interface InfiltrationStats {
  files: number;
  functions: number;
  edges: number;
  privilege_ops: number;
  dataflow_paths: number;
  critical_ops: number;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  layer: string;
  file?: string;
  language?: string;
  line_start?: number;
  line_end?: number;
  privilege_ops?: string[];
  risk_level?: string;
  is_input_source?: boolean;
  is_dangerous_sink?: boolean;
  weight?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  layer: string;
  label?: string;
  weight?: number;
  risk_level?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface InfiltrationResult {
  session_id: string;
  stats: InfiltrationStats;
  graph: GraphData;
  feeding_points: FeedingPoint[];
  infiltration_complete: boolean;
}

export interface EvolutionSession {
  session_id: string;
  strains: Strain[];
  generation: number;
  dominant_strain?: Strain;
  dead_strains: Strain[];
  evolution_log: string[];
  complete: boolean;
}

export interface RevelationResult {
  session_id: string;
  attack_paths: AttackPath[];
  kill_simulation: KillSimulation;
  time_to_impact: TimeToImpact;
  dominant_strain_id: string;
  dominant_target: string;
  revelation_log: string[];
  final_verdict: string;
  complete: boolean;
}
