import pandas as pd
import joblib
import streamlit as st
from io import BytesIO

st.set_page_config(layout='wide', page_icon="📈",page_title="Categorizador - v0.2")

@st.cache_data
def load_data():
    vector = joblib.load('vetorizador.pkl')
    model_class = joblib.load('modelo_GRIDSEARCH_balanceado.pkl')
    vector_rec_1 = joblib.load('vetorizador_rec.pkl')
    model_rec_1 = joblib.load('modelo_GRIDSEARCH_rec.pkl')
    vector_gest_1 = joblib.load('vetorizador_gest.pkl')
    model_gest_1 = joblib.load('modelo_GRIDSEARCH_gest.pkl')
    return vector, model_class, vector_rec_1, model_rec_1, vector_gest_1, model_gest_1

vectorizer, model, vector_rec, model_rec, vector_gest, model_gest = load_data()

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

    def categoriza_rf(dataset):
        df_novos_ativos_rf = pd.read_excel(uploaded_file,sheet_name='Renda Fixa')
        df_novos_ativos_rf.fillna('',inplace = True)

        dataset = pd.DataFrame()
        dataset['Ativo'] = df_novos_ativos_rf['asset_name']
        dataset['Categoria'] = df_novos_ativos_rf['class'].str.upper()
        dataset['Recomendação'] = df_novos_ativos_rf['class'].apply(lambda x: 'NÃO' if 'COE' in x else 'PORTFEL')
        dataset['Tipo Gestão'] = df_novos_ativos_rf['class'].apply(lambda x: 'ATIVO' if 'COE' in x else 'PASSIVO')
        dataset['Origem'] = df_novos_ativos_rf['class'].apply(lambda x: 'OUTROS' if 'COE' in x else 'BANCÁRIO')

        return dataset

    if uploaded_file is not None:
        df_novos_ativos = pd.read_excel(uploaded_file)
        df_novos_ativos.fillna('', inplace=True)

        df_renda_fixa_categorizado = categoriza_rf(uploaded_file)


        df_novos_ativos_names = pd.DataFrame()
        df_novos_ativos_names['Ativos'] = (df_novos_ativos['asset_name'] + " " +
                                           df_novos_ativos['category'] + " " +
                                           df_novos_ativos['sub_category'] + " " +
                                           df_novos_ativos['category_fixed_income'] + " " +
                                           df_novos_ativos['index_fixed_income'] + " " +
                                           df_novos_ativos['percentual_index_fixed_income']
                                           )

        # Categorização: Classificação
        X_novos_ativos = vectorizer.transform(df_novos_ativos_names['Ativos'])

        categorias = model.predict(X_novos_ativos)

        df_categorizado = pd.DataFrame()
        df_categorizado['Ativo'] = df_novos_ativos['asset_name']
        df_categorizado['Categoria'] = categorias

        # Categorização: Recomendação Portfel
        df_novos_ativos_names_rec = df_categorizado['Ativo']

        X_novos_ativos_rec = vector_rec.transform(df_novos_ativos_names_rec)
        recomendacao = model_rec.predict(X_novos_ativos_rec)
        df_categorizado['Recomendação'] = recomendacao

        # Categorização: Tipo de gestão
        df_novos_ativos_names_gest = df_categorizado['Ativo']

        X_novos_ativos_gest = vector_gest.transform(df_novos_ativos_names_gest)
        gestao = model_gest.predict(X_novos_ativos_gest)
        df_categorizado['Tipo Gestão'] = gestao

        # Atribui a origem para ativos bancários
        df_categorizado['Origem'] = df_categorizado['Ativo'].apply(
            lambda x: 'BANCÁRIO' if any(substr in x for substr in ['CDB','LCI','LCA']) else 'OUTROS')

        # Filtra ativos bancários como PASSIVO caso o algoritimo classifique como ATIVO
        df_categorizado.loc[
            (df_categorizado['Origem'] == 'BANCÁRIO') & (df_categorizado['Tipo Gestão'] == 'ATIVO'),
            'Tipo Gestão'] = 'PASSIVO'

        # Remove duplicatas
        df_categorizado = df_categorizado.drop_duplicates(subset='Ativo')

        st.markdown("### Ativos categorizados")
        df_final = pd.concat([df_categorizado,df_renda_fixa_categorizado], ignore_index=True)
        st.dataframe(df_final)


        # Converte o DataFrame para um arquivo Excel
        def convert_df_to_excel(df):
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Assets")
            buffer.seek(0)  # Retorna o ponteiro para o início do buffer
            return buffer


        # Gera o arquivo Excel
        excel_data = convert_df_to_excel(df_final)

        st.download_button("Download", data=excel_data, file_name="pre-categorized-assets.xlsx", mime="text/xlsx")

    if st.button("Sair"):
        st.session_state.authenticated = False







