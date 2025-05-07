import React, { ElementType, ComponentPropsWithoutRef } from 'react';
import styled, { css } from 'styled-components';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
export type ButtonSize = 'small' | 'medium' | 'large';

// Define button style props separately from functional props
type ButtonStyleProps = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  hasLeftIcon?: boolean;
  hasRightIcon?: boolean;
};

// Polymorphic component type setup
type ButtonAsProps<C extends ElementType = 'button'> = {
  as?: C;
};

export type ButtonProps<C extends ElementType = 'button'> = {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  disabled?: boolean; // Allow disabled for all element types
} & ButtonAsProps<C> & Omit<ComponentPropsWithoutRef<C>, keyof ButtonStyleProps | keyof ButtonAsProps<C> | 'disabled'>;

const StyledButton = styled.button<{
  variant: ButtonVariant;
  size: ButtonSize;
  fullWidth: boolean;
  hasLeftIcon: boolean;
  hasRightIcon: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  border-radius: 6px;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  border: none;
  position: relative;

  /* Full width */
  ${(props) =>
    props.fullWidth &&
    css`
      width: 100%;
    `}

  /* Size variants */
  ${(props) => {
    switch (props.size) {
      case 'small':
        return css`
          padding: 8px 12px;
          font-size: 14px;
        `;
      case 'large':
        return css`
          padding: 12px 24px;
          font-size: 16px;
        `;
      default:
        return css`
          padding: 10px 16px;
          font-size: 15px;
        `;
    }
  }}

  /* Style variants */
  ${(props) => {
    switch (props.variant) {
      case 'secondary':
        return css`
          background-color: #f3f4f6;
          color: #4b5563;
          &:hover {
            background-color: #e5e7eb;
          }
          &:active {
            background-color: #d1d5db;
          }
        `;
      case 'danger':
        return css`
          background-color: #ef4444;
          color: white;
          &:hover {
            background-color: #dc2626;
          }
          &:active {
            background-color: #b91c1c;
          }
        `;
      case 'ghost':
        return css`
          background-color: transparent;
          color: #4b5563;
          &:hover {
            background-color: #f3f4f6;
          }
          &:active {
            background-color: #e5e7eb;
          }
        `;
      default:
        return css`
          background-color: #3b82f6;
          color: white;
          &:hover {
            background-color: #2563eb;
          }
          &:active {
            background-color: #1d4ed8;
          }
        `;
    }
  }}

  /* Disabled state */
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  }

  /* Icon spacing */
  ${(props) =>
    props.hasLeftIcon &&
    css`
      padding-left: ${props.size === 'small' ? '10px' : '12px'};
    `}

  ${(props) =>
    props.hasRightIcon &&
    css`
      padding-right: ${props.size === 'small' ? '10px' : '12px'};
    `}
`;

const IconContainer = styled.span<{ position: 'left' | 'right'; size: ButtonSize }>`
  display: flex;
  align-items: center;
  margin-left: ${(props) => (props.position === 'right' ? '8px' : '0')};
  margin-right: ${(props) => (props.position === 'left' ? '8px' : '0')};
  font-size: ${(props) => (props.size === 'small' ? '16px' : '20px')};
`;

const LoadingSpinner = styled.div`
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top: 2px solid white;
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

export const Button = <C extends React.ElementType = 'button'>(
  {
    variant = 'primary',
    size = 'medium',
    fullWidth = false,
    isLoading = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    as,
    ...rest
  }: ButtonProps<C>
) => {
  return (
    <StyledButton
      as={as}
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      hasLeftIcon={!!leftIcon}
      hasRightIcon={!!rightIcon}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading && <LoadingSpinner />}
      {!isLoading && leftIcon && (
        <IconContainer position="left" size={size}>
          {leftIcon}
        </IconContainer>
      )}
      {children}
      {!isLoading && rightIcon && (
        <IconContainer position="right" size={size}>
          {rightIcon}
        </IconContainer>
      )}
    </StyledButton>
  );
};

export default Button;
