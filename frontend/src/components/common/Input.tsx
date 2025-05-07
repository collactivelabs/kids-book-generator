import React, { forwardRef } from 'react';
import styled, { css } from 'styled-components';

export type InputSize = 'small' | 'medium' | 'large';
export type InputVariant = 'default' | 'filled' | 'outlined';

// Omit the size prop from InputHTMLAttributes to avoid type conflict
interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  helperText?: string;
  error?: boolean;
  errorText?: string;
  size?: InputSize;
  variant?: InputVariant;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  isLoading?: boolean;
}

const InputContainer = styled.div<{ fullWidth: boolean }>`
  display: flex;
  flex-direction: column;
  
  ${(props) =>
    props.fullWidth &&
    css`
      width: 100%;
    `}
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
`;

const StyledInputWrapper = styled.div<{
  size: InputSize;
  variant: InputVariant;
  error: boolean;
  disabled: boolean;
  hasLeftIcon: boolean;
  hasRightIcon: boolean;
}>`
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  
  ${(props) => {
    switch (props.variant) {
      case 'filled':
        return css`
          background-color: #f3f4f6;
          border: 1px solid #f3f4f6;
          border-radius: 6px;
          
          &:focus-within {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        `;
      case 'outlined':
        return css`
          background-color: transparent;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          
          &:focus-within {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        `;
      default:
        return css`
          background-color: white;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          
          &:focus-within {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
          }
        `;
    }
  }}
  
  ${(props) =>
    props.error &&
    css`
      border-color: #ef4444 !important;
      
      &:focus-within {
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
      }
    `}
  
  ${(props) =>
    props.disabled &&
    css`
      opacity: 0.6;
      cursor: not-allowed;
      
      &:focus-within {
        border-color: #d1d5db;
        box-shadow: none;
      }
    `}
`;

const StyledInput = styled.input<{ 
  size: InputSize;
  hasLeftIcon: boolean;
  hasRightIcon: boolean;
}>`
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  width: 100%;
  font-family: inherit;
  
  ${(props) => {
    switch (props.size) {
      case 'small':
        return css`
          padding: 8px 12px;
          font-size: 14px;
        `;
      case 'large':
        return css`
          padding: 12px 16px;
          font-size: 16px;
        `;
      default:
        return css`
          padding: 10px 14px;
          font-size: 15px;
        `;
    }
  }}
  
  ${(props) =>
    props.hasLeftIcon &&
    css`
      padding-left: 40px;
    `}
  
  ${(props) =>
    props.hasRightIcon &&
    css`
      padding-right: 40px;
    `}
    
  &:disabled {
    cursor: not-allowed;
  }
`;

const IconContainer = styled.div<{ position: 'left' | 'right'; size: InputSize }>`
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  
  ${(props) => {
    switch (props.position) {
      case 'left':
        return css`
          left: 12px;
        `;
      case 'right':
        return css`
          right: 12px;
        `;
    }
  }}
  
  ${(props) => {
    switch (props.size) {
      case 'small':
        return css`
          font-size: 16px;
        `;
      case 'large':
        return css`
          font-size: 20px;
        `;
      default:
        return css`
          font-size: 18px;
        `;
    }
  }}
`;

const HelperText = styled.span<{ error: boolean }>`
  font-size: 12px;
  margin-top: 4px;
  
  ${(props) =>
    props.error
      ? css`
          color: #ef4444;
        `
      : css`
          color: #6b7280;
        `}
`;

const LoadingSpinner = styled.div`
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 2px solid #3b82f6;
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      helperText,
      error = false,
      errorText,
      size = 'medium',
      variant = 'default',
      fullWidth = false,
      leftIcon,
      rightIcon,
      isLoading = false,
      disabled = false,
      ...rest
    },
    ref
  ) => {
    return (
      <InputContainer fullWidth={fullWidth}>
        {label && <Label>{label}</Label>}
        
        <StyledInputWrapper
          size={size}
          variant={variant}
          error={error}
          disabled={disabled}
          hasLeftIcon={!!leftIcon}
          hasRightIcon={!!rightIcon || isLoading}
        >
          {leftIcon && (
            <IconContainer position="left" size={size}>
              {leftIcon}
            </IconContainer>
          )}
          
          <StyledInput
            ref={ref}
            size={size}
            hasLeftIcon={!!leftIcon}
            hasRightIcon={!!rightIcon || isLoading}
            disabled={disabled}
            {...rest}
          />
          
          {isLoading && (
            <IconContainer position="right" size={size}>
              <LoadingSpinner />
            </IconContainer>
          )}
          
          {!isLoading && rightIcon && (
            <IconContainer position="right" size={size}>
              {rightIcon}
            </IconContainer>
          )}
        </StyledInputWrapper>
        
        {(helperText || (error && errorText)) && (
          <HelperText error={error}>
            {error ? errorText : helperText}
          </HelperText>
        )}
      </InputContainer>
    );
  }
);

Input.displayName = 'Input';

export default Input;
