from sqlalchemy import create_engine
from sqlalchemy import text
from dotenv import dotenv_values
import streamlit as st
import pandas as pd


st.set_page_config(layout="wide")
values = dotenv_values()
name = values["NAME"]
user = values["USER"]
password = values["PASSWORD"]
port = int(values["PORT"])
engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@localhost:{port}/{name}"
)

st.header("Хомякова Лилия Сергеевна, 4 группа, 4 курс")
mapper = {"Users": "Users", "Diary Entries": "DiaryEntries"}
table = st.selectbox("Select table", options=mapper.keys())
df = pd.read_sql_query(f"select * from {mapper[table]}", con=engine)
df = df.set_index(df.columns[0], drop=True)
pddict = {}
for col, dtype in df.dtypes.items():
    pddict[col] = pd.Series([], dtype=dtype)
add_df = pd.DataFrame(pddict)
edited = st.data_editor(
    df[~df["delete"]],
    hide_index=True,
    column_config={
        "moodrating": st.column_config.SelectboxColumn(
            "Mood rating",
            options=list(range(11)),
            required=True,
        ),
    },
)
added = st.data_editor(
    add_df,
    hide_index=True,
    num_rows="dynamic",
    column_config={
        "moodrating": st.column_config.SelectboxColumn(
            "Mood rating",
            options=list(range(11)),
            required=True,
        ),
        "delete": None,

    },
)
if st.button("Change data"):
    id_col=df.columns[0]
    last_ind = max(df.index) + 1
    added.index = list(range(last_ind, last_ind + len(added)))
    added["delete"] = False
    with engine.begin() as conn:
        edited_rows = edited[(df != edited).sum(axis=1) > 0]
        if len(edited_rows) > 0:
            edited_rows.to_sql('temp_table', engine, if_exists='replace')
            for col in edited_rows.columns:
                sql = f"UPDATE {mapper[table]} AS f SET {col} = t.{col} FROM temp_table AS t WHERE f.{id_col} = t.{id_col}"
                conn.execute(text(sql))
        if len(added) > 0:
            added.to_sql('temp_table', engine, if_exists='replace')
            sql = f"INSERT INTO {mapper[table]} (SELECT * FROM temp_table)"
            conn.execute(text(sql))
    st.write("Done")


