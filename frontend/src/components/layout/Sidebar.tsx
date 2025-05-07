import React from 'react';
import { NavLink } from 'react-router-dom';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../../store';

// Styled components
const SidebarContainer = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--color-surface);
`;

const SidebarHeader = styled.div`
  padding: var(--spacing-md);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
`;

const SidebarTitle = styled.h3`
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--color-primary);
`;

const SidebarContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md) 0;
`;

const NavSection = styled.div`
  margin-bottom: var(--spacing-md);
`;

const NavSectionTitle = styled.h4`
  margin: 0;
  padding: 0 var(--spacing-md);
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  color: var(--color-text-light);
  margin-bottom: var(--spacing-sm);
`;

const NavItems = styled.nav`
  display: flex;
  flex-direction: column;
`;

const StyledNavLink = styled(NavLink)`
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text);
  text-decoration: none;
  transition: background-color var(--transition-fast);
  
  svg {
    width: 20px;
    height: 20px;
    margin-right: var(--spacing-sm);
  }
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
  
  &.active {
    color: var(--color-primary);
    background-color: rgba(67, 97, 238, 0.1);
    font-weight: 500;
  }
`;

const SidebarFooter = styled.div`
  padding: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
`;

/**
 * Sidebar component
 * 
 * Provides navigation links and sections based on user permissions
 */
const Sidebar: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  
  // Check if user has a specific scope
  const hasScope = (scope: string): boolean => {
    return user?.scopes.includes(scope) || false;
  };
  
  // Book management is available to users with 'books:read' scope
  const canManageBooks = hasScope('books:read');
  
  // Batch processing is available to users with 'books:write' scope
  const canProcessBatch = hasScope('books:write');
  
  return (
    <SidebarContainer>
      <SidebarHeader>
        <SidebarTitle>Navigation</SidebarTitle>
      </SidebarHeader>
      
      <SidebarContent>
        {/* Dashboard section */}
        <NavSection>
          <NavItems>
            <StyledNavLink to="/dashboard">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
              </svg>
              Dashboard
            </StyledNavLink>
          </NavItems>
        </NavSection>
        
        {/* Books section - only visible if user has books:read scope */}
        {canManageBooks && (
          <NavSection>
            <NavSectionTitle>Books</NavSectionTitle>
            <NavItems>
              <StyledNavLink to="/books">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                </svg>
                All Books
              </StyledNavLink>
              
              <StyledNavLink to="/books/create">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Create Book
              </StyledNavLink>
            </NavItems>
          </NavSection>
        )}
        
        {/* Batch jobs section - only visible if user has books:write scope */}
        {canProcessBatch && (
          <NavSection>
            <NavSectionTitle>Batch Processing</NavSectionTitle>
            <NavItems>
              <StyledNavLink to="/batch">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                Batch Jobs
              </StyledNavLink>
              
              <StyledNavLink to="/batch/create">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Create Batch Job
              </StyledNavLink>
            </NavItems>
          </NavSection>
        )}
        
        {/* Settings section */}
        <NavSection>
          <NavSectionTitle>Settings</NavSectionTitle>
          <NavItems>
            <StyledNavLink to="/profile">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
              Profile
            </StyledNavLink>
            
            <StyledNavLink to="/settings">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
              </svg>
              Settings
            </StyledNavLink>
          </NavItems>
        </NavSection>
      </SidebarContent>
      
      <SidebarFooter>
        <div>Kids Book Generator v1.0.0</div>
      </SidebarFooter>
    </SidebarContainer>
  );
};

export default Sidebar;
