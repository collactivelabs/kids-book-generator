import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';
import { toggleSidebar, toggleTheme } from '../../store/slices/uiSlice';

// Styled components
const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-md);
  height: 60px;
  background-color: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 20;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: white;
  text-decoration: none;
  
  &:hover {
    color: white;
    opacity: 0.9;
  }
`;

const MenuToggle = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  margin-right: var(--spacing-md);
  
  svg {
    width: 24px;
    height: 24px;
  }
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
`;

const NavItem = styled.div`
  margin-left: var(--spacing-md);
`;

const ThemeToggle = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const UserMenu = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

const UserMenuButton = styled.button`
  display: flex;
  align-items: center;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: var(--font-size-md);
  
  span {
    margin-right: var(--spacing-sm);
  }
  
  svg {
    width: 16px;
    height: 16px;
    margin-left: var(--spacing-xs);
  }
`;

const DropdownMenu = styled.div<{ isOpen: boolean }>`
  position: absolute;
  top: 100%;
  right: 0;
  display: ${({ isOpen }) => (isOpen ? 'block' : 'none')};
  background-color: white;
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-md);
  min-width: 200px;
  z-index: 30;
  margin-top: var(--spacing-sm);
  overflow: hidden;
`;

const DropdownItem = styled.button`
  display: flex;
  align-items: center;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: var(--font-size-md);
  color: var(--color-text);
  
  &:hover {
    background-color: var(--color-surface);
  }
  
  svg {
    width: 16px;
    height: 16px;
    margin-right: var(--spacing-sm);
  }
`;

/**
 * Header component
 * 
 * Displays the application header with navigation, user menu, and theme toggle
 */
const Header: React.FC = () => {
  const [userMenuOpen, setUserMenuOpen] = React.useState(false);
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
  const { currentTheme } = useSelector((state: RootState) => state.ui);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  // Toggle user dropdown menu
  const toggleUserMenu = () => {
    setUserMenuOpen(!userMenuOpen);
  };
  
  // Close user menu when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (_: MouseEvent) => {
      if (userMenuOpen) {
        setUserMenuOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [userMenuOpen]);
  
  // Handle logout
  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };
  
  return (
    <HeaderContainer>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        {/* Mobile menu toggle button */}
        {isAuthenticated && (
          <MenuToggle onClick={() => dispatch(toggleSidebar())}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          </MenuToggle>
        )}
        
        {/* App logo */}
        <Logo to="/">Kids Book Generator</Logo>
      </div>
      
      <Nav>
        {/* Theme toggle button */}
        <NavItem>
          <ThemeToggle onClick={() => dispatch(toggleTheme())} title="Toggle theme">
            {currentTheme === 'light' ? (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            )}
          </ThemeToggle>
        </NavItem>
        
        {/* User menu (only shown when authenticated) */}
        {isAuthenticated && user ? (
          <NavItem>
            <UserMenu>
              <UserMenuButton onClick={toggleUserMenu}>
                <span>{user.username}</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </UserMenuButton>
              
              <DropdownMenu isOpen={userMenuOpen}>
                <DropdownItem onClick={() => navigate('/dashboard')}>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                  </svg>
                  Dashboard
                </DropdownItem>
                <DropdownItem onClick={() => navigate('/profile')}>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                  Profile
                </DropdownItem>
                <DropdownItem onClick={handleLogout}>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V4a1 1 0 00-1-1H3zm11 3a1 1 0 00-1-1H7a1 1 0 00-1 1v1a1 1 0 001 1h6a1 1 0 001-1V6zm-6 7a1 1 0 011-1h4a1 1 0 110 2H9a1 1 0 01-1-1z" clipRule="evenodd" />
                    <path d="M4 8a1 1 0 100 2h6a1 1 0 100-2H4z" />
                  </svg>
                  Logout
                </DropdownItem>
              </DropdownMenu>
            </UserMenu>
          </NavItem>
        ) : (
          // Login/Register links for unauthenticated users
          <>
            <NavItem>
              <Link to="/login" style={{ color: 'white', textDecoration: 'none' }}>Login</Link>
            </NavItem>
            <NavItem>
              <Link to="/register" style={{ color: 'white', textDecoration: 'none' }}>Register</Link>
            </NavItem>
          </>
        )}
      </Nav>
    </HeaderContainer>
  );
};

export default Header;
