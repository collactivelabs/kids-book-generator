import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';

// Define types for the slice state
export interface User {
  username: string;
  email: string;
  fullName: string;
  scopes: string[];
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  tokenExpiry: number | null;
}

// Check token validity when initializing state
const getStoredToken = () => {
  const token = localStorage.getItem('token');
  
  // If token exists, check if it's expired or malformed
  if (token) {
    try {
      // Clear token if it appears to be malformed
      if (token.split('.').length !== 3) {
        localStorage.removeItem('token');
        return null;
      }
      
      // Try to decode token to check validity
      // This is a basic check - a real implementation would verify with server
      const base64Url = token.split('.')[1];
      if (!base64Url) {
        console.log('Invalid token format');
        localStorage.removeItem('token');
        return null;
      }
    } catch (e) {
      console.log('Error processing token, removed it:', e);
      localStorage.removeItem('token');
      return null;
    }
  }
  return token;
};

// Initial state - don't automatically trust the token on load
// We'll verify it properly with an initialization action
const storedToken = getStoredToken();
const initialState: AuthState = {
  user: null,
  token: storedToken,
  isAuthenticated: false, // Start with false and verify on app load
  loading: true, // Start with loading true until we verify the token
  error: null,
  tokenExpiry: null,
};

/**
 * Auth slice for managing authentication state
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action: PayloadAction<{ user: User; token: string; expiresAt: string }>) => {
      state.loading = false;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.isAuthenticated = true;
      state.tokenExpiry = new Date(action.payload.expiresAt).getTime();
      // Save token to localStorage
      localStorage.setItem('token', action.payload.token);
    },
    loginFail: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
      state.isAuthenticated = false;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.tokenExpiry = null;
      // Remove token from localStorage
      localStorage.removeItem('token');
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    registerStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    registerSuccess: (state) => {
      state.loading = false;
      // Registration successful, but user still needs to log in
    },
    registerFail: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
    },
  },
});

// Add a new action to initialize auth state from stored token
const initializeAuthState = createAsyncThunk<{ success: boolean }, void>(
  'auth/initializeAuthState',
  async (_, { dispatch }): Promise<{ success: boolean }> => {
    const token = localStorage.getItem('token');
    if (!token) {
      return { success: false };
    }

    try {
      // Make API request to get current user with the stored token
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        // Token is invalid or expired
        console.log('Token validation failed, clearing auth state');
        localStorage.removeItem('token');
        return { success: false };
      }

      const userData = await response.json();
      console.log('User data from token:', userData);

      // Successfully validated token and got user data
      dispatch(loginSuccess({
        user: {
          username: userData.username,
          email: userData.email || '',
          fullName: userData.full_name || userData.username,
          scopes: userData.scopes || ['user:read'],
        },
        token: token,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // Assume 24h from now
      }));

      return { success: true };
    } catch (error) {
      console.error('Error validating token:', error);
      localStorage.removeItem('token');
      return { success: false };
    }
  }
);

export const {
  loginStart,
  loginSuccess,
  loginFail,
  logout,
  setLoading,
  registerStart,
  registerSuccess,
  registerFail,
  clearError,
  updateUser,
} = authSlice.actions;

// Export the thunk action
export { initializeAuthState };

export default authSlice.reducer;
