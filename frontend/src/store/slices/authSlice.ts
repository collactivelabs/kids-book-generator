import { createSlice, PayloadAction } from '@reduxjs/toolkit';

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

// Initial state
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
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

export const {
  loginStart,
  loginSuccess,
  loginFail,
  logout,
  registerStart,
  registerSuccess,
  registerFail,
  clearError,
  updateUser,
} = authSlice.actions;

export default authSlice.reducer;
