import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { GenerationSettingsData } from '../../services/generationService';

// Styled components
const Container = styled.div`
  width: 100%;
  padding: 1.5rem;
  border-radius: 8px;
  background-color: ${({ theme }) => theme.colors.background.card};
  box-shadow: ${({ theme }) => theme.shadows.small};
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.text.primary};
`;

const Input = styled.input`
  width: 100%;
  padding: 10px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 4px;
  background-color: ${({ theme }) => theme.colors.background.light};
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 14px;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 10px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 4px;
  background-color: ${({ theme }) => theme.colors.background.light};
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 14px;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 10px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 4px;
  background-color: ${({ theme }) => theme.colors.background.light};
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const NumberInput = styled.input.attrs({ type: 'number' })`
  width: 100%;
  padding: 10px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 4px;
  background-color: ${({ theme }) => theme.colors.background.light};
  color: ${({ theme }) => theme.colors.text.primary};
  font-size: 14px;
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

// Default settings for a new book
const defaultSettings: GenerationSettingsData = {
  storyType: 'adventure',
  ageRange: '5-8',
  language: 'english',
  theme: '',
  characters: '',
  illustrationStyle: 'cartoon',
  additionalNotes: '',
  pagesCount: 10
};

// Props interface
interface GenerationSettingsProps {
  settings?: GenerationSettingsData;
  onChange?: (settings: GenerationSettingsData) => void;
  disabled?: boolean;
}

/**
 * GenerationSettings Component
 * 
 * Allows users to configure book generation settings, including story type,
 * age range, language, theme, characters, and illustration style.
 */
const GenerationSettings: React.FC<GenerationSettingsProps> = ({
  settings,
  onChange,
  disabled = false
}) => {
  // Local state to manage form values
  const [formData, setFormData] = useState<GenerationSettingsData>({
    ...defaultSettings,
    ...settings
  });

  // Update local state when props change
  useEffect(() => {
    if (settings) {
      setFormData({...defaultSettings, ...settings});
    }
  }, [settings]);

  // Handle text/select input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    const updatedData = { ...formData, [name]: value };
    
    setFormData(updatedData);
    
    // Notify parent component
    if (onChange) {
      onChange(updatedData);
    }
  };

  // Handle number input changes
  const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const numValue = parseInt(value, 10);
    
    if (!isNaN(numValue)) {
      const updatedData = { ...formData, [name]: numValue };
      setFormData(updatedData);
      
      // Notify parent component
      if (onChange) {
        onChange(updatedData);
      }
    }
  };

  return (
    <Container>
      <FormGroup>
        <Label>Story Type</Label>
        <Select 
          name="storyType" 
          value={formData.storyType}
          onChange={handleChange}
          disabled={disabled}
        >
          <option value="adventure">Adventure</option>
          <option value="fantasy">Fantasy</option>
          <option value="educational">Educational</option>
          <option value="bedtime">Bedtime</option>
          <option value="fable">Fable</option>
          <option value="coloring">Coloring Book</option>
        </Select>
      </FormGroup>

      <FormGroup>
        <Label>Age Range</Label>
        <Select 
          name="ageRange" 
          value={formData.ageRange}
          onChange={handleChange}
          disabled={disabled}
        >
          <option value="0-3">Toddlers (0-3)</option>
          <option value="3-5">Preschool (3-5)</option>
          <option value="5-8">Early Readers (5-8)</option>
          <option value="8-12">Middle Grade (8-12)</option>
        </Select>
      </FormGroup>

      <FormGroup>
        <Label>Language</Label>
        <Select 
          name="language" 
          value={formData.language}
          onChange={handleChange}
          disabled={disabled}
        >
          <option value="english">English</option>
          <option value="spanish">Spanish</option>
          <option value="french">French</option>
          <option value="german">German</option>
          <option value="italian">Italian</option>
        </Select>
      </FormGroup>

      <FormGroup>
        <Label>Theme/Title</Label>
        <Input 
          type="text" 
          name="theme" 
          value={formData.theme}
          onChange={handleChange}
          placeholder="Enter a theme or title for your book"
          disabled={disabled}
        />
      </FormGroup>

      <FormGroup>
        <Label>Characters</Label>
        <Textarea 
          name="characters" 
          value={formData.characters}
          onChange={handleChange}
          placeholder="Describe the main characters of your story"
          disabled={disabled}
        />
      </FormGroup>

      <FormGroup>
        <Label>Illustration Style</Label>
        <Select 
          name="illustrationStyle" 
          value={formData.illustrationStyle}
          onChange={handleChange}
          disabled={disabled}
        >
          <option value="cartoon">Cartoon</option>
          <option value="watercolor">Watercolor</option>
          <option value="digital">Digital Art</option>
          <option value="realistic">Realistic</option>
          <option value="minimalist">Minimalist</option>
        </Select>
      </FormGroup>

      <FormGroup>
        <Label>Number of Pages</Label>
        <NumberInput 
          name="pagesCount" 
          value={formData.pagesCount}
          onChange={handleNumberChange}
          min={5}
          max={40}
          disabled={disabled}
        />
      </FormGroup>

      <FormGroup>
        <Label>Additional Notes</Label>
        <Textarea 
          name="additionalNotes" 
          value={formData.additionalNotes}
          onChange={handleChange}
          placeholder="Any additional details or requirements for your book"
          disabled={disabled}
        />
      </FormGroup>
    </Container>
  );
};

export default GenerationSettings;
