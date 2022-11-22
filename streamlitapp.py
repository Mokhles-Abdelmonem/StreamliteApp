import pandas as pd
import streamlit as st
import plotly.express as px
from io import StringIO
import os
import requests

# from views import BaseData, SaveData




# ---- BODY ----
st.set_page_config(page_title='Streamlite visualization')


st.header('Simple visualization of Data ')

def fetch():
    query_params = st.experimental_get_query_params()
    token = query_params["token"][0]
    json = {"token":token}
    url = "https://data-production-4fc9.up.railway.app/discoverdata/rest-api-file/"
    result = requests.post(url,json=json)
    st.subheader(result)

    data = result.json()["data"]
    data = StringIO(data)
    df = pd.read_csv(data, sep=",")
    return df



df = fetch()


try :

    
    # ---- READ DATA FRAME ----

    def fetch():
        query_params = st.experimental_get_query_params()
        token = query_params["token"][0]
        json = {"token":token}
        url = "https://data-production-4fc9.up.railway.app/discoverdata/rest-api-file/"
        result = requests.post(url,json=json)
        data = result.json()["data"]
        data = StringIO(data)
        df = pd.read_csv(data, sep=",")
        return df



    df = fetch()


    # ---- Variables ----


    def has_numbers(listString):
        for inputString in listString :
            if not any(char.isdigit() for char in str(inputString)):
                return False
        return True


    measurment_dict ={
        "SUM":"sum",
        "AVRAGE":"mean",
        "MEDIAN":"median",
        "COUNT":"count",
        "COUNT (DISTINCT)":"count",
        "MINIMUM":"min",
        "MAXIMUM":"max",
        "STANDARD DEVIATION":"std",
        "STANDARD DEVIATION (POPULATION)":"std",
        "VARIANCE":"var",
        "VARIANCE (POPULATION)":"var",
    }
    numerics = ['int16', 'int32', 'int64','float16', 'float32', 'float64']
    numeric_columns = df.select_dtypes(include=numerics)
    num_col_list  = numeric_columns.columns.to_list()
    bool_columns = df.select_dtypes(include=bool)
    bool_col_list = bool_columns.columns.to_list()
    col_list = df.columns.to_list()

    cat_col_list = list((set(col_list) - set(bool_col_list)) - set(num_col_list))
    date_time_list = []
    for col in  df[cat_col_list]:
        sample = df[col].sample(10).to_list()
        if len(col) > 6 and has_numbers(sample) :
            try:
                df[col] = pd.to_datetime(df[col])
                date_time_list.append(col)
                cat_col_list.remove(col)
            except:
                pass 





    # ---- column ---- 


    col_list = ["(Count)"] + col_list
    columns = st.multiselect(
        "Select the Columns :",
        options=col_list,
        
    )

    rows = st.multiselect(
        "Select the Rows :",
        options=col_list,
        
    )


    # ---- SIDEBAR ----


    dt_col = None
    mask = None 
    st.sidebar.header("Filters:")
    if date_time_list :
        date_time_filter = st.sidebar.multiselect(
            "date&time filter: ",
            options=date_time_list,
        )
        if date_time_filter :
            for date_col in date_time_filter:
                dt_options = ["year", "month", "day", "hour", "minute", "second"]
                tab1, tab2, tab3 = st.sidebar.tabs(["filter", "filter by", "filter type"])
                dt_filter_value = tab2.selectbox(
                f"{date_col} filter",
                options=dt_options,
                )
                filter_type = tab3.selectbox(
                f"{date_col} filter type",
                options=["range", "values"],
                )
                if filter_type == "range" :
                    cmd = f"dt_col = df[date_col].dt.{dt_filter_value}"
                    exec(cmd)
                    mini = int(dt_col.max())
                    maxi = int(dt_col.min())
                    slid_range = maxi - mini
                    steps = None
                    if slid_range > 1000000 :
                        steps = int(slid_range / 1000000)
                    dt_slider_values = tab1.slider(
                        f'Select a range of {date_col} values',
                        mini, maxi, (mini, maxi),
                        step=steps,
                        )
                    cmd = F"mask =  (df[date_col].dt.{dt_filter_value} >= {dt_slider_values[0]}) & (df[date_col].dt.{dt_filter_value} <= {dt_slider_values[1]})"
                    exec(cmd)
                    df = df[mask]
                if filter_type == 'values':
                    dt_list = df[date_col].dt.year.unique()
                    dt_value_list = []
                    for dt in dt_list:
                        checked = tab1.checkbox(str(dt), value=True)
                        if checked :
                            dt_value_list.append(dt)
                    if dt_value_list:
                        mask =  ( df[date_col].dt.year.isin(dt_value_list) )
                        df = df[mask]




    categoric_filter = st.sidebar.multiselect(
        "filter by catogery and boolian values: ",
        options=cat_col_list+bool_col_list,
        
    )


    if categoric_filter :
        for col in categoric_filter:
            options = df[col].unique().tolist()
            cat_filter_value = st.sidebar.multiselect(
            f"{col} filter",
            options=options,
            )
            if cat_filter_value:
                df = df[df[col].isin(cat_filter_value)]



    numberic_filter = st.sidebar.multiselect(
        "filter by measurment values: ",
        options=num_col_list,
        
    )


    measures_options = measurment_dict.keys()
    numberic_filter_dict = {}
    if numberic_filter :
        for col in numberic_filter:
            measure_option = st.sidebar.selectbox(
            f"{col} Measurement",
            options=measures_options,
            )
            numberic_filter_dict[col]=measure_option


    grouped = None

    # --- DISPLAY DATAFRAME ---
    def filter_groupby(col):
        if not col in num_col_list and col != "(Count)" :
            if numberic_filter_dict:
                df_grouped = df.groupby(col)
                df_filtered =  df
                for filter_col, measurs in  numberic_filter_dict.items():
                    ldict = {}
                    df_filtered =  df_filtered.groupby(col)
                    if len(df_grouped) <= 1 :
                        return df
                    cmd = f"global grouped; grouped = df_grouped.{measurment_dict[measurs]}()[['{filter_col}']]"
                    exec(cmd)
                    mini = int(grouped.min()[0])
                    maxi = int(grouped.max()[0])
                    slider_range = maxi - mini
                    step = None
                    if slider_range > 1000000 :
                        step = int(slider_range / 1000000)
                    values = st.slider(
                        f'Select a range of {filter_col} values for each {col} ',
                        mini, maxi, (mini, maxi),
                        step=step,
                        )
                    cmd = f"df_filtered = df_filtered.filter(lambda x: {values[1]} >= x['{filter_col}'].{measurment_dict[measurs]}() >= {values[0]})"
                    exec(cmd, locals(), ldict)
                    df_filtered = ldict["df_filtered"]
                return df_filtered
        return df

    df_grouped= None
    chart = None
    for col in columns:
        df = filter_groupby(col)
        for row in  rows:
            df = filter_groupby(row)
            count = "Count"
            if col != "(Count)" and row != "(Count)":
                if col in num_col_list:
                    if row in num_col_list:
                        if row == col :
                            df[f"_{row}"] =  df[row]
                            row = f"_{row}"
                        df_grouped = df
                    else:
                        measure_option = st.selectbox(
                        f"Measurement applied on col {col}",
                        options=measures_options,
                        )
                        exec(f"df_grouped = df.groupby(row).{measurment_dict[measure_option]}().reset_index()")
                else:
                    if row in num_col_list:
                        measure_option = st.selectbox(
                        f"Measurement applied on row {row} for column {col}",
                        options=measures_options,
                        )
                        exec(f"df_grouped = df.groupby(col).{measurment_dict[measure_option]}().reset_index()")
                    else:
                        if row == col :
                            df[f"_{row}"] =  df[row]
                            row = f"_{row}"
                        df_grouped = df.groupby([row, col]).count().reset_index()


            else:
                while count in col_list :
                    count += '_'
                if row != "(Count)":
                    df_grouped = df.groupby(row).size()
                    col = count
                elif col != "(Count)":
                    df_grouped = df.groupby(col).size()
                    row = count
                else:
                    continue 
                df_grouped = df_grouped.reset_index(name=count)
                print("\n df_grouped.heqad() \n ")
                print(df_grouped[[col,row]].head)

            chart_options = ["bar", "line", "histogram", "area","box", "pie"]
            chart_selected = st.selectbox(
            f"chart for row {row} & column {col}",
            options=chart_options,
            )
            color= f"color_discrete_sequence = ['#F63366']*{len(df_grouped)},"
            if chart_selected == "line":
                color_cols = cat_col_list+bool_col_list
                color_cols.insert(0, None)
                col_selected = st.selectbox(
                f"Select color columns to row {row} & column {col}",
                options=color_cols,
                )
                if col_selected :
                    color = f'color="{col_selected}",'
            cmd = f"""chart = px.{chart_selected}(df_grouped,
                            '{col}',
                            '{row}',
                            {color}
                            template= 'plotly_white')"""
            exec(cmd)
            st.plotly_chart(chart)

except :
    st.error('Something goes Wrong make sure that the data is clean and in right format and Try again , if issuse still please tell us in report issue section', icon="🚨")














# import numpy as np
# df_test = pd.DataFrame(np.array(([1, 2, 3], [1, 2, 3], [1, 2, 3])),
#             columns=['one', 'two', 'three'])
# chart = px.bar(df_test,
#                 x="one",
#                 y="two",
#                 text="one",
#                 color_discrete_sequence = ['#F63366']*len(df_test),
#                 template= 'plotly_white')
# st.plotly_chart(chart)

