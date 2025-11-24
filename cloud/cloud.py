from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import shutil
import os
from typing import List
from utils.utils import encrypt_file_content, decrypt_file_content
import requests

app = FastAPI()


cloud_folder = Path("cloud_storage")
if not cloud_folder.exists():
    cloud_folder.mkdir(parents=True)

user_storage = {}

@app.post('/cloud/')
async def cloud(user: str = Form(...), password: str = Form(...), files: List[UploadFile] = File(...)):
    try:
        total_size = 0
        for file in files:
            file_path = os.path.join(cloud_folder, file.filename)
            
            with open(file_path, 'wb') as f:
                f.write(await file.read())
            
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            cryptography_encrypt(file_path=file_path, password=password)

        requests.post('http://127.0.0.1:8000/plus_size/', data={
            'user': user,
            'file': total_size
        })
        return {"message": f"{len(files)} file(s) uploaded successfully, total size: {total_size} bytes"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    

@app.get("/files/{unique_name}")
async def get_file(unique_name, original_filename, password):
    file_path = cloud_folder / unique_name
    cryptography_decrypt(file_path=file_path, password=password)
    

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=original_filename, media_type="application/octet-stream")


@app.get("/storage/{username}")
async def get_storage(username: str):
    # Получаем информацию о свободном пространстве на диске
    total, used, free = shutil.disk_usage(cloud_folder)
    
    # Запрос к другому API для получения использованного пространства для конкретного пользователя
    response = requests.get('http://127.0.0.1:8000/get_size/', params={'user': username})
    
    if response.status_code == 200:
        use_user = response.json().get('size', 0)
    else:
        use_user = 0 

    free_user = 10  

    # Преобразуем байты в гигабайты
    free_gb = free / (1024 ** 3)
    total_gb = total / (1024 ** 3)
    used_gb = use_user / (1024 ** 3)

    return {
        "storage_used": use_user,
        "storage_total": free_user,
        "storage_free": free_gb,
        "storage_used_gb": used_gb
    }



def cryptography_encrypt(file_path, password):
    encrypt_file_content(input_file_path=file_path, password_str=password)


def cryptography_decrypt(file_path, password):
    decrypt_file_content(file_path=file_path, password_str=password)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('cloud:app', host='0.0.0.0', port=8002)
