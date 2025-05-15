import subprocess
import json
import os

def call_java_payroll_service(employee_data):
    try:
        # Get the current directory where your Python script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Build the classpath - assuming your Java class is in the same directory or a subdirectory
        java_classpath = current_dir
        
        # Prepare the command to run the Java program
        command = [
            'java', 
            '-cp', java_classpath, 
            '../../calculate/service',  # Replace with the actual class name (without .java extension)
            str(employee_data.id),
            str(employee_data.total_hours)
        ]
        
        # Run the Java process with a timeout to prevent hanging
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        
        # Check for errors
        if result.returncode == 0:
            try:
                # Assuming Java outputs JSON, parse it
                payroll_result = json.loads(result.stdout)
                return payroll_result
            except json.JSONDecodeError:
                print(f"Failed to parse JSON output: {result.stdout}")
                return None
        else:
            print(f"Error calling Java: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("Java process timed out")
        return None
    except Exception as e:
        print(f"Error in call_java_payroll_service: {str(e)}")
        return None