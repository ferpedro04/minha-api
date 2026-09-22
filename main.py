from fastapi import FastAPI
# fastapi -> Framework utilizado para criação da API.
# FastAPI -> Classe utilizada para criar e configurar a aplicação.

from pydantic import BaseModel, Field, field_validator
# field_validator -> Permite criar validações personalizadas para campos do modelo.
# BaseModel -> Classe base utilizada para criar modelos de dados.
# Field -> Permite definir regras de validação para os campos.

from fastapi.responses import JSONResponse
# JSONResponse -> Permite definir manualmente o status HTTP e o conteúdo da resposta JSON.

from fastapi.exceptions import RequestValidationError
# RequestValidationError -> Erro gerado pelo FastAPI quando os dados recebidos não atendem às validações dos modelos.

app = FastAPI()
# Cria a aplicação FastAPI que será responsável por disponibilizar os endpoints da nossa API.

def validar_nome_produto(nome):
    nome = nome.strip()

    if nome == "":
        raise ValueError("Nome inválido")

    return nome

class DadosNecessarios(BaseModel):
    nome: str
    preco: float = Field(ge=0)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome):
        return validar_nome_produto(nome)
# Modelo utilizado para definir os dados obrigatórios no cadastro de um produto.
# O nome e o preço são necessários para criar um novo produto.

class DadosAtualizacao(BaseModel):
    nome: str
    preco: float = Field(ge=0)
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome):
        return validar_nome_produto(nome)
# Modelo utilizado para receber os dados enviados durante a atualização de um produto. O ID não é necessário, pois ele é informado pela URL.
# O campo ativo pode ser alterado durante a atualização.

class Produto(BaseModel):
    id: int
    nome: str
    preco: float = Field(ge=0)
    ativo: bool = True
# Modelo que representa um produto completo dentro da API.
# O ID identifica o produto, o nome e o preço armazenam seus dados, e o campo ativo indica se o produto está ativo.
# O preço deve ser maior ou igual a zero e, por padrão, todo novo produto é criado como ativo.

class Respostas(BaseModel):
    erro: int
    codigo: int 
    mensagem: str
    data: Produto | list[Produto] | None
# Modelo responsável por padronizar as respostas da API.
# "erro" indica se a operação apresentou erro.
# "codigo" representa o código HTTP relacionado à resposta.
# "mensagem" informa o resultado da operação de forma textual.
# "data" contém os dados retornados ou None quando não houver dados.

produtos = []
# Lista utilizada para armazenar os produtos em memória durante a execução da API.

@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "erro": 1,
            "codigo": 422,
            "mensagem": "Dados inválidos.",
            "data": None
        }
    )
# Trata erros de validação dos dados enviados para a API.
# Quando os dados não atendem às regras dos modelos, a API retorna uma resposta JSON padronizada com o status HTTP 422.

@app.exception_handler(Exception)
async def tratar_erro_interno(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "erro": 1,
            "codigo": 500,
            "mensagem": "Erro interno",
            "data": None
        }
    )
# Trata erros internos inesperados da aplicação.
# Nesse caso, a API retorna uma resposta JSON padronizada com o status HTTP 500.

@app.get("/produtos", response_model= Respostas)
def listar_produtos(ativo: bool = None, preco: float = None):
    if (ativo is None) and (preco is None):
        return Respostas(
            erro=0,
            codigo= 200,
            mensagem="Produtos listados com sucesso",
            data=produtos
        )
    produtos_filtrados = []
    for produto in produtos:
        if (ativo is None or produto.ativo == ativo) and (preco is None or produto.preco >= preco):
            produtos_filtrados.append(produto)
    return Respostas(
        erro=0,
        codigo= 200,
        mensagem="Produtos filtrados com sucesso",
        data=produtos_filtrados
    )
# Endpoint responsável por listar os produtos cadastrados.
# Permite filtrar os resultados pelo status ativo e pelo preço mínimo.
# Quando os filtros não são informados, todos os produtos são retornados.

@app.get("/produtos/{id}", response_model= Respostas) 
def listar_produto(id: int, preco: float = None):
    for produto in produtos:
        if (id == produto.id) and (preco is None or produto.preco >= preco):
            return Respostas(
                erro= 0,
                codigo= 200,
                mensagem= "Produto localizado com sucesso",
                data= produto
            )
    return JSONResponse(
    status_code=404,
    content={
        "erro": 1,
        "codigo": 404,
        "mensagem": "Produto não localizado",
        "data": None
    }
)
# Endpoint responsável por buscar um produto específico pelo ID.
# Também permite informar um preço mínimo para validar o resultado.
# Caso o produto não seja encontrado ou não atenda ao preço informado, a API retorna uma resposta com status HTTP 404.

@app.post("/produtos", status_code=201, response_model = Respostas)
def postar_produto(produto: DadosNecessarios):
    maior_id = 0
    for produto_existente in produtos:
        if produto_existente.id > maior_id:
            maior_id = produto_existente.id

    proximo_id = maior_id + 1

    novo_produto = Produto(
        id=proximo_id,
        nome=produto.nome,
        preco=produto.preco
    )

    produtos.append(novo_produto)
    return Respostas(
        erro = 0,
        codigo= 201,
        mensagem= "Produto Cadastrado com sucesso",
        data = [novo_produto]
    )
# Endpoint responsável por cadastrar novos produtos.
# O ID é gerado automaticamente pela API e o produto é criado como ativo por padrão.
# O endpoint retorna status HTTP 201 quando o cadastro é realizado.

@app.put("/produtos/{id}", response_model= Respostas) 
def editar_produto(id: int, produto: DadosAtualizacao):
    for indice, produto_existente in enumerate(produtos):
        if id == produto_existente.id:
            produto_atualizado = Produto(
                id= id,
                nome= produto.nome,
                preco= produto.preco,
                ativo= produto.ativo
            )
            produtos[indice] = produto_atualizado
            return Respostas(
                erro= 0,
                codigo= 200,
                mensagem = "Produto atualizado com sucesso",
                data = produto_atualizado
            )
    return JSONResponse(
        status_code=404,
        content={
            "erro": 1,
            "codigo": 404,
            "mensagem": "Produto não localizado",
            "data": None
        }
)
# Endpoint responsável por atualizar um produto existente pelo ID.
# Quando o produto é encontrado, seus dados são substituídos pelos novos dados enviados na requisição.
# Caso o ID não seja encontrado, a API retorna status HTTP 404.

@app.delete("/produtos/{id}", response_model= Respostas)
def deletar_produto(id: int):
    for produto in produtos:
        if id == produto.id:
            produtos.remove(produto)
            return Respostas(
                erro= 0,
                codigo= 200,
                mensagem= "Produto removido com sucesso.",
                data= produto
)
    return JSONResponse(
            status_code=404,
            content={
                "erro": 1,
                "codigo": 404,
                "mensagem": "Produto não cadastrado ou já excluído.",
                "data": None
            }
)
# Endpoint responsável por remover um produto existente pelo ID.
# Quando o produto é encontrado, ele é removido da lista em memória e seus dados são retornados na resposta.
# Caso o ID não seja encontrado, a API retorna status HTTP 404.