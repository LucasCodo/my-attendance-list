from asyncio import sleep
import schedule
from fastapi import FastAPI, Request, requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from peewee import IntegrityError

from authenticator import *
from backgroundtasks import clean_invalid_tokens as cit
from backgroundtasks import stop_run_continuously
from database import insert
from enumerations import UserType
from Payment_methods.lightning_payment import *
from temporary_token import Token as TToken
from websocket_manager import *
from fastapi.responses import RedirectResponse


class Student(BaseModel):
    name: str
    cod: str
    token: str


class UserSignUp(BaseModel):
    username: str
    full_name: str
    email: str
    password: str
    usertype: str
    registration_code: Union[str, None] = None


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
tokens = {}


@app.on_event("startup")
async def startup_event():
    schedule.every(5).minutes.do(cit, tokens)


@app.on_event("shutdown")
async def shutdown_event():
    stop_run_continuously.set()


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("token.html", {"request": request})


@app.get("/temporary-token/seconds={id}")
async def get_token(id: int):
    token = TToken(seconds=id)
    tokens.update(token)
    return str(token)


@app.post("/validar")
async def validar(student: Student):
    token = tokens.get(student.token, TToken(alive=False))
    if token.is_valid():
        tokens.pop(student.token)
        return "Operação realizada com sucesso"
    return "Token invalido"


@app.get("/login", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
        current_user: User = Security(get_current_active_user, scopes=["items"])
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/status/")
async def read_system_status(current_user: User = Depends(get_current_user)):
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            token = TToken(seconds=3)
            tokens.update(token)
            await manager.send_personal_message(token.base64_qr_code, websocket)
            await sleep(token.duration)
    except Exception as e:
        print(e)
        manager.disconnect(websocket)


# endpoints of the student

@app.get("/student/profile")
async def profile_teacher(current_user: User = Depends(get_current_user)):
    return "perfil do aluno " + current_user.username


@app.get("/student/dashboard")
async def teacher(current_user: User = Depends(get_current_user)):
    return "Dashboard do aluno " + current_user.username


@app.get("/student/attendance-list/")
async def student_attendance_list(token: str, current_user: User = Depends(get_current_user)):
    return "Dashboard do aluno " + current_user.username


# endpoints of the teacher

@app.get("/teacher/profile")
async def profile_teacher(current_user: User = Depends(get_current_user)):
    return "perfil do professor " + current_user.username


@app.get("/teacher/dashboard")
async def dashboard_teacher(current_user: User = Depends(get_current_user)):
    return "Dashboard do professor " + current_user.username


@app.get("/teacher/courses/")
async def teacher_courses(current_user: User = Depends(get_current_user)):
    return "Tela de gerencia de cursos do professor " + current_user.username


@app.get("/teacher/attendance-lists/")
async def attendance_lists(current_user: User = Depends(get_current_user)):
    return "Tela de gerencia das listas de frequencia do professor " + current_user.username


@app.get("/teacher/attendance-lists/course/{id_course}/token", response_class=HTMLResponse)
async def attendance_lists_token(id_course: int, request: Request,
                                 current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("token.html", {"request": request, "user": current_user})


# endpoints of the Organization

@app.get("/organization/dashboard")
async def dashboard_organization(current_user: User = Depends(get_current_user)):
    return "Dashboard da organização " + current_user.username


@app.get("/organization/profile")
async def organization_profile(current_user: User = Depends(get_current_user)):
    return "Perfil da organização " + current_user.username


@app.get("/organization/dashboard/teachers/")
async def dashboard_organization_teachers(current_user: User = Depends(get_current_user)):
    return "Tela de gerencia de professores da organização " + current_user.username


@app.get("/organization/dashboard/courses/")
async def dashboard_organization_courses(current_user: User = Depends(get_current_user)):
    return "Tela de gerencia de cursos da organização " + current_user.username


# endpoints of the Organization
@app.get("/buy-license")
async def buy_license():
    return "Tela de compra de licença "


@app.get('/payment/lightning', response_class=HTMLResponse)
async def payment_lightning(request: Request):
    invoice = get_invoice()
    return templates.TemplateResponse("invoice.html",
                                      {"request": request,
                                       "qrcode": invoice_qrcode(invoice),
                                       "invoice": invoice["payment_request"],
                                       "invoice_id": invoice["id"]})


@app.websocket("/ws/lightning-invoice")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        data = await websocket.receive_text()
        while True:
            await manager.send_personal_message(str(been_invoice_paid(data)), websocket)
            await sleep(3)
    except Exception as e:
        manager.disconnect(websocket)


# endpoints da api

@app.post("/sign-up/user")
async def sign_up_user(user: UserSignUp):
    if user.usertype not in map(lambda x: x.value, list(UserType)):
        raise HTTPException(status_code=400, detail="Incorrect UserType")
    data = dict(user)
    if user.usertype != UserType.Student.value:
        data.pop("registration_code")
    data["hashed_password"] = get_password_hash(user.password)
    data.pop("password")
    data.pop("usertype")
    try:
        insert[user.usertype](data=data)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return data
