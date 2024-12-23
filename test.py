from typing import Union
from fastapi import FastAPI, Query
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from pydantic import BaseModel, EmailStr,constr
from datetime import datetime
import uvicorn
app = FastAPI()

@app.get("/hello")
async def read_hello():
    return {"Hello, World!"}
#@app.get("/echo"))
# async def echo(input_data: str):
#    return  {"echo": input_data}
@app.get("/math/sum")
async def math_sum(a: float,b: float):
    return a+b

class EchoRequest(BaseModel):
    input_data: str


@app.get("/echo")
async def echo(input_data: str = Query(...)):
    return JSONResponse(content={"echo": input_data})


#限定用户名字，邮件，密码
class UserRegistrationModel(BaseModel):
    username : constr(min_length=2, max_length=10)
    email : EmailStr
    password : constr(min_length=8,max_length=16)
    signup_ts :datetime =datetime| None



#定义响应模型类
class UserRegistrationResponseModel(BaseModel) :
    username :str
    message : str
register_users=set()


def register_user(user_data:UserRegistrationModel) -> UserRegistrationResponseModel:
    return UserRegistrationResponseModel(
        message="用户注册成功",
        username=user_data.username,

    )


#获取得到的客户端数据
external_data= {

    'username' : 'Zhou Yu',
    'email' : '2752414916@qq.com',
    'password' : "Zxy20031120@"
}

#利用得到的客户端数据创建实例用户对象
user_input =UserRegistrationModel(**external_data)


response=register_user(user_input)


register_users.add(user_input.username)
print(response.model_dump_json())

#运行就开启路由服务器，不需要输命令
if __name__=='__main__':
    uvicorn.run("test:app",host="127.0.0.1",port=8080,reload=True)