from fastapi import APIRouter,File,UploadFile
from pathlib import Path

upload_router = APIRouter(tags=["File Uploads"])
folder= Path("./uploads")
folder.mkdir(exist_ok=True)

# file =open(folder/"first.txt","w")
# file.write("Hello World")
# file.close()

@upload_router.post("")
def upload_file(payload:UploadFile=File(...)):
    print(payload)
    file_path =folder/payload.filename
    print(file_path)
    print(payload.file)
    with open(file_path,'wb') as file:
        file.write(payload.file.read())



    
    print("File uploaded successfully")