# Student Roster Generator

This Python script extracts student data (names, emails, and photos) from PDF files and generates a photo roster in PDF format using LaTeX. It's designed to process PDFs containing student information, such as those exported from systems like Workday, and create a formatted grid of student photos with clickable email links.

## Features
- Extracts student names, emails, and photos from PDF files
- Generates a LaTeX document with a grid layout of student photos
- Supports sorting by first name or last name
- Flexible page layout with options for number of pages or maximum photos per page
- Automatic LaTeX compilation (requires pdflatex or lualatex)
- Temporary file handling with optional permanent storage
- Customizable output filename

## Prerequisites
- Python 3.6+
- Required Python packages:
  - `PyMuPDF` (`fitz`) - for PDF processing
  - `Pillow` (`PIL`) - for image handling
- A LaTeX distribution (e.g., TeX Live or MiKTeX) with `pdflatex` or `lualatex` in one of these locations:
  - In PATH
  - TeX Live: `C:\texlive\[2022-2024]\bin\windows` or `C:\texlive\bin\win32`
  - MiKTeX: `C:\miktex\bin`

Install Python dependencies:
```bash
pip install PyMuPDF Pillow
```

## Installation
1. Clone or download this repository
2. Ensure you have the prerequisites installed
3. Make the script executable (optional):
   ```bash
   chmod +x student-roster-print-from-workday.py
   ```

## Usage
Run the script from the command line with one or more PDF files as input:

```bash
python student-roster-print-from-workday.py [PDF_FILES] [OPTIONS]
```

### Arguments
- `pdf_files`: One or more input PDF files (required)

### Options
- `--n_pages N`: Number of pages for output (default: 1)
- `--max-per-page N`: Maximum photos per page (overrides `--n_pages`)
- `--sort-lastname`: Sort by last name instead of first name
- `--save-files`: Save output files in current directory instead of temporary folder
- `-o, --output FILE`: Output PDF filename (default: `./student_roster.pdf`)
- `-h, --help`: Show help message

### Examples
Basic usage with one PDF:
```bash
python student-roster-print-from-workday.py input.pdf
```

Process multiple PDFs with 6 photos per page:
```bash
python student-roster-print-from-workday.py file1.pdf file2.pdf --max-per-page 6
```

Sort by last name, 2 pages, custom output:
```bash
python student-roster-print-from-workday.py input.pdf --n_pages 2 --sort-lastname --output roster.pdf
```

Save files permanently:
```bash
python student-roster-print-from-workday.py input.pdf --save-files
```

## Output
- Generates a PDF roster at the specified output location (default: `./student_roster.pdf`)
- Each student's photo is displayed with their name below it
- Names are hyperlinks to email addresses
- Images are automatically sized based on the number of students and page constraints

## How It Works
1. **Extraction**: Parses PDF files for student names, emails, and photos
   - Names: Matches patterns like "John Doe (123456789)"
   - Emails: Matches any valid email address (e.g., `user@domain.com`)
   - Photos: Extracts embedded images
2. **Processing**: Sorts students and calculates layout based on options
3. **Generation**: Creates a LaTeX document with a TikZ-based grid
4. **Compilation**: Uses `pdflatex` or `lualatex` to compile to PDF

## Troubleshooting
- **No LaTeX compiler found**: Ensure `pdflatex` or `lualatex` is in your PATH or in a supported location:
  - TeX Live: `C:\texlive\[2022-2024]\bin\windows` or `C:\texlive\bin\win32`
  - MiKTeX: `C:\miktex\bin`
- **PDF compilation errors**: Check the `.log` file in the output directory (or temp directory if `--save-files` isn't used)
- **No student data extracted**: Verify the PDF contains the expected format of names, emails, and images

## Limitations
- Assumes specific name formatting with a 9-digit ID in parentheses
- Requires images to be embedded in the PDF
- LaTeX compilation requires an installed TeX distribution

## License
This project is released under the MIT License. See LICENSE file for details.

## Contributing
Feel free to submit issues or pull requests with improvements or bug fixes!
