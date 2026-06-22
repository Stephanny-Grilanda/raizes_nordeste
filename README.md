🌵 Projeto Raízes do Nordeste - API Back-End

Bem-vindo(a) ao repositório do Back-End da rede Raízes do Nordeste.

📖 Sobre o Projeto

Esta API foi desenvolvida para atender a rede de restaurantes e lanchonetes Raízes do Nordeste, uma empresa que nasceu como um pequeno negócio familiar em Recife e hoje se encontra em franca expansão por diversas cidades do Brasil.  O objetivo desta aplicação é fornecer uma base tecnológica moderna, robusta e escalável para padronizar as operações da franquia. A API centraliza e gerencia uma experiência de consumo integrada, suportando as seguintes regras de negócio:

- Multicanalidade: Suporte para pedidos originados de diferentes canais, como Aplicativo, Totem de autoatendimento, Balcão e Web.
- Gestão de Unidades e Estoque: Controle de disponibilidade de produtos e estoque individualizado para cada unidade da franquia.
- Pagamentos Desacoplados: Fluxo de transação simulada (mock) que prepara o sistema para comunicação assíncrona com gateways de pagamento externos.
- Segurança e Privacidade: Autenticação de clientes e funcionários com controle de acesso baseado em perfis, desenhado com foco na proteção de dados sensíveis e respeito à LGPD.

🚀 Como Executar e Testar

Para testar a API localmente, siga as instruções detalhadas abaixo.

A documentação está dividida em três partes:

1. [Configurações iniciais do ambiente](#configuracao-do-ambiente)
2. [Configurações do banco de dados](#configuracao-do-banco-de-dados)
3. [Utilização da API](#utilizacao-da-api)

---

<h2 id="configuracao-do-ambiente">Configuração do ambiente</h2>

1. Clonar o repositório do projeto utilizando o comando `git clone <link do repo>`

2. Navegar até a pasta do projeto utilizando o terminal do vs code.

3. Criar a venv digitando o comando  `python -m venv venv` no terminal do vs code.

4. Ativar a venv com o comando `.\venv\Scripts\activate.bat`.

5. Entrar na pasta do repositório do projeto utilizando o comando `cd <nome-da-pasta>`.

6. Rodar o comando `pip install -r requirements.txt` para instalar as bibliotecas necessárias.

7. Criar um arquivo `.env` na raiz do projeto e preenchê-lo utilizando o arquivo `.env.example` como modelo. Você pode utilizar o site https://acte.ltd/utils/randomkeygen para gerar uma chave secreta e utilizar no campo `SECRET_KEY` do arquivo `.env`.

Com essas configurações iniciais prontas você pode seguir para os próximos passos.

---

<h2 id="configuracao-do-banco-de-dados">Configuração do banco de dados</h2>

1. Rode o comando `alembic revision --autogenerate -m "migracao inicial"` para criar a migração inicial do banco de dados.

2. Rode o comando `alembic upgrade head` para aplicar a migração e criar as tabelas no banco de dados.

3. Verifique a criação das tabelas utilizando o próprio vs code com a extensão SQLite Viewer ou utilizando o DB Browser for SQLite (precisa ser instalado através do site https://sqlitebrowser.org/).

4. Rode o comando `python amostra_dados.py` para popular o banco de dados com dados de exemplo.

---

<h2 id="utilizacao-da-api">Utilização da API</h2>

1. Rode o comando `uvicorn main:app --reload` no terminal para iniciar a API. Caso deseje utilizar uma porta diferente da 8000 ou ela esteja demorando demais para carregar, utilize o comando `uvicorn main:app --reload --port <numero-da-porta>`.

2. Acesse a API através do endereço disponibilizado no terminal após rodar o comando acima, geralmente é `http://localhost:8000`.

3. Acesse a documentação interativa da API adicionando `/docs` ao endereço da API, ou seja, `http://localhost:8000/docs`. Nessa documentação interativa, você pode testar os endpoints da API e visualizar as respostas.

4. Para acessar os endpoints protegidos, faça o login utilizando o botão Authorize no canto superior direito da documentação.

5. Faça o login utilizando a credencial de um usuário que possui acesso ao endpoint que deseja testar. Você pode utilizar as credenciais do usuário admin criadas no arquivo `amostra_dados.py` ou criar um novo usuário utilizando o endpoint de cadastro.

---

<h3>Importante</h3>

Lembre-se que alguns endpoints possuem restrições de acesso, ou seja, apenas usuários com determinados papéis (roles) podem acessá-los. Certifique-se de utilizar um usuário com as permissões adequadas para acessar os endpoints desejados.

<h4>Permissões de acesso:</h4>

<ul>
    <li><strong>Cliente:</strong> Acesso a endpoints de login, criação e pagamento de pedidos.</li>
    <li><strong>Funcionário:</strong> Acesso a endpoints de login, criação, pagamento e listagem de pedidos da unidade em que está alocado.</li>
    <li><strong>Cozinha:</strong> Acesso a endpoints de listagem e atualização do status dos pedidos da unidade em que está alocado.</li>
    <li><strong>Gerente:</strong> Acesso a endpoints de gerenciamento e relatórios de desempenho da unidade em que está alocado.</li>
    <li><strong>Admin:</strong> Acesso total a todos os endpoints, incluindo gerenciamento de usuários e configurações do sistema.</li>
    Login padrão para teste:
    <strong>Admin:</strong> email: admin@raizes.com | senha: admin123</li>
</ul>