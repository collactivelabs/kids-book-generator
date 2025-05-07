import React from 'react';
import styled from 'styled-components';
import LoginForm from '../components/auth/LoginForm';

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
 * LoginPage component
 * 
 * Displays the login form and handles redirects after authentication
 */
const LoginPage: React.FC = () => {
  return (
    <PageContainer>
      <FormContainer>
        <Title>Sign In to Kids Book Generator</Title>
        <LoginForm />
      </FormContainer>
    </PageContainer>
  );
};

export default LoginPage;
