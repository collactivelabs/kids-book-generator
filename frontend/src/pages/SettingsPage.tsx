import React, { useState } from 'react';
import styled from 'styled-components';
import { Card, Button } from '../components/common';

const PageContainer = styled.div`
  padding: ${props => props.theme.spacing.md};
`;

const PageTitle = styled.h1`
  margin-bottom: ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.text.primary};
`;

const SettingsCard = styled(Card)`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  margin-bottom: ${props => props.theme.spacing.md};
  font-size: ${props => props.theme.typography.fontSize.lg};
`;

const OptionGroup = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const OptionRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.sm} 0;
  border-bottom: 1px solid ${props => props.theme.colors.border.light};
`;

const OptionLabel = styled.label`
  display: flex;
  align-items: center;
  font-weight: ${props => props.theme.typography.fontWeight.medium};
`;

const OptionDescription = styled.p`
  color: ${props => props.theme.colors.text.secondary};
  font-size: ${props => props.theme.typography.fontSize.sm};
  margin-top: ${props => props.theme.spacing.xs};
`;

const Switch = styled.div<{ $active: boolean }>`
  width: 50px;
  height: 24px;
  background-color: ${props => props.$active ? props.theme.colors.primary.main : props.theme.colors.border.main};
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s ease;
  
  &:after {
    content: '';
    position: absolute;
    top: 2px;
    left: ${props => props.$active ? '26px' : '2px'};
    width: 20px;
    height: 20px;
    background-color: white;
    border-radius: 50%;
    transition: left 0.3s ease;
  }
`;

const Select = styled.select`
  padding: 0.5rem;
  border-radius: ${props => props.theme.borderRadius.small};
  border: 1px solid ${props => props.theme.colors.border.main};
  background-color: ${props => props.theme.colors.background.input};
  min-width: 150px;
`;

/**
 * SettingsPage component
 * 
 * Allows users to configure application settings and preferences
 */
const SettingsPage: React.FC = () => {
  // Settings state
  const [darkMode, setDarkMode] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(false);
  const [language, setLanguage] = useState('en');
  
  // Handle toggle changes
  const handleToggle = (setter: React.Dispatch<React.SetStateAction<boolean>>) => {
    return () => setter(prev => !prev);
  };
  
  // Handle language change
  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLanguage(e.target.value);
  };
  
  // Save settings
  const saveSettings = () => {
    // TODO: Implement settings save functionality
    console.log('Settings saved:', {
      darkMode,
      emailNotifications,
      pushNotifications,
      language,
    });
    alert('Settings saved successfully!');
  };

  return (
    <PageContainer>
      <PageTitle>Settings</PageTitle>
      
      <SettingsCard>
        <SectionTitle>Appearance</SectionTitle>
        <OptionGroup>
          <OptionRow>
            <div>
              <OptionLabel>Dark Mode</OptionLabel>
              <OptionDescription>Switch between light and dark themes</OptionDescription>
            </div>
            <Switch $active={darkMode} onClick={handleToggle(setDarkMode)} />
          </OptionRow>
          
          <OptionRow>
            <div>
              <OptionLabel>Language</OptionLabel>
              <OptionDescription>Select your preferred language</OptionDescription>
            </div>
            <Select value={language} onChange={handleLanguageChange}>
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </Select>
          </OptionRow>
        </OptionGroup>
      </SettingsCard>
      
      <SettingsCard>
        <SectionTitle>Notifications</SectionTitle>
        <OptionGroup>
          <OptionRow>
            <div>
              <OptionLabel>Email Notifications</OptionLabel>
              <OptionDescription>Receive updates and notifications via email</OptionDescription>
            </div>
            <Switch $active={emailNotifications} onClick={handleToggle(setEmailNotifications)} />
          </OptionRow>
          
          <OptionRow>
            <div>
              <OptionLabel>Push Notifications</OptionLabel>
              <OptionDescription>Receive notifications in your browser</OptionDescription>
            </div>
            <Switch $active={pushNotifications} onClick={handleToggle(setPushNotifications)} />
          </OptionRow>
        </OptionGroup>
      </SettingsCard>
      
      <SettingsCard>
        <SectionTitle>Privacy</SectionTitle>
        <OptionGroup>
          <OptionRow>
            <div>
              <OptionLabel>Data Collection</OptionLabel>
              <OptionDescription>Allow anonymous usage data collection to improve the application</OptionDescription>
            </div>
            <Switch $active={true} onClick={() => {}} />
          </OptionRow>
        </OptionGroup>
      </SettingsCard>
      
      <Button variant="primary" onClick={saveSettings}>
        Save Settings
      </Button>
    </PageContainer>
  );
};

export default SettingsPage;
