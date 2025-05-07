import React from 'react';
import styled from 'styled-components';
import RegisterForm from '../components/auth/RegisterForm';

// Styled components
const PageContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: var(--spacing-xl) var(--spacing-md);
`;

const FormContainer = styled.div`
  width: 100%;
  max-width: 500px;
`;

const Title = styled.h1`
  margin-bottom: var(--spacing-xl);
  text-align: center;
  color: var(--color-primary);
`;

/**
 * RegisterPage component
 * 
 * Displays the registration form for new users
 */
const RegisterPage: React.FC = () => {
  return (
    <PageContainer>
      <FormContainer>
        <Title>Create Your Account</Title>
        <RegisterForm />
      </FormContainer>
    </PageContainer>
  );
};

export default RegisterPage;
