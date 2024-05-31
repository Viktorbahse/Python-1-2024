import requests

SERVER_URL = "http://127.0.0.1:5000/"  # И тут вроде надо изменить, чтобы не локально было


def update_stat(level):
    result = requests.post(SERVER_URL + 'game_statistic', json=[str(level)])
    return result.json()

def get_rating():
    result = requests.post(SERVER_URL + 'rating').json()
    result = sorted(result, key=lambda x: x[1], reverse=True)
    return result

