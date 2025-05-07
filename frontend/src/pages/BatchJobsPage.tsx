import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

// Styled components
const PageContainer = styled.div`
  padding: var(--spacing-md);
`;

const Title = styled.h1`
  margin-bottom: var(--spacing-lg);
  color: var(--color-text);
`;

const CreateButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-md);
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  margin-bottom: var(--spacing-lg);
  
  &:hover {
    background-color: var(--color-primary-dark);
    color: white;
  }
  
  svg {
    width: 16px;
    height: 16px;
    margin-right: var(--spacing-sm);
  }
`;

/**
 * BatchJobsPage component
 * 
 * Displays a list of batch jobs with status and filtering options
 */
const BatchJobsPage: React.FC = () => {
  return (
    <PageContainer>
      <Title>Batch Jobs</Title>
      
      <CreateButton to="/batch/create">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
        </svg>
        Create Batch Job
      </CreateButton>
      
      <p>Batch jobs list will be implemented here</p>
    </PageContainer>
  );
};

export default BatchJobsPage;
