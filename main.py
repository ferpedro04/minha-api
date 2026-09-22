from fastapi import FastAPI, HTTPException
# fastapi -> Framework utilizado para criação de APIs em Python.
# FastAPI -> Classe utilizada para criar e configurar a aplicação.
# HTTPException -> Exceção utilizada para retornar erros HTTP.

from pydantic import BaseModel, Field, field_validator
# pydantic -> Biblioteca utilizada para validação e estruturação de dados.
# BaseModel -> Classe base utilizada para criar modelos de dados e realizar validações.
# Field -> Função utilizada para definir regras e configurações específicas dos campos do modelo.

from fastapi.responses import JSONResponse

from fastapi.exceptions import RequestValidationError

app = FastAPI()
# Cria a aplicação FastAPI

class DadosNecessarios(BaseModel):
    nome: str
    preco: float = Field(ge=0)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome):
        nome = nome.strip()

        if nome == "":
            raise ValueError("Nome inválido")

        return nome
#Define os dados necessários do produto.

class Produto(BaseModel):
    id: int
    nome: str
    preco: float = Field(ge=0)
    ativo: bool = True
# Define a estrutura e as regras de validação dos produtos, além de definir o ID do produto e deixá-lo ativo.
# Field(ge=0) define o preço como número decimal e impede valores menores que 0.

class Respostas(BaseModel):
    erro: int
    codigo: int | None = None
    mensagem: str
    data: Produto | list[Produto] | None


produtos = []
# Lista utilizada para armazenar os produtos em memória durante a execução da API.

@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "erro": 1,
            "codigo": 422,
            "mensagem": "Nome e/ou preço inválido(s)",
            "data": None
        }
    )

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

@app.get("/produtos", response_model=Respostas)
def listar_produtos(ativo: bool = None, preco: float = None):
    if (ativo is None) and (preco is None):
        return Respostas(
            erro=0,
            mensagem="Produtos listados com sucesso",
            data=produtos
        )
    produtos_filtrados = []
    for produto in produtos:
        if (ativo is None or produto.ativo == ativo) and (preco is None or produto.preco >= preco):
            produtos_filtrados.append(produto)
    return Respostas(
        erro=0,
        mensagem="Produtos filtrados com sucesso",
        data=produtos_filtrados
    )
# Endpoint responsável por listar e filtrar produtos pelo status ativo.

@app.get("/produtos/{id}") 
def listar_produto(id: int, preco: float = None):
    for produto in produtos:
        if (id == produto.id) and (preco is None or produto.preco >= preco):
            return Respostas(
                erro= 0,
                mensagem= "Produto localizado com sucesso",
                data= [produto]
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
# Endpoint criado para buscar um produto específico pelo ID.

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
        mensagem= "Produto Cadastrado com sucesso",
        data = [novo_produto]
    )
# Endpoint criado para postar um produto

@app.put("/produtos/{id}") 
def editar_produto(id: int, produto: Produto):
    for indice, produto_existente in enumerate(produtos):
        if id == produto_existente.id:
            produto.id = id
            produtos[indice] = produto
            return Respostas(
                erro= 0,
                mensagem = "Produto atualizado com sucesso",
                data = [produto]
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
# Endpoint criado para editar um produto

@app.delete("/produtos/{id}")
def deletar_produto(id: int):
    for produto in produtos:
        if id == produto.id:
            produtos.remove(produto)
            return Respostas(
                erro= 0,
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
# Endpoint criado para deletar um produto