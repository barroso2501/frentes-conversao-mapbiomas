"""
io.py — carregamento e junção dos CSVs exportados do GEE.

Por que este módulo existe: os CSVs do Earth Engine (exportados via Drive) saem
com separador ';' e decimal vírgula (','), então TODAS as colunas numéricas vêm
como TEXTO. Ler com pandas padrão silenciosamente trata "1,5" como string e
qualquer soma vira concatenação ou erro. Este módulo centraliza a conversão para
não repetir esse cuidado em todo script.

O que pode quebrar e como você perceberia:
 - Se um CSV vier com separador diferente (vírgula), a leitura joga tudo numa
   coluna só. Sintoma: df com 1 coluna. Ajuste `sep`.
 - Se cell_id vier como float (ex.: "123.0"), a junção por período falha
   silenciosamente. Aqui forçamos cell_id para inteiro.
 - Se faltar um período, a tabela mestre fica com menos linhas que
   n_células * 8. O script 00 checa isso e avisa.
"""

from pathlib import Path
import pandas as pd


# colunas que devem permanecer categóricas / identificadoras (não converter p/ float)
COLS_ID = {"cell_id", "periodo", "ano_ini", "bioma", "UT"}


def _to_num(serie: pd.Series) -> pd.Series:
    """Converte uma coluna texto com decimal vírgula para float.
    Trata vazio/espaco como 0.0 (área ausente = zero hectares, não NaN)."""
    return (
        serie.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)   # remove separador de milhar se houver
        .str.replace(",", ".", regex=False)  # vírgula decimal -> ponto
        .replace({"": "0", "nan": "0", "None": "0"})
        .astype(float)
    )


def ler_csv_gee(caminho: str | Path) -> pd.DataFrame:
    """Lê um CSV do GEE convertendo colunas numéricas corretamente."""
    df = pd.read_csv(caminho, sep=";", dtype=str)
    # remove a coluna de geometria que o GEE às vezes injeta
    df = df.drop(columns=[c for c in df.columns if c.lower() in {".geo", "system:index"}],
                 errors="ignore")
    for col in df.columns:
        if col not in COLS_ID:
            df[col] = _to_num(df[col])
    if "cell_id" in df.columns:
        df["cell_id"] = df["cell_id"].astype(float).astype("int64")
    return df


def ler_muitos(padrao_glob: str, pasta: str | Path) -> pd.DataFrame:
    """Concatena vários CSVs (ex.: os 8 períodos, ou os lotes de cell_id)."""
    pasta = Path(pasta)
    arquivos = sorted(pasta.glob(padrao_glob))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo casou {padrao_glob} em {pasta}")
    return pd.concat((ler_csv_gee(a) for a in arquivos), ignore_index=True)
