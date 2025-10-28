// Minimal coach types
export interface Message {
  id?: string;
  sender?: string;
  content?: string;
  timestamp?: string | Date;
  [key: string]: any;
}

export interface Conversation {
  id?: string;
  title?: string;
  messages?: Message[];
  created_at?: string | Date;
  updated_at?: string | Date;
  [key: string]: any;
}
