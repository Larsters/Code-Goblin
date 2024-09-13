import openai
import requests

# Function to call OpenAI API and get style suggestions
def analyze_code_with_chatgpt(code_snippet):
    prompt = f"Review the following Java code for style and suggest improvements:\n\n{code_snippet}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Java code reviewer."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content']

# TODO: make it work 
# Example usage:
def fetch_code_from_pr(pr_diff_url):
    # Fetch diff or raw Java code from the pull request
    diff_response = requests.get(pr_diff_url)  
    if diff_response.status_code == 200:
        return diff_response.text
    else:
        raise Exception("Unable to fetch the pull request diff.")

# Simulating review process
pr_diff_url = "https://github.com/user/repo/pull/1.diff"  # Example URL
java_code_diff = fetch_code_from_pr(pr_diff_url)
review_suggestions = analyze_code_with_chatgpt(java_code_diff)

print("Review Suggestions:\n", review_suggestions)
