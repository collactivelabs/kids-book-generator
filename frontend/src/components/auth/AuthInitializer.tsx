import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../../store';
import { loginSuccess, logout, setLoading } from '../../store/slices/authSlice';

/**
 * AuthInitializer component
 * 
 * Initializes authentication state on app load
 * Validates stored token and fetches user data if token exists
 */
const AuthInitializer: React.FC = () => {
  const dispatch = useDispatch();
  const [initialized, setInitialized] = useState(false);
  
  // Get current auth state to monitor loading changes
  const { loading } = useSelector((state: RootState) => state.auth);

  // Check for existing token and initialize auth state on app load
  useEffect(() => {
    if (initialized) return;
    
    const validateToken = async () => {
      const token = localStorage.getItem('token');
      
      if (!token) {
        dispatch(logout());
        setTimeout(() => {
          dispatch(setLoading(false));
        }, 50);
        setInitialized(true);
        return;
      }
      
      try {
        // Make API request to validate token
        const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          localStorage.removeItem('token');
          dispatch(logout());
          // Explicitly set loading to false with a small delay
          setTimeout(() => {
            dispatch(setLoading(false));
          }, 50);
          setInitialized(true);
          return;
        }
        
        const userData = await response.json();
        
        // Dispatch successful login with user data
        dispatch(loginSuccess({
          user: {
            username: userData.username,
            email: userData.email || '',
            fullName: userData.full_name || userData.username,
            scopes: userData.scopes || ['users:read'],
          },
          token: token,
          expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24h from now
        }));
        
        // Ensure loading is false after successful login
        setTimeout(() => {
          if (loading) {
            dispatch(setLoading(false));
          }
        }, 50);
        
      } catch (error) {
        console.error('Error validating token:', error);
        localStorage.removeItem('token');
        dispatch(logout());
        setTimeout(() => {
          dispatch(setLoading(false));
        }, 50);
      } finally {
        setInitialized(true);
      }
    };
    
    validateToken();
  }, [dispatch, initialized, loading]);

  // This component doesn't render anything
  return null;
};

export default AuthInitializer;
