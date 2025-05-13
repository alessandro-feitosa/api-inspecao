import requests
import json

def validar_api_fertecnica(cnpj, numero_serie):

    api_url = "https://prod-18.brazilsouth.logic.azure.com/workflows/12301fc9e3734493b1a89c4e1db2d35b/triggers/manual/paths/invoke"
    headers = {'Accept':'text/html', 'Content-Type': 'application/json'}
    params = {
        "api-version": "2016-06-01",
        "sp": "/triggers/manual/run",
        "sv": "1.0",
        "sig": "Yo8npecZ121qyRCJwKKfCZWYCwgn2sOIHlKmXC8LStc"
    }
    payload = json.dumps({"cnpj": cnpj, "numero_serie": numero_serie})

    try:
        response = requests.post(api_url, headers=headers, params=params, data=payload)
        response.raise_for_status()  # Levanta uma exceção para códigos de status de erro (4xx ou 5xx)
        data = response.json()
        
        if 'status' in data and isinstance(data['status'], bool):
            return data['status']
        else:
            print(f"Erro: Resposta da API em formato inesperado: {data}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para a API: {e}")
        return False
    except json.JSONDecodeError:
        print(f"Erro ao decodificar a resposta JSON da API: {response.text}")
        return False

if __name__ == "__main__":
    ##cnpj_para_validar = input("Digite o CNPJ para validar (apenas números): ")

    cnpj = '06238884000101' ## BQR139096
    resultado_validacao = validar_cnpj_api(cnpj,"")

    if resultado_validacao:
        print(f"O CNPJ '{cnpj}' é válido.")
    else:
        print(f"O CNPJ '{cnpj}' não é válido.")