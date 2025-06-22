import React, { useEffect, useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  CircularProgress, 
  Card, 
  CardContent, 
  CardHeader 
} from '@mui/material';
import { Grid } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { userApi } from '../../services/api';
import { UserStats } from '../../types/auth';
import AssignmentIcon from '@mui/icons-material/Assignment';
import FolderIcon from '@mui/icons-material/Folder';
import TimerIcon from '@mui/icons-material/Timer';

const UserDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await userApi.getStats();
        setStats(response.data);
      } catch (err) {
        console.error('Failed to fetch user stats:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  // Format time tracked (milliseconds to hours)
  const formatTimeTracked = (ms: number) => {
    const hours = Math.floor(ms / (1000 * 60 * 60));
    const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
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
        Welcome, {user?.name}!
      </Typography>
      
      <Typography variant="subtitle1" color="textSecondary" paragraph>
        Here's an overview of your work activity
      </Typography>
      
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Stats Cards */}
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardHeader
              avatar={<FolderIcon color="primary" />}
              title="Projects"
            />
            <CardContent>
              <Typography variant="h4">{stats?.activeProjects || 0}</Typography>
              <Typography variant="body2" color="textSecondary">
                Active Projects (Total: {stats?.totalProjects || 0})
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardHeader
              avatar={<AssignmentIcon color="primary" />}
              title="Tasks"
            />
            <CardContent>
              <Typography variant="h4">{stats?.activeTasks || 0}</Typography>
              <Typography variant="body2" color="textSecondary">
                Active Tasks (Total: {stats?.totalTasks || 0})
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card elevation={3}>
            <CardHeader
              avatar={<TimerIcon color="primary" />}
              title="Time Tracked"
            />
            <CardContent>
              <Typography variant="h4">
                {stats?.totalTimeTracked ? formatTimeTracked(stats.totalTimeTracked) : '0h 0m'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Time Tracked
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Recent Activity */}
        <Grid item xs={12} sx={{ mt: 2 }}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Your recent activity will appear here.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserDashboard;