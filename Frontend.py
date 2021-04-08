import math
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import operator
import streamlit as st
import plotly.express as px



# ----------------- Funktionen


def t(beta, n):
    return stats.t.ppf(beta, n)


def beta_calc(t_value, n):
    return stats.t.cdf(t_value, n)


# ----------------- Frontend

st.title("Prototyp systematisches Ersatzteilmanagement")

Kalk_Zinssatz_jährlich = st.slider("Wähle den jährlichen kalk. Zinssatz aus in %", 0, 30, 10, 1)/100 # 10% / Jahr für Berechnung der Kapitalbindungskosten
Kalk_Zinssatz = (Kalk_Zinssatz_jährlich +1)**(1/365) - 1 # Kalkulation des täglichen Zinssatzes
Lagerkostensatz = st.slider("Wähle den Lagerkostensatz aus pro  Jahr pro Werkzeug Instanz in CHF", 1, 100, 20, 1)/365 # CHF pro Tags; später abhängig machen von z.B. Gewicht etc.?


Standmenge_durch = st.number_input("Wähle die durchschnittliche Standmenge aus", 0, 2000000, 100000)



Werkzeugvebrauch = st.number_input("Wähle den Werkzeugverbrauch aus", 1, 100, 10)
Anzahl_zu_produzierende_Teile_max = st.number_input("Wähle die Menge der in dem Wiederbeschaffungszeitraum zu beschaffende Teile aus", 1, 2000000, Standmenge_durch*2)

Pönale = st.slider("Wähle die Pönale falls es zu einem Ausfall kommt in CHF ", 0, 200000, 10000, 500)
Werkzeugkosten = st.slider("Wähle den Werkzeugpreis aus in CHF", 1, 10000, 400, 10)
Standmenge_stdv_perc= st.slider("Wähle die Standardabweichung der Standmenge in % aus:", 0, 100, 25,5)/100
Standmenge_stdv = Standmenge_stdv_perc * Standmenge_durch


min_beta = math.ceil(Anzahl_zu_produzierende_Teile_max / Standmenge_durch)
max_beta = math.ceil(Anzahl_zu_produzierende_Teile_max / Standmenge_durch) + 20
step_beta = 1

Kosten = {}
Kritische_Lagermenge = {}
Kapitalbindungskosten = {}
Lagerkosten = {}
Stillstandskosten = {}
t_value = {}
beta = {}

for MldMenge in range(min_beta, max_beta, step_beta):
    t_value[MldMenge] = (Standmenge_durch - Anzahl_zu_produzierende_Teile_max / MldMenge) * math.sqrt(
        MldMenge) / Standmenge_stdv

    beta[MldMenge] = beta_calc(t_value[MldMenge], MldMenge)

    Kapitalbindungskosten[MldMenge] = Kalk_Zinssatz * MldMenge * Werkzeugkosten * 365
    Lagerkosten[MldMenge] = Lagerkostensatz * MldMenge * 365

    Stillstandskosten[MldMenge] = (1 - beta[MldMenge]) * Werkzeugvebrauch * Pönale

    Kosten[MldMenge] = (Kapitalbindungskosten[MldMenge] + Lagerkosten[MldMenge]) + Stillstandskosten[MldMenge]
label = min(Kosten.items(), key=operator.itemgetter(1))[0]
MldMenge = range(min_beta, max_beta, step_beta)

data = [list(MldMenge),list(Kosten.values()),list(Stillstandskosten.values()), list(Lagerkosten.values()), list(Kapitalbindungskosten.values())]
df = pd.DataFrame(data).transpose()
df.columns = ["Meldemenge","Gesamtkosten", "Ausfallkosten", "Lagerkosten", "Kapitalbindungskosten"]


fig2 = px.line(df, x="Meldemenge", y=["Gesamtkosten", "Ausfallkosten", "Lagerkosten", "Kapitalbindungskosten"], labels=dict(variable ="Kostenart"))

fig2.update_xaxes(range=[min_beta, label+3], title_text="Meldemenge")
fig2.update_yaxes(range=[0, min(Kosten.values())*4], title_text="Kosten [CHF]")
fig2.update_layout(font=dict(size=16), legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99
))

st.write("Die kritische Lagermenge liegt bei " + str(label) + " Stück.")
st.write("Die erwartete Wahrscheinlichkeit eines Ausfalls in einem Jahr ist "+"{:10.2f}".format((1 - beta[label]) * Werkzeugvebrauch * 100) + " %.")
st.plotly_chart(fig2)


