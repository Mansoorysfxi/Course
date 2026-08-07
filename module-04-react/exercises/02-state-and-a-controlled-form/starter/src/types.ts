export type Priority = "low" | "medium" | "high";

export interface Quest {
  id: string;
  title: string;
  priority: Priority;
  done: boolean;
}
