import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

// Styled components
const HomeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-xl) var(--spacing-md);
  max-width: 1200px;
  margin: 0 auto;
`;

const Hero = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: var(--spacing-xxl);
  
  @media (min-width: 768px) {
    flex-direction: row;
    text-align: left;
    align-items: flex-start;
  }
`;

const HeroContent = styled.div`
  flex: 1;
  margin-bottom: var(--spacing-xl);
  
  @media (min-width: 768px) {
    margin-right: var(--spacing-xl);
    margin-bottom: 0;
  }
`;

const HeroTitle = styled.h1`
  font-size: var(--font-size-xxxl);
  margin-bottom: var(--spacing-md);
  color: var(--color-primary);
`;

const HeroSubtitle = styled.p`
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-light);
  max-width: 600px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  justify-content: center;
  
  @media (min-width: 768px) {
    justify-content: flex-start;
  }
`;

const Button = styled(Link)`
  display: inline-block;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  font-weight: 500;
  text-decoration: none;
  transition: all var(--transition-fast);
`;

const PrimaryButton = styled(Button)`
  background-color: var(--color-primary);
  color: white;
  
  &:hover {
    background-color: var(--color-primary-dark);
    color: white;
  }
`;

const SecondaryButton = styled(Button)`
  background-color: transparent;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  
  &:hover {
    background-color: var(--color-primary-light);
    color: white;
  }
`;

const HeroImage = styled.div`
  flex: 1;
  max-width: 500px;
  
  img {
    width: 100%;
    height: auto;
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-lg);
  }
`;

const FeaturesSection = styled.section`
  margin-bottom: var(--spacing-xxl);
  width: 100%;
`;

const SectionTitle = styled.h2`
  text-align: center;
  margin-bottom: var(--spacing-xl);
  font-size: var(--font-size-xxl);
  color: var(--color-text);
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
  
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (min-width: 992px) {
    grid-template-columns: repeat(3, 1fr);
  }
`;

const FeatureCard = styled.div`
  background-color: var(--color-surface);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-md);
  }
`;

const FeatureIcon = styled.div`
  width: 50px;
  height: 50px;
  margin-bottom: var(--spacing-md);
  color: var(--color-primary);
  
  svg {
    width: 100%;
    height: 100%;
  }
`;

const FeatureTitle = styled.h3`
  margin-bottom: var(--spacing-sm);
  color: var(--color-text);
`;

const FeatureDescription = styled.p`
  color: var(--color-text-light);
`;

/**
 * HomePage component
 * 
 * Landing page for the Kids Book Generator application
 */
const HomePage: React.FC = () => {
  return (
    <HomeContainer>
      <Hero>
        <HeroContent>
          <HeroTitle>Create Amazing Children's Books with AI</HeroTitle>
          <HeroSubtitle>
            Generate custom illustrated storybooks and coloring books for children with our AI-powered platform.
            Ready for Amazon KDP publishing.
          </HeroSubtitle>
          <ButtonGroup>
            <PrimaryButton to="/register">Get Started</PrimaryButton>
            <SecondaryButton to="/login">Sign In</SecondaryButton>
          </ButtonGroup>
        </HeroContent>
        <HeroImage>
          {/* Placeholder for hero image */}
          <img src="https://placehold.co/600x400/4361ee/ffffff?text=Kids+Book+Generator" alt="Kids Book Generator" />
        </HeroImage>
      </Hero>
      
      <FeaturesSection>
        <SectionTitle>Features</SectionTitle>
        <FeatureGrid>
          <FeatureCard>
            <FeatureIcon>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </FeatureIcon>
            <FeatureTitle>AI Story Generation</FeatureTitle>
            <FeatureDescription>
              Create custom stories with GPT-4 tailored to specific themes, characters, and age groups.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </FeatureIcon>
            <FeatureTitle>AI Illustrations</FeatureTitle>
            <FeatureDescription>
              Generate beautiful, consistent illustrations with DALL-E 3 to bring your stories to life.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </FeatureIcon>
            <FeatureTitle>KDP-Ready Formatting</FeatureTitle>
            <FeatureDescription>
              Automatically format your books according to Amazon KDP specifications for easy publishing.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </FeatureIcon>
            <FeatureTitle>Coloring Books</FeatureTitle>
            <FeatureDescription>
              Create custom coloring books with line art illustrations perfect for young artists.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </FeatureIcon>
            <FeatureTitle>Batch Processing</FeatureTitle>
            <FeatureDescription>
              Create multiple books at once with batch processing, perfect for series or collections.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </FeatureIcon>
            <FeatureTitle>Multiple Templates</FeatureTitle>
            <FeatureDescription>
              Choose from a variety of templates for different book types, age groups, and styles.
            </FeatureDescription>
          </FeatureCard>
        </FeatureGrid>
      </FeaturesSection>
    </HomeContainer>
  );
};

export default HomePage;
