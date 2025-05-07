import { DefaultTheme } from 'styled-components';

// Define our theme structure
declare module 'styled-components' {
  export interface DefaultTheme {
    colors: {
      primary: {
        main: string;
        light: string;
        dark: string;
      };
      secondary: {
        main: string;
        light: string;
        dark: string;
      };
      text: {
        primary: string;
        secondary: string;
        disabled: string;
      };
      background: {
        main: string;
        light: string;
        dark: string;
        card: string;
        input: string;
      };
      border: {
        main: string;
        light: string;
        dark: string;
      };
      status: {
        success: string;
        error: string;
        warning: string;
        info: string;
        pending: string;
        inProgress: string;
        successLight: string;
        errorLight: string;
        warningLight: string;
        infoLight: string;
        pendingLight: string;
      };
    };
    shadows: {
      small: string;
      medium: string;
      large: string;
      card: string;
      dropdown: string;
    };
    breakpoints: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
    };
    spacing: {
      xs: string;
      sm: string;
      md: string;
      lg: string;
      xl: string;
      xxl: string;
      calc: (multiplier?: number) => string;
    };
    borderRadius: {
      small: string;
      medium: string;
      large: string;
      round: string;
    };
    typography: {
      fontFamily: string;
      fontSize: {
        xs: string;
        sm: string;
        md: string;
        lg: string;
        xl: string;
        xxl: string;
      };
      fontWeight: {
        light: number;
        regular: number;
        medium: number;
        semiBold: number;
        bold: number;
      };
      lineHeight: {
        xs: number;
        sm: number;
        md: number;
        lg: number;
        xl: number;
      };
    };
    zIndex: {
      appBar: number;
      drawer: number;
      modal: number;
      snackbar: number;
      tooltip: number;
    };
    transitions: {
      short: string;
      medium: string;
      long: string;
    };
  }
}

// Default theme
const theme: DefaultTheme = {
  colors: {
    primary: {
      main: '#4F46E5',
      light: '#818CF8',
      dark: '#3730A3',
    },
    secondary: {
      main: '#14B8A6',
      light: '#5EEAD4',
      dark: '#0F766E',
    },
    text: {
      primary: '#1F2937',
      secondary: '#6B7280',
      disabled: '#9CA3AF',
    },
    background: {
      main: '#F9FAFB',
      light: '#F3F4F6',
      dark: '#E5E7EB',
      card: '#FFFFFF',
      input: '#FFFFFF',
    },
    border: {
      main: '#D1D5DB',
      light: '#E5E7EB',
      dark: '#9CA3AF',
    },
    status: {
      success: '#10B981',
      error: '#EF4444',
      warning: '#F59E0B',
      info: '#3B82F6',
      pending: '#9CA3AF',
      inProgress: '#6366F1',
      successLight: '#D1FAE5',
      errorLight: '#FEE2E2',
      warningLight: '#FEF3C7',
      infoLight: '#DBEAFE',
      pendingLight: '#F3F4F6',
    },
  },
  shadows: {
    small: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    medium: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    large: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    card: '0 2px 4px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
    dropdown: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
  breakpoints: {
    xs: '0px',
    sm: '600px',
    md: '960px',
    lg: '1280px',
    xl: '1920px',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
    // Keep the function for backward compatibility and custom values
    calc: (multiplier = 1) => `${multiplier * 8}px`
  },
  borderRadius: {
    small: '4px',
    medium: '8px',
    large: '12px',
    round: '50%',
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
    fontSize: {
      xs: '0.75rem', // 12px
      sm: '0.875rem', // 14px
      md: '1rem',     // 16px
      lg: '1.125rem', // 18px
      xl: '1.25rem',  // 20px
      xxl: '1.5rem',  // 24px
    },
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      semiBold: 600,
      bold: 700,
    },
    lineHeight: {
      xs: 1.2,
      sm: 1.4,
      md: 1.6,
      lg: 1.8,
      xl: 2,
    },
  },
  zIndex: {
    appBar: 1100,
    drawer: 1200,
    modal: 1300,
    snackbar: 1400,
    tooltip: 1500,
  },
  transitions: {
    short: '0.15s ease-in-out',
    medium: '0.3s ease-in-out',
    long: '0.5s ease-in-out',
  },
};

export default theme;
