# Student Roster Generator

This Python script extracts student information (names, emails, and images) from course rosters in PDF format and generates a visually appealing LaTeX roster document using dynamic layout calculations based on the average aspect ratio of student images.

## Requirements
- Python 3.x
- PyMuPDF (fitz)
- Pillow (PIL)

Install required Python packages using:

```bash
pip install PyMuPDF Pillow
```

## File Structure
```
.
├── student_roster.py
├── extracted_students/
│   └── (student images will be saved here)
└── student_roster.tex
```

## Usage
Run the Python script to process your PDFs and generate the LaTeX document:
```bash
python student_roster.py
```

Compile the generated LaTeX file (`student_roster.tex`) using your preferred LaTeX editor or command line:
```bash
pdflatex student_roster.tex
```

## Configuration
- Adjust the paths to your PDF files in the script.
- Toggle sorting by first or last name (`sort_by_lastname` boolean).
- Adjust the number of pages (`n_pages`) as needed.

## Customization
You can modify:
- Margins and spacing by editing the `geometry` settings in the LaTeX preamble.
- Image sizing logic within the Python script.
- Sorting options by adjusting the boolean `sort_by_lastname`.

## Output
- A neatly formatted PDF roster including clickable email hyperlinks below each student's photo.