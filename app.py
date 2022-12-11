import copy
import pydantic_models
import fastapi

import config
from database import crud
from database.models import *
from database.db import *


api = fastapi.FastAPI()


@api.put('/user/{user_id}')
def update_user(user_id: int, user: pydantic_models.UserToUpdate = fastapi.Body()):
    if user_id == user.id:
        return crud.update_user(user).to_dict()


@api.delete('/user/{user_id}')
@crud.db_session
def delete_user(user_id: int = fastapi.Path()):
    crud.get_user_by_id(user_id).delete()
    return True


@api.post('/user/create')
def create_user(user: pydantic_models.UserToCreate):
    return crud.create_user(tg_id=user.tg_ID,
                            nick=user.nick if user.nick else None).to_dict()


@api.get('/get_user_balance_by_id/{user_id:int}')
@crud.db_session
def get_user_balance_by_id(user_id):
    crud.update_wallet_balance(crud.User[user_id].wallet)
    return crud.User[user_id].wallet.balance


@api.get('/get_user_balance_by_id/{user_id:int}') # получение баланса пользователя
@crud.db_session
def get_user_balance_by_id(user_id):
    crud.update_wallet_balance(crud.User[user_id].wallet)
    return crud.User[user_id].wallet.balance




@api.get('/get_total_balance')  # получение баланса всех пользователей
@crud.db_session
def get_total_balance():
    balance = 0.0
    crud.update_all_wallets()
    for user in crud.User.select()[:]:
        balance += user.wallet.balance
    return balance


@api.get('/users')
@crud.db_session
def get_users():
    users = []
    for user in crud.User.select()[:]:
        users.append(user.to_dict())
    return users


@api.get('/user_by_tg_id/{tg_id:int}')
@crud.db_session
def get_user_by_tg_id(tg_id):
    user = crud.get_user_info(crud.User.get(tg_ID=tg_id))
    return user



@api.post('/create_transaction')
@crud.db_session
def create_transaction(transaction: pydantic_models.CreateTransaction = fastapi.Body()):
    user = crud.User.get(tg_ID=transaction.tg_ID)
    return crud.create_transaction(
            sender=user,
            amount_btc_without_fee=transaction.amount_btc_without_fee,
            receiver_address=transaction.receiver_address,
            fee=transaction.fee if transaction.fee else None,
            testnet=transaction.testnet
    ).to_dict()


@api.get('/get_user_wallet/{user_id:int}')
@crud.db_session
def get_user_wallet(user_id):
    return crud.get_wallet_info(crud.User[user_id].wallet)


@api.get('/get_user_transactions/{user_id:int}')
@crud.db_session
def get_user_transactions(user_id: int = fastapi.Path()):
    return crud.get_user_transactions(user_id)

