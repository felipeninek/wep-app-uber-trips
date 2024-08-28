from pymongo import MongoClient

# Configuração do cliente MongoDB
def conectar_mongodb(uri, db_name):
    """
    Conecta ao MongoDB e retorna o cliente e o banco de dados.

    :param uri: URI de conexão com o MongoDB.
    :param db_name: Nome do banco de dados.
    :return: Cliente MongoDB e banco de dados.
    """
    client = MongoClient(uri)
    db = client[db_name]
    return client, db

def criar_colecao(db, nome_colecao):
    """
    Cria uma nova coleção no banco de dados.

    :param db: Banco de dados.
    :param nome_colecao: Nome da coleção a ser criada.
    :return: Referência para a nova coleção.
    """
    colecao = db[nome_colecao]
    return colecao

def inserir_documento(colecao, documento):
    """
    Insere um documento na coleção.

    :param colecao: Coleção onde o documento será inserido.
    :param documento: Documento a ser inserido.
    :return: ID do documento inserido.
    """
    resultado = colecao.insert_one(documento)
    return resultado.inserted_id

def inserir_multiplos_documentos(colecao, documentos):
    """
    Insere múltiplos documentos na coleção.

    :param colecao: Coleção onde os documentos serão inseridos.
    :param documentos: Lista de documentos a serem inseridos.
    :return: Lista de IDs dos documentos inseridos.
    """
    resultado = colecao.insert_many(documentos)
    return resultado.inserted_ids

def atualizar_documento(colecao, filtro, atualizacoes):
    """
    Atualiza documentos na coleção.

    :param colecao: Coleção onde os documentos serão atualizados.
    :param filtro: Filtro para selecionar os documentos a serem atualizados.
    :param atualizacoes: Atualizações a serem aplicadas.
    :return: Número de documentos modificados.
    """
    resultado = colecao.update_many(filtro, {'$set': atualizacoes})
    return resultado.modified_count

def buscar_documentos(colecao, filtro=None):
    """
    Busca documentos na coleção.

    :param colecao: Coleção onde a busca será realizada.
    :param filtro: Filtro para selecionar os documentos (opcional).
    :return: Cursor com os documentos encontrados.
    """
    if filtro is None:
        filtro = {}
    documentos = colecao.find(filtro)
    return documentos

def deletar_documentos(colecao, filtro):
    """
    Deleta documentos na coleção.

    :param colecao: Coleção onde os documentos serão deletados.
    :param filtro: Filtro para selecionar os documentos a serem deletados.
    :return: Número de documentos deletados.
    """
    resultado = colecao.delete_many(filtro)
    return resultado.deleted_count
