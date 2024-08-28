from pymongo import MongoClient

# Configuração do cliente MongoDB
def conectar_mongodb(uri, db_name):
    client = MongoClient(uri)
    db = client[db_name]
    return client, db

def criar_colecao(db, nome_colecao):
    colecao = db[nome_colecao]
    return colecao

def inserir_documento(colecao, documento):
    resultado = colecao.insert_one(documento)
    return resultado.inserted_id

def inserir_multiplos_documentos(colecao, documentos):
    resultado = colecao.insert_many(documentos)
    return resultado.inserted_ids

def atualizar_documento(colecao, filtro, atualizacoes):
    resultado = colecao.update_many(filtro, {'$set': atualizacoes})
    return resultado.modified_count

def buscar_documentos(colecao, filtro=None):
    if filtro is None:
        filtro = {}
    documentos = colecao.find(filtro)
    return documentos

def deletar_documentos(colecao, filtro):
    resultado = colecao.delete_many(filtro)
    return resultado.deleted_count
