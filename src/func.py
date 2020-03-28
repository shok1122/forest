import requests

def invoke(token, expr, attr, count = 10, model = 'latest'):

    options = ''
    if expr  is not None: options += f'expr={expr}&'
    if model is not None: options += f'model={model}&'
    if count is not None: options += f'count={count}&'
    if attr  is not None: options += f'attributes={attr}&'
    options = options[:-1]

    print(options)
    url = f'https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?{options}'

    print(url)
    response = requests.get(
        url,
        headers = {
            'Content-Type' : 'application/json',
            'Ocp-Apim-Subscription-Key' : token
        }
    )

    print(response.json())

def print_str(str):
    print(str)