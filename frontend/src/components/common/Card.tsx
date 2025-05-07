import React from 'react';
import styled, { css } from 'styled-components';

export type CardVariant = 'default' | 'outlined' | 'elevated';
export type CardPadding = 'none' | 'small' | 'medium' | 'large';

interface CardProps {
  variant?: CardVariant;
  padding?: CardPadding;
  fullWidth?: boolean;
  className?: string;
  onClick?: () => void;
  children: React.ReactNode;
  interactive?: boolean;
}

const StyledCard = styled.div<{
  variant: CardVariant;
  padding: CardPadding;
  fullWidth: boolean;
  interactive: boolean;
}>`
  border-radius: 8px;
  overflow: hidden;
  
  ${(props) =>
    props.fullWidth &&
    css`
      width: 100%;
    `}
  
  ${(props) => {
    switch (props.padding) {
      case 'none':
        return css`
          padding: 0;
        `;
      case 'small':
        return css`
          padding: 12px;
        `;
      case 'large':
        return css`
          padding: 24px;
        `;
      default:
        return css`
          padding: 16px;
        `;
    }
  }}
  
  ${(props) => {
    switch (props.variant) {
      case 'outlined':
        return css`
          border: 1px solid #e5e7eb;
          background-color: transparent;
        `;
      case 'elevated':
        return css`
          border: none;
          background-color: white;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        `;
      default:
        return css`
          border: none;
          background-color: white;
          box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        `;
    }
  }}
  
  ${(props) =>
    props.interactive &&
    css`
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      }
      
      &:active {
        transform: translateY(0);
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
      }
    `}
`;

const CardHeader = styled.div`
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CardTitle = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
`;

const CardContent = styled.div``;

const CardFooter = styled.div`
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
`;

export const Card: React.FC<CardProps> & {
  Header: typeof CardHeader;
  Title: typeof CardTitle;
  Content: typeof CardContent;
  Footer: typeof CardFooter;
} = ({
  variant = 'default',
  padding = 'medium',
  fullWidth = false,
  className,
  onClick,
  children,
  interactive = false,
}) => {
  return (
    <StyledCard
      variant={variant}
      padding={padding}
      fullWidth={fullWidth}
      className={className}
      onClick={onClick}
      interactive={interactive || !!onClick}
    >
      {children}
    </StyledCard>
  );
};

// Add subcomponents to Card
Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;
