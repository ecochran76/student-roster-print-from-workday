#!/usr/bin/env python3
# ./student-roster-print-from-workday.py
import fitz
import re
import os
import sys
import argparse
import subprocess
import shutil
import tempfile
from PIL import Image
from pathlib import Path
import math

def extract_student_info_and_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    email_pattern = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
    name_pattern = re.compile(r"([A-Za-z ,.'\-]+) \(\d{9}\)")

    student_data = []
    for page in doc:
        text = page.get_text()
        names = name_pattern.findall(text)
        emails = email_pattern.findall(text)
        images = page.get_images(full=True)

        for idx, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            if idx < len(names) and idx < len(emails):
                image_name = f"{names[idx].strip().replace(' ', '_')}.{image_ext}"
                image_path = os.path.join(output_folder, image_name)

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                student_data.append({
                    'name': names[idx].strip(),
                    'email': emails[idx],
                    'image': image_path.replace('\\', '/')  # for LaTeX compatibility
                })

                print(f"Extracted: Name: {names[idx].strip()}, Email: {emails[idx]}, Image: {image_name}")

    return student_data

def generate_latex(student_data, output_tex, sort_by_lastname=False, n_pages=1, max_per_page=None):
    if sort_by_lastname:
        student_data.sort(key=lambda x: x['name'].split()[-1])
    else:
        student_data.sort(key=lambda x: x['name'].split()[0])

    aspect_ratios = [Image.open(student['image']).size[0] / Image.open(student['image']).size[1] 
                    for student in student_data]
    avg_aspect_ratio = sum(aspect_ratios) / len(aspect_ratios)

    if max_per_page:
        n_pages = math.ceil(len(student_data) / max_per_page)
        students_per_page = max_per_page
    else:
        students_per_page = len(student_data) // n_pages + (len(student_data) % n_pages > 0)

    with open(output_tex, 'w') as tex_file:
        tex_file.write(r"""\documentclass[letterpaper]{article}
\usepackage[margin=1cm]{geometry}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{positioning}
\usepackage[colorlinks,urlcolor=blue!25!black]{hyperref}
\pagestyle{empty}
\begin{document}
""")

        for i in range(n_pages):
            tex_file.write("\n\\centerline{\n\\begin{tikzpicture}[node distance=1ex and 1ex]")
            page_students = student_data[i*students_per_page:(i+1)*students_per_page]
            num_students = len(page_students)

            cols = round((avg_aspect_ratio * num_students)**0.5)
            rows = (num_students + cols - 1) // cols

            img_width = (20 - (cols - 1) * 0.2) / cols * 0.95
            img_height = (25 - (rows - 1) * 1.5) / rows

            for idx, student in enumerate(page_students):
                row, col = divmod(idx, cols)
                tex_file.write(
                    f"\n\\node[anchor=north west] (img{idx}) at ({col * (img_width + 0.2)}, {-row * (img_height + 1.5)})"
                    f" {{\\includegraphics[width={img_width}cm,height={img_height}cm,keepaspectratio]{{{student['image']}}}}};"
                    f"\n\\node[below=0.1cm of img{idx}] {{\\href{{mailto:{student['email']}}}{{{student['name']}}}}};"
                )

            tex_file.write("\n\\end{tikzpicture}\n}")

        tex_file.write("\n\\end{document}")

def compile_latex(tex_path, output_pdf):
    tex_dir = os.path.dirname(tex_path)
    tex_base = os.path.splitext(os.path.basename(tex_path))[0]
    
    compilers = ['lualatex', 'pdflatex']
    compiler_path = None
    
    # Check PATH first
    for compiler in compilers:
        compiler_path = shutil.which(compiler)
        if compiler_path:
            break
    
    # Check common TeX Live and MiKTeX locations if not in PATH
    if not compiler_path:
        texlive_paths = [
            r"C:\texlive\2024\bin\windows\pdflatex.exe",
            r"C:\texlive\2023\bin\windows\pdflatex.exe",
            r"C:\texlive\2022\bin\win32\pdflatex.exe",
            r"C:\texlive\bin\win32\pdflatex.exe"  # Older generic path
        ]
        miktex_path = r"C:\miktex\bin\pdflatex.exe"
        
        for path in texlive_paths + [miktex_path]:
            if os.path.exists(path):
                compiler_path = path
                break
    
    if not compiler_path:
        print("Error: No LaTeX compiler found in PATH or standard locations (TeX Live: C:\\texlive\\[2022-2024]\\bin\\windows or C:\\texlive\\bin\\win32, MiKTeX: C:\\miktex\\bin)")
        return False

    try:
        result = subprocess.run(
            [compiler_path, tex_base],
            cwd=tex_dir,
            capture_output=True,
            text=True,
            check=True
        )
        shutil.move(os.path.join(tex_dir, f"{tex_base}.pdf"), output_pdf)
        for ext in ['.aux', '.log']:
            try:
                os.remove(os.path.join(tex_dir, f"{tex_base}{ext}"))
            except OSError:
                pass
        return True
    except subprocess.CalledProcessError as e:
        log_file = os.path.join(tex_dir, f"{tex_base}.log")
        print(f"Error compiling LaTeX: See log file at {log_file}")
        print(f"Compiler output: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate student roster from PDF files")
    parser.add_argument("pdf_files", nargs="+", help="Input PDF files")
    parser.add_argument("--n_pages", type=int, default=1, help="Number of pages for output")
    parser.add_argument("--max-per-page", type=int, help="Maximum photos per page (overrides n_pages)")
    parser.add_argument("--sort-lastname", action="store_true", help="Sort by last name instead of first name")
    parser.add_argument("--save-files", action="store_true", help="Save output files in current directory instead of temp")
    parser.add_argument("-o", "--output", default="./student_roster.pdf", help="Output PDF filename")

    args = parser.parse_args()

    if not args.pdf_files:
        parser.print_help()
        sys.exit(1)

    if args.max_per_page and args.max_per_page <= 0:
        print("Error: --max-per-page must be a positive integer")
        sys.exit(1)

    if args.save_files:
        output_dir = "extracted_students"
        tex_path = "student_roster.tex"
    else:
        temp_dir = tempfile.TemporaryDirectory()
        output_dir = os.path.join(temp_dir.name, "extracted_students")
        tex_path = os.path.join(temp_dir.name, "student_roster.tex")

    all_students = []
    for pdf_file in args.pdf_files:
        if not os.path.exists(pdf_file):
            print(f"Error: File not found: {pdf_file}")
            sys.exit(1)
        all_students.extend(extract_student_info_and_images(pdf_file, output_dir))

    if not all_students:
        print("Error: No student data extracted from PDFs")
        sys.exit(1)

    generate_latex(all_students, tex_path, 
                  sort_by_lastname=args.sort_lastname, 
                  n_pages=args.n_pages,
                  max_per_page=args.max_per_page)
    success = compile_latex(tex_path, args.output)

    if success:
        print(f"Successfully generated roster at: {args.output}")
        if args.max_per_page:
            n_pages = math.ceil(len(all_students) / args.max_per_page)
            print(f"Generated {n_pages} pages with up to {args.max_per_page} students per page")
        else:
            print(f"Generated {args.n_pages} pages")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
