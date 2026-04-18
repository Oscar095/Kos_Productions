import os
import math
import qrcode
import barcode
from barcode.writer import ImageWriter
import pandas as pd
from dotenv import load_dotenv
from consultas_sql_excel import fetch_data

# Cargar variables del archivo .env
load_dotenv()

API_OP_NUMEROS = os.getenv("API_OP_NUMEROS")
df = fetch_data(API_OP_NUMEROS)
df["docto"] = df["docto"].astype(str)

# Crear carpetas si no existen
os.makedirs("Barcodes/Qr", exist_ok=True)
os.makedirs("Barcodes/Code128", exist_ok=True)

def procesar_op(numero_op):
    if numero_op not in df["docto"].values:
        print("No Existe OP. Intente nuevamente.")
        return

    filtro = (df["docto"] == numero_op) & (df["tipo_inv"] == "IN1430K.ex")

    Cantidad_OP = df.loc[filtro, "cantidad"].values[0]
    item = df.loc[filtro, "id_item"].values[0]
    lote = df.loc[filtro, "lote"].values[0]
    ext1 = df.loc[filtro, "ext1"].values[0].strip()
    ext2 = df.loc[filtro, "ext2"].values[0].strip()

    Unidad_empaque_caja = int(input("Digite Cantidad por Caja:").strip())
    Unidad_Tira = int(input("Digite Cantidad por tira:").strip())

    Numero_Cajas = math.floor(Cantidad_OP / Unidad_empaque_caja)
    fraccion = Cantidad_OP / Unidad_empaque_caja - Numero_Cajas
    Saldo = round(fraccion * Unidad_empaque_caja)

    print(f"{Numero_Cajas} cajas completas y un saldo de: {Saldo} unidades")

    cadena_codificada = f"{numero_op}|{item}|{lote}|{ext1}|{ext2}|{Unidad_empaque_caja}"
    cadena_codificada_saldo = f"{numero_op}|{item}|{lote}|{ext1}|{ext2}|{Saldo}"

    while True:
        opcion_impresion = input("¿Desea imprimir [T]otalidad o solo el [S]aldo? ").strip().upper()
        if opcion_impresion in ["T", "S"]:
            break
        print("Opción inválida. Escriba 'T' o 'S'.")

    if opcion_impresion == "T":
        qr = qrcode.make(cadena_codificada)
        qr.save(os.path.join("Barcodes", "Qr", "codigo_qr.png"))

        codigo128 = barcode.get('code128', cadena_codificada, writer=ImageWriter())
        codigo128.save(os.path.join("Barcodes", "Code128", "codigo_ean128"))

        qr_saldo = qrcode.make(cadena_codificada_saldo)
        qr_saldo.save(os.path.join("Barcodes", "Qr", "codigo_qr_saldo.png"))

        codigo128_saldo = barcode.get('code128', cadena_codificada_saldo, writer=ImageWriter())
        codigo128_saldo.save(os.path.join("Barcodes", "Code128", "codigo_ean128_saldo"))

    elif opcion_impresion == "S":
        Saldo = int(input("Digite Saldo de la Caja: ").strip())
        cadena_codificada_saldo = f"{numero_op}|{item}|{lote}|{ext1}|{ext2}|{Saldo}"

        qr = qrcode.make(cadena_codificada_saldo)
        qr.save(os.path.join("Barcodes", "Qr", "codigo_qr_saldof.png"))

        codigo128 = barcode.get('code128', cadena_codificada_saldo, writer=ImageWriter())
        codigo128.save(os.path.join("Barcodes", "Code128", "codigo_ean128_saldof"))

# Bucle principal para múltiples OP
while True:
    opcion = input("¿Desea imprimir otra OP [S][N]? ").strip().upper()
    if opcion == "N":
        break
    elif opcion == "S":
        Numero_op = input("Digite la Orden de Produccion: ").strip()
        procesar_op(Numero_op)
    else:
        print("Opción inválida. Use 'S' o 'N'.")
