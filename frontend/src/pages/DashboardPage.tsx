import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../store';

// Styled components
const DashboardContainer = styled.div`
  padding: var(--spacing-md);
`;

const DashboardHeader = styled.div`
  margin-bottom: var(--spacing-xl);
`;

const Title = styled.h1`
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
`;

const Subtitle = styled.p`
  color: var(--color-text-light);
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-lg);
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (min-width: 992px) {
    grid-template-columns: repeat(3, 1fr);
  }
`;

const StatCard = styled.div`
  background-color: var(--color-surface);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
`;

const StatTitle = styled.h3`
  color: var(--color-text-light);
  font-size: var(--font-size-md);
  margin-bottom: var(--spacing-sm);
  font-weight: normal;
`;

const StatValue = styled.div`
  font-size: var(--font-size-xxl);
  font-weight: bold;
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
`;

const StatChange = styled.div<{ $positive: boolean }>`
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
  color: ${({ $positive }) => ($positive ? 'var(--color-success)' : 'var(--color-error)')};
`;

const ActionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
`;

const ActionCard = styled.div`
  background-color: var(--color-surface);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-md);
  }
`;

const ActionHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const ActionIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-md);
  
  svg {
    width: 24px;
    height: 24px;
  }
`;

const ActionTitle = styled.h3`
  color: var(--color-text);
  font-size: var(--font-size-lg);
  margin: 0;
`;

const ActionDescription = styled.p`
  color: var(--color-text-light);
  margin-bottom: var(--spacing-md);
`;

const ActionButton = styled.button`
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
  transition: background-color var(--transition-fast);
  
  &:hover {
    background-color: var(--color-primary-dark);
  }
  
  svg {
    width: 16px;
    height: 16px;
    margin-left: var(--spacing-sm);
  }
`;

const RecentActivitySection = styled.div`
  margin-bottom: var(--spacing-xl);
`;

const SectionTitle = styled.h2`
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
`;

const ActivityList = styled.div`
  background-color: var(--color-surface);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  
  &:last-child {
    border-bottom: none;
  }
`;

const ActivityIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(67, 97, 238, 0.1);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-md);
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityTitle = styled.div`
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
  color: var(--color-text);
`;

const ActivityMeta = styled.div`
  display: flex;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
`;

const ActivityTime = styled.span`
  margin-right: var(--spacing-md);
`;

const ActivityStatus = styled.span<{ $status: string }>`
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 500;
  
  ${({ $status }) => {
    switch ($status) {
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

const EmptyState = styled.div`
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-light);
`;

/**
 * DashboardPage component
 * 
 * Displays a user dashboard with statistics, quick actions, and recent activity
 */
const DashboardPage: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const navigate = useNavigate();
  
  // Sample data for the dashboard
  const stats = [
    { title: 'Total Books', value: 12, change: 3, positive: true },
    { title: 'Published Books', value: 8, change: 2, positive: true },
    { title: 'Pending Books', value: 4, change: 1, positive: false },
  ];
  
  const recentActivity = [
    {
      id: 1,
      title: 'Adventure in the Forest',
      time: '2 hours ago',
      status: 'completed',
      type: 'book',
    },
    {
      id: 2,
      title: 'Batch Processing: Animal Series',
      time: '1 day ago',
      status: 'processing',
      type: 'batch',
    },
    {
      id: 3,
      title: 'Dinosaur Adventures',
      time: '3 days ago',
      status: 'failed',
      type: 'book',
    },
  ];
  
  const hasActivity = recentActivity.length > 0;
  
  return (
    <DashboardContainer>
      <DashboardHeader>
        <Title>Dashboard</Title>
        <Subtitle>Welcome back, {user?.fullName || 'User'}!</Subtitle>
      </DashboardHeader>
      
      <StatsGrid>
        {stats.map((stat, index) => (
          <StatCard key={index}>
            <StatTitle>{stat.title}</StatTitle>
            <StatValue>{stat.value}</StatValue>
            <StatChange $positive={stat.positive}>
              {stat.positive ? (
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="18 15 12 9 6 15"></polyline>
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              )}
              {stat.change} {stat.positive ? 'increase' : 'decrease'} from last month
            </StatChange>
          </StatCard>
        ))}
      </StatsGrid>
      
      <ActionsGrid>
        <ActionCard onClick={() => navigate('/books/create')}>
          <ActionHeader>
            <ActionIcon>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
            </ActionIcon>
            <ActionTitle>Create New Book</ActionTitle>
          </ActionHeader>
          <ActionDescription>
            Generate a new illustrated children's book or coloring book with AI.
          </ActionDescription>
          <ActionButton>
            Get Started
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </ActionButton>
        </ActionCard>
        
        <ActionCard onClick={() => navigate('/batch/create')}>
          <ActionHeader>
            <ActionIcon>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </ActionIcon>
            <ActionTitle>Create Batch Job</ActionTitle>
          </ActionHeader>
          <ActionDescription>
            Generate multiple books at once with batch processing.
          </ActionDescription>
          <ActionButton>
            Start Batch
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </ActionButton>
        </ActionCard>
      </ActionsGrid>
      
      <RecentActivitySection>
        <SectionTitle>Recent Activity</SectionTitle>
        <ActivityList>
          {hasActivity ? (
            recentActivity.map((activity) => (
              <ActivityItem key={activity.id} onClick={() => {
                if (activity.type === 'book') {
                  navigate(`/books/${activity.id}`);
                } else {
                  navigate(`/batch/${activity.id}`);
                }
              }}>
                <ActivityIcon>
                  {activity.type === 'book' ? (
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                    </svg>
                  )}
                </ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>{activity.title}</ActivityTitle>
                  <ActivityMeta>
                    <ActivityTime>{activity.time}</ActivityTime>
                    <ActivityStatus $status={activity.status}>
                      {activity.status.charAt(0).toUpperCase() + activity.status.slice(1)}
                    </ActivityStatus>
                  </ActivityMeta>
                </ActivityContent>
              </ActivityItem>
            ))
          ) : (
            <EmptyState>
              No recent activity. Start by creating your first book!
            </EmptyState>
          )}
        </ActivityList>
      </RecentActivitySection>
    </DashboardContainer>
  );
};

export default DashboardPage;
