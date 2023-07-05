import re

def extract_styles_from_doc(doc):
    # Remove leading/trailing whitespaces and split the document by newline
    lines = doc.strip().split('\n')
    
    # Filter out empty lines and extract styles
    styles = [line for line in lines if line.strip()]

    return styles

# Open txt file
with open("styles.txt", "r") as f:
    # Read the file contents
    file_contents = f.read()

# Extract styles from the document
styles_list = extract_styles_from_doc(file_contents)

print(styles_list)