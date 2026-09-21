from fastapi import FastAPI, HTTPException
# fastapi -> Framework utilizado para criação de APIs em Python.
# FastAPI -> Classe utilizada para criar e configurar a aplicação.
# HTTPException -> Exceção utilizada para retornar erros HTTP.

from pydantic import BaseModel, Field, field_validator
# pydantic -> Biblioteca utilizada para validação e estruturação de dados.
# BaseModel -> Classe base utilizada para criar modelos de dados e realizar validações.
# Field -> Função utilizada para definir regras e configurações específicas dos campos do modelo.

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

class Produto(BaseModel):
    id: int
    nome: str
    preco: float = Field(ge=0)
    ativo: bool = True
# Define a estrutura e as regras de validação dos produtos.
# Field(ge=0) define o preço como número decimal e impede valores menores que 0.

produtos = []
# Lista utilizada para armazenar os produtos em memória durante a execução da API.

@app.get("/produtos")
def listar_produtos(ativo: bool = None):
    if ativo is None:
        return(produtos)
    produtos_ativos = []
    for produto in produtos:
        if produto.ativo == ativo:
            produtos_ativos.append(produto)
    return(produtos_ativos)
# Endpoint responsável por listar e filtrar produtos pelo status ativo.

@app.get("/produtos/{id}") 
def listar_produto(id: int):
    for produto in produtos:
        if id == produto.id:
            return produto
    raise HTTPException(status_code=404)
# Endpoint criado para buscar um produto específico pelo ID.

@app.post("/produtos", status_code=201)
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
    return novo_produto
# Endpoint criado para postar um produto

@app.put("/produtos/{id}") 
def editar_produto(id: int, produto: Produto):
    for indice, produto_existente in enumerate(produtos):
        if id == produto_existente.id:
            produto.id = id
            produtos[indice] = produto
            return produto
    raise HTTPException(status_code=404)
# Endpoint criado para editar um produto

@app.delete("/produtos/{id}")
def deletar_produto(id: int):
    for produto in produtos:
        if id == produto.id:
            produtos.remove(produto)
            return("Produto removido com sucesso. Pode encerrar a função")
    raise HTTPException(status_code=404)
# Endpoint criado para deletar um produto