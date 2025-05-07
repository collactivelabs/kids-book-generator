import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredScopes?: string[];
}

/**
 * ProtectedRoute component
 * 
 * Checks if the user is authenticated and has the required scopes.
 * If not, redirects to the login page with the intended destination as a query parameter.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredScopes = [] 
}) => {
  const { isAuthenticated, user, loading } = useAuth();
  
  // Show loading state
  if (loading) {
    // You could replace this with a LoadingSpinner component
    return <div>Loading...</div>;
  }
  const location = useLocation();

  // If not authenticated, redirect to login with return path
  if (!isAuthenticated) {
    return <Navigate to={`/login?returnUrl=${encodeURIComponent(location.pathname)}`} replace />;
  }

  // If scopes are required and user doesn't have them, redirect to dashboard
  if (requiredScopes.length > 0 && user) {
    const hasRequiredScopes = requiredScopes.every(scope => 
      user.scopes.includes(scope)
    );

    if (!hasRequiredScopes) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  // User is authenticated and has required scopes
  return <>{children}</>;
};

export default ProtectedRoute;
