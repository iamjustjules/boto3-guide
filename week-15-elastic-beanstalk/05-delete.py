import boto3
import json

# Load environment details from JSON
try:
    with open('beanstalk_env.json', 'r') as f:
        data = json.load(f)
        environment_name = data.get('EnvironmentName')
        application_name = data.get('ApplicationName')
except FileNotFoundError:
    print("File 'beanstalk_env.json' not found.")
    exit()

# Initialize the Elastic Beanstalk client
eb = boto3.client('elasticbeanstalk')

# Step 1: Terminate the environment if it exists
try:
    response = eb.describe_environments(ApplicationName=application_name)
    environments = {env['EnvironmentName']: env['EnvironmentId'] for env in response['Environments']}
    
    if environment_name in environments:
        response = eb.terminate_environment(EnvironmentName=environment_name)
        print(f"Environment '{environment_name}' terminated.")
    else:
        print(f"No environment found with the name '{environment_name}'.")

except Exception as e:
    print(f"Error terminating the environment: {e}")

# Step 2: Delete the application if no environments remain
try:
    remaining_environments = eb.describe_environments(ApplicationName=application_name)['Environments']
    if not remaining_environments:
        eb.delete_application(ApplicationName=application_name, TerminateEnvByForce=True)
        print(f"Application '{application_name}' deleted.")
        data.pop('ApplicationName', None)  # Remove app data if deleted
except Exception as e:
    print(f"Error deleting the application: {e}")

# Step 3: Update the JSON file
with open('beanstalk_env.json', 'w') as f:
    json.dump(data, f)
    print("Updated 'beanstalk_env.json' to reflect deleted resources.")
