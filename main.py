import streamlit as st
import pandas as pd
import datetime as datetime
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt

st.title("Lifty Downloading")
st.markdown('***')

st.markdown("#### Load Range Date Database")
st.write ("Nota : Solo serán usadas las 3 primeras columnas : Publisher, Date Time 1, Date Time 2")
es_numeric=False
es_timestamp=False
es_date=False
publisher=""
Range_file = st.file_uploader("Choose your Range Date Base",type=["xlsx", "xls"])
if Range_file is not None:
    try:
        df_range = pd.read_excel(Range_file)
        if df_range.shape[1]>=3:
            df_range.rename(columns={df_range.columns[0]:"Publisher"},inplace=True)
            df_range.rename(columns={df_range.columns[1]:"Range1"},inplace=True)
            df_range.rename(columns={df_range.columns[2]:"Range2"},inplace=True)
            df_range = df_range[["Publisher","Range1","Range2"]]
            try:
                datetime_obj = datetime.datetime.strptime(str(df_range["Range1"][0]), "%Y-%m-%d %H:%M:%S")
                datetime_obj = datetime.datetime.strptime(str(df_range["Range2"][0]), "%Y-%m-%d %H:%M:%S")
                es_timestamp = True
                st.write(df_range)
            except Exception as e:
                es_timestamp = False
                st.write ("Las variables Range1, Range2 deben ser del tipo Timestamp : YYYY-mm-dd : HH-mm-ss")
                
        else:
            st.write ("El archivo debe tener al menos 3 columnas : Publisher, Range1, Range2")
    except Exception as e:
        st.write ("Revise la estructura del file deben ser 3 columnas : Publisher, Range1, Range2")
else:
    st.write ("Esperando Upload del archivo de fechas...")

st.markdown("#### Load Ad manager Report")
st.write ("Nota : El archivo debe ser generado directo de GAM : Date, Hour, Country, Device, CountryID, DeviceID, Impressions, Revenue, Requests")

am_file = st.file_uploader("Choose your Ad manager Report",type=["xlsx", "xls"])
try:
    df_pub=pd.read_excel(am_file,sheet_name="Properties")
    publisher=df_pub.T[1][1]
    st.write(publisher)
except Exception as e:
    st.write("El archivo debe poseer caratula Properties de GAM")

if am_file is not None:
    try:
        df_gam = pd.read_excel(am_file,sheet_name="Report data")
        if df_gam.shape[1]>=6:
            df_gam.rename(columns={df_gam.columns[3]:"Device"},inplace=True)
            df_gam.rename(columns={df_gam.columns[6]:"Impressions"},inplace=True)
            df_gam.rename(columns={df_gam.columns[7]:"Revenue"},inplace=True)
            df_gam.rename(columns={df_gam.columns[8]:"Requests"},inplace=True)
            df_gam = df_gam[["Date","Hour","Country","Device","Impressions","Revenue","Requests"]]
            try:
                numeric_obj1 = isinstance(df_gam["Hour"][0], int) or isinstance(df_gam["Hour"][0], float)
                numeric_obj2 = isinstance(df_gam["Impressions"][0], int) or isinstance(df_gam["Impressions"][0], float)
                numeric_obj3 = isinstance(df_gam["Revenue"][0], int) or isinstance(df_gam["Revenue"][0], float)
                numeric_obj4 = isinstance(df_gam["Requests"][0], int) or isinstance(df_gam["Requests"][0], float)
                fecha = isinstance(df_gam["Date"][0], datetime.date)
                es_numeric = True
                es_date = True
                st.write(df_gam)
            except Exception as e:
                es_numeric = False
                es_date = False
                st.write ("Las variables Hour, Impressions, Revenue, Requests deben ser numéricas y Date debe ser fecha")
                
        else:
            st.write ("Revise la estructura de su archivo, en la Nota se da una guía")
    except Exception as e:
        st.write ("Revise la estructura de su archivo, en la Nota se da una guía")
else:
    st.write ("Esperando Upload del archivo de GAM")

if (es_numeric and es_timestamp and es_date and publisher != ""):
    
    df_gam = df_gam[df_gam["Date"] != 'Total']
    df_gam["Seller"]="LIFTY" 
    for i,j in enumerate(df_gam["Date"]):
       anio=df_gam["Date"][i].year
       mes=df_gam["Date"][i].month
       dia=df_gam["Date"][i].day
       for k,pub in enumerate(df_range["Publisher"]):
            if pub==publisher: 
                dia1=df_range["Range1"][k].day
                dia2=df_range["Range2"][k].day
                mes1=df_range["Range1"][k].month
                mes2=df_range["Range2"][k].month
                anio1=df_range["Range1"][k].year
                anio2=df_range["Range2"][k].year
                hora1=df_range["Range1"][k].hour
                hora2=df_range["Range2"][k].hour
                if(anio == anio1 and mes== mes1 and dia == dia1 and df_gam["Hour"][i]==hora1) or (anio == anio2 and mes== mes2 and dia == dia2 and df_gam["Hour"][i]==hora2):
                        df_gam["Seller"][i]="BENCHMARK"
                        break
                else:
                        pass
                
            else:
                pass
             
       

    st.markdown("### ** Asignación de benchmark Finalizada ** ")
    st.write(df_gam)
    if st.button("Download Excel"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_gam.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        excel_data = output.read()
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="lifty_benchmark.xlsx">Download Excel file</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        pass

    st.markdown("#### Visualizaciones")
    df_gam["fec"]=None
    for i,fec in enumerate(df_gam["Date"]):
        df_gam["fec"][i]=fec.strftime('%d-%m-%Y')

    country_list=df_gam["Country"].unique().tolist()
    devi_list=df_gam["Device"].unique().tolist()
    countries = st.multiselect("Seleccione Paises :",country_list,default = country_list)
    devies=st.multiselect("Seleccione Devices :",devi_list,default = devi_list)
    fec_list=df_gam["fec"].unique().tolist()
    fecs = st.multiselect("Seleccione Fechas :",fec_list,default = fec_list)
    df_gam=df_gam[df_gam["Country"].isin(countries) & df_gam["Device"].isin(devies) & df_gam["fec"].isin(fecs)]

    st.markdown("##### RPM General Level : ")
    st.write("")
    insight1=df_gam.groupby(["Seller"]).aggregate({"Revenue":"sum",
                                            "Requests":"sum",
                                            "Impressions":"sum"})
        
    insight1["RPM"]=insight1.Revenue*1000/insight1.Requests
    st.write(insight1)
    st.write("")

    st.markdown("##### RPM by Country : ")
    insight1=df_gam.groupby(["Country","Seller"]).aggregate({"Revenue":"sum",
                                            "Requests":"sum",
                                            "Impressions":"sum"})
    insight1["RPM"]=insight1.Revenue*1000/insight1.Requests
    grouped = insight1.pivot_table(index="Country", columns="Seller", values="RPM", aggfunc="mean")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    countries = grouped.index
    rpm_benchmark = grouped["BENCHMARK"]
    rpm_lifty = grouped["LIFTY"]
    bar_width = 0.35
    x = range(len(countries))
    plt.bar(x, rpm_benchmark, width=bar_width, label="Benchmark")
    plt.bar([i + bar_width for i in x], rpm_lifty, width=bar_width, label="Lifty")
    ax.set_xlabel("Country")
    ax.set_ylabel('RPM')
    ax.set_title('RPM by Country & Seller')
    ax.set_xticks([i + bar_width/2 for i in x])
    ax.set_xticklabels(countries,rotation=90)
    ax.legend()
    st.pyplot(fig)

    st.markdown("##### RPM by Device : ")
    insight1=df_gam.groupby(["Device","Seller"]).aggregate({"Revenue":"sum",
                                            "Requests":"sum",
                                            "Impressions":"sum"})
    insight1["RPM"]=insight1.Revenue*1000/insight1.Requests
    grouped = insight1.pivot_table(index="Device", columns="Seller", values="RPM", aggfunc="mean")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    devices = grouped.index
    rpm_benchmark = grouped["BENCHMARK"]
    rpm_lifty = grouped["LIFTY"]
    bar_width = 0.35
    x = range(len(devices))
    plt.bar(x, rpm_benchmark, width=bar_width, label="Benchmark")
    plt.bar([i + bar_width for i in x], rpm_lifty, width=bar_width, label="Lifty")
    ax.set_xlabel("Device")
    ax.set_ylabel('RPM')
    ax.set_title('RPM by Device & Seller')
    ax.set_xticks([i + bar_width/2 for i in x])
    ax.set_xticklabels(devices,rotation=90)
    ax.legend()
    st.pyplot(fig)
else:
    if am_file is not "None" and Range_file is not None: 
        st.write("Revise si cargo ambos archivos correctamente...")
    else:
        pass
st.write(":heavy_minus_sign:" * 32)   

