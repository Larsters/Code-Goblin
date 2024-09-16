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
    prompt = f"""Review the following Java code for style issues and suggest improvements if necessary, otherwise do nothing.:

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
    return response.choices[0].message.content

def parse_checkstyle_output(xml_output):
    if not xml_output.strip():
        print("No Checkstyle output to parse.")
        return "No Checkstyle violations found."
    
    # if xml if malformed, catch the exception
    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return f"Error parsing Checkstyle output: {e}"
    # for cases xml output is not in the expected format for some reason
    violations = []
    for file in root.findall('file'):
        filename = file.get('name')
        for error in file.findall('error'):
            message = error.get('message')
            line = error.get('line')
            column = error.get('column')
            severity = error.get('severity')
            violations.append(f"{filename} - Line {line}, Column {column}, Severity: {severity}: {message}")
    
    return '\n'.join(violations) if violations else "No Checkstyle violations found."

def format_combined_output(checkstyle_output, ai_review_output, java_file):
    combined_output = "=== Combined Code Review ===\n\n"
    combined_output += "=== Checkstyle Results ===\n"
    combined_output += f"File: {java_file}\n"
    combined_output += checkstyle_output
    combined_output += "\n\n=== AI Review Suggestions ===\n"
    combined_output += ai_review_output
    return combined_output

def main():
    java_file = 'sample.java'
    checkstyle_jar = 'checkstyle-10.18.1-all.jar'
    config_file = 'google_checks.xml'
    
    # Ensure files exist
    for file in [java_file, checkstyle_jar, config_file]:
        if not os.path.exists(file):
            print(f"Error: {file} not found in the current directory.")
            return

    print("Running Checkstyle...")
    checkstyle_output = run_checkstyle(java_file, checkstyle_jar, config_file)
    parsed_checkstyle_output = parse_checkstyle_output(checkstyle_output)
    
    print("Running AI Code Review...")
    with open(java_file, 'r') as file:
        java_code = file.read()
    ai_review_output = ai_code_review(java_code)
    
    formatted_output = format_combined_output(parsed_checkstyle_output, ai_review_output, java_file)
    print(formatted_output)

if __name__ == "__main__":
    main()