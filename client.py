import requests
import pydantic_models

from config import API_URL

# создаем заголовок в котором указываем, что тип контента - форма
form_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

payload = 'username=admin&password=admin' # здесь логин и пароль
raw_token = requests.post(API_URL+'/token',
                         headers=form_headers,
                         data=payload)
token = raw_token.json()     # получаем словарь из ответа сервера
sesh = requests.Session()   # создаем экземпляр сессии
# добавляем хедеры с токеном авторизации, благодаря чему API будет понимать кто мы и возвращать нужные нам ответы
sesh.headers = {
      'accept': 'application/json',
  'Authorization': "Bearer " + token['access_token']
}


def create_user(user: pydantic_models.UserToCreate):
    """
    Создаем Юзера
    :param user:
    :return:
    """
    # валидируем данные о пользователе, так как мы не под декоратором fastapi и это нужно делать вручную
    user = pydantic_models.UserToCreate.validate(user)
    return sesh.post(f'{API_URL}/user/create', data=user.json()).json()


def update_user(user: dict):
    """
    Обновляем пользователя
    :param user:
    :return:
    """
    user = pydantic_models.UserToUpdate.validate(user)
    responce = sesh.put(f'{API_URL}/user/{user.id}', data=user.json())
    try:
        return responce.json()
    except requests.exceptions.JSONDecodeError:
        return responce.text


def delete_user(user_id: int):
    """
    Удаляем пользователя
    :param user_id:
    :return:
    """
    return sesh.delete(f'{API_URL}/user/{user_id}').json()


def get_users():
    """
    Получаем всех пользователей
    :return list:
    """
    return sesh.get(f'{API_URL}/users').json()


def get_info_about_user(user_id):
    """
    Получаем информацию о пользователей
    :param user_id:
    :return:
    """
    return sesh.get(f'{API_URL}/get_info_by_user_id/{user_id}').json()


def get_user_by_tg_id(tg_id):
    """
    Получаем пользователя по его ID в Телеграм
    :param tg_id:
    :return:
    """
    return sesh.get(f'{API_URL}/user_by_tg_id/{tg_id}').json()


def get_user_wallet_by_tg_id(tg_id):
    """
    Получаем данные о кошельке пользователя по его ID в Телеграм
    :param tg_id:
    :return:
    """
    user_dict = get_user_by_tg_id(tg_id)
    return sesh.get(f"{API_URL}/get_user_wallet/{user_dict['id']}").json()


def get_user_balance_by_id(user_id):
    """
    Получаем баланс пользователя
    :param user_id:
    :return:
    """
    responce = sesh.get(f'{API_URL}/get_user_balance_by_id/{user_id}')
    try:
        return float(responce.text)
    except TypeError:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_total_balance():
    """
    Получаем общий баланс

    :return:
    """
    responce = sesh.get(f'{API_URL}/get_total_balance')
    try:
        return float(responce.text)
    except TypeError:
        return f'Error: Not a Number\nResponce: {responce.text}'


def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
    """
    Создаем транзакцию
    :param tg_id:
    :param receiver_address:
    :param amount_btc_without_fee:
    :return:
    """
    user_dict = get_user_by_tg_id(tg_id)
    payload = {'receiver_address': receiver_address,
               'amount_btc_without_fee': amount_btc_without_fee}
    responce = sesh.post(f"{API_URL}/create_transaction/{user_dict['id']}", json=payload)
    return responce.text


def get_user_transactions(user_id):
    """
    Получаем список транзакций пользователя
    :param user_id:
    :return:
    """
    responce = sesh.get(f'{API_URL}/get_user_transactions/{user_id}')
    try:
        return responce.json()
    except ValueError as E:
        return f'{responce.text} \n' \
               f'Exception: {E.args, E.__traceback__}'

