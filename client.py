import requests
import pydantic_models
from config import api_url

form_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

payload = 'username=admin&password=admin'
raw_token = requests.post(api_url+"/token",
                         headers=form_headers,
                         data=payload)
token = raw_token.json()
sesh = requests.Session()

sesh.headers = {
      'accept': 'application/json',
    'Authorization': "Bearer " + token['access_token']
}


def update_user(user: dict):
    """Обновляем пользователя"""
    user = pydantic_models.UserToUpdate.validate(user)
    response = sesh.put(f'{api_url}/user/{user.id}', data=user.json())
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return response.text


def delete_user(user_id: int):
    """
    Удаляем пользователя
    :param user_id:
    :return:
    """
    return sesh.delete(f'{api_url}/user/{user_id}').json()


def create_user(user: pydantic_models.UserToCreate):
    """
    Создаем пользователя
    :param user:
    :return:
    """
    user = pydantic_models.UserToCreate.validate(user)
    return sesh.post(f'{api_url}/user/create', data=user.json()).json()


def get_info_about_user(user_id):
    """
    Получаем информацию о пользователе
    :param user_id:
    :return:
    """
    return sesh.get(f'{api_url}/get_info_by_user_id/{user_id}').json()


def get_user_balance_by_id(user_id):
    """
    Получаем баланс пользователя
    :param user_id:
    :return:
    """
    response = sesh.get(f'{api_url}/get_user_balance_by_id/{user_id}')
    try:
        return float(response.text)
    except TypeError:
        return f'Error: Not a Number\nResponse: {response.text}'


def get_total_balance():
    """
    Получаем общий баланс
    :return:
    """
    response = sesh.get(f'{api_url}/get_total_balance')
    try:
        return float(response.text)
    except TypeError:
        return f'Error: Not a Number\nResponce: {response.text}'


def get_users():
    """
    Получаем всех пользователей
    :return list:
    """
    return sesh.get(f"{api_url}/users").json()


def get_user_by_tg_id(tg_id):
    """
    Получаем пользователя по айди его ТГ
    :param tg_id:
    :return:
    """
    return sesh.get(f"{api_url}/user_by_tg_id/{tg_id}").json()


def get_user_wallet_by_tg_id(tg_id):
    """
    Получаем баланс пользователя
    :param tg_id:
    :return:
    """
    user_dict = get_user_by_tg_id(tg_id)
    return sesh.get(f"{api_url}/get_user_wallet/{user_dict['id']}").json()


def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
    """
    Отправка транзакции
    :param tg_id:
    :param receiver_address:
    :param amount_btc_without_fee:
    :return:
    """
    user_dict = get_user_by_tg_id(tg_id)
    payload = {'receiver_address': receiver_address,
               'amount_btc_without_fee': amount_btc_without_fee}
    response = sesh.post(f"{api_url}/create_transaction/{user_dict['id']}", json=payload)
    return response.text


def get_user_transactions(user_id: int):
    """
    Получаем транказакции пользователя
    :param user_id:
    :return:
    """
    response = requests.get(f"{api_url}/get_user_transactions/{user_id}")
    try:
        return response.json()
    except ValueError as E:
        return f"{response.text} \n" \
               f"Exception: {E.args, E.__traceback__}"

