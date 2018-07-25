# Finxi code Challenge

### Desenvolva um sistema web para importação e processamento de vendas, seguindo os requisitos:

1. Preencher um formulário com nome da empresa (texto livre) e importar o arquivo contendo minhas vendas do mês (arquivo em anexo);
2. Após enviar o arquivo, o sistema deverá identificar as vendas por produto, o total de produtos vendidos, a média do preço de venda, custo e categoria;
3. Como usuário, preciso ter acesso a essas importações e realizar alguns filtros, como nome da empresa, nome do produto e categoria;
4. Ao fim do processamento, o usuário deverá receber algum tipo de alerta que a planilha enviada foi processada com sucesso;



### Informações importantes:

1. O formulário de importação das vendas deve ser feitos através de um CMS. Não utilize o admin do Django para isso;
2. A visualização de produtos, filtros e médias deve ser por empresa;
3. O processamento da planilha deve acontecer em segundo plano, possibilitando que o usuário receba o alerta de conclusão em qualquer área do sistema (fora o admin do django). Ex: Após enviar a planilha, como usuário, devo poder retornar a tela de importação ou listagem e enviar outro arquivo enquanto o primeiro está sendo processado, recebendo o alerta onde eu estiver;

## Getting Started

1. Clone this repository
2. Install Python 3.7+ and create a virtualenv
3. Activate the virtualenv
4. Install the dependencies
5. Configure .env instance
6. Run the tests

```console
git clone https://rubimpassos@bitbucket.org/rubimpassos/finxichallenge.git finxiChallenge
cd finxiChallenge
python -m venv .venv
source .venv/Scripts/activate.bat
pip install -r requirements-dev.txt
cp contrib/env-sample .env
python -m pytest
```

## Deployment

1. Create a app in Heroku
2. Send the config to heroku
3. Define a secure secret key in heroku config vars
4. Define DEBUG=False
5. Configure a worker(e.g Redis)
6. Push to heroku

```console
heroku create myapp
heroku config:push
heroku config:set SECRET_KEY=`python contrib/secret_gen.py`
heroku config:set DEBUG=False
# configure a worker service that you like
git push heroku master --force
```