from sqlalchemy import create_engine
from sqlalchemy import text
from dotenv import dotenv_values
import streamlit as st
import pandas as pd


class user_class:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __str__(self):
        return self.name


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
tables = pd.read_sql_query("""SELECT table_name
  FROM information_schema.tables
 WHERE table_schema='public'
   AND table_type='BASE TABLE';
""", con=engine)
tables = [t for t in tables["table_name"].tolist() if t != "temp_table"]
table = st.selectbox("Select table", options=tables[::-1])
users = pd.read_sql_query(f"select * from users", con=engine)
# entries = pd.read_sql_query(f"select * from diaryentries", con=engine)
df = pd.read_sql_query(f"select * from {table}", con=engine)
df = df.set_index(df.columns[0], drop=True)
pddict = {}
for col, dtype in df.dtypes.items():
    pddict[col] = pd.Series([], dtype=dtype)
add_df = pd.DataFrame(pddict)
mapper = {id_user: name for id_user, name in zip(users["userid"].tolist(),users["name"].tolist())}
#names = make_unique(list(mapper.values()))
if table == "diaryentries":
    temp_df = df[~df["delete"]].copy()
    temp_df["change_user"] = False
    temp_df["user_name"] = [mapper[x["userid"]] for ind, x in temp_df.iterrows()]
    edited = st.data_editor(
        temp_df,
        hide_index=True,
        column_config={
            "moodrating": st.column_config.SelectboxColumn(
                "Mood rating",
                options=list(range(11)),
                required=True,
            ),
            "userid": None,
            "user_name" : st.column_config.Column(disabled=True)
        },
    )
else:
    edited = st.data_editor(
        df[~df["delete"]].copy(),
        hide_index=True,
        column_config={
            "moodrating": st.column_config.SelectboxColumn(
                "Mood rating",
                options=list(range(11)),
                required=True,
            ),
        },
    )

if st.button("Edit data"):
    id_col = df.index.name
    with engine.begin() as conn:
        if table != "users": edited = edited.drop(["change_user", "user_name"], axis=1)
        edited_rows = edited[(df[~df["delete"]] != edited).sum(axis=1) > 0]
        if len(edited_rows) > 0:
            edited_rows.to_sql('temp_table', engine, if_exists='replace')
            for col in edited_rows.columns:
                sql = f"UPDATE {table} AS f SET {col} = t.{col} FROM temp_table AS t WHERE f.{id_col} = t.{id_col}"
                conn.execute(text(sql))
else:
    if table == "diaryentries":
        users = pd.read_sql_query(f"select * from users", con=engine)
        users = [user_class(x["name"], x["userid"]) for ind, x in users.iterrows()]
        change_df = edited[edited["change_user"]]
        with st.form("form"):
            st.write("Edit user for chosen entry")
            label_select = "No entry selected" if len(change_df) == 0 else change_df.iloc[0, :]["textcontent"]
            new_user = st.selectbox(options=users, label=label_select)
            b = st.form_submit_button("change")
            if b:
                with engine.begin() as conn:
                    sql = f"UPDATE {table} AS f SET userid = {new_user.id} WHERE entryid = {change_df.index[0]}"
                    conn.execute(text(sql))
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
if st.button("Add data"):
    last_ind = max(df.index) + 1
    added.index = list(range(last_ind, last_ind + len(added)))
    added["delete"] = False
    if len(added) > 0:
        with engine.begin() as conn:
            added.to_sql('temp_table', engine, if_exists='replace')
            sql = f"INSERT INTO {table} (SELECT * FROM temp_table)"
            conn.execute(text(sql))
            add_df = None
    st.write("Done")

