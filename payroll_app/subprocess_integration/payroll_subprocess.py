import subprocess
import json

def call_java_payroll_service(employee_data):
    # Prepare the command to run the Java program
    command = [
        'java', 
        '-cp', 'path_to_your_classes', 
        'service', 
        str(employee_data.id),  # Pass employee data
        str(employee_data.total_hours)  # Other parameters
    ]
    
    # Run the Java process and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Check for errors
    if result.returncode == 0:
        # Assuming Java outputs JSON, parse it
        payroll_result = json.loads(result.stdout)
        return payroll_result
    else:
        print(f"Error calling Java: {result.stderr}")
        return None
