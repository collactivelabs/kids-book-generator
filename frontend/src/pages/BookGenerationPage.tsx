import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import AuthContext from '../contexts/AuthContext';
import { GenerationSettings, GenerationProgressTracker, BookPreview } from '../components/generation';
import type { Book } from '../services/booksService';
import { booksService } from '../services/booksService';
import generationService from '../services/generationService';
import { Button } from '../components/common';

// Import types from services
import { GenerationSettingsData, GenerationStatusResponse } from '../services/generationService';

// Local interface for generation progress tracking
interface GenerationProgress extends GenerationStatusResponse {}


// Styled components
const PageContainer = styled.div`
  padding: ${({ theme }) => theme.spacing.lg};
`;

const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${({ theme }) => theme.spacing.lg};
`;

const Title = styled.h1`
  margin: 0;
`;

const ContentWrapper = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: ${({ theme }) => theme.spacing.lg};
  
  @media (min-width: 1200px) {
    grid-template-columns: 1fr 1fr;
  }
`;

const SettingsWrapper = styled.div`
  grid-column: 1;
`;

const PreviewWrapper = styled.div`
  grid-column: 1;
  
  @media (min-width: 1200px) {
    grid-column: 2;
  }
`;

const ProgressWrapper = styled.div`
  margin-bottom: ${({ theme }) => theme.spacing.lg};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: ${({ theme }) => theme.spacing.md};
  margin-top: ${({ theme }) => theme.spacing.lg};
`;

const BookGenerationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = React.useContext(AuthContext);
  
  // State
  const [book, setBook] = useState<Book | null>(null);
  const [generationSettings, setGenerationSettings] = useState<GenerationSettingsData>({
    storyType: 'adventure',
    ageRange: '5-8',
    language: 'english',
    theme: '',
    characters: '',
    illustrationStyle: 'cartoon',
    additionalNotes: '',
    pagesCount: 10
  });
  const [generationProgress, setGenerationProgress] = useState<GenerationProgress>({
    status: 'idle',
    currentStep: '',
    progress: 0
  });
  const [showPreview, setShowPreview] = useState(false);
  
  // Fetch book if editing an existing book
  useEffect(() => {
    const fetchBook = async () => {
      if (id) {
        try {
          const bookData = await booksService.getBook(id);
          setBook(bookData);
          // Initialize settings from book data if available
          if (bookData.metadata) {
            // Convert metadata to generation settings format
            const settings = generationService.convertFromBookMetadata(bookData.metadata);
            setGenerationSettings(settings);
          }
        } catch (error) {
          console.error('Error fetching book:', error);
        }
      }
    };

    if (isAuthenticated) {
      fetchBook();
    }
  }, [id, isAuthenticated]);

  // Handle settings change
  const handleSettingsChange = (newSettings: GenerationSettingsData) => {
    setGenerationSettings(newSettings);
  };

  // Start generation process
  const handleStartGeneration = async () => {
    // Skip if already generating or completed
    if (generationProgress.status === 'completed' || generationProgress.status === 'generating') {
      return;
    }
    
    try {
      setGenerationProgress({
        status: 'generating',
        currentStep: 'Initializing generation process',
        progress: 0
      });

      // Mock generation process with simulated steps
      // In a real implementation, these would be API calls
      setTimeout(() => {
        setGenerationProgress({
          status: 'generating',
          currentStep: 'Creating story outline',
          progress: 20
        });
      }, 2000);
      
      setTimeout(() => {
        setGenerationProgress({
          status: 'generating',
          currentStep: 'Generating story content',
          progress: 50
        });
      }, 4000);
      
      setTimeout(() => {
        setGenerationProgress({
          status: 'generating',
          currentStep: 'Creating illustrations',
          progress: 75
        });
      }, 6000);
      
      setTimeout(() => {
        setGenerationProgress({
          status: 'completed',
          currentStep: 'Book generation completed',
          progress: 100
        });
        setShowPreview(true);
      }, 8000);
      
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

  // Create a new book
  const createNewBook = async () => {
    try {
      // Convert generation settings to book metadata
      const metadata = generationService.convertToBookMetadata(generationSettings);
      
      const bookData = {
        metadata: metadata,
        template_id: 'default' // Required field for book creation
      };
      
      const createdBook = await booksService.createBook(bookData);
      setBook(createdBook);
      return createdBook.id;
    } catch (error) {
      console.error('Error creating book:', error);
      setGenerationProgress({
        status: 'failed',
        currentStep: 'Failed to create book',
        progress: 0,
        error: 'Could not create book. Please try again.'
      });
      return null;
    }
  };

  // Handle save book
  const handleSaveBook = async () => {
    try {
      const bookData = {
        title: generationSettings.theme || 'New Book',
        description: generationSettings.additionalNotes || 'Generated book',
        language: generationSettings.language,
        metadata: generationService.convertToBookMetadata(generationSettings),
        // Add other necessary book data
      };
      
      if (id) {
        // Update existing book
        await booksService.updateBook(id, bookData);
      } else {
        // Create new book
        const newBookId = await createNewBook();
        if (newBookId) {
          navigate(`/books/${newBookId}`);
        }
      }
    } catch (error) {
      console.error('Error saving book:', error);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    navigate('/books');
  };

  return (
    <PageContainer>
      <PageHeader>
        <Title>{id ? 'Edit Book' : 'Generate New Book'}</Title>
      </PageHeader>
      
      <ContentWrapper>
        <SettingsWrapper>
          <ProgressWrapper>
            <GenerationProgressTracker 
              status={generationProgress.status}
              currentStep={generationProgress.currentStep}
              progress={generationProgress.progress}
              error={generationProgress.error}
              estimatedTimeRemaining={generationProgress.estimatedTimeRemaining}
            />
          </ProgressWrapper>
          
          {!showPreview && (
            <>
              <GenerationSettings
                settings={generationSettings}
                onChange={handleSettingsChange}
                disabled={generationProgress.status === 'generating'}
              />
              
              <ActionButtons>
                {(generationProgress.status === 'idle' || generationProgress.status === 'failed') && (
                  <Button 
                    onClick={handleStartGeneration}
                    disabled={generationProgress.status !== 'idle' && generationProgress.status !== 'failed'}
                  >
                    Generate Book
                  </Button>
                )}
                
                {book && generationProgress.status === 'completed' && (
                  <Button onClick={() => setShowPreview(true)}>
                    View Book Preview
                  </Button>
                )}
                
                <Button variant="secondary" onClick={handleCancel}>
                  Cancel
                </Button>
              </ActionButtons>
            </>
          )}
        </SettingsWrapper>
        
        {showPreview && (
          <PreviewWrapper>
            {book && (
              <>
                <BookPreview
                  book={book}
                  onClose={() => setShowPreview(false)}
                  onSave={handleSaveBook}
                  showDownloadOptions={true}
                />
                <ActionButtons>
                  <Button onClick={handleSaveBook}>Save Book</Button>
                  <Button variant="secondary" onClick={() => setShowPreview(false)}>Close Preview</Button>
                </ActionButtons>
              </>
            )}
          </PreviewWrapper>
        )}
      </ContentWrapper>
    </PageContainer>
  );
};

export default BookGenerationPage;
