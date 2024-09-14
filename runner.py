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

# AI Code Review Function
def ai_code_review(code_snippet):
    prompt = f"""Review the following Java code for style issues and suggest improvements:

```java
{code_snippet}
```"""
    response = client.chat.completions.create(
        model='gpt-4o-mini', 
        messages=[
            {'role': 'system', 'content': 'You are a senior Java developer and code reviewer.'},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=500,
        temperature=0.2,
    )
    response_dict = response.to_dict()
    return response_dict['choices'][0]['message']['content']

# for parsing the checkstyle output, xml for the checkstyle output 
def parse_checkstyle_output(xml_output):
    root = ET.fromstring(xml_output)
    violations = []
    for file in root.findall('file'):
        filename = file.get('name')
        for error in file.findall('error'):
            message = error.get('message')
            line = error.get('line')
            column = error.get('column')
            severity = error.get('severity')
            violations.append(f"{filename} - Line {line}, Column {column}, Severity: {severity}: {message}")
    return '\n'.join(violations)

def format_combined_output(checkstyle_output, ai_review_output, java_file):
    # Header for combined output
    combined_output = "=== Combined Code Review ===\n\n"

    # Format Checkstyle output
    combined_output += "=== Checkstyle Results ===\n"
    if not checkstyle_output:
        combined_output += "No Checkstyle violations found.\n"
    else:
        combined_output += f"File: {java_file}\nViolations:\n"
        combined_output += checkstyle_output

    # Format AI Review output
    combined_output += "\n\n=== AI Review Suggestions ===\n"
    combined_output += "Summary of Issues:\n"
    combined_output += ai_review_output

    return combined_output

def main():
    java_file = 'Sample.java'
    checkstyle_jar = 'checkstyle-10.18.1-all.jar'
    config_file = 'google_checks.xml'
    
    # Run Checkstyle
    print("Running Checkstyle...")
    checkstyle_output = run_checkstyle(java_file, checkstyle_jar, config_file)
    parsed_checkstyle_output = parse_checkstyle_output(checkstyle_output)
    
    # Read Java code for AI code review
    with open(java_file, 'r') as file:
        java_code = file.read()

    # Run AI Code Review
    print("Running AI Code Review...")
    ai_review_output = ai_code_review(java_code)

    # Formatting and displaying results of Checkstyle and AI Code Review
    formatted_output = format_combined_output(parsed_checkstyle_output, ai_review_output, java_file)
    print(formatted_output)

if __name__ == "__main__":
    main()