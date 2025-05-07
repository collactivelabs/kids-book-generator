import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';

// Styled components
const PageContainer = styled.div`
  padding: var(--spacing-md);
`;

const Title = styled.h1`
  margin-bottom: var(--spacing-lg);
  color: var(--color-text);
`;

const StatusBadge = styled.span<{ status: string }>`
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-weight: 500;
  font-size: var(--font-size-sm);
  margin-left: var(--spacing-md);
  
  ${({ status }) => {
    switch (status) {
      case 'completed':
        return `
          background-color: rgba(76, 175, 80, 0.1);
          color: var(--color-success);
        `;
      case 'processing':
        return `
          background-color: rgba(33, 150, 243, 0.1);
          color: var(--color-info);
        `;
      case 'failed':
        return `
          background-color: rgba(244, 67, 54, 0.1);
          color: var(--color-error);
        `;
      default:
        return `
          background-color: rgba(158, 158, 158, 0.1);
          color: var(--color-text-light);
        `;
    }
  }}
`;

/**
 * BatchJobDetailPage component
 * 
 * Displays detailed information about a specific batch job
 */
const BatchJobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  // Placeholder batch job status for UI demo
  const status = 'processing';
  
  return (
    <PageContainer>
      <Title>
        Batch Job Details
        <StatusBadge status={status}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </StatusBadge>
      </Title>
      
      <p>Batch Job ID: {id}</p>
      <p>Batch job details will be implemented here</p>
    </PageContainer>
  );
};

export default BatchJobDetailPage;
