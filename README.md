# R2 Image Sync

A simple Python script to synchronize images between a Cloudflare R2 bucket and a local directory. It downloads new images from the bucket and deletes remote objects when you remove local files, keeping both sides in sync each run.

## Prerequisites

- Python 3.6+
- `boto3`, `botocore`, and `python-dotenv` libraries

## Installation

```bash
pip install boto3 botocore python-dotenv
```

## Configuration (.env)

Create a `.env` file in this directory with:

```env
AWS_ACCESS_KEY_ID=<your_access_key>
AWS_SECRET_ACCESS_KEY=<your_secret_key>
```

The script uses `python-dotenv` to load these automatically.

Alternatively, you can still set them manually:

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

_On Windows (PowerShell):_
```powershell
$Env:AWS_ACCESS_KEY_ID="..."
$Env:AWS_SECRET_ACCESS_KEY="..."
```

## Usage

Run the script with your account and bucket info:

```bash
python download.py \
  --account-id <CLOUDFLARE_ACCOUNT_ID> \
  --bucket <R2_BUCKET_NAME> \
  --directory <LOCAL_DIR_NAME>  # defaults to "images"
```

### Examples

- **macOS/Linux**
  ```bash
  export AWS_ACCESS_KEY_ID=...
  export AWS_SECRET_ACCESS_KEY=...
  python download.py -a abcd1234 -b my-images -d images
  ```

- **Windows (cmd)**
  ```cmd
  set AWS_ACCESS_KEY_ID=...
  set AWS_SECRET_ACCESS_KEY=...
  python download.py -a abcd1234 -b my-images -d images
  ```

- **Windows (PowerShell)**
  ```powershell
  $Env:AWS_ACCESS_KEY_ID = "..."
  $Env:AWS_SECRET_ACCESS_KEY = "..."
  python download.py -a abcd1234 -b my-images -d images
  ```

After running, the `<LOCAL_DIR_NAME>` folder will mirror your R2 bucket’s images.

## License

MIT
