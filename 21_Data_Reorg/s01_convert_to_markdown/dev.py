
# Standardize Document Formats: Convert diverse file types (Pdf, Word, PowerPoint, Excel)
#   into a uniform format—preferably PDF or Markdown—before extraction.
#   This simplifies downstream parsing and prevents "brittle" custom code.

from markitdown import MarkItDown

def standardize_to_markdown(file_path):
    """
    Converts diverse file types (Word, PPT, Excel, PDF)
    into a uniform Markdown string.
    """
    md = MarkItDown()
    try:
        # The .convert() method handles the complexity of different
        # file types automatically, returning a standardized result.
        result = md.convert(file_path)
        return result.text_content
    except Exception as e:
        print(f"Error converting {file_path}: {e}")
        return None

# Example usage for a multi-format dataset
base_path = "..\\data\\stock_market\\"
files_to_process = ["Infosys_Q3_FY26_Full_Dataset.xlsx",
                   "Infosys_Q3_FY26_Investor_Presentation.pptx",
                   "Infosys_Q3_FY26_Management_Report.docx",
                   "Report1.pdf"]

for one_file in files_to_process:
    markdown_content = standardize_to_markdown(base_path + one_file)
    if markdown_content:
        print(f"\n\n\n\n\n\n\n--- Standardized Content for {one_file} ---")
        # print(markdown_content[:200] + "...")
        print(markdown_content)
        md_file_path = base_path + one_file.replace(".", "_") + ".md"
        with open(md_file_path, "w", encoding="utf-8") as markdown_file:
            markdown_file.write(markdown_content)

