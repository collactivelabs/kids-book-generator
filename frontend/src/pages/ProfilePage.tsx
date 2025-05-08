import React from 'react';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import { RootState } from '../store';
import { Card, Button } from '../components/common';

const PageContainer = styled.div`
  padding: ${props => props.theme.spacing.md};
`;

const PageTitle = styled.h1`
  margin-bottom: ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.text.primary};
`;

const ProfileCard = styled(Card)`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  margin-bottom: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.lg};
`;

const ProfileForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
`;

const Label = styled.label`
  font-weight: ${props => props.theme.typography.fontWeight.medium};
  color: ${props => props.theme.colors.text.primary};
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 1px solid ${props => props.theme.colors.border.main};
  border-radius: ${props => props.theme.borderRadius.medium};
  font-size: ${props => props.theme.typography.fontSize.md};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary.main};
    box-shadow: 0 0 0 2px ${props => props.theme.colors.primary.light}30;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
`;

/**
 * ProfilePage component
 * 
 * Displays and allows editing of the user's profile information
 */
const ProfilePage: React.FC = () => {
  // Get user from Redux store
  const { user } = useSelector((state: RootState) => state.auth);
  
  // Local form state
  const [formData, setFormData] = React.useState({
    username: user?.username || '',
    email: user?.email || '',
    fullName: user?.fullName || '',
  });
  
  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement profile update functionality
    console.log('Profile update submitted:', formData);
    // Will need to dispatch an action to update the user profile
    alert('Profile update functionality will be implemented in a future release');
  };

  return (
    <PageContainer>
      <PageTitle>My Profile</PageTitle>
      
      <ProfileCard>
        <SectionTitle>Personal Information</SectionTitle>
        <ProfileForm onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="username">Username</Label>
            <Input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              disabled // Username can't be changed
            />
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="email">Email</Label>
            <Input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="fullName">Full Name</Label>
            <Input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
            />
          </FormGroup>
          
          <ActionButtons>
            <Button type="submit" variant="primary">
              Save Changes
            </Button>
          </ActionButtons>
        </ProfileForm>
      </ProfileCard>
      
      <ProfileCard>
        <SectionTitle>Account Security</SectionTitle>
        <Button variant="secondary">
          Change Password
        </Button>
      </ProfileCard>
    </PageContainer>
  );
};

export default ProfilePage;
