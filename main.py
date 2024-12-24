import pandas as pd
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

import joblib
roda_modelo = True

dataset_assets = pd.read_excel('portfel-product-list.xlsx')
dataset_assets['Classificação Portfel'] = dataset_assets['Classificação Portfel'].str.upper()

st.set_page_config(layout="wide")
st.dataframe(dataset_assets['Classificação Portfel'].groupby(dataset_assets['Classificação Portfel']).count().sort_values(ascending=False))

dataset_assets['Classificação Portfel'] = dataset_assets['Classificação Portfel'].apply(lambda x: "OUTROS" if x in ["PRIVATE EXTERIOR",
                                                                                                                    "PRIVATE BRASIL",
                                                                                                                    "EXTERIOR - MULTIMERCADO",
                                                                                                                    "CAIXA",
                                                                                                                    "OURO",
                                                                                                                    "AÇÕES - LONG BIASED"] else x)

dataset_assets.fillna("",inplace = True)

dataset_assets_categorizado = pd.DataFrame()
dataset_assets_categorizado['Ativo'] = dataset_assets['Ativo'].astype(str) + " " + dataset_assets['Classificação Portfel']

st.dataframe(dataset_assets['Classificação Portfel'].groupby(dataset_assets['Classificação Portfel']).count().sort_values(ascending=False))


#===========================================================================================================================
if roda_modelo:
    # Converter os nomes dos ativos em vetores numéricos usando o TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(dataset_assets_categorizado['Ativo'].astype(str))
    y = dataset_assets['Classificação Portfel']

    #Salvar o vetor
    joblib.dump(vectorizer, 'C:/Users/guilh/Desktop/tratamento-assets/vetorizador.pkl')

    # Passo 3: Dividir os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=0.3,
                                                        random_state=42,
                                                        stratify=y)
    param_grid = {
        "n_estimators": [100, 200, 300, 400,500],
        "max_depth": [10, 15, 20],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 5, 10],
        "class_weight": ["balanced", "balanced_subsample"]
    }

    model = GridSearchCV(
        estimator=RandomForestClassifier(random_state=42, criterion ='entropy'),
        param_grid=param_grid,
        scoring="f1_weighted",
        cv=3,
        verbose=2
    )

    st.write("Rodando o modelo")
    model.fit(X_train, y_train)

    # Passo 5: Avaliar o modelo
    y_pred = model.predict(X_test)
    st.write("Modelo gerado")

    # Parâmetros e modelo final
    melhores_parametros = model.best_params_
    modelo_final = model.best_estimator_
    st.write("Melhores parâmetros")
    st.write(melhores_parametros)
    st.write("Melhor modelo")
    st.write(modelo_final)

    #Salvar o modelo
    joblib.dump(model, 'C:/Users/guilh/Desktop/tratamento-assets/modelo_GRIDSEARCH_balanceado.pkl')

