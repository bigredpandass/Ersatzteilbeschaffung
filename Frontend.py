import math
from scipy import stats
import matplotlib.pyplot as plt
import operator
import streamlit as st



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
Pönale = st.number_input("Wähle die Pönale falls es zu einem Ausfall kommt in CHF ", 0, 200000, 10000)

Standmenge_durch = st.number_input("Wähle die durchschnittliche Standmenge aus", 0, 2000000, 100000)
Standmenge_stdv_perc= st.slider("Wähle die Standardabweichung der Standmenge in % aus:", 0, 100, 25,5)/100
Standmenge_stdv = Standmenge_stdv_perc * Standmenge_durch

Werkzeugkosten = st.number_input("Wähle den Werkzeugpreis aus in CHF", 1, 10000, 400)
Werkzeugvebrauch = st.number_input("Wähle den Werkzeugverbrauch aus", 1, 100, 10)
Anzahl_zu_produzierende_Teile_max = st.number_input("Wähle die Menge der in dem Wiederbeschaffungszeitraum zu beschaffende Teile aus", 1, 2000000, Standmenge_durch*2)



min_beta = math.ceil(Anzahl_zu_produzierende_Teile_max / Standmenge_durch)
max_beta = math.ceil(Anzahl_zu_produzierende_Teile_max / Standmenge_durch) + 10
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

fig, ax = plt.subplots(2, figsize=(6, 6), dpi=200)
ax[0].plot(list(MldMenge), list(Kosten.values()), label="Gesamtkosten")
ax[0].plot(list(MldMenge), list(Stillstandskosten.values()), label="Ausfallkosten")
ax[0].plot(list(MldMenge), list(Lagerkosten.values()), label="Lagerkosten")
ax[0].plot(list(MldMenge), list(Kapitalbindungskosten.values()), label="Kapitalbindungskosten")
ax[0].legend()
ax[0].set_xlim(right = label+3, left = min_beta)
ax[0].set_ylim( bottom = 0, top = min(Kosten.values())*4)
ax[0].set_xlabel("Meldemenge")
ax[0].set_ylabel("Kosten [CHF]")

ax[1].plot(list(MldMenge), list(beta.values()), label="beta values")
ax[1].set_xlim(right = label+3, left = min_beta)
ax[1].set_xlabel("Meldemenge")
ax[1].set_ylabel(r"$\beta$")

st.write("Die kritische Lagermenge liegt bei " + str(label) + " Stück.")
st.write("Die erwartete Wahrscheinlichkeit eines Ausfalls in einem Jahr ist "+"{:10.2f}".format((1 - beta[label]) * Werkzeugvebrauch * 100) + " %.")

st.pyplot(fig)







# print(sum([(1-label)**x for x in range(1,n_Werkzeuge)]))

