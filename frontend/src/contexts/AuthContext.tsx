import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService, { User, LoginData } from '../services/authService';

// Auth context state interface
interface AuthContextState {
  user: User | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (data: LoginData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

// Initial context state
const initialState: AuthContextState = {
  user: null,
  loading: true,
  error: null,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
  clearError: () => {},
};

// Create context
const AuthContext = createContext<AuthContextState>(initialState);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Clear auth error
  const clearError = () => setError(null);

  // Load user data if token exists
  const loadUser = async () => {
    try {
      if (authService.isAuthenticated()) {
        setLoading(true);
        const userData = await authService.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      }
    } catch (err) {
      console.error('Failed to load user:', err);
      authService.logout();
      setUser(null);
      setIsAuthenticated(false);
      setError('Session expired. Please log in again.');
    } finally {
      setLoading(false);
    }
  };

  // User login
  const login = async (loginData: LoginData) => {
    try {
      setLoading(true);
      setError(null);
      const tokenResponse = await authService.login(loginData);
      authService.setToken(tokenResponse.access_token);
      await loadUser();
    } catch (err) {
      console.error('Login failed:', err);
      let errorMessage = 'Login failed. Please check your credentials.';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setLoading(false);
    }
  };

  // User logout
  const logout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  // Load user on initial mount
  useEffect(() => {
    loadUser();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        isAuthenticated,
        login,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for using auth context
export const useAuth = () => useContext(AuthContext);

export default AuthContext;
