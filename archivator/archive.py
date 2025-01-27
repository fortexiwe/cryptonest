import os
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import zipfile
import io
from pathlib import Path
from typing import List

ARCHIVE_FOLDER = Path("/home/fortex/Рабочий стол/diplomka/sxron")
CLOUD_SERVER_URL = "http://0.0.0.0:8002/cloud/"  

ARCHIVE_FOLDER.mkdir(parents=True, exist_ok=True)

app = FastAPI()

@app.post("/archive/")
async def create_archive(user: str = Form(...), password: str = Form(...), files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail='No files uploaded.')

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for uploaded_file in files:
                file_content = await uploaded_file.read()
                zipf.writestr(uploaded_file.filename, file_content)
        
        zip_buffer.seek(0)

        archive_filename = f"{Path(files[0].filename).stem}.zip"
        archive_path = ARCHIVE_FOLDER / archive_filename

        with open(archive_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        with open(archive_path, 'rb') as f:
            files_to_send = {'files': (archive_filename, f)}
            response = requests.post(CLOUD_SERVER_URL, files=files_to_send, data={'password': password, 'user': user})

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get('detail', 'OShibka'))

        return JSONResponse(content={
            'archive_filename': archive_filename,
            'archive_path': str(archive_path)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
