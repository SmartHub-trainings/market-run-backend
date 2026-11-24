from fastapi import APIRouter,File,UploadFile
from pathlib import Path
from datetime import datetime
import boto3
from secret import R2_ACCESS_KEY_ID,R2_BUCKET_NAME,R2_ENDPOINT,R2_SECRET_ACCESS_KEY

s3 = boto3.client(
    service_name="s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
)

upload_router = APIRouter(tags=["File Uploads"])
folder= Path("./uploads")
folder.mkdir(exist_ok=True)
print(datetime.now().timestamp())

# file =open(folder/"first.txt","w")
# file.write("Hello World")
# file.close()

@upload_router.post("")
def upload_file(payload:UploadFile=File(...)):
    print(payload)
    original_name =payload.filename
    name_paths= original_name.split(".")
    print(name_paths)
    file_name=f"{name_paths[0]}-{datetime.now().timestamp()}.{name_paths[-1]}"
    file_path =folder/f"{name_paths[0]}-{datetime.now().timestamp()}.{name_paths[-1]}"
    print(file_path)
    print(payload.file)
    with open(file_path,'wb') as file:
        file.write(payload.file.read())
        

    with open(file_path, "rb") as file:
        response=s3.upload_fileobj(file, R2_BUCKET_NAME, file_name)

    print(response)
    
    

    print("File uploaded successfully")

    # awsa
    # cloudflare R@
    # cloundinary
    # Azure