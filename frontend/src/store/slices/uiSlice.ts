import { createSlice, PayloadAction } from '@reduxjs/toolkit';

/**
 * Interface for notifications displayed to the user
 */
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  autoClose?: boolean;
  duration?: number;
}

/**
 * Interface for UI state
 */
export interface UiState {
  notifications: Notification[];
  sidebarOpen: boolean;
  currentTheme: 'light' | 'dark';
  loading: {
    [key: string]: boolean;
  };
}

// Initial state
const initialState: UiState = {
  notifications: [],
  sidebarOpen: window.innerWidth > 768, // Default open on desktop, closed on mobile
  currentTheme: 'light',
  loading: {},
};

/**
 * UI slice for managing UI state
 */
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Add a notification to the queue
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const id = Date.now().toString();
      state.notifications.push({
        ...action.payload,
        id,
        autoClose: action.payload.autoClose ?? true,
        duration: action.payload.duration ?? 5000,
      });
    },
    
    // Remove a notification by ID
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    
    // Toggle sidebar open/closed state
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    
    // Set sidebar to a specific state
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    
    // Toggle between light and dark theme
    toggleTheme: (state) => {
      state.currentTheme = state.currentTheme === 'light' ? 'dark' : 'light';
    },
    
    // Set a specific theme
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.currentTheme = action.payload;
    },
    
    // Set loading state for a specific key
    setLoading: (state, action: PayloadAction<{ key: string; isLoading: boolean }>) => {
      state.loading[action.payload.key] = action.payload.isLoading;
    },
    
    // Clear all notifications
    clearNotifications: (state) => {
      state.notifications = [];
    },
  },
});

export const {
  addNotification,
  removeNotification,
  toggleSidebar,
  setSidebarOpen,
  toggleTheme,
  setTheme,
  setLoading,
  clearNotifications,
} = uiSlice.actions;

export default uiSlice.reducer;
