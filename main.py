import subprocess
from openai import OpenAI
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def run_checkstyle(java_file, checkstyle_jar, config_file):
    cmd = [
        'java', '-jar', checkstyle_jar,
        '-c', config_file,
        '-f', 'xml',
        java_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def ai_code_review(code_snippet):
    prompt = f"""Review the following Java code for style issues and suggest improvements.
The code is written by students, so please preserve the original language of the code (either Russian or English). Do not translate or change the language of the code itself, just provide improvements and feedback in Russian:

```java
{code_snippet}
```"""
    response = client.chat.completions.create(
        model='gpt-4',  
        messages=[
            {'role': 'system', 'content': 'You are a senior Java developer and code reviewer.'},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=500,
        temperature=0.2,
    )
    return response.choices[0].message.content

# Parsing Checkstyle XML output
def parse_checkstyle_output(xml_output):
    if not xml_output.strip():
        return "No Checkstyle violations found."
    # violations just in case the XML is not well-formed
    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError as e:
        return f"Error parsing Checkstyle output: {e}"

    violations = []
    for file in root.findall('file'):
        for error in file.findall('error'):
            message = error.get('message')
            line = error.get('line')
            column = error.get('column')
            severity = error.get('severity')
            violations.append(f"Line {line}, Column {column}: {message}")
    
    return '\n'.join(violations) if violations else "No Checkstyle violations found."

# Combined review using LLM
def generate_combined_review(checkstyle_output, ai_review_output):
    prompt = f"""The following two reviews were generated: one from Checkstyle and one from an AI review of the code. Summarize them into one concise review in Russian, but preserve the original language of the code, and do not change or translate the code:

Checkstyle Output:
{checkstyle_output}

AI Review Output:
{ai_review_output}

Return a concise and useful review in Russian.
"""
    response = client.chat.completions.create(
        model='gpt-4',  
        messages=[
            {'role': 'system', 'content': 'You are a senior Java developer and code reviewer.'},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=500,
        temperature=0.2,
    )
    return response.choices[0].message.content

def main():
    java_file = 'sample.java'
    checkstyle_jar = 'checkstyle-10.18.1-all.jar'
    config_file = 'google_checks.xml'
    
    # Ensure files exist
    for file in [java_file, checkstyle_jar, config_file]:
        if not os.path.exists(file):
            print(f"Error: {file} not found in the current directory.")
            return

    # Run Checkstyle
    print("Running Checkstyle...")
    checkstyle_output = run_checkstyle(java_file, checkstyle_jar, config_file)
    parsed_checkstyle_output = parse_checkstyle_output(checkstyle_output)
    
    # Run AI Code Review
    print("Running AI Code Review...")
    with open(java_file, 'r') as file:
        java_code = file.read()
    ai_review_output = ai_code_review(java_code)
    
    # Generate and display the combined review
    print("Generating combined review...")
    combined_review = generate_combined_review(parsed_checkstyle_output, ai_review_output)
    print(combined_review)

if __name__ == "__main__":
    main()
