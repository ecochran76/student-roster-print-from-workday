import fitz
import re
import os
from PIL import Image

def extract_student_info_and_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)

    email_pattern = re.compile(r'\b[\w.-]+@iastate\.edu\b')
    name_pattern = re.compile(r"([A-Za-z ,.'\-]+) \(\d{9}\)")

    student_data = []

    for page_num, page in enumerate(doc, start=1):
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

# LaTeX Generation with dynamic aspect ratio calculation
def generate_latex(student_data, output_tex, sort_by_lastname=False, n_pages=1):
    if sort_by_lastname:
        student_data.sort(key=lambda x: x['name'].split()[-1])
    else:
        student_data.sort(key=lambda x: x['name'].split()[0])

    # Calculate average aspect ratio
    aspect_ratios = []
    for student in student_data:
        with Image.open(student['image']) as img:
            width, height = img.size
            aspect_ratios.append(width / height)

    avg_aspect_ratio = sum(aspect_ratios) / len(aspect_ratios)

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

        students_per_page = len(student_data) // n_pages + (len(student_data) % n_pages > 0)

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

# Example usage
pdf_files = [
    r'e:\\Syncthing\\Downloads\\CHE_5470-1_-_Polymers_and_Polymer_Engineering.pdf',
    r'e:\\Syncthing\\Downloads\\CHE_4470-1_-_Polymers_and_Polymer_Engineering.pdf'
]

all_students = []
for pdf_file in pdf_files:
    all_students.extend(extract_student_info_and_images(pdf_file, 'extracted_students'))

generate_latex(all_students, 'student_roster.tex', sort_by_lastname=False, n_pages=1)