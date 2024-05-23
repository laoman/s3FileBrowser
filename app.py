from flask import Flask, render_template
import boto3
import os

app = Flask(__name__)


endpoint_url = "http://localhost.localstack.cloud:4566"
# alternatively, to use HTTPS endpoint on port 443:
# endpoint_url = "https://localhost.localstack.cloud"

# Configure your S3 bucket name from environment variable
BUCKET_NAME = os.getenv('BUCKET_NAME')

# Initialize the S3 client
s3 = boto3.client(
    's3',endpoint_url=endpoint_url)

@app.route('/')
def list_files():
    try:
        # List objects in the specified bucket
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        files = response.get('Contents', [])
        
        # Extract folder structure
        file_structure = {}
        for file in files:
            folder = file['Key'].split('/')[0]
            if folder not in file_structure:
                file_structure[folder] = []
            file_structure[folder].append(file['Key'])

        app.logger.info('Listed files from bucket: %s', BUCKET_NAME)
        return render_template('list_files.html', files=file_structure)
    except Exception as e:
        app.logger.error('Error listing files: %s', e)
        return str(e)

@app.route('/logs')
def view_logs():
    try:
        with open('app.log', 'r') as log_file:
            logs = log_file.read()
        return render_template('logs.html', logs=logs)
    except Exception as e:
        app.logger.error('Error reading log file: %s', e)
        return str(e)
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)