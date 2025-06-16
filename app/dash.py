"""App Dashboard Projeto Vitivinicultura"""
import os
import sys
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import PowerTransformer

# Caminho absoluto da raiz do projeto (onde está a pasta 'src')
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Adiciona ao sys.path se não estiver lá
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
from src.train import visualizar_coluna_por_cluster_streamlit

# Configurações da página
st.set_page_config(
    page_title="Dashboard Embrapa",
    page_icon="img/logo_uva.png",
    layout="wide"
)

# instância da variável que recebe o endereço da api em produção
API_URL = st.secrets.get("API_URL", "https://sua-api-em-producao.com")

# verificação de state da aplicação
if "token" not in st.session_state:
    st.session_state.token = None
if "data_carregada" not in st.session_state:
    st.session_state.data_carregada = False
    st.session_state.df = None
    st.session_state.X_transformed = None

# título e cabeçalho
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("img/fiap.png", width=400)
    st.markdown("""
        <h1 style='text-align: center; color: gray;'>Dados Exportação Vitivinicultura Embrapa</h1>
        <h3 style='text-align: center; color: pink;'>Análise interativa de categorizacao de países</h3>
    """, unsafe_allow_html=True)
    st.markdown("""
        Esse aplicativo foi desenvolvido para ajudar na análise do perfil dos países compradores de produtos de Vitivinicultura.
        Você pode escolher o número de categorias, visualizar os resultados em gráficos interativos e baixar os dados processados com a categoria atribuída.
    """)

st.markdown("---")

# autenticação do usuário
st.subheader("Autenticação")
usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password")

# construção de um botão para realizar autenticação via token
if st.button("Login"):
    try:
        auth_url = f"{API_URL}/auth/token"
        response = requests.post(
            auth_url, data={"username": usuario, "password": senha}, timeout=10)
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                st.session_state.token = token
                st.success("✅ Login realizado com sucesso!")
            else:
                st.error("❌ Não foi possível obter o token.")
        else:
            st.error(f"❌ Erro no login: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Falha na autenticação: {e}")

if not st.session_state.token:
    st.warning("⚠️ Faça login para acessar o dashboard.")
    st.stop()

# slider com o número de clusters
n_clusters = st.slider("Selecione o número de categorias:", 2, 11, 2)

# construção de um botão para gerar os visuis de dados a partir da chamada de api do modelo
if st.button("Gerar Visualizações"):
    try:
        clustering_url = f"{API_URL}/clustering"
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        payload = {"categorias": n_clusters}
        # realiza a requisição dos dados no endereço da api com o parâmetro payload
        response = requests.post(
            clustering_url, json=payload, headers=headers, timeout=15)

        if response.status_code == 201:
            # recebe os dados da api no formato json e transforma no formato dataframe
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
                if 'categoria' not in df.columns:
                    st.error(
                        "Erro: coluna 'categoria' não está presente nos dados retornados pela API.")
                    st.stop()

                X = df.drop(columns=['pais'])
                transformer = PowerTransformer(
                    method='yeo-johnson', standardize=True)
                output = transformer.fit_transform(
                    X.drop(columns=['categoria']))
                X_transformed = pd.DataFrame(
                    output, columns=[col for col in X.columns if col != 'categoria'])
                X_transformed['categoria'] = df['categoria']

                # armazena os dados em state para recuperação dos visuais.
                st.session_state.df = df
                st.session_state.X_transformed = X_transformed
                st.session_state.data_carregada = True

                st.success("✅ Dados carregados com sucesso!")
            else:
                st.error("❌ Resposta da API não está no formato esperado.")
        elif response.status_code == 401:
            st.error("⚠️ Token expirado ou inválido. Faça login novamente.")
            st.session_state.token = None
        else:
            st.error(f"❌ Erro na API: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Falha na requisição: {e}")

# Visualizações dos dados carregados
if st.session_state.data_carregada:
    X_transformed = st.session_state.X_transformed
    df = st.session_state.df

    # visual scatterplot dos clusters a partir de dados transformados via pca
    st.subheader("Distribuição dos Países")
    pca = PCA(n_components=2)
    components = pca.fit_transform(X_transformed.drop(columns=['categoria']))

    fig_pca, ax = plt.subplots(figsize=(4, 2))
    sns.scatterplot(
        x=components[:, 0],
        y=components[:, 1],
        hue=X_transformed['categoria'],
        palette='deep',
        ax=ax
    )
    ax.legend(loc='upper right', fontsize=8)
    ax.set_title(
        'Análise da distribuição das categorias por influência de dados.', fontsize=8)
    ax.set_xlabel('Influência Indicadores Socioeconômicos', fontsize=7)
    ax.set_ylabel('Influência Indicadores de Transação', fontsize=7)

    st.pyplot(fig_pca)

    # visual striplot das features por clusters
    st.subheader("Análise dos dados da tabela por categoria")
    coluna_selecionada = st.selectbox(
        "Selecione a coluna para visualizar:",
        options=[col for col in X_transformed.columns if col != 'categoria']
    )
    st.write(f"### Visualização de: {coluna_selecionada}")
    fig = visualizar_coluna_por_cluster_streamlit(
        X_transformed, coluna=coluna_selecionada)
    st.pyplot(fig)

    # tabela para download dos dados com os clusters inseridos
    st.subheader("Tabela de Resultados")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Baixar tabela em CSV",
        data=csv,
        file_name='resultado_clusters.csv',
        mime='text/csv'
    )
