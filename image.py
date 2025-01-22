import os
import uvicorn
from fastapi import FastAPI,HTTPException,UploadFile,File
from fastapi.responses import JSONResponse

app = FastAPI()
local_path= 'uploads/'
os.makedirs(local_path, exist_ok=True)

@app.post("/upload")
async def image_upload(file:UploadFile=File(...)):
    try:
        if file is None:return{"message":"document isn't existence"}
        if not file.filename.endswith(('.png', '.jpg')):
            return{"message":"document does not  support upload,please upload suffix only in png or jpg"}
        file_location = os.path.join(local_path, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        return JSONResponse(content={"url": f"/uploads/{file.filename}"}, status_code=200)
    except Exception as e:
        print(f"exception occurred:{e}")

@app.post("/delete/{filename}")
def image_delete(filename:str):
    file_path = os.path.join(local_path,filename)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件未找到")

    os.remove(file_path)
    return JSONResponse(content={"success": "文件已删除"}, status_code=200)


if __name__=='__main__':
    uvicorn.run("image:app",host="127.0.0.1",port=6060,reload=True)