import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { GenerationSettings, GenerationProgressTracker, BookPreview } from '../components/generation';
import { Button, Card } from '../components/common';
// Book service will be used in a future implementation
import generationService, { GenerationSettingsData, GenerationStatusResponse } from '../services/generationService';

// Types are imported from generationService.ts

// Styled components
const PageContainer = styled.div`
  padding: ${({ theme }) => theme.spacing.md};
`;

const Title = styled.h1`
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  color: ${({ theme }) => theme.colors.text.primary};
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: ${({ theme }) => theme.spacing.lg};
  
  @media (min-width: 1200px) {
    grid-template-columns: 1fr 1fr;
  }
`;

const Section = styled(Card)`
  padding: ${({ theme }) => theme.spacing.lg};
  margin-bottom: ${({ theme }) => theme.spacing.lg};
`;

const SectionTitle = styled.h2`
  margin-bottom: ${({ theme }) => theme.spacing.md};
  font-size: ${({ theme }) => theme.typography.fontSize.lg};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.md};
  margin-top: ${({ theme }) => theme.spacing.lg};
`;

/**
 * BookCreatePage component
 * 
 * Form for creating a new book with all configuration options including
 * generation workflow, settings, and preview.
 */
const BookCreatePage: React.FC = () => {
  const navigate = useNavigate();
  
  // State
  const [activeStep, setActiveStep] = useState<'settings' | 'generating' | 'preview'>('settings');
  const [generationOptions, setGenerationOptions] = useState<GenerationSettingsData>({
    storyType: 'adventure',
    ageRange: '5-8',
    language: 'english',
    theme: 'Magic and Adventure',
    characters: 'A brave child and a friendly dragon',
    illustrationStyle: 'cartoon',
    additionalNotes: '',
    pagesCount: 10
  });
  const [generationProgress, setGenerationProgress] = useState<GenerationStatusResponse>({
    status: 'idle',
    currentStep: '',
    progress: 0
  });
  const [generatedBook, setGeneratedBook] = useState<any>(null);

  // Handle settings change
  const handleSettingsChange = (newSettings: GenerationSettingsData) => {
    setGenerationOptions(newSettings);
  };

  // Start generation process
  const handleStartGeneration = async () => {
    try {
      setActiveStep('generating');
      setGenerationProgress({
        status: 'preparing',
        currentStep: 'Preparing generation parameters',
        progress: 5
      });

      // Start actual generation process
      const generatedBook = await generationService.mockGeneration(generationOptions);
      
      // In a real implementation, we would start the generation and poll for status:
      // const result = await generationService.startGeneration({ settings: generationOptions });
      // const bookId = result.bookId;
      // const statusPoller = setInterval(async () => {
      //   const status = await generationService.getGenerationStatus(bookId);
      //   setGenerationProgress(status);
      //   if (status.status === 'completed' || status.status === 'failed') {
      //     clearInterval(statusPoller);
      //     if (status.status === 'completed') {
      //       const generatedBook = await booksService.getBook(bookId);
      //       setGeneratedBook(generatedBook);
      //       setActiveStep('preview');
      //     }
      //   }
      // }, 2000);
      
      setGeneratedBook(generatedBook);
      setGenerationProgress({
        status: 'completed',
        currentStep: 'Book generation completed',
        progress: 100
      });
      
      // Move to preview step
      setActiveStep('preview');
      
    } catch (error) {
      console.error('Generation error:', error);
      setGenerationProgress({
        status: 'failed',
        currentStep: 'Generation failed',
        progress: 0,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      });
    }
  };

  // Save the generated book
  const handleSaveBook = async () => {
    try {
      if (!generatedBook) return;
      
      // In a real implementation with createBook from the API:
      // const bookMetadata = generationService.convertToBookMetadata(generationOptions);
      // const savedBook = await booksService.createBook({
      //   metadata: bookMetadata,
      //   template_id: 'default-template' // Would be selected by user or determined by book type
      // });
      
      // For now, let's just navigate as if it was saved
      navigate(`/books/${generatedBook.id}`);
    } catch (error) {
      console.error('Error saving book:', error);
    }
  };

  // Cancel generation and go back to book list
  const handleCancel = () => {
    navigate('/books');
  };

  return (
    <PageContainer>
      <Title>Create a New Book</Title>
      
      {activeStep === 'settings' && (
        <Section>
          <SectionTitle>Generation Settings</SectionTitle>
          <GenerationSettings 
            settings={generationOptions}
            onChange={handleSettingsChange}
          />
          <ActionButtons>
            <Button onClick={handleStartGeneration}>Generate Book</Button>
            <Button variant="secondary" onClick={handleCancel}>Cancel</Button>
          </ActionButtons>
        </Section>
      )}
      
      {activeStep === 'generating' && (
        <Section>
          <SectionTitle>Generating Your Book</SectionTitle>
          <GenerationProgressTracker
            status={generationProgress.status}
            currentStep={generationProgress.currentStep}
            progress={generationProgress.progress}
            error={generationProgress.error}
          />
          <ActionButtons>
            <Button variant="secondary" onClick={handleCancel} disabled={generationProgress.status === 'generating'}>Cancel</Button>
          </ActionButtons>
        </Section>
      )}
      
      {activeStep === 'preview' && generatedBook && (
        <ContentGrid>
          <Section>
            <SectionTitle>Book Preview</SectionTitle>
            <p>Your book has been generated. Review the preview and make any necessary adjustments before saving.</p>
            <ActionButtons>
              <Button onClick={handleSaveBook}>Save Book</Button>
              <Button variant="secondary" onClick={() => setActiveStep('settings')}>Back to Settings</Button>
              <Button onClick={handleCancel}>Cancel</Button>
            </ActionButtons>
          </Section>
          
          <BookPreview 
            book={generatedBook}
            onClose={() => setActiveStep('settings')}
          />
        </ContentGrid>
      )}
    </PageContainer>
  );
};

export default BookCreatePage;
