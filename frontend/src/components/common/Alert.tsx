import React, { useState, useEffect } from 'react';
import styled, { css, keyframes } from 'styled-components';

export type AlertType = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  type?: AlertType;
  title?: string;
  message: string;
  dismissible?: boolean;
  autoClose?: boolean;
  autoCloseTime?: number;
  onClose?: () => void;
  elevation?: boolean;
}

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const AlertContainer = styled.div<{ type: AlertType; elevation: boolean }>`
  display: flex;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 12px;
  animation: ${fadeIn} 0.3s ease-out;
  
  ${props => props.elevation && css`
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  `}
  
  ${props => {
    switch (props.type) {
      case 'success':
        return css`
          background-color: #ecfdf5;
          border-left: 4px solid #10b981;
        `;
      case 'warning':
        return css`
          background-color: #fffbeb;
          border-left: 4px solid #f59e0b;
        `;
      case 'error':
        return css`
          background-color: #fef2f2;
          border-left: 4px solid #ef4444;
        `;
      default:
        return css`
          background-color: #eff6ff;
          border-left: 4px solid #3b82f6;
        `;
    }
  }}
`;

const IconContainer = styled.div<{ type: AlertType }>`
  display: flex;
  align-items: center;
  margin-right: 12px;
  
  ${props => {
    switch (props.type) {
      case 'success':
        return css`color: #10b981;`;
      case 'warning':
        return css`color: #f59e0b;`;
      case 'error':
        return css`color: #ef4444;`;
      default:
        return css`color: #3b82f6;`;
    }
  }}
`;

const ContentContainer = styled.div`
  flex: 1;
`;

const Title = styled.h4<{ type: AlertType }>`
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  
  ${props => {
    switch (props.type) {
      case 'success':
        return css`color: #047857;`;
      case 'warning':
        return css`color: #b45309;`;
      case 'error':
        return css`color: #b91c1c;`;
      default:
        return css`color: #1e40af;`;
    }
  }}
`;

const Message = styled.p`
  margin: 0;
  font-size: 14px;
  color: #4b5563;
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 12px;
  padding: 4px;
  
  &:hover {
    color: #4b5563;
  }
`;

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  message,
  dismissible = true,
  autoClose = false,
  autoCloseTime = 5000,
  onClose,
  elevation = true,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  
  useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose();
      }, autoCloseTime);
      
      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseTime, onClose]);
  
  const handleClose = () => {
    setIsVisible(false);
    if (onClose) onClose();
  };
  
  if (!isVisible) return null;
  
  const getIcon = () => {
    switch (type) {
      case 'success':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        );
      case 'warning':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        );
      case 'error':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
        );
      default:
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
        );
    }
  };
  
  return (
    <AlertContainer type={type} elevation={elevation}>
      <IconContainer type={type}>
        {getIcon()}
      </IconContainer>
      
      <ContentContainer>
        {title && <Title type={type}>{title}</Title>}
        <Message>{message}</Message>
      </ContentContainer>
      
      {dismissible && (
        <CloseButton onClick={handleClose} aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </CloseButton>
      )}
    </AlertContainer>
  );
};

export default Alert;
