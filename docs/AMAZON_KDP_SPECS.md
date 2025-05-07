# Amazon KDP Specifications Guide

## Overview

This document outlines the specific requirements for publishing children's books and coloring books on Amazon KDP.

## Book Types

### 1. Children's Story Books
- **Recommended Color**: Premium color
- **Paper Type**: White paper (best for color images)
- **Typical Page Count**: 24-32 pages

### 2. Coloring Books
- **Recommended Color**: Standard color or Black & White
- **Paper Type**: White paper
- **Typical Page Count**: 50-100 pages

## Technical Specifications

### Trim Sizes (Width x Height)

#### Standard Sizes for Children's Books:
- **8.5" x 8.5"** (Square format) - Popular for picture books
- **8.5" x 11"** (Letter format) - Standard coloring book size
- **6" x 9"** - Common for chapter books
- **8" x 10"** - Alternative picture book size

#### Page Count Requirements:
- **Minimum**: 24 pages
- **Maximum**: 
  - Black ink on white paper: 828 pages
  - Color ink: 480 pages
  - Large format (> 6.12" width or > 9" height): 600 pages

### Print Requirements

#### Resolution:
- **Minimum**: 300 DPI for all images
- **Recommended**: 300-600 DPI for best quality

#### Bleed Settings:
- **Required bleed**: 0.125" (3.2 mm) on all sides
- **Safe zone**: Keep important content 0.25" (6.4 mm) from edges

#### Color Specifications:
- **Color Space**: RGB for digital files
- **Color Profile**: sRGB IEC61966-2.1
- **Black Text**: Use 100% K for text (in CMYK)

### File Formats

#### Interior:
- **Format**: PDF
- **Fonts**: All fonts must be embedded
- **Layers**: Flatten all layers
- **Transparency**: Flatten transparent objects

#### Cover:
- **Format**: PDF
- **Include**: Front cover, back cover, and spine
- **Spine Text**: Only for books with 79+ pages

### Cover Specifications

#### Dimensions Formula:
```
Cover Width = Bleed + Back Cover Width + Spine Width + Front Cover Width + Bleed
Cover Height = Bleed + Trim Height + Bleed

Where:
- Bleed = 0.125"
- Spine Width = Page Count × Paper Thickness
```

#### Paper Thickness:
- **White pages**: 0.0025" per page
- **Cream pages**: 0.0025" per page

#### Barcode:
- **Size**: 2" x 1.2"
- **Position**: Lower right of back cover
- **Margin**: 0.25" from edges

### Content Guidelines

#### Text Requirements:
- **Minimum font size**: 7 pt
- **Recommended font size**: 12-16 pt for children's books
- **Line height**: 1.2-1.5x font size

#### Image Requirements:
- **File types**: JPEG, PNG, TIFF
- **Compression**: High quality (low compression)
- **Color mode**: RGB

#### Margin Requirements:

| Page Count | Inside Margin | Outside Margin |
|------------|---------------|----------------|
| 24-150     | 0.375"        | 0.25"          |
| 151-300    | 0.5"          | 0.25"          |
| 301-500    | 0.625"        | 0.25"          |
| 501+       | 0.75"         | 0.25"          |

### AI Content Disclosure

Amazon requires disclosure of AI-generated content:
- **Text**: Must disclose if AI-generated
- **Images**: Must disclose if AI-generated
- **Translations**: Must disclose if AI-generated

## Book Categories

### Children's Book Categories:
- Children's Books > Ages 3-5
- Children's Books > Ages 6-8
- Children's Books > Ages 9-12
- Children's Books > Animals
- Children's Books > Education & Reference
- Children's Books > Literature & Fiction

### Coloring Book Categories:
- Children's Books > Activities, Crafts & Games > Activity Books
- Coloring Books for Kids
- Educational Coloring Books
- Seasonal & Holiday Coloring Books

## Pricing Guidelines

### Print Cost Calculation:
```
Printing Cost = Fixed Cost + (Page Count × Per Page Cost)

Black & White:
- Fixed Cost: $2.15
- Per Page Cost: $0.012

Standard Color:
- Fixed Cost: $3.65
- Per Page Cost: $0.042

Premium Color:
- Fixed Cost: $3.65
- Per Page Cost: $0.06
```

### Suggested Retail Prices:
- **Picture Books**: $9.99 - $14.99
- **Coloring Books**: $6.99 - $9.99
- **Chapter Books**: $7.99 - $12.99

## Quality Checklist

### Pre-submission Checklist:
- [ ] All images are 300 DPI or higher
- [ ] Fonts are embedded in PDF
- [ ] Bleed is exactly 0.125" on all sides
- [ ] No content in the bleed area
- [ ] Page count meets minimum requirement
- [ ] Cover includes spine (if applicable)
- [ ] Barcode space is reserved on back cover
- [ ] All text is readable and properly sized
- [ ] Colors are in RGB color space
- [ ] PDF is optimized and under 650MB
- [ ] AI content is properly disclosed

### Common Rejection Reasons:
1. Low resolution images (< 300 DPI)
2. Missing bleed
3. Content in bleed area
4. Fonts not embedded
5. Incorrect trim size
6. Poor image quality
7. Text too close to edges
8. Missing or incorrect spine

## Best Practices

### For Story Books:
1. Use premium color for best quality
2. Include full-page illustrations
3. Keep text large and readable
4. Use high contrast for readability
5. Consider double-page spreads carefully

### For Coloring Books:
1. Use thick, clear outlines
2. Leave white space for coloring
3. Avoid fine details that are hard to color
4. Include variety in complexity
5. Consider single-sided printing

### General Tips:
1. Always order a proof copy
2. Test print on home printer first
3. View PDF at 100% zoom
4. Check all pages thoroughly
5. Consider professional editing

## File Naming Convention

Recommended naming structure:
```
Title_Type_Version_Date.pdf

Examples:
- MagicalForest_Interior_v1_2024-01-15.pdf
- MagicalForest_Cover_v1_2024-01-15.pdf
```

## Resources

- [KDP Print Specifications](https://kdp.amazon.com/en_US/help/topic/G201834180)
- [Cover Calculator](https://kdp.amazon.com/en_US/cover-calculator)
- [Paperback Submission Guidelines](https://kdp.amazon.com/en_US/help/topic/G201834180)
- [Content Guidelines](https://kdp.amazon.com/en_US/help/topic/G200672390)
