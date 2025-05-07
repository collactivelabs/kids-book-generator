import React from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../../store';
import { toggleSidebar } from '../../store/slices/uiSlice';
import Header from './Header';
import Sidebar from './Sidebar';
import NotificationContainer from '../common/NotificationContainer';

// Styled components
const LayoutContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

const MainContent = styled.div`
  display: flex;
  flex: 1;
`;

const SidebarWrapper = styled.div<{ isOpen: boolean }>`
  width: ${({ isOpen }) => (isOpen ? '250px' : '0')};
  transition: width var(--transition-normal);
  overflow: hidden;
  background-color: var(--color-surface);
  box-shadow: var(--shadow-sm);
  z-index: 10;
  height: calc(100vh - 60px);
  position: sticky;
  top: 60px;
  
  @media (max-width: 768px) {
    position: fixed;
    height: 100vh;
    top: 0;
    left: 0;
  }
`;

const Content = styled.main`
  flex: 1;
  padding: var(--spacing-lg);
  background-color: var(--color-background);
  min-height: calc(100vh - 60px);
`;

const Overlay = styled.div<{ visible: boolean }>`
  display: ${({ visible }) => (visible ? 'block' : 'none')};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 5;
  
  @media (min-width: 769px) {
    display: none;
  }
`;

/**
 * Main layout component
 * 
 * Provides the application's layout structure with header, sidebar, and content area
 */
const MainLayout: React.FC = () => {
  const { sidebarOpen } = useSelector((state: RootState) => state.ui);
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();
  
  // Handle overlay click (close sidebar on mobile)
  const handleOverlayClick = () => {
    if (window.innerWidth <= 768) {
      dispatch(toggleSidebar());
    }
  };
  
  return (
    <LayoutContainer>
      <Header />
      
      <MainContent>
        {/* Sidebar only shows for authenticated users */}
        {isAuthenticated && (
          <>
            <SidebarWrapper isOpen={sidebarOpen}>
              <Sidebar />
            </SidebarWrapper>
            <Overlay visible={sidebarOpen} onClick={handleOverlayClick} />
          </>
        )}
        
        <Content>
          <Outlet />
        </Content>
      </MainContent>
      
      {/* Notification container for displaying alerts/messages */}
      <NotificationContainer />
    </LayoutContainer>
  );
};

export default MainLayout;
