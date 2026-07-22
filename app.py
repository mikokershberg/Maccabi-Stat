import streamlit as st
import pandas as pd
import sqlite3
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Maccabi Basketball Portal",
    page_icon="🏀",
    layout="wide"
)

DB_FILE = "maccabi_stats.db"

# --- FULL 2026-2027 SCHEDULE DATA SEED ---
SCHEDULE_DATA = [
    ("2026-09-12", "19:00:00", "Guco Lier HSE F", "Willibies Antwerpen HSE A"),
    ("2026-09-12", "19:30:00", "BBC Laakdal HSE A", "BBC Geel HSE B"),
    ("2026-09-12", "20:00:00", "Duffel K.B.B.C. HSE A", "Phantoms Basket Boom HSE C"),
    ("2026-09-12", "20:15:00", "BBC Schelle HSE A", "Zuiderkempen Diamonds HSE B"),
    ("2026-09-12", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2026-09-12", "21:00:00", "Antwerp Giants HSE D", "Oxaco BBC Boechout HSE C"),
    ("2026-09-13", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Maccabi Antwerpen HSE A"),
    ("2026-09-18", "21:00:00", "Phantoms Basket Boom HSE C", "Koninklijke Herentalse BBC HSE A"),
    ("2026-09-19", "18:00:00", "Zuiderkempen Diamonds HSE B", "BBC Laakdal HSE A"),
    ("2026-09-19", "19:30:00", "Oxaco BBC Boechout HSE C", "Duffel K.B.B.C. HSE A"),
    ("2026-09-19", "20:00:00", "Willibies Antwerpen HSE A", "BBC Schelle HSE A"),
    ("2026-09-19", "20:30:00", "BBC Geel HSE B", "BBC Lyra Nila Nijlen HSE A"),
    ("2026-09-20", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Guco Lier HSE F"),
    ("2026-09-22", "20:00:00", "Duffel K.B.B.C. HSE A", "Maccabi Antwerpen HSE A"),
    ("2026-09-26", "19:00:00", "Guco Lier HSE F", "Phantoms Basket Boom HSE C"),
    ("2026-09-26", "19:30:00", "BBC Laakdal HSE A", "Willibies Antwerpen HSE A"),
    ("2026-09-26", "20:15:00", "BBC Schelle HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2026-09-26", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Oxaco BBC Boechout HSE C"),
    ("2026-09-27", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Zuiderkempen Diamonds HSE B"),
    ("2026-09-27", "17:00:00", "Antwerp Giants HSE D", "BBC Geel HSE B"),
    ("2026-09-29", "20:30:00", "Maccabi Antwerpen HSE A", "Zuiderkempen Diamonds HSE B"),
    ("2026-10-03", "18:00:00", "Zuiderkempen Diamonds HSE B", "Antwerp Giants HSE D"),
    ("2026-10-03", "19:30:00", "Oxaco BBC Boechout HSE C", "Guco Lier HSE F"),
    ("2026-10-03", "20:00:00", "Willibies Antwerpen HSE A", "BBC Lyra Nila Nijlen HSE A"),
    ("2026-10-03", "20:30:00", "BBC Geel HSE B", "Duffel K.B.B.C. HSE A"),
    ("2026-10-04", "13:30:00", "Rucon Gembo Borgerhout HSE C", "BBC Laakdal HSE A"),
    ("2026-10-04", "17:00:00", "Phantoms Basket Boom HSE C", "BBC Schelle HSE A"),
    ("2026-10-10", "19:00:00", "Guco Lier HSE F", "BBC Geel HSE B"),
    ("2026-10-10", "19:30:00", "BBC Laakdal HSE A", "Phantoms Basket Boom HSE C"),
    ("2026-10-10", "20:00:00", "Duffel K.B.B.C. HSE A", "Zuiderkempen Diamonds HSE B"),
    ("2026-10-10", "20:15:00", "BBC Schelle HSE A", "Oxaco BBC Boechout HSE C"),
    ("2026-10-10", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Willibies Antwerpen HSE A"),
    ("2026-10-11", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2026-10-11", "19:00:00", "Maccabi Antwerpen HSE A", "Phantoms Basket Boom HSE C"),
    ("2026-10-17", "18:00:00", "Zuiderkempen Diamonds HSE B", "Guco Lier HSE F"),
    ("2026-10-17", "19:30:00", "Oxaco BBC Boechout HSE C", "BBC Laakdal HSE A"),
    ("2026-10-17", "20:00:00", "Willibies Antwerpen HSE A", "Duffel K.B.B.C. HSE A"),
    ("2026-10-17", "21:00:00", "Antwerp Giants HSE D", "BBC Lyra Nila Nijlen HSE A"),
    ("2026-10-18", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Phantoms Basket Boom HSE C"),
    ("2026-10-18", "19:00:00", "Maccabi Antwerpen HSE A", "BBC Geel HSE B"),
    ("2026-10-22", "20:30:00", "Maccabi Antwerpen HSE A", "Koninklijke Herentalse BBC HSE A"),
    ("2026-10-24", "19:00:00", "Guco Lier HSE F", "Antwerp Giants HSE D"),
    ("2026-10-24", "19:30:00", "BBC Laakdal HSE A", "BBC Schelle HSE A"),
    ("2026-10-24", "20:00:00", "Duffel K.B.B.C. HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2026-10-24", "20:30:00", "BBC Geel HSE B", "Koninklijke Herentalse BBC HSE A"),
    ("2026-10-24", "21:00:00", "Maccabi Antwerpen HSE A", "Antwerp Giants HSE D"),
    ("2026-10-25", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Oxaco BBC Boechout HSE C"),
    ("2026-10-25", "17:00:00", "Phantoms Basket Boom HSE C", "Willibies Antwerpen HSE A"),
    ("2026-11-07", "18:00:00", "Zuiderkempen Diamonds HSE B", "BBC Geel HSE B"),
    ("2026-11-07", "19:30:00", "Maccabi Antwerpen HSE A", "Willibies Antwerpen HSE A"),
    ("2026-11-07", "19:30:00", "Oxaco BBC Boechout HSE C", "Phantoms Basket Boom HSE C"),
    ("2026-11-07", "20:15:00", "BBC Schelle HSE A", "BBC Lyra Nila Nijlen HSE A"),
    ("2026-11-07", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Guco Lier HSE F"),
    ("2026-11-07", "21:00:00", "Antwerp Giants HSE D", "Duffel K.B.B.C. HSE A"),
    ("2026-11-08", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Willibies Antwerpen HSE A"),
    ("2026-11-14", "19:00:00", "Guco Lier HSE F", "BBC Schelle HSE A"),
    ("2026-11-14", "19:30:00", "BBC Laakdal HSE A", "Koninklijke Herentalse BBC HSE A"),
    ("2026-11-14", "20:00:00", "Duffel K.B.B.C. HSE A", "BBC Lyra Nila Nijlen HSE A"),
    ("2026-11-14", "20:00:00", "Willibies Antwerpen HSE A", "Oxaco BBC Boechout HSE C"),
    ("2026-11-14", "20:30:00", "BBC Geel HSE B", "Rucon Gembo Borgerhout HSE C"),
    ("2026-11-14", "21:00:00", "Guco Lier HSE F", "Maccabi Antwerpen HSE A"),
    ("2026-11-15", "17:00:00", "Phantoms Basket Boom HSE C", "Zuiderkempen Diamonds HSE B"),
    ("2026-11-21", "18:00:00", "Zuiderkempen Diamonds HSE B", "Willibies Antwerpen HSE A"),
    ("2026-11-21", "19:30:00", "Maccabi Antwerpen HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2026-11-21", "20:15:00", "BBC Schelle HSE A", "BBC Geel HSE B"),
    ("2026-11-21", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Duffel K.B.B.C. HSE A"),
    ("2026-11-21", "21:00:00", "Antwerp Giants HSE D", "BBC Laakdal HSE A"),
    ("2026-11-22", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Guco Lier HSE F"),
    ("2026-11-22", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Oxaco BBC Boechout HSE C"),
    ("2026-11-28", "19:00:00", "Guco Lier HSE F", "Duffel K.B.B.C. HSE A"),
    ("2026-11-28", "19:30:00", "BBC Laakdal HSE A", "BBC Lyra Nila Nijlen HSE A"),
    ("2026-11-28", "19:30:00", "Oxaco BBC Boechout HSE C", "Zuiderkempen Diamonds HSE B"),
    ("2026-11-28", "20:00:00", "Willibies Antwerpen HSE A", "Antwerp Giants HSE D"),
    ("2026-11-28", "20:30:00", "BBC Geel HSE B", "Phantoms Basket Boom HSE C"),
    ("2026-11-28", "21:00:00", "BBC Laakdal HSE A", "Maccabi Antwerpen HSE A"),
    ("2026-11-29", "17:00:00", "Phantoms Basket Boom HSE C", "Maccabi Antwerpen HSE A"),
    ("2026-12-05", "18:00:00", "Zuiderkempen Diamonds HSE B", "Koninklijke Herentalse BBC HSE A"),
    ("2026-12-05", "20:00:00", "Duffel K.B.B.C. HSE A", "BBC Laakdal HSE A"),
    ("2026-12-05", "20:15:00", "BBC Schelle HSE A", "Maccabi Antwerpen HSE A"),
    ("2026-12-05", "20:30:00", "BBC Geel HSE B", "Oxaco BBC Boechout HSE C"),
    ("2026-12-05", "21:00:00", "Antwerp Giants HSE D", "Rucon Gembo Borgerhout HSE C"),
    ("2026-12-06", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Phantoms Basket Boom HSE C"),
    ("2026-12-06", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Willibies Antwerpen HSE A"),
    ("2026-12-12", "19:00:00", "Guco Lier HSE F", "BBC Laakdal HSE A"),
    ("2026-12-12", "19:30:00", "Oxaco BBC Boechout HSE C", "Maccabi Antwerpen HSE A"),
    ("2026-12-12", "20:00:00", "Willibies Antwerpen HSE A", "BBC Geel HSE B"),
    ("2026-12-12", "20:30:00", "Koninklijke Herentalse BBC HSE A", "BBC Lyra Nila Nijlen HSE A"),
    ("2026-12-12", "21:00:00", "Antwerp Giants HSE D", "Phantoms Basket Boom HSE C"),
    ("2026-12-13", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Zuiderkempen Diamonds HSE B"),
    ("2026-12-13", "20:00:00", "Duffel K.B.B.C. HSE A", "BBC Schelle HSE A"),
    ("2026-12-19", "18:00:00", "Zuiderkempen Diamonds HSE B", "Guco Lier HSE F"),
    ("2026-12-19", "19:30:00", "BBC Laakdal HSE A", "BBC Schelle HSE A"),
    ("2026-12-19", "19:30:00", "Maccabi Antwerpen HSE A", "BBC Schelle HSE A"),
    ("2026-12-19", "20:00:00", "Willibies Antwerpen HSE A", "Koninklijke Herentalse BBC HSE A"),
    ("2026-12-19", "20:30:00", "BBC Geel HSE B", "Phantoms Basket Boom HSE C"),
    ("2026-12-20", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Duffel K.B.B.C. HSE A"),
    ("2026-12-20", "17:00:00", "Phantoms Basket Boom HSE C", "Oxaco BBC Boechout HSE C"),
    ("2027-01-09", "19:00:00", "Guco Lier HSE F", "BBC Geel HSE B"),
    ("2027-01-09", "19:30:00", "BBC Laakdal HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2027-01-09", "19:30:00", "Oxaco BBC Boechout HSE C", "Antwerp Giants HSE D"),
    ("2027-01-09", "20:00:00", "Duffel K.B.B.C. HSE A", "Willibies Antwerpen HSE A"),
    ("2027-01-09", "20:15:00", "BBC Schelle HSE A", "Phantoms Basket Boom HSE C"),
    ("2027-01-09", "21:00:00", "Koninklijke Herentalse BBC HSE A", "Maccabi Antwerpen HSE A"),
    ("2027-01-10", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Zuiderkempen Diamonds HSE B"),
    ("2027-01-16", "18:00:00", "Zuiderkempen Diamonds HSE B", "BBC Schelle HSE A"),
    ("2027-01-16", "20:00:00", "Willibies Antwerpen HSE A", "Guco Lier HSE F"),
    ("2027-01-16", "20:30:00", "BBC Geel HSE B", "BBC Laakdal HSE A"),
    ("2027-01-16", "21:00:00", "Antwerp Giants HSE D", "Koninklijke Herentalse BBC HSE A"),
    ("2027-01-17", "13:30:00", "Rucon Gembo Borgerhout HSE C", "BBC Lyra Nila Nijlen HSE A"),
    ("2027-01-17", "17:00:00", "Phantoms Basket Boom HSE C", "Duffel K.B.B.C. HSE A"),
    ("2027-01-23", "19:00:00", "Guco Lier HSE F", "Rucon Gembo Borgerhout HSE C"),
    ("2027-01-23", "19:30:00", "BBC Laakdal HSE A", "Zuiderkempen Diamonds HSE B"),
    ("2027-01-23", "20:00:00", "Duffel K.B.B.C. HSE A", "Oxaco BBC Boechout HSE C"),
    ("2027-01-23", "20:00:00", "Maccabi Antwerpen HSE A", "BBC Lyra Nila Nijlen HSE A"),
    ("2027-01-23", "20:15:00", "BBC Schelle HSE A", "Willibies Antwerpen HSE A"),
    ("2027-01-23", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Phantoms Basket Boom HSE C"),
    ("2027-01-24", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "BBC Geel HSE B"),
    ("2027-01-30", "18:00:00", "Zuiderkempen Diamonds HSE B", "Maccabi Antwerpen HSE A"),
    ("2027-01-30", "19:30:00", "Oxaco BBC Boechout HSE C", "Koninklijke Herentalse BBC HSE A"),
    ("2027-01-30", "20:00:00", "Willibies Antwerpen HSE A", "BBC Laakdal HSE A"),
    ("2027-01-30", "20:30:00", "BBC Geel HSE B", "Antwerp Giants HSE D"),
    ("2027-01-30", "21:00:00", "Zuiderkempen Diamonds HSE B", "Maccabi Antwerpen HSE A"),
    ("2027-01-31", "13:30:00", "Rucon Gembo Borgerhout HSE C", "BBC Schelle HSE A"),
    ("2027-01-31", "17:00:00", "Phantoms Basket Boom HSE C", "Guco Lier HSE F"),
    ("2027-02-06", "19:00:00", "Guco Lier HSE F", "Oxaco BBC Boechout HSE C"),
    ("2027-02-06", "19:30:00", "BBC Laakdal HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2027-02-06", "20:00:00", "Duffel K.B.B.C. HSE A", "BBC Geel HSE B"),
    ("2027-02-06", "20:15:00", "BBC Schelle HSE A", "Phantoms Basket Boom HSE C"),
    ("2027-02-06", "20:30:00", "BBC Geel HSE B", "Maccabi Antwerpen HSE A"),
    ("2027-02-06", "21:00:00", "Antwerp Giants HSE D", "Zuiderkempen Diamonds HSE B"),
    ("2027-02-07", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Willibies Antwerpen HSE A"),
    ("2027-02-13", "18:00:00", "Zuiderkempen Diamonds HSE B", "Duffel K.B.B.C. HSE A"),
    ("2027-02-13", "19:30:00", "Oxaco BBC Boechout HSE C", "BBC Schelle HSE A"),
    ("2027-02-13", "20:00:00", "Willibies Antwerpen HSE A", "Koninklijke Herentalse BBC HSE A"),
    ("2027-02-13", "20:30:00", "BBC Geel HSE B", "Guco Lier HSE F"),
    ("2027-02-13", "21:00:00", "Maccabi Antwerpen HSE A", "Duffel K.B.B.C. HSE A"),
    ("2027-02-14", "13:30:00", "Rucon Gembo Borgerhout HSE C", "BBC Lyra Nila Nijlen HSE A"),
    ("2027-02-14", "17:00:00", "Phantoms Basket Boom HSE C", "BBC Laakdal HSE A"),
    ("2027-02-20", "19:00:00", "Guco Lier HSE F", "Zuiderkempen Diamonds HSE B"),
    ("2027-02-20", "19:30:00", "BBC Laakdal HSE A", "Oxaco BBC Boechout HSE C"),
    ("2027-02-20", "20:00:00", "Duffel K.B.B.C. HSE A", "Willibies Antwerpen HSE A"),
    ("2027-02-20", "20:30:00", "Koninklijke Herentalse BBC HSE A", "BBC Geel HSE B"),
    ("2027-02-20", "21:00:00", "Maccabi Antwerpen HSE A", "Guco Lier HSE F"),
    ("2027-02-21", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Antwerp Giants HSE D"),
    ("2027-02-21", "17:00:00", "Phantoms Basket Boom HSE C", "Rucon Gembo Borgerhout HSE C"),
    ("2027-02-28", "09:30:00", "Rucon Gembo Borgerhout HSE C", "Maccabi Antwerpen HSE A"),
    ("2027-03-06", "18:00:00", "Zuiderkempen Diamonds HSE B", "Phantoms Basket Boom HSE C"),
    ("2027-03-06", "19:30:00", "Oxaco BBC Boechout HSE C", "BBC Lyra Nila Nijlen HSE A"),
    ("2027-03-06", "20:00:00", "Willibies Antwerpen HSE A", "Phantoms Basket Boom HSE C"),
    ("2027-03-06", "20:15:00", "BBC Schelle HSE A", "BBC Laakdal HSE A"),
    ("2027-03-06", "20:30:00", "Koninklijke Herentalse BBC HSE A", "BBC Geel HSE B"),
    ("2027-03-06", "21:00:00", "Antwerp Giants HSE D", "Guco Lier HSE F"),
    ("2027-03-06", "21:00:00", "Maccabi Antwerpen HSE A", "BBC Laakdal HSE A"),
    ("2027-03-07", "13:30:00", "Rucon Gembo Borgerhout HSE C", "Duffel K.B.B.C. HSE A"),
    ("2027-03-13", "19:00:00", "Guco Lier HSE F", "Koninklijke Herentalse BBC HSE A"),
    ("2027-03-13", "19:30:00", "BBC Laakdal HSE A", "Antwerp Giants HSE D"),
    ("2027-03-13", "20:00:00", "Duffel K.B.B.C. HSE A", "Guco Lier HSE F"),
    ("2027-03-13", "20:30:00", "BBC Geel HSE B", "Zuiderkempen Diamonds HSE B"),
    ("2027-03-13", "21:00:00", "Antwerp Giants HSE D", "Maccabi Antwerpen HSE A"),
    ("2027-03-14", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "BBC Schelle HSE A"),
    ("2027-03-14", "17:00:00", "Phantoms Basket Boom HSE C", "Oxaco BBC Boechout HSE C"),
    ("2027-03-20", "18:00:00", "Zuiderkempen Diamonds HSE B", "Oxaco BBC Boechout HSE C"),
    ("2027-03-20", "20:00:00", "Willibies Antwerpen HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2027-03-20", "20:15:00", "BBC Schelle HSE A", "Guco Lier HSE F"),
    ("2027-03-20", "20:30:00", "Koninklijke Herentalse BBC HSE A", "BBC Laakdal HSE A"),
    ("2027-03-20", "21:00:00", "Willibies Antwerpen HSE A", "Maccabi Antwerpen HSE A"),
    ("2027-03-21", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Duffel K.B.B.C. HSE A"),
    ("2027-03-21", "13:30:00", "Rucon Gembo Borgerhout HSE C", "BBC Geel HSE B"),
    ("2027-03-28", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "Maccabi Antwerpen HSE A"),
    ("2027-04-03", "19:00:00", "Guco Lier HSE F", "BBC Lyra Nila Nijlen HSE A"),
    ("2027-04-03", "19:30:00", "BBC Laakdal HSE A", "Duffel K.B.B.C. HSE A"),
    ("2027-04-03", "19:30:00", "Oxaco BBC Boechout HSE C", "Rucon Gembo Borgerhout HSE C"),
    ("2027-04-03", "20:00:00", "Willibies Antwerpen HSE A", "Zuiderkempen Diamonds HSE B"),
    ("2027-04-03", "20:30:00", "BBC Geel HSE B", "BBC Schelle HSE A"),
    ("2027-04-03", "20:30:00", "Koninklijke Herentalse BBC HSE A", "Antwerp Giants HSE D"),
    ("2027-04-04", "17:00:00", "Phantoms Basket Boom HSE C", "Antwerp Giants HSE D"),
    ("2027-04-06", "20:30:00", "Maccabi Antwerpen HSE A", "Oxaco BBC Boechout HSE C"),
    ("2027-04-10", "18:00:00", "Zuiderkempen Diamonds HSE B", "Rucon Gembo Borgerhout HSE C"),
    ("2027-04-10", "20:00:00", "Duffel K.B.B.C. HSE A", "Koninklijke Herentalse BBC HSE A"),
    ("2027-04-10", "20:15:00", "BBC Schelle HSE A", "Guco Lier HSE F"),
    ("2027-04-10", "20:30:00", "BBC Geel HSE B", "Willibies Antwerpen HSE A"),
    ("2027-04-10", "21:00:00", "Antwerp Giants HSE D", "Willibies Antwerpen HSE A"),
    ("2027-04-11", "09:00:00", "Phantoms Basket Boom HSE C", "Maccabi Antwerpen HSE A"),
    ("2027-04-11", "13:00:00", "BBC Lyra Nila Nijlen HSE A", "BBC Laakdal HSE A"),
    ("2027-04-24", "19:00:00", "Koninklijke Herentalse BBC HSE A", "BBC Lyra Nila Nijlen HSE A"),
    ("2027-04-24", "19:30:00", "BBC Laakdal HSE A", "Rucon Gembo Borgerhout HSE C"),
    ("2027-04-24", "20:00:00", "Willibies Antwerpen HSE A", "Duffel K.B.B.C. HSE A"),
    ("2027-04-25", "11:15:00", "Guco Lier HSE F", "BBC Geel HSE B"),
    ("2027-04-25", "13:30:00", "Oxaco BBC Boechout HSE C", "Zuiderkempen Diamonds HSE B")
]

# --- ROSTER DATA SEED ---
MACCABI_ROSTER = [
    ("Abraham Michaely", 30.23, 2.19, 6.77, 2.08, 11.04, 11.35, 2.42),
    ("Avi Medina", 13.12, 0.18, 0.71, 0.53, 1.41, 1.00, 1.53),
    ("Benjamin Fischler", 23.15, 0.60, 2.20, 0.15, 2.95, 9.90, 2.65),
    ("Eitham Tzah", 27.33, 1.76, 5.90, 0.57, 8.24, 8.05, 2.62),
    ("Itai Lavan", 29.21, 3.08, 12.00, 3.38, 18.46, 14.96, 2.25)
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            status TEXT DEFAULT 'Scheduled'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            player_name TEXT,
            season TEXT,
            minutes REAL,
            ft_made INTEGER,
            fg2_made INTEGER,
            fg3_made INTEGER,
            points INTEGER,
            plus_minus REAL,
            fouls INTEGER
        )
    ''')
    
    # Check if matches table is empty, if so, seed schedule
    c.execute("SELECT COUNT(*) FROM matches")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO matches (date, time, home_team, away_team, status) VALUES (?, ?, ?, ?, 'Scheduled')",
            SCHEDULE_DATA
        )
    
    # Check if roster is seeded for multi-season stats
    c.execute("SELECT COUNT(*) FROM player_stats")
    if c.fetchone()[0] == 0:
        for p in MACCABI_ROSTER:
            c.execute(
                "INSERT INTO player_stats (player_name, season, minutes, ft_made, fg2_made, fg3_made, points, plus_minus, fouls) VALUES (?, '2025-2026', ?, ?, ?, ?, ?, ?, ?)",
                (p[0], p[1], int(p[2]), int(p[3]), int(p[4]), int(p[5]), p[6], int(p[7]))
            )
            
    conn.commit()
    conn.close()

init_db()

def get_connection():
    return sqlite3.connect(DB_FILE)

# --- HEADER & NAVIGATION ---
st.title("🏀 Maccabi Antwerpen — Team & League Portal")
st.caption("2e Provincial Heren Antwerpen B | 182 Pre-Loaded Matches")

tabs = st.tabs([
    "📅 Schedule & Results",
    "📊 Player & Team Stats",
    "🔄 Last Season vs. Current",
    "🔍 Prompt Query",
    "🔒 Admin Interface"
])

# ==========================================
# TAB 1: SCHEDULE & RESULTS
# ==========================================
with tabs[0]:
    st.header("Schedule & Results (2e Provincial Heren B)")
    
    conn = get_connection()
    matches_df = pd.read_sql_query("SELECT * FROM matches ORDER BY date ASC", conn)
    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        team_filter = st.selectbox("Filter Team", ["All Teams"] + sorted(list(set(matches_df['home_team']).union(set(matches_df['away_team'])))))
    with col2:
        status_filter = st.radio("Status", ["All", "Upcoming", "Completed"], horizontal=True)

    filtered = matches_df.copy()
    if team_filter != "All Teams":
        filtered = filtered[(filtered['home_team'] == team_filter) | (filtered['away_team'] == team_filter)]
    if status_filter == "Upcoming":
        filtered = filtered[filtered['status'] == 'Scheduled']
    elif status_filter == "Completed":
        filtered = filtered[filtered['status'] == 'Completed']

    st.write(f"Showing **{len(filtered)}** matches:")
    st.dataframe(
        filtered[['date', 'time', 'home_team', 'home_score', 'away_score', 'away_team', 'status']],
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# TAB 2: PLAYER & TEAM STATS
# ==========================================
with tabs[1]:
    st.header("Current Season Statistics (2026–2027)")
    
    conn = get_connection()
    stats_df = pd.read_sql_query("SELECT * FROM player_stats WHERE season = '2026-2027'", conn)
    conn.close()

    if stats_df.empty:
        st.info("No current season games logged yet. Admin can log box scores in the Admin panel!")
    else:
        player_summary = stats_df.groupby('player_name').agg(
            Games=('id', 'count'),
            Avg_Points=('points', 'mean'),
            Avg_3PT=('fg3_made', 'mean'),
            Avg_Fouls=('fouls', 'mean'),
            Avg_PlusMinus=('plus_minus', 'mean')
        ).reset_index().round(2)

        st.subheader("Player Performance Averages")
        st.dataframe(player_summary.sort_values(by="Avg_Points", ascending=False), use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: MULTI-SEASON COMPARISON
# ==========================================
with tabs[2]:
    st.header("Last Season (2025–2026) vs. Current Season (2026–2027)")
    
    conn = get_connection()
    all_stats = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()

    if not all_stats.empty:
        season_comp = all_stats.groupby(['player_name', 'season']).agg(
            Games=('id', 'count'),
            PPG=('points', 'mean'),
            Avg_3PT=('fg3_made', 'mean'),
            Avg_Fouls=('fouls', 'mean')
        ).reset_index().round(2)

        st.dataframe(season_comp, use_container_width=True, hide_index=True)

# ==========================================
# TAB 4: NATURAL LANGUAGE PROMPT QUERY
# ==========================================
with tabs[3]:
    st.header("🔍 Ask the Stats Hub")
    st.write("Type questions to search matches, opponents, or stat trends.")

    query = st.text_input("e.g., 'Maccabi', 'Geel', or 'Guco Lier'")
    
    if query:
        conn = get_connection()
        all_matches = pd.read_sql_query("SELECT * FROM matches", conn)
        conn.close()

        res = all_matches[(all_matches['home_team'].str.contains(query, case=False)) | (all_matches['away_team'].str.contains(query, case=False))]
        st.write(f"Found **{len(res)}** matching fixtures:")
        st.dataframe(res[['date', 'time', 'home_team', 'away_team', 'status']], use_container_width=True, hide_index=True)

# ==========================================
# TAB 5: ADMIN INTERFACE (Password Protected)
# ==========================================
with tabs[4]:
    st.header("🔒 Admin Panel — Log Match Scores")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "Michael%7":
        st.success("Authenticated as Administrator.")
        
        conn = get_connection()
        matches_df = pd.read_sql_query("SELECT * FROM matches WHERE status = 'Scheduled' ORDER BY date ASC", conn)
        
        if not matches_df.empty:
            match_options = {f"{row['date']} | {row['home_team']} vs {row['away_team']}": row['id'] for _, row in matches_df.iterrows()}
            selected_match_label = st.selectbox("Select Scheduled Game to Log", list(match_options.keys()))
            selected_match_id = match_options[selected_match_label]
            
            with st.form("score_entry_form"):
                col1, col2 = st.columns(2)
                with col1:
                    home_score = st.number_input("Home Team Score", min_value=0, step=1)
                with col2:
                    away_score = st.number_input("Away Team Score", min_value=0, step=1)
                
                submit_score = st.form_submit_button("Submit Game Score")
                
                if submit_score:
                    c = conn.cursor()
                    c.execute(
                        "UPDATE matches SET home_score = ?, away_score = ?, status = 'Completed' WHERE id = ?",
                        (home_score, away_score, selected_match_id)
                    )
                    conn.commit()
                    st.success("Game score updated and synchronized live!")
                    st.rerun()
        conn.close()
    elif password != "":
        st.error("Incorrect password.")
