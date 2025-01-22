from pydantic import BaseModel,EmailStr,constr
from fastapi import FastAPI,HTTPException
from sqlalchemy import create_engine, Column, String, Integer, TIMESTAMP, func, Sequence, ForeignKey
from sqlalchemy.orm import sessionmaker,declarative_base,Session
import uvicorn
import jwt
from passlib.context import CryptContext
from datetime import datetime,timedelta


app=FastAPI()
Base = declarative_base()
DATABASE_URL = "postgresql://postgres:Zxy20031120%40@volcengine.zhelearn.com:5432/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#生成用bcrypt算法生成hash值的对象
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#定义jtw令牌密钥
SECRETS_KEY = "eamnak%4Ndka"

#定义User模型类并通过Base类映射到user
class User(Base) :
    __tablename__ = 'users'
    id =Column(Integer,Sequence("user_id_seq"),primary_key=True,index=True)#postgresql中创建一个从1开始依次增1的序列
    username =Column(String(10),unique=True,nullable=False)
    email = Column(String(255),unique=True,nullable=False)
    password = Column(String(255),nullable=False)


#定义Session模型类并通过Base映射到postgresql中的sessions表
class Session(Base) :
    __tablename__ ='sessions'

    id = Column(Integer,Sequence('session_id_seq'),primary_key=True,index=True,)#利用外键根据user_id定义session_id
    user_id = Column(Integer,nullable=False)
    title = Column(String(255), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())


#定义用户注册模型类
class UserRegisterModel(BaseModel):
    username: constr(min_length=3,max_length=10)
    email :EmailStr
    password : constr (min_length=8,max_length=255)

#定义用户注册响应类
class UserRegisterResponse(BaseModel):
    username :str
    message :str




Base.metadata.create_all(bind=engine)

#任务2.1及扩展任务：编写登录api并把密码生成hash值
@app.post("/register",response_model=UserRegisterResponse)


async def register_user(user_data:UserRegisterModel) -> UserRegisterResponse:
    db=SessionLocal()

    try:

        new_user =User(username=user_data.username,email=user_data.email,password=pwd_context.hash(user_data.password))
        db.add(new_user)
        new_session = Session( user_id=new_user.id,title="session:" + str(new_user.id))
        db.add(new_session)
        db.commit()

        db.refresh(new_user)
        db.refresh(new_session)

        return UserRegisterResponse(
            username=user_data.username,

            message="register successfully"
        )
    except Exception as e :
        db.rollback()
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=400,detail="register failed")
    finally:
        db.close()

class UserLogin(BaseModel):
    username:str
    password:str

#任务2.2及扩展任务：编写登录api，并生成jwt令牌，还有密码hash值验证
@app.post("/login")
async def login_response(user:UserLogin):
    db=SessionLocal()
    #查询到与名字相同的数据
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user is None : return {"No the account,please register first"}
    if  pwd_context.verify(user.password, db_user.password):
        #生成jwt令牌
        token=jwt.encode({"sub":user.username,"exp":datetime.now()+timedelta(minutes=30)},
                         SECRETS_KEY,algorithm="HS256")
        return {"message:":"login successfully","welcome back":user.username,"JWT token":token}
    else: return {"login failed":"password default"}


#任务三：获取会话列表，根据会话id查找会话
@app.get("/sessions/all")
async def get_sessions(limit: int = 10,offset: int = 0):
    db = SessionLocal()
    all_sessions = db.query(Session).limit(limit).offset(offset).all()
    return all_sessions

@app.get("/session/search")
async def get_session(session_id : int):
    db=SessionLocal()
    db_session = db.query(Session).filter(Session.id == session_id).first()
    if db_session :
        return db_session
    else : return {"The session is not existence!"}


# @app.get("/session/manage")
# def update_session(session_id: int,session_new_title:str,sessionz_new_duration:):
#     db = SessionLocal()
#     manage_session = db.query(Session).filter(Session.id == session_id).first()
#     db.update(manage_session)

#任务三扩展：编写一个删除会话的api，并实现会话按时间排序
@app.get("/session/delete")
async def delete_session(session_id : int):
    try:
        db=SessionLocal()
        d_session = db.query(Session).filter(Session.id ==session_id).first()
        d_user = db.query(User).filter(User.id == session_id).first()
        #删除
        if d_session and d_user:
            db.delete(d_session)
            db.delete(d_user)
            db.commit()
            users_table=db.query(User).order_by(User.id).all()
            sessions_table=db.query(Session).order_by(Session.timestamp).all()
            #排序
            next_id=1
            for session in sessions_table:
                session.id=next_id
                next_id+=1
            db.commit()
            next_id=1
            for user in users_table:
                user.id=next_id
                next_id+=1
            db.commit()
            return {"delete successfully"}
        else :
            return {"No the session"}
    except Exception as e:
        db.rollback()
        print(f"Exception occurred:{e}")
    finally:
        db.close()



if __name__=='__main__':
    uvicorn.run("user:app",host="127.0.0.1",port=8080,reload=True)

