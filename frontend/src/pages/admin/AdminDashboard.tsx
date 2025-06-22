import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  CircularProgress, 
  Card, 
  CardContent, 
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { Grid } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { adminApi } from '../../services/api';
import { ProjectTimeAnalytics, Screenshot } from '../../types/admin';
import BarChartIcon from '@mui/icons-material/BarChart';
import PeopleIcon from '@mui/icons-material/People';
import PhotoLibraryIcon from '@mui/icons-material/PhotoLibrary';

const AdminDashboard: React.FC = () => {
  const { } = useAuth(); // Removed unused user variable
  const [analytics, setAnalytics] = useState<ProjectTimeAnalytics | null>(null);
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get data for the last 7 days
        const now = Date.now();
        const sevenDaysAgo = now - 7 * 24 * 60 * 60 * 1000;
        
        // Fetch project time analytics
        const analyticsResponse = await adminApi.getProjectTimeAnalytics({
          start: sevenDaysAgo,
          end: now
        });
        
        // Fetch recent screenshots
        const screenshotsResponse = await adminApi.getScreenshots({
          start: sevenDaysAgo,
          end: now,
          limit: 5
        });
        
        setAnalytics(analyticsResponse.data);
        setScreenshots(screenshotsResponse.data);
      } catch (err) {
        console.error('Failed to fetch admin dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Format time tracked (milliseconds to hours)
  const formatTimeTracked = (ms: number) => {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  // Format timestamp to date
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box mt={4}>
        <Typography color="error" variant="h6" align="center">
          {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      
      <Typography variant="subtitle1" color="textSecondary" paragraph>
        Organization overview for the last 7 days
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Stats Cards */}
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardHeader
              avatar={<BarChartIcon color="primary" />}
              title="Total Time Tracked"
            />
            <CardContent>
              <Typography variant="h4">
                {analytics?.totalTime ? formatTimeTracked(analytics.totalTime) : '0h 0m'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Across all projects
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardHeader
              avatar={<PeopleIcon color="primary" />}
              title="Active Projects"
            />
            <CardContent>
              <Typography variant="h4">
                {analytics?.projectBreakdown ? Object.keys(analytics.projectBreakdown).length : 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Projects with activity
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardHeader
              avatar={<PhotoLibraryIcon color="primary" />}
              title="Recent Screenshots"
            />
            <CardContent>
              <Typography variant="h4">{screenshots.length}</Typography>
              <Typography variant="body2" color="textSecondary">
                Screenshots captured
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Project Breakdown */}
        <Grid item xs={12} sx={{ mt: 2 }}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Project Time Breakdown
            </Typography>
            
            {analytics && Object.keys(analytics.projectBreakdown).length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Project</TableCell>
                      <TableCell>Time Tracked</TableCell>
                      <TableCell>Percentage</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.values(analytics.projectBreakdown).map((project) => (
                      <TableRow key={project.projectId}>
                        <TableCell>{project.projectName}</TableCell>
                        <TableCell>{formatTimeTracked(project.totalTime)}</TableCell>
                        <TableCell>{`${project.percentage.toFixed(2)}%`}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body1" color="textSecondary">
                No project data available for the selected period.
              </Typography>
            )}
          </Paper>
        </Grid>
        
        {/* Recent Screenshots */}
        <Grid item xs={12} sx={{ mt: 2 }}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Screenshots
            </Typography>
            
            {screenshots.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Employee</TableCell>
                      <TableCell>Project</TableCell>
                      <TableCell>Task</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Activity Level</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {screenshots.map((screenshot) => (
                      <TableRow key={screenshot.id}>
                        <TableCell>{screenshot.employeeName}</TableCell>
                        <TableCell>{screenshot.projectName}</TableCell>
                        <TableCell>{screenshot.taskName}</TableCell>
                        <TableCell>{formatTimestamp(screenshot.timestamp)}</TableCell>
                        <TableCell>{`${screenshot.activityLevel}%`}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body1" color="textSecondary">
                No screenshots available for the selected period.
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminDashboard;