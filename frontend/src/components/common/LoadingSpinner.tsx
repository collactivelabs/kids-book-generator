import React from 'react';
import styled, { keyframes } from 'styled-components';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  thickness?: number;
  fullPage?: boolean;
  text?: string;
}

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const SpinnerContainer = styled.div<{ fullPage: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  ${({ fullPage }) =>
    fullPage &&
    `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.8);
    z-index: 1000;
  `}
`;

const Spinner = styled.div<{
  size: string;
  color: string;
  thickness: number;
}>`
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  
  ${({ size, color, thickness }) => {
    let dimensions;
    
    switch (size) {
      case 'small':
        dimensions = '24px';
        break;
      case 'large':
        dimensions = '48px';
        break;
      default:
        dimensions = '36px';
    }
    
    return `
      width: ${dimensions};
      height: ${dimensions};
      border: ${thickness}px solid rgba(0, 0, 0, 0.1);
      border-top: ${thickness}px solid ${color};
    `;
  }}
`;

const SpinnerText = styled.p`
  margin-top: 12px;
  font-size: 14px;
  color: #4b5563;
`;

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  color = '#3b82f6',
  thickness = 2,
  fullPage = false,
  text,
}) => {
  return (
    <SpinnerContainer fullPage={fullPage}>
      <Spinner size={size} color={color} thickness={thickness} />
      {text && <SpinnerText>{text}</SpinnerText>}
    </SpinnerContainer>
  );
};

export default LoadingSpinner;
