import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import UserLayout from './components/UserLayout';
import AdminLayout from './components/AdminLayout';

// Pages
import LoginPage from './pages/auth/LoginPage';
import UserDashboard from './pages/user/UserDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Redirect root to login */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            
            {/* User routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/user" element={<UserLayout />}>
                <Route path="dashboard" element={<UserDashboard />} />
                {/* Add more user routes here */}
                <Route path="*" element={<Navigate to="/user/dashboard" replace />} />
              </Route>
            </Route>
            
            {/* Admin routes */}
            <Route element={<ProtectedRoute requireAdmin={true} />}>
              <Route path="/admin" element={<AdminLayout />}>
                <Route path="dashboard" element={<AdminDashboard />} />
                {/* Add more admin routes here */}
                <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
              </Route>
            </Route>
            
            {/* Catch all */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
