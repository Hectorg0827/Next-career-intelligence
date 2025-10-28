// Minimal user types
export interface UserProfile {
  uid?: string;
  email?: string | null;
  displayName?: string | null;
  isPro?: boolean;
  [key: string]: any;
}
