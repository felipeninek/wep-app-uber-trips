from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import pandas as pd
import folium
import os
from pymongo import MongoClient
import src.bd  # Importa funções do arquivo bd.py
import src.pre_processamento as pre_proc

app = Flask(__name__)

# Configuração do MongoDB
MONGO_URI = 'mongodb://localhost:27017/'  # Substitua pela URI do seu MongoDB
DATABASE_NAME = 'uber'
COLLECTION_NAME = 'viagens'

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Carregar e filtrar dados ###### depois essa funcao passara a carregar dados do monbodb
def carregar_dados():
    data = list(collection.find())  # Buscar todos os documentos da coleção
    df = pd.DataFrame(data)  # Converter os documentos em um DataFrame
    df['DataHora'] = pd.to_datetime(df['DataHora'])  # Converter a coluna 'DataHora' para datetime
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

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/mapa_com_filtros', methods=['GET', 'POST'])
def mapa_com_filtros():
    # Carregar dados
    df = carregar_dados()

    # Aplicar filtros se fornecidos
    hora_inicio = request.args.get('hora_inicio', '00:00:00')
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

    # Salvar o mapa em um arquivo HTML dentro da pasta 'static'
    mapa_path = os.path.join('static', 'mapa_com_filtros.html')
    mapa.save(mapa_path)

    return render_template('mapa_com_filtros.html', mapa_path='mapa_com_filtros.html')


@app.route('/')
def index():
    # Carregar dados
    df = carregar_dados()

    # Aplicar filtros se fornecidos
    hora_inicio = request.args.get('hora_inicio', '00:00:00')
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

    ########## desconsiderar filtro
    df_filtrado = df.copy()

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

    # Salvar o mapa em um arquivo HTML dentro da pasta 'static'
    mapa_path = os.path.join('static', 'mapa_origem_destino_filtrado.html')
    mapa.save(mapa_path)

    return render_template('index.html', mapa_path='mapa_origem_destino_filtrado.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            # Passo 1: Carregar o CSV
            df = pre_proc.carregar_dados(file)

            # Passo 2: Aplicar as funções de pré-processamento
            df_limpo = pre_proc.limpar_dados(df)
            df_processado = pre_proc.converter_colunas(df_limpo)

            # Passo 3: Inserir os dados processados no MongoDB
            data = df_processado.to_dict(orient='records')
            collection.insert_many(data)

            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
