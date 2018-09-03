# Manual do desenvolvedor

## Ferramentas necessárias

* Python, SQL, SQLite3, Flask.

## Descrição de arquivos

* adduser.py: a partir do arquivo users.csv, adiciona novos usuários ao banco de dados e gera automaticamente uma senha, que é igual ao nome de usuário;
* softdes.py: conecta-se ao banco de dados e a aplicação via Flask, e compara o arquivo enviado com o gabarito, gerando uma nota e a salvando no banco de dados e exibindo na aplicação, na conta referente ao usuário que enviou o arquivo. Também realiza a função de login, comparando o que foi inserido com os dados de usuário e senha do banco de dados, e o processo de alteração da senha.

## Para rodar a aplicação

* Acessar o prompt de comando do SQLite3 e rodar o script quiz.sql:
  
        SQLITE3 quiz.db < quiz.sql

* Criar um arquivo chamado users.csv com um usuário e seu respectivo tipo na mesma cédula separado por vírgula:
    
        Exemplo: maria, user

Salvar o arquivo na mesma pasta de adduser.py.

* Rodar o arquivo adduser.py no prompt de comando:

        python adduser.py

* Rodar o arquivo softdes.py no prompt de comando:
    
        python softdes.py

* Acessar no browser http://127.0.0.1:80 e inserir no campo user o mesmo nome que foi criado no arquivo users.csv, e no campo password, o próprio usuário de novo:
    
        Exemplo: 
        user: maria
        password: maria