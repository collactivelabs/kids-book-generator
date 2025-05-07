import React, { FormEvent, ReactNode } from 'react';
import styled from 'styled-components';

interface FormProps {
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  children: ReactNode;
  className?: string;
  id?: string;
  autoComplete?: string;
}

const StyledForm = styled.form`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const FormGroup = styled.div`
  margin-bottom: 16px;
`;

const FormLabel = styled.label`
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
`;

const FormError = styled.div`
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
`;

const FormActions = styled.div`
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  gap: 12px;
`;

const FormDivider = styled.div`
  width: 100%;
  height: 1px;
  background-color: #e5e7eb;
  margin: 24px 0;
`;

const FormHint = styled.p`
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
  margin-bottom: 0;
`;

const Form: React.FC<FormProps> & {
  Group: typeof FormGroup;
  Label: typeof FormLabel;
  Error: typeof FormError;
  Actions: typeof FormActions;
  Divider: typeof FormDivider;
  Hint: typeof FormHint;
} = ({ onSubmit, children, className, id, autoComplete }) => {
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit(e);
  };

  return (
    <StyledForm 
      onSubmit={handleSubmit} 
      className={className} 
      id={id}
      autoComplete={autoComplete}
    >
      {children}
    </StyledForm>
  );
};

// Add subcomponents to Form
Form.Group = FormGroup;
Form.Label = FormLabel;
Form.Error = FormError;
Form.Actions = FormActions;
Form.Divider = FormDivider;
Form.Hint = FormHint;

export default Form;
