from flask import Flask, render_template, request, jsonify
import boto3
import logging
import os

app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


BUCKET_NAME = os.getenv('BUCKET_NAME')
bucket='liquiman-logs'
endpoint_url = "http://localhost.localstack.cloud:4566"

s3 = boto3.client('s3',endpoint_url=endpoint_url)

@app.route('/', methods=['GET', 'POST'])
def list_files_and_folders():
    root_prefix = request.args.get('root_folder', '')  # Get the root folder from query parameters
    
    try:
        # List objects in the specified folder
        response = s3.list_objects_v2(Bucket='liquiman-logs', Prefix=root_prefix, Delimiter='/')
        
        folders = response.get('CommonPrefixes', [])
        files = response.get('Contents', [])
        
        # Filter out the root folder itself if it appears in the files list
        if root_prefix:
            files = [file for file in files if file['Key'] != root_prefix]
        
        return render_template('list_files_and_folders.html', folders=folders, files=files, root_prefix=root_prefix)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/file-content', methods=['GET'])
def file_content():
    file_key = request.args.get('file_key')
    
    try:
        print(f"Fetching content for file: {file_key}")
        obj = s3.get_object(Bucket='liquiman-logs', Key=file_key)
        content = obj['Body'].read().decode('utf-8')
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)})

'''
@app.route('/search-folders', methods=['GET'])
def search_folders():

    bucket_name = 'your-bucket-name'
    filter_text = request.args.get('filter', '')

    # List objects in the bucket with a prefix matching the filter text
    response = s3.list_objects_v2(
        Bucket='liquiman-logs',
        Prefix=filter_text,
        Delimiter='/'
    )
    print(response)
    # Extract folder names from response
    # folders = [prefix['Prefix'].split('/')[2] for prefix in response.get('CommonPrefixes', [])]
    folders = [prefix['Prefix'] for prefix in response.get('CommonPrefixes', []) if filter_text in prefix['Prefix']]

    return jsonify(folders)
'''



def list_folders(bucket_name, prefix):
    print("Searching in folder:", prefix)  # Debugging statement
    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix,
        Delimiter='/'
    )
    folders = []  # Use a list to store folder paths
    for common_prefix in response.get('CommonPrefixes', []):
        subfolder = common_prefix['Prefix']
        print("Found subfolder:", subfolder)  # Debugging statement
        folders.append(subfolder)
        folders.extend(list_folders(bucket_name, subfolder))  # Recursively add subfolders
    return folders

@app.route('/search-folders', methods=['GET'])
def search_folders():
    bucket_name = bucket
    filter_text = request.args.get('filter', '')

    # List folders recursively in the bucket with a prefix matching the filter text
    folders = list_folders(bucket_name, filter_text)

    return jsonify(folders)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)