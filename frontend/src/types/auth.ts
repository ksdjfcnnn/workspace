export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  isAdmin: boolean;
  emailVerified: boolean;
  deactivated: boolean;
  organizationId: string;
  teamId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserStats {
  totalProjects: number;
  totalTasks: number;
  totalTimeTracked: number;
  activeProjects: number;
  activeTasks: number;
}

export interface DecodedToken {
  sub: string;
  email: string;
  isAdmin: boolean;
  exp: number;
}