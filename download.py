import os
import argparse
from botocore.config import Config
import boto3
from dotenv import load_dotenv

# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Supported image extensions
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

def get_s3_client(account_id, access_key, secret_key, region="auto"):
    """Return an S3-compatible client for Cloudflare R2."""
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    return boto3.client(
        's3',
        region_name=region,
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4')
    )

def list_bucket_objects(client, bucket_name):
    """Return list of image object keys in the bucket."""
    keys = []
    paginator = client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.lower().endswith(IMAGE_EXTENSIONS):
                keys.append(key)
    return keys

def list_local_files(local_dir):
    """Return list of local image file paths relative to local_dir."""
    local_files = []
    for root, _, files in os.walk(local_dir):
        for fname in files:
            if fname.lower().endswith(IMAGE_EXTENSIONS):
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, local_dir)
                key = rel_path.replace(os.sep, '/')
                local_files.append(key)
    return local_files

def download_new_files(client, bucket_name, keys, local_dir):
    for key in keys:
        local_path = os.path.join(local_dir, *key.split('/'))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        print(f"Downloading {key} to {local_path}")
        client.download_file(bucket_name, key, local_path)

def delete_remote_files(client, bucket_name, keys):
    for key in keys:
        print(f"Deleting remote object {key}")
        client.delete_object(Bucket=bucket_name, Key=key)

def main():
    parser = argparse.ArgumentParser(description='Sync images between R2 bucket and local directory')
    parser.add_argument('--bucket', '-b', required=False, help='R2 bucket name (can also set R2_BUCKET_NAME env var)')
    parser.add_argument('--account-id', '-a', required=False, help='Cloudflare account ID (can also set R2_ACCOUNT_ID env var)')
    parser.add_argument('--directory', '-d', default=None, help='Local directory name (defaults to images, can also set R2_DIRECTORY env var)')
    parser.add_argument('--region', '-r', default=None, help='Optional region (can also set R2_REGION env var)')
    args = parser.parse_args()
    # Override with environment variables if not provided via flags
    account_id = args.account_id or os.getenv('R2_ACCOUNT_ID')
    bucket_name = args.bucket or os.getenv('R2_BUCKET_NAME')
    directory = args.directory or os.getenv('R2_DIRECTORY', 'images')
    region = args.region or os.getenv('R2_REGION')
    if not account_id:
        parser.error('Please set R2_ACCOUNT_ID environment variable or supply --account-id')
    if not bucket_name:
        parser.error('Please set R2_BUCKET_NAME environment variable or supply --bucket')

    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    if not access_key or not secret_key:
        parser.error('Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables')

    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_dir = os.path.join(base_dir, directory)
    os.makedirs(local_dir, exist_ok=True)

    client = get_s3_client(account_id, access_key, secret_key, region)

    remote_keys = set(list_bucket_objects(client, bucket_name))
    local_keys = set(list_local_files(local_dir))

    # Download new images
    to_download = remote_keys - local_keys
    if to_download:
        download_new_files(client, bucket_name, to_download, local_dir)
    else:
        print('No new images to download.')

    # Delete images removed locally
    to_delete = local_keys - remote_keys
    if to_delete:
        delete_remote_files(client, bucket_name, to_delete)
    else:
        print('No remote images to delete.')

if __name__ == '__main__':
    main()