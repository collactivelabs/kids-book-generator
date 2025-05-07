import React from 'react';
import { ThemeProvider as StyledThemeProvider, createGlobalStyle } from 'styled-components';
import theme from './theme';

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  
  html, body {
    font-family: ${({ theme }) => theme.typography.fontFamily};
    font-size: ${({ theme }) => theme.typography.fontSize.md};
    color: ${({ theme }) => theme.colors.text.primary};
    background-color: ${({ theme }) => theme.colors.background.main};
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  a {
    color: ${({ theme }) => theme.colors.primary.main};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  button, input, select, textarea {
    font-family: inherit;
    font-size: inherit;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-bottom: 16px;
    font-weight: ${({ theme }) => theme.typography.fontWeight.semiBold};
    line-height: 1.2;
  }
  
  h1 {
    font-size: ${({ theme }) => theme.typography.fontSize.xxl};
  }
  
  h2 {
    font-size: ${({ theme }) => theme.typography.fontSize.xl};
  }
  
  h3 {
    font-size: ${({ theme }) => theme.typography.fontSize.lg};
  }
  
  p {
    margin-bottom: 16px;
  }
  
  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
    background-color: ${({ theme }) => theme.colors.background.light};
    padding: 2px 4px;
    border-radius: ${({ theme }) => theme.borderRadius.small};
  }
  
  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  ::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.colors.background.light};
  }
  
  ::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.colors.primary.light};
    border-radius: ${({ theme }) => theme.borderRadius.small};
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: ${({ theme }) => theme.colors.primary.main};
  }
`;

interface ThemeProviderProps {
  children: React.ReactNode;
}

const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  return (
    <StyledThemeProvider theme={theme}>
      <GlobalStyle />
      {children}
    </StyledThemeProvider>
  );
};

export default ThemeProvider;
