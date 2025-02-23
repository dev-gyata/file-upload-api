from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
from pathlib import Path
import uuid
from fastapi.staticfiles import StaticFiles

app = FastAPI()

UPLOAD_DIR = "media"
Path(UPLOAD_DIR).mkdir(exist_ok=True)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Get the file extension
        file_extension = os.path.splitext(file.filename)[1]

        # Save the file to the upload directory
        generated_name = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR,generated_name + file_extension)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Generate the URL for the uploaded file
        file_url = f"{RENDER_EXTERNAL_URL}/{UPLOAD_DIR}/{generated_name}{file_extension}"

        return JSONResponse(content={
            "message": "File uploaded successfully",
            "file_url": file_url,
            "file_extension": file_extension
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@app.get("/media/{filename}")
async def serve_media_file(filename: str):
    file_path = os.path.join(os.getcwd(),UPLOAD_DIR, filename)
    print(file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app ,host='0.0.0.0',port=os.environ.get('PORT',8080))