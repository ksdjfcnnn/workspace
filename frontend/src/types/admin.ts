export interface ProjectTimeAnalytics {
  totalTime: number;
  projectBreakdown: {
    [projectId: string]: {
      projectId: string;
      projectName: string;
      totalTime: number;
      percentage: number;
    };
  };
}

export interface Screenshot {
  id: string;
  employeeId: string;
  employeeName: string;
  projectId: string;
  projectName: string;
  taskId: string;
  taskName: string;
  timestamp: number;
  imageUrl: string;
  activityLevel: number;
}

export interface ScreenshotResponse {
  items: Screenshot[];
  nextToken?: string;
}