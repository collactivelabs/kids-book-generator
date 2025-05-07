import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../../store';
import { removeNotification } from '../../store/slices/uiSlice';

// Styled components
const Container = styled.div`
  position: fixed;
  top: 70px;
  right: 20px;
  z-index: 1000;
  width: 350px;
`;

interface NotificationItemProps {
  type: 'success' | 'error' | 'info' | 'warning';
}

const NotificationItem = styled.div<NotificationItemProps>`
  margin-bottom: 10px;
  padding: 16px;
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: flex-start;
  animation: slideIn 0.3s ease-out forwards;
  
  ${({ type }) => {
    switch (type) {
      case 'success':
        return `
          background-color: #e6f7ed;
          border-left: 4px solid var(--color-success);
          color: #0a5d2a;
        `;
      case 'error':
        return `
          background-color: #fdecea;
          border-left: 4px solid var(--color-error);
          color: #a72a18;
        `;
      case 'warning':
        return `
          background-color: #fef7e6;
          border-left: 4px solid var(--color-warning);
          color: #8a5d00;
        `;
      case 'info':
      default:
        return `
          background-color: #e8f3fc;
          border-left: 4px solid var(--color-info);
          color: #0a5899;
        `;
    }
  }}
  
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
`;

const IconContainer = styled.div`
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
  padding: 0;
  margin-left: auto;
  
  &:hover {
    opacity: 1;
  }
`;

const Message = styled.div`
  flex: 1;
  padding-right: 8px;
`;

/**
 * Notification container component
 * 
 * Displays notifications from the UI state
 */
const NotificationContainer: React.FC = () => {
  const { notifications } = useSelector((state: RootState) => state.ui);
  const dispatch = useDispatch();
  
  // Handle notification close
  const handleClose = (id: string) => {
    dispatch(removeNotification(id));
  };
  
  // Set up auto-close timers for notifications
  useEffect(() => {
    notifications.forEach((notification) => {
      if (notification.autoClose) {
        const timer = setTimeout(() => {
          dispatch(removeNotification(notification.id));
        }, notification.duration);
        
        return () => {
          clearTimeout(timer);
        };
      }
    });
  }, [notifications, dispatch]);
  
  // Get icon based on notification type
  const getIcon = (type: 'success' | 'error' | 'info' | 'warning') => {
    switch (type) {
      case 'success':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        );
      case 'error':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        );
      case 'warning':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        );
      case 'info':
      default:
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
        );
    }
  };
  
  if (notifications.length === 0) {
    return null;
  }
  
  return (
    <Container>
      {notifications.map((notification) => (
        <NotificationItem key={notification.id} type={notification.type}>
          <IconContainer>
            {getIcon(notification.type)}
          </IconContainer>
          <Message>{notification.message}</Message>
          <CloseButton onClick={() => handleClose(notification.id)}>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </CloseButton>
        </NotificationItem>
      ))}
    </Container>
  );
};

export default NotificationContainer;
