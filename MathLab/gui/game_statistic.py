import requests

# Чтобы было локально
SERVER_URL = "http://127.0.0.1:5000/"
# Чтобы не локально было
# SERVER_URL = 'http://18.226.177.149:5000/'


def update_stat(level):
    result = requests.post(SERVER_URL + 'game_statistic', json=[str(level)])
    return result.json()


def get_rating():
    result = requests.post(SERVER_URL + 'rating').json()
    result = sorted(result, key=lambda x: x[1], reverse=True)
    return result

