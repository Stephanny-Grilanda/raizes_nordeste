# Documentação de Testes com Postman

Este documento descreve como testar a API "Raízes do Nordeste" usando a coleção Postman fornecida. Pressupõe-se que as instruções do README já foram seguidas (dependências instaladas, banco configurado e a aplicação consegue ser iniciada).

## Arquivos relevantes
- Coleção Postman: testes/API Raízes do Nordeste.postman_collection.json
- Script opcional de dados de teste: amostra_dados.py

## Iniciar a API
No diretório do projeto, iniciar a aplicação (exemplo):
```powershell
# executar a partir da raiz do projeto
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```
A API deve ficar disponível em http://127.0.0.1:8000 (padrão usado na coleção).

## Popular dados de teste (opcional)
Se desejar dados fictícios para testar fluxos administrativos e de cliente:
```powershell
python amostra_dados.py
```
(O script insere clientes, funcionários, unidades, produtos e estoques.)

## Importar e configurar a coleção no Postman
1. Em Postman → Import → escolha o ficheiro:
   testes/API Raízes do Nordeste.postman_collection.json
2. Criar/selecionar um Environment no Postman e definir a variável:
   - baseUrl = http://127.0.0.1:8000
3. Ativar o Environment antes de rodar as requests.

## Fluxo de teste sugerido
1. Criar um cliente (request de cadastro).
2. Fazer login do cliente (JSON) — obter access_token.
3. No Environment, salvar o token (ou usar Authorization → Bearer Token).
4. Nos requests protegidos, usar o header:
   Authorization: Bearer {{accessToken}}
5. Testar endpoints principais:
   - Pedidos: criação, listagem e atualização (respeitar regras de permissão e canais).
   - Pagamentos (mock): simular sucesso/falha usando o campo simular_falha.
   - Cardápio/Estoque por unidade.
6. Para operações administrativas (criar funcionário, atualizar pedidos com permissões), autenticar com um funcionário ADMIN/Gerente e usar o token resultante.
   - Se usou amostra_dados.py, existe um admin com email `admin@raizes.com`.

## Importante
Sempre que for testar endpoints protegidos, certifique-se de que o token JWT válido esteja sendo enviado no header Authorization. Caso contrário, a API retornará 401 Unauthorized.

## Exemplos de testes
Na pasta [imagens](Imagens-Testes/) você encontrará o resultado dos testes que foram realizados utilizando a coleção Postman disponibilizada. As imagens mostram a execução de requests, respostas e status codes esperados.