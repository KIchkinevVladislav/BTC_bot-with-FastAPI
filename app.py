import fastapi

import pydantic_models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

import config
from database import crud
from pydantic_models import Token, TokenData, Admin, UserInDB

api = fastapi.FastAPI()

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def verify_password(plain_password, hashed_password):
    """
    Проверка соответствия полученного пароля хешу
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Хеширование пароля от пользователя
    """
    return pwd_context.hash(password)


def get_user(username: str):
    """
    Проверяем полученное имя пользователя на соответствие данным из базы (в нашем случае, конкретный логин админа)
    :param username:
    :return:
    """
    if username == config.USERNAME:
        return UserInDB(username=username, hashed_password=config.PASSWORD)


def authenticate_user(username: str, password: str):
    """
    Проверка имени и пароля пользователя
    на соответствие данным из базы
    :param username:
    :param password:
    :return:
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict):
    """
    Создание нового JWT
    :param data:
    :return:
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Создаем зависимость
    доступ получает
    только авторизированный пользователь
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@api.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Получаем информацию о токене
    :param form_data:
    :return:
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(
        data={'sub': user.username})
    return {'access_token': access_token, 'token_type': 'bearer'}

"""
current_user: Admin = Depends(get_current_user)
используем в обработчиках пути 
чтобы предоставить доступ только авторизованному клиенту (в нашем случае, только админу)
"""


@api.get('/users/me/', response_model=Admin)
async def read_users_me(current_user: Admin = Depends(get_current_user)):
    """
    Получаем информацию о текущем пользователе
    :return:
    """
    return current_user


@api.post('/user/create')
def create_user(
        user: pydantic_models.UserToCreate,
        current_user: Admin = Depends(get_current_user)
):
    """
    Создаем пользователя
    :param user:
    :return: Новый объект пользователя
    """
    return crud.create_user(tg_id=user.tg_ID,
                            nick=user.nick if user.nick else None).to_dict()


@api.put('/user/{user_id}')
def update_user(
        user_id: int,
        user: pydantic_models.UserToUpdate = fastapi.Body(),
        current_user: Admin = Depends(get_current_user)
):
    """
    Обновляем данные пользователя
    :param user_id:
    :param user: обновляемые данные в виде словаря
    :return:
    """
    if user_id == user.id:
        return crud.update_user(user).to_dict()


@api.delete('/user/{user_id}')
@crud.db_session
def delete_user(
        user_id: int = fastapi.Path(),
        current_user: Admin = Depends(get_current_user)
):
    """
    Удаляем пользователя
    :param user_id:
    :return:
    """
    crud.get_user_by_id(user_id).delete()
    return True


@api.get('/get_info_by_user_id/{user_id:int}')
@crud.db_session
def get_info_about_user(
        user_id,
        current_user: Admin = Depends(get_current_user)
):
    """
    Получаем информацию о пользователе
    :param user_id:
    :return:
    """
    return crud.get_user_info(crud.User[user_id])


@api.get('/get_user_balance_by_id/{user_id:int}')
@crud.db_session
def get_user_balance_by_id(
        user_id,
        current_user: Admin = Depends(get_current_user)
):
    """
    Получаем баланс пользователя
    :param user_id:
    :return:
    """
    crud.update_wallet_balance(crud.User[user_id].wallet)
    return crud.User[user_id].wallet.balance


@api.get('/get_total_balance')
@crud.db_session
def get_total_balance(current_user: Admin = Depends(get_current_user)):
    """
    Получаем общий баланс

    :return:
    """
    balance = 0.0
    crud.update_all_wallets()
    for user in crud.User.select()[:]:
        balance += user.wallet.balance
    return balance


@api.get('/users')
@crud.db_session
def get_users(current_user: Admin = Depends(get_current_user)):
    """
    Получаем всех пользователей
    :return list:
    """
    users = []
    for user in crud.User.select()[:]:
        users.append(user.to_dict())
    return users


@api.get('/user_by_tg_id/{tg_id:int}')
@crud.db_session
def get_user_by_tg_id(
        tg_id,
        current_user: Admin = Depends(get_current_user)
):
    """
    Получаем юзера по его id в Телеграмм
    :param tg_id:
    :return:
    """
    user = crud.get_user_info(crud.User.get(tg_ID=tg_id))
    return user


@api.post('/create_transaction/{user_id:int}')
@crud.db_session
def create_transaction(
        user_id,
        transaction: pydantic_models.TransactionToCreate,
        current_user: Admin = Depends(get_current_user)
):
    """
    Создаем транзакции
    :param user_id:
    :param transaction: данные в виде словаря передаем в тело запроса
    :return:
    """
    return crud.create_transaction(crud.get_user_by_id(user_id), transaction.amount_btc_without_fee,
                                   transaction.receiver_address)


@api.get('/get_user_transactions/{user_id:int}')
@crud.db_session
def get_user_transactions(
        user_id,
        current_user: Admin = Depends(get_current_user)
):
    """
    Получение списка транзакций пользователя
    :param user_id:
    :return:
    """
    return crud.get_user_transactions(user_id)


@api.get('/get_user_wallet/{user_id:int}')
@crud.db_session
def get_user_wallet(
        user_id,
        current_user: Admin = Depends(get_current_user)
):
    """
    Получаем данные кошелька пользователя
    :param user_id:
    :return:
    """
    return crud.get_wallet_info(crud.User[user_id].wallet)

