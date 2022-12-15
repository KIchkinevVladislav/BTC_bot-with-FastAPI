import requests
import pydantic_models
from config import API_URL


def update_user(user: dict):
    """Обновляем юзера"""
    # валидируем данные о юзере, так как мы не под декоратором fastapi и это нужно делать вручную
    user = pydantic_models.UserToUpdate.validate(user)
    # чтобы отправить пост запрос - используем метод .post, в аргументе data - отправляем строку в формате json
    responce = requests.put(f'{API_URL}/user/{user.id}', data=user.json())
    try:
        return responce.json()
    except:
        return responce.text


def delete_user(user_id: int):
    """
    Удаляем юзера
    :param user_id:
    :return:
    """
    return requests.delete(f'{API_URL}/user/{user_id}').json()


def create_user(user: pydantic_models.UserToCreate):
    """
    Создаем Юзера
    :param user:
    :return:
    """
    user = pydantic_models.UserToCreate.validate(user)
    return requests.post(f'{API_URL}/user/create', data=user.json()).json()


def get_info_about_user(user_id):
    """
    Получаем инфу по юзеру
    :param user_id:
    :return:
    """
    return requests.get(f'{API_URL}/get_info_by_user_id/{user_id}').json()


def get_user_balance_by_id(user_id):
    """
    Получаем баланс юзера
    :param user_id:
    :return:
    """
    responce = requests.get(f'{API_URL}/get_user_balance_by_id/{user_id}')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_total_balance():
    """
    Получаем общий баланс

    :return:
    """
    responce = requests.get(f'{API_URL}/get_total_balance')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_users():
    """
    Получаем всех юзеров
    :return list:
    """
    return requests.get(f"{API_URL}/users").json()


def get_user_wallet_by_tg_id(tg_id):
    user_dict = get_user_by_tg_id(tg_id)
    return requests.get(f"{API_URL}/get_user_wallet/{user_dict['id']}").json()


def get_user_by_tg_id(tg_id):
    """
    Получаем юзера по айди его ТГ
    :param tg_id:
    :return:
    """
    return requests.get(f"{API_URL}/user_by_tg_id/{tg_id}").json()


def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
    user_dict = get_user_by_tg_id(tg_id)
    payload = {'receiver_address': receiver_address,
               'amount_btc_without_fee': amount_btc_without_fee}
    responce = requests.post(f"{API_URL}/create_transaction/{user_dict['id']}", json=payload)
    return responce.text


def get_user_transactions(user_id):
    responce = requests.get(f"{API_URL}/get_user_transactions/{user_id}")
    try:
        return responce.json()
    except Exception as E:
        return f"{responce.text} \n" \
               f"Exception: {E.args, E.__traceback__}"


# def update_user(user: dict):
#     user = pydantic_models.UserToUpdate.validate(user)
#     response = requests.put(f'{API_URL}/user/{user.id}', data=user.json())
#     try:
#         return response.json()
#     except requests.exceptions.JSONDecodeError:
#         return response.text
#
#
# def delete_user(user_id: int):
#     return requests.delete(f'{API_URL}/user/{user_id}').json()
#
#
# def create_user(user: pydantic_models.UserToCreate):
#     user = pydantic_models.UserToCreate.validate(user)
#     return requests.post(f'{API_URL}/user/create', data=user.json()).json()
#
#
# def get_info_about_user(user_id):
#     return requests.get(f'{API_URL}/get_info_by_user_id/{user_id}').json()
#
#
# def get_user_balance_by_id(user_id):
#     response = requests.get(f'{API_URL}/get_user_balance_by_id/{user_id}')
#     try:
#         return float(response.text)
#     except TypeError:
#         return f'Error: Not a Number\nResponse: {response.text}'
#
#
# def get_total_balance():
#     response = requests.get(f'{API_URL}/get_total_balance')
#     try:
#         return float(response.text)
#     except TypeError:
#         return f'Error: Not a Number\nResponse: {response.text}'
#
#
# def get_users():
#     return requests.get(f"{API_URL}/users").json()
#
#
# def get_user_wallet_by_tg_id(tg_id):
#     user_dict = get_user_by_tg_id(tg_id)
#     return requests.get(f"{API_URL}/get_user_wallet/{user_dict['id']}").json()
#
#
# def get_user_by_tg_id(tg_id):
#     return requests.get(f"{API_URL}/user_by_tg_id/{tg_id}").json()
#
#
# def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
#     user_dict = get_user_by_tg_id(tg_id)
#     payload = {'receiver_address': receiver_address,
#                'amount_btc_without_fee': amount_btc_without_fee}
#     response = requests.post(f"{API_URL}/create_transaction/{user_dict['id']}", json=payload)
#     return response.text
#
#
# def get_user_transactions(user_id: int):
#     return requests.get(f"{API_URL}/get_user_transactions/{user_id}").json()
