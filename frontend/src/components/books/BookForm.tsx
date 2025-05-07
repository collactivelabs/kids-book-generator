import React from 'react';
import styled from 'styled-components';
import { Book, BookCreationRequest } from '../../services/booksService';
import Form from '../common/Form';
import Input from '../common/Input';
import Button from '../common/Button';
import useForm from '../../hooks/useForm';
import { required, minLength, maxLength, composeValidators } from '../../utils/validation';
import Card from '../common/Card';

interface BookFormProps {
  initialBook?: Partial<Book>;
  onSubmit: (bookData: BookCreationRequest) => Promise<void>;
  isSubmitting?: boolean;
  templates: Array<{ id: string; name: string; preview_url?: string }>;
}

const TemplateGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-top: 12px;
`;

const TemplateCard = styled.div<{ selected: boolean }>`
  border: 2px solid ${props => props.selected ? '#3b82f6' : '#e5e7eb'};
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: ${props => props.selected ? '#3b82f6' : '#d1d5db'};
    transform: translateY(-2px);
  }
`;

const TemplateImage = styled.div<{ hasImage: boolean }>`
  width: 100%;
  aspect-ratio: 0.7;
  background-color: #f3f4f6;
  position: relative;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  ${props => !props.hasImage && `
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:after {
      content: 'No Preview';
      color: #9ca3af;
      font-size: 14px;
    }
  `}
`;

const TemplateInfo = styled.div`
  padding: 8px 12px;
`;

const TemplateName = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: #374151;
`;

const FormSection = styled.div`
  margin-bottom: 24px;
`;

const StyledCard = styled(Card)`
  margin-bottom: 24px;
`;

const TwoColumnGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const BookForm: React.FC<BookFormProps> = ({
  initialBook,
  onSubmit,
  isSubmitting = false,
  templates,
}) => {
  // Initialize with default values or provided book
  const initialValues: BookCreationRequest = {
    metadata: {
      title: initialBook?.metadata?.title || '',
      author: initialBook?.metadata?.author || '',
      age_group: initialBook?.metadata?.age_group || '3-5',
      book_type: initialBook?.metadata?.book_type || 'story',
      theme: initialBook?.metadata?.theme || '',
      educational_focus: initialBook?.metadata?.educational_focus || '',
      trim_size: initialBook?.metadata?.trim_size || '8.5x11',
      page_count: initialBook?.metadata?.page_count || 24,
    },
    template_id: initialBook?.template_id || '',
  };
  
  // Use form hook for form state and validation
  const form = useForm<BookCreationRequest>({
    initialValues,
    validationSchema: {
      'metadata.title': (value: string) => {
        return composeValidators(
          (val: string) => required(val, 'Title'),
          (val: string) => minLength(val, 3, 'Title'),
          (val: string) => maxLength(val, 100, 'Title')
        )(value);
      },
      'metadata.author': (value: string) => {
        return composeValidators(
          (val: string) => required(val, 'Author'),
          (val: string) => maxLength(val, 50, 'Author')
        )(value);
      },
      'metadata.theme': (value: string) => {
        return composeValidators(
          (val: string) => required(val, 'Theme'),
          (val: string) => maxLength(val, 50, 'Theme')
        )(value);
      },
      'template_id': (value: string) => required(value, 'Template'),
    },
    onSubmit,
  });
  
  // Handle form submission
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    form.handleSubmit(e);
  };
  
  // Handle template selection
  const handleTemplateSelect = (templateId: string) => {
    form.setValue('template_id', templateId);
  };
  
  return (
    <Form onSubmit={handleSubmit}>
      <StyledCard>
        <Card.Header>
          <Card.Title>Book Details</Card.Title>
        </Card.Header>
        <Card.Content>
          <FormSection>
            <Form.Group>
              <Form.Label htmlFor="metadata.title">Book Title *</Form.Label>
              <Input
                id="metadata.title"
                name="metadata.title"
                value={form.values.metadata.title}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                error={!!form.touched['metadata.title'] && !!form.errors['metadata.title']}
                errorText={form.touched['metadata.title'] ? form.errors['metadata.title'] : ''}
                placeholder="Enter book title"
                fullWidth
              />
            </Form.Group>
            
            <Form.Group>
              <Form.Label htmlFor="metadata.author">Author *</Form.Label>
              <Input
                id="metadata.author"
                name="metadata.author"
                value={form.values.metadata.author}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                error={!!form.touched['metadata.author'] && !!form.errors['metadata.author']}
                errorText={form.touched['metadata.author'] ? form.errors['metadata.author'] : ''}
                placeholder="Enter author name"
                fullWidth
              />
            </Form.Group>
            
            <TwoColumnGrid>
              <Form.Group>
                <Form.Label htmlFor="metadata.age_group">Age Group *</Form.Label>
                <select
                  id="metadata.age_group"
                  name="metadata.age_group"
                  value={form.values.metadata.age_group}
                  onChange={form.handleChange}
                  onBlur={form.handleBlur}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '15px',
                  }}
                >
                  <option value="0-3">0-3 years</option>
                  <option value="3-5">3-5 years</option>
                  <option value="5-7">5-7 years</option>
                  <option value="7-12">7-12 years</option>
                </select>
              </Form.Group>
              
              <Form.Group>
                <Form.Label htmlFor="metadata.book_type">Book Type *</Form.Label>
                <select
                  id="metadata.book_type"
                  name="metadata.book_type"
                  value={form.values.metadata.book_type}
                  onChange={form.handleChange}
                  onBlur={form.handleBlur}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '15px',
                  }}
                >
                  <option value="story">Storybook</option>
                  <option value="coloring">Coloring Book</option>
                </select>
              </Form.Group>
            </TwoColumnGrid>
            
            <Form.Group>
              <Form.Label htmlFor="metadata.theme">Theme *</Form.Label>
              <Input
                id="metadata.theme"
                name="metadata.theme"
                value={form.values.metadata.theme}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                error={!!form.touched['metadata.theme'] && !!form.errors['metadata.theme']}
                errorText={form.touched['metadata.theme'] ? form.errors['metadata.theme'] : ''}
                placeholder="Enter book theme (e.g., Adventure, Animals, Space)"
                fullWidth
              />
            </Form.Group>
            
            <Form.Group>
              <Form.Label htmlFor="metadata.educational_focus">Educational Focus (Optional)</Form.Label>
              <Input
                id="metadata.educational_focus"
                name="metadata.educational_focus"
                value={form.values.metadata.educational_focus || ''}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                placeholder="Enter educational focus (e.g., Counting, Colors, Friendship)"
                fullWidth
              />
            </Form.Group>
            
            <TwoColumnGrid>
              <Form.Group>
                <Form.Label htmlFor="metadata.trim_size">Trim Size *</Form.Label>
                <select
                  id="metadata.trim_size"
                  name="metadata.trim_size"
                  value={form.values.metadata.trim_size}
                  onChange={form.handleChange}
                  onBlur={form.handleBlur}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '15px',
                  }}
                >
                  <option value="8.5x11">8.5" x 11" (Letter)</option>
                  <option value="8.5x8.5">8.5" x 8.5" (Square)</option>
                </select>
              </Form.Group>
              
              <Form.Group>
                <Form.Label htmlFor="metadata.page_count">Page Count *</Form.Label>
                <select
                  id="metadata.page_count"
                  name="metadata.page_count"
                  value={form.values.metadata.page_count}
                  onChange={(e) => form.setValue('metadata.page_count', parseInt(e.target.value))}
                  onBlur={form.handleBlur}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '15px',
                  }}
                >
                  <option value="16">16 pages</option>
                  <option value="24">24 pages</option>
                  <option value="32">32 pages</option>
                  <option value="40">40 pages</option>
                </select>
              </Form.Group>
            </TwoColumnGrid>
          </FormSection>
        </Card.Content>
      </StyledCard>
      
      <StyledCard>
        <Card.Header>
          <Card.Title>Book Template *</Card.Title>
        </Card.Header>
        <Card.Content>
          <FormSection>
            {form.errors.template_id && form.touched.template_id && (
              <Form.Error>{form.errors.template_id}</Form.Error>
            )}
            
            <TemplateGrid>
              {templates.map((template) => (
                <TemplateCard
                  key={template.id}
                  selected={form.values.template_id === template.id}
                  onClick={() => handleTemplateSelect(template.id)}
                >
                  <TemplateImage hasImage={!!template.preview_url}>
                    {template.preview_url && <img src={template.preview_url} alt={template.name} />}
                  </TemplateImage>
                  <TemplateInfo>
                    <TemplateName>{template.name}</TemplateName>
                  </TemplateInfo>
                </TemplateCard>
              ))}
            </TemplateGrid>
          </FormSection>
        </Card.Content>
      </StyledCard>
      
      <Form.Actions>
        <Button type="submit" disabled={isSubmitting} isLoading={isSubmitting}>
          {initialBook ? 'Update Book' : 'Create Book'}
        </Button>
      </Form.Actions>
    </Form>
  );
};

export default BookForm;
