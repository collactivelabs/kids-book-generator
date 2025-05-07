import React from 'react';
import styled from 'styled-components';

// Generation status types
export type GenerationStatus = 'idle' | 'preparing' | 'generating' | 'completed' | 'failed';

interface GenerationProgressTrackerProps {
  status: GenerationStatus;
  currentStep: string;
  progress: number; // 0-100
  error?: string;
  estimatedTimeRemaining?: number; // in seconds
}

const Container = styled.div`
  width: 100%;
  margin: 1rem 0;
  padding: 1.5rem;
  border-radius: 8px;
  background-color: ${({ theme }) => theme.colors.background.card};
  box-shadow: ${({ theme }) => theme.shadows.card};
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const Title = styled.h3`
  font-size: 1.125rem;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const StatusBadge = styled.span<{ status: GenerationStatus }>`
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 600;
  background-color: ${({ status, theme }) => {
    const getBackgroundColor = (status: GenerationStatus) => {
      switch (status) {
        case 'idle':
          return theme.colors.status.pending;
        case 'preparing':
          return theme.colors.status.info;
        case 'generating':
          return theme.colors.status.inProgress;
        case 'completed':
          return theme.colors.status.success;
        case 'failed':
          return theme.colors.status.error;
        default:
          return theme.colors.status.info;
      }
    };
    return getBackgroundColor(status);
  }};
  color: white;
`;

const ProgressBarContainer = styled.div`
  width: 100%;
  height: 8px;
  background-color: ${({ theme }) => theme.colors.background.light};
  border-radius: 4px;
  overflow: hidden;
  margin: 0.75rem 0;
`;

const ProgressBar = styled.div<{ progress: number; status: GenerationStatus }>`
  height: 8px;
  background-color: ${({ theme }) => theme.colors.background.dark};
  border-radius: 4px;
  position: relative;
  overflow: hidden;
  flex: 1;
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: ${({ progress }) => `${progress}%`};
    background-color: ${({ theme, status }) => 
      status === 'failed' 
        ? theme.colors.status.error 
        : status === 'completed' 
          ? theme.colors.status.success 
          : theme.colors.primary.main
    };
    transition: width 0.3s ease-in-out;
  }
`;

const ProgressText = styled.span`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const StepInfo = styled.span`
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const TimeEstimate = styled.span`
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const ErrorMessage = styled.div`
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: ${({ theme }) => theme.colors.status.errorLight};
  border-radius: 4px;
  color: ${({ theme }) => theme.colors.status.error};
  font-size: 0.875rem;
`;

const ErrorIcon = styled.span`
  margin-right: 0.5rem;
`;

const SuccessMessage = styled.div`
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: ${({ theme }) => theme.colors.status.successLight};
  border-radius: 4px;
  color: ${({ theme }) => theme.colors.status.success};
  font-size: 0.875rem;
`;

const SuccessIcon = styled.span`
  margin-right: 0.5rem;
`;

const WaitingMessage = styled.div`
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: ${({ theme }) => theme.colors.status.pendingLight};
  border-radius: 4px;
  color: ${({ theme }) => theme.colors.status.pending};
  font-size: 0.875rem;
`;

/**
 * Generation Progress Tracker Component
 * 
 * Displays the current status and progress of book generation
 */
const GenerationProgressTracker: React.FC<GenerationProgressTrackerProps> = ({
  status,
  currentStep,
  progress,
  error,
  estimatedTimeRemaining
}) => {

  // Get status text based on generation status
  const getStatusText = () => {
    switch (status) {
      case 'idle':
        return 'Ready';
      case 'preparing':
        return 'Preparing';
      case 'generating':
        return 'Generating';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      default:
        return 'In Progress';
    }
  };

  // Format estimated time remaining
  const formatTimeRemaining = () => {
    if (!estimatedTimeRemaining) return null;
    const minutes = Math.floor(estimatedTimeRemaining / 60);
    const seconds = Math.floor(estimatedTimeRemaining % 60);
    
    return (
      <TimeEstimate>
        Estimated time: {minutes > 0 ? `${minutes}m ` : ''}{seconds}s
      </TimeEstimate>
    );
  };
  
  // Render correct content based on status
  const renderContent = () => {
    if (status === 'failed' && error) {
      return (
        <ErrorMessage>
          <ErrorIcon /> {error}
        </ErrorMessage>
      );
    }
    
    if (status === 'completed') {
      return (
        <SuccessMessage>
          <SuccessIcon /> Book generation completed successfully!
        </SuccessMessage>
      );
    }
    
    return (
      <>
        <ProgressBarContainer>
          <ProgressBar progress={progress} status={status} />
          <ProgressText>
            {progress.toFixed(0)}%
          </ProgressText>
        </ProgressBarContainer>
        
        {status !== 'idle' && (
          <StepInfo>
            {currentStep}
          </StepInfo>
        )}
        
        {status === 'idle' ? (
          <WaitingMessage>Waiting to start generation...</WaitingMessage>
        ) : status === 'generating' || status === 'preparing' ? (
          formatTimeRemaining()
        ) : null}
      </>
    );
  };

  return (
    <Container>
      <Header>
        <Title>Generation Progress</Title>
        <StatusBadge status={status}>{getStatusText()}</StatusBadge>
      </Header>
      
      {renderContent()}
    </Container>
  );
};

export default GenerationProgressTracker;
