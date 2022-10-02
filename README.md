# my-attendance-list
A API que gerencia listas de frequencia

# Pre-requisitos:
  - Python >= 3.8
  - Libs do requiriments.txt, instale com o comando: 'pip install -r requiriments.txt'
  - Banco de dados PostgreSQL
  - As variaveis de ambiente configuradas:
  'db_password',
  'db_name',
  'db_user',
  'db_host',
  'db_port',
  'ALGORITHM' = HS256,
  'ACCESS_TOKEN_EXPIRE_MINUTES' = 30,
  'SECRET_KEY'.
  - Para 'SECRET_KEY' use o valor obtido do comando: 'openssl rand -hex 32'

# Para rodar o serviço:
  + 1 - abra o cmd na pasta do projeto
  + 2 - execute o comando: uvicorn main:app --reload
