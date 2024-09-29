from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import pandas as pd
import folium
from pymongo import MongoClient
from src import bd

app = Flask(__name__)

# Configuração do MongoDB
MONGO_URI = os.getenv('MONGO_URI')
DATABASE_NAME = 'uber'
COLLECTION_NAME = 'viagens'

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Carregar do MongoDB
def carregar_dados_MongoDB(uri, db_name, colecao):
    client, db = bd.conectar_mongodb(uri, db_name)
    documentos = bd.buscar_documentos(db[colecao])
    df = pd.DataFrame(list(documentos))  # Convertendo documentos em DataFrame
    df['DataHora'] = pd.to_datetime(df['DataHora'])
    return df

# Funções de filtro
def filtrar_por_hora(df, hora_inicio, hora_fim):
    return df[(df['DataHora'].dt.time >= pd.to_datetime(hora_inicio).time()) & 
              (df['DataHora'].dt.time <= pd.to_datetime(hora_fim).time())]

def filtrar_por_dia_semana(df, dia_semana):
    return df[df['DiaSemana'] == dia_semana]

def filtrar_por_semana_mes(df, semana_mes):
    return df[df['SemanaMes'] == semana_mes]

def filtrar_por_mes_ano(df, mes_ano):
    return df[df['MesAno'] == mes_ano]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/aumente_seus_ganhos', methods=['GET', 'POST'])
def aumente_seus_ganhos():
    # Carregar dados
    df = carregar_dados_MongoDB(MONGO_URI, DATABASE_NAME, COLLECTION_NAME)

    # Aplicar filtros se fornecidos
    hora_inicio = request.args.get('hora_inicio', '23:00:00')
    hora_fim = request.args.get('hora_fim', '23:59:59')
    dia_semana = request.args.get('dia_semana')
    semana_mes = request.args.get('semana_mes', type=int)
    mes_ano = request.args.get('mes_ano', type=int)

    df_filtrado = filtrar_por_hora(df, hora_inicio, hora_fim)
    if dia_semana:
        df_filtrado = filtrar_por_dia_semana(df_filtrado, dia_semana)
    if semana_mes:
        df_filtrado = filtrar_por_semana_mes(df_filtrado, semana_mes)
    if mes_ano:
        df_filtrado = filtrar_por_mes_ano(df_filtrado, mes_ano)

    # Calcular a média dos preços no DataFrame filtrado
    media_preco = df_filtrado['Preco'].mean()

    # Adicionar uma coluna para a cor do marcador
    df_filtrado['Cor'] = df_filtrado['Preco'].apply(lambda x: 'green' if x > media_preco else 'red')

    # Criar um mapa centrado em São Paulo com estilo mais limpo
    mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=12, tiles='CartoDB positron')

    # Adicionar marcadores de origem e destino com cores baseadas no preço
    for _, row in df_filtrado.iterrows():
        popup_text = f"Preço: R${row['Preco']:.2f}<br>Média: R${media_preco:.2f}"

        if pd.notna(row['LatOrigem']) and pd.notna(row['LonOrigem']):
            folium.Marker(
                location=[row['LatOrigem'], row['LonOrigem']],
                popup=popup_text,
                icon=folium.Icon(icon='circle', color=row['Cor'])
            ).add_to(mapa)
            
        if pd.notna(row['LatDestino']) and pd.notna(row['LonDestino']):
            folium.Marker(
                location=[row['LatDestino'], row['LonDestino']],
                popup=popup_text,
                icon=folium.Icon(icon='circle', color=row['Cor'])
            ).add_to(mapa)

    return render_template('aumente_seus_ganhos.html', mapa=mapa._repr_html_())

############## Testar com os dados resultantes de web-scraper-uber-trips ##################################################
@app.route('/colabore', methods=['GET', 'POST'])
def colabore():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            try:
                # Ler o CSV em um DataFrame
                df = pd.read_csv(file, sep=';', encoding='utf-8', on_bad_lines='warn')  # Usa 'warn' para exibir avisos sobre linhas problemáticas
                
                # Conectar ao MongoDB
                client, db = bd.conectar_mongodb(MONGO_URI, DATABASE_NAME)
                colecao = bd.criar_colecao(db, COLLECTION_NAME)
                
                # Converter o DataFrame para uma lista de dicionários
                documentos = df.to_dict(orient='records')
                
                # Inserir documentos no MongoDB
                resultado = bd.inserir_multiplos_documentos(colecao, documentos)
                
                # Fechar a conexão com o MongoDB
                client.close()
                
                # Redirecionar após o sucesso
                return redirect(url_for('index'))
            except pd.errors.ParserError as e:
                return f"Erro ao processar o arquivo CSV: {e}", 400
            except Exception as e:
                return f"Erro ao inserir dados no MongoDB: {e}", 500
        else:
            return "Formato de arquivo não suportado. Por favor, envie um arquivo CSV.", 400

    return render_template('colabore.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
