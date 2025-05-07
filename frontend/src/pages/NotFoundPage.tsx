import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

// Styled components
const NotFoundContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: calc(100vh - 200px);
  padding: var(--spacing-xl) var(--spacing-md);
`;

const ErrorCode = styled.h1`
  font-size: 8rem;
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
  line-height: 1;
`;

const Title = styled.h2`
  font-size: var(--font-size-xxl);
  margin-bottom: var(--spacing-lg);
  color: var(--color-text);
`;

const Message = styled.p`
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-xl);
  color: var(--color-text-light);
  max-width: 600px;
`;

const Button = styled(Link)`
  display: inline-block;
  padding: var(--spacing-sm) var(--spacing-lg);
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  text-decoration: none;
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: var(--color-primary-dark);
    color: white;
  }
`;

/**
 * NotFoundPage component
 * 
 * Displays a 404 error page when a route is not found
 */
const NotFoundPage: React.FC = () => {
  return (
    <NotFoundContainer>
      <ErrorCode>404</ErrorCode>
      <Title>Page Not Found</Title>
      <Message>
        The page you are looking for might have been removed, had its name changed,
        or is temporarily unavailable.
      </Message>
      <Button to="/">Back to Home</Button>
    </NotFoundContainer>
  );
};

export default NotFoundPage;
