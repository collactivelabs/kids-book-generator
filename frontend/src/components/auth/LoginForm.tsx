import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { loginStart, loginSuccess, loginFail } from '../../store/slices/authSlice';
import { RootState } from '../../store';
import { addNotification } from '../../store/slices/uiSlice';

// Styled components
const FormContainer = styled.div`
  max-width: 400px;
  margin: 0 auto;
  padding: var(--spacing-lg);
  background-color: var(--color-surface);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
`;

const Label = styled.label`
  font-weight: 500;
  color: var(--color-text);
`;

const Input = styled.input`
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid #ddd;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-md);
  transition: border-color var(--transition-fast);
  
  &:focus {
    outline: none;
    border-color: var(--color-primary);
  }
`;

const Button = styled.button`
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: var(--color-primary-dark);
  }
  
  &:disabled {
    background-color: var(--color-text-light);
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.p`
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
`;

const API_BASE_URL = import.meta.env.VITE_API_URL;

/**
 * Login form component
 * 
 * Allows users to log in to the application using username/email and password
 */
const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  
  // Get full auth state and log it
  const authState = useSelector((state: RootState) => {
    return state.auth;
  });
  const { loading, error } = authState;
  
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Handle navigation destination after login
  const getNavigationDestination = () => {
    const searchParams = new URLSearchParams(location.search);
    const returnUrl = searchParams.get('returnUrl');
    
    // Make sure returnUrl is valid and not the login page itself
    if (returnUrl && returnUrl !== '/login' && !returnUrl.includes('/login') && returnUrl.startsWith('/')) {
      return returnUrl;
    }
    
    return '/dashboard';
  };
  
  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if all required fields are filled
    const requiredFields = ['username', 'password'];
    const emptyFields = requiredFields.filter(field => !formData[field as keyof typeof formData]);
    
    if (emptyFields.length > 0) {
      dispatch(addNotification({
        type: 'error',
        message: `Please fill in all required fields: ${emptyFields.join(', ')}`
      }));
      return;
    }
    
    try {
      dispatch(loginStart());
      
      // Make API request to login endpoint
      const response = await fetch(`${API_BASE_URL}/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: formData.username,
          password: formData.password,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      // Store token in localStorage
      localStorage.setItem('token', data.access_token);
      
      // Calculate token expiry (default: 24 hours from now if not provided)
      const expiresIn = data.expires_in || 86400; // Default: 24 hours in seconds
      const expiresAt = new Date(Date.now() + expiresIn * 1000).toISOString();
      
      // Get user data
      try {
        const userResponse = await fetch(`${API_BASE_URL}/users/me`, {
          headers: {
            'Authorization': `Bearer ${data.access_token}`,
          },
        });
        
        if (!userResponse.ok) {
          const errorData = await userResponse.json().catch(() => ({}));
          console.error('User data fetch error:', errorData);
          throw new Error(errorData.detail || 'Failed to fetch user data');
        }
        
        const userData = await userResponse.json();
        
        // Dispatch login success with user data and token
        dispatch(loginSuccess({
          user: {
            username: userData.username,
            email: userData.email || formData.username + '@example.com',
            fullName: userData.full_name || formData.username,
            scopes: userData.scopes || ['users:read'],
          },
          token: data.access_token,
          expiresAt: expiresAt
        }));
        
        // Show success notification
        dispatch(addNotification({
          type: 'success',
          message: 'Login successful!',
        }));
        
        // Navigate to return URL or dashboard
        // Use replace:true to prevent back button returning to login
        // Use setTimeout with longer delay to ensure all state updates are complete before navigation
        setTimeout(() => {
          const destination = getNavigationDestination();
          // Force navigation to the dashboard with replace to avoid navigation loops
          navigate(destination, { replace: true });
          
          // Extra safety check - ensure we're actually on the dashboard after a short delay
          setTimeout(() => {
            const currentPath = window.location.pathname;
            if (currentPath.includes('/login')) {
              window.location.href = '/dashboard';
            }
          }, 100);
        }, 100); // Increased timeout to ensure Redux state is fully updated
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Login failed';
        dispatch(loginFail(errorMessage));
        
        // Show error notification
        dispatch(addNotification({
          type: 'error',
          message: errorMessage,
        }));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      dispatch(loginFail(errorMessage));
      
      // Show error notification
      dispatch(addNotification({
        type: 'error',
        message: errorMessage,
      }));
    }
  };
  
  return (
    <FormContainer>
      <h2>Login</h2>
      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="username">Username</Label>
          <Input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="password">Password</Label>
          <Input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </FormGroup>
        
        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        <Button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Log In'}
        </Button>
      </Form>
    </FormContainer>
  );
};

export default LoginForm;
