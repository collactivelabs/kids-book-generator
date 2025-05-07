# Children's Book and Coloring Book Generator for Amazon KDP

An AI-powered agent that automatically generates children's story books and coloring books for publication on Amazon KDP (Kindle Direct Publishing).

## Overview

This project creates an automated system that:
- Generates children's stories with accompanying illustrations
- Creates coloring book pages
- Formats books according to Amazon KDP specifications
- Prepares files for direct upload to Amazon KDP

## Technologies Used

- **Canva Connect API**: For professional book layout and design
- **OpenAI DALL-E 3 API**: For generating high-quality illustrations
- **OpenAI GPT-4 API**: For generating story content
- **Python**: Primary programming language
- **FastAPI**: For building the agent's web interface

## Features

- Automated story generation with age-appropriate content
- High-quality AI-generated illustrations
- Coloring page generation with proper specifications
- Amazon KDP-compliant formatting
- Multiple book format support (story books and coloring books)
- Batch processing for creating multiple books
- Content moderation and safety checks

## Amazon KDP Requirements Met

- **Trim Sizes**: 8.5" x 11" (standard) and 8.5" x 8.5" (square)
- **Color Options**: Premium color for story books, standard color for coloring books
- **Page Count**: Minimum 24 pages maintained
- **Bleed Settings**: 0.125" (3.2 mm) on all sides
- **File Format**: PDF with embedded fonts
- **Resolution**: 300 DPI for all images
- **Cover Requirements**: Spine calculations and full wraparound cover

## Project Structure

```
kids-book-generator/
├── docs/                    # Documentation
├── src/                     # Source code
│   ├── api/                # API endpoints
│   ├── generators/         # Content generation modules
│   ├── formatters/         # Book formatting modules
│   └── utils/              # Utility functions
├── templates/              # Book templates
├── output/                 # Generated books
└── tests/                  # Test files
```

## Getting Started

### Requirements

- Python 3.11 or 3.12 (Python 3.13 not fully supported yet)
- PostgreSQL (for database)
- Redis (for caching)

### Installation

1. Clone the repository
2. Set up Python environment:
   ```bash
   # Using pyenv (recommended)
   pyenv install 3.11.7
   pyenv local 3.11.7
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Set up API keys in `.env` file
5. Run the application: `python main.py`

**Note**: If you encounter installation errors, refer to `docs/installation-guide.md` for troubleshooting.

## License

MIT License

## Contributing

See CONTRIBUTING.md for guidelines
# kids-book-generator
