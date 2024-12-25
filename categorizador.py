import pandas as pd
import joblib
import streamlit as st
from io import BytesIO

st.set_page_config(layout='wide', page_icon="📈",page_title="Categorizador - v0.1")

@st.cache_data
def load_data():
    vector = joblib.load('vetorizador.pkl')
    model_class = joblib.load('modelo_GRIDSEARCH_balanceado.pkl')
    return vector, model_class

vectorizer, model = load_data()

PASSWORD = st.secrets["general"]["PASSWORD"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.password == PASSWORD:
        st.session_state.authenticated = True
        del st.session_state.password  # Remove a senha da memória
    else:
        st.error("Senha incorreta!")

if not st.session_state.authenticated:
    st.title("Acesso Restrito")
    st.text_input("Digite a senha 🔑", type="password", key="password")
    st.button("Entrar", on_click=check_password)
else:

    st.title("Categorizador de ativos")
    st.write("Você está autenticado ✅")

    # Passo 6: Usar o modelo para prever em novos dados
    # Carregar a nova planilha com os nomes dos ativos

    uploaded_file = st.file_uploader("Upload", type='xlsx', label_visibility="hidden")

    if uploaded_file is not None:
        df_novos_ativos = pd.read_excel(uploaded_file)

        df_novos_ativos.fillna('', inplace=True)

        df_novos_ativos_names = pd.DataFrame()
        df_novos_ativos_names['Ativos'] = (df_novos_ativos['asset_name'] + " " +
                                           df_novos_ativos['category'] + " " +
                                           df_novos_ativos['sub_category'] + " " +
                                           df_novos_ativos['category_fixed_income'] + " " +
                                           df_novos_ativos['index_fixed_income'] + " " +
                                           df_novos_ativos['percentual_index_fixed_income']
                                           )

        X_novos_ativos = vectorizer.transform(df_novos_ativos_names['Ativos'])
        categorias = model.predict(X_novos_ativos)

        df_categorizado = pd.DataFrame()
        df_categorizado['Ativo'] = df_novos_ativos['asset_name']
        df_categorizado['Categoria'] = categorias
        df_categorizado['Broker'] = df_novos_ativos['broker']
        df_categorizado['Emissor'] = df_novos_ativos['issuer_name']

        st.markdown("### Ativos categorizados")
        st.dataframe(df_categorizado)


        # Converte o DataFrame para um arquivo Excel
        def convert_df_to_excel(df):
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Assets")
            buffer.seek(0)  # Retorna o ponteiro para o início do buffer
            return buffer


        # Gera o arquivo Excel
        excel_data = convert_df_to_excel(df_categorizado)

        st.download_button("Download", data=excel_data, file_name="pre-categorized-assets.xlsx", mime="text/xlsx")

    if st.button("Sair"):
        st.session_state.authenticated = False







