import subprocess

def run_checkstyle(java_file, checkstyle_jar, config_file):
    cmd = [
        'java', '-jar', checkstyle_jar,
        '-c', config_file,
        java_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout


if __name__ == "__main__":
    java_file = 'Sample.java'
    checkstyle_jar = 'checkstyle-10.18.1-all.jar'
    config_file = 'google_checks.xml'
    
    output = run_checkstyle(java_file, checkstyle_jar, config_file)
    print("Checkstyle Output:\n", output)
