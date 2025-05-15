import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Button, Label
import fitz  # PyMuPDF

def encontrar_posicion_texto(pdf_path, texto_buscar):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        areas = page.search_for(texto_buscar)
        if areas:
            x0, y0, x1, y1 = areas[0]
            return page_num, x0, y0
    return None, None, None

def firmar_pdf(pdf_path, firma_path, texto_buscar):
    doc = fitz.open(pdf_path)
    firma_img = open(firma_path, "rb").read()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        areas = page.search_for(texto_buscar)
        if areas:
            x0, y0, x1, y1 = areas[0]

            firma_width = 200
            firma_height = 26
            x_firma = x0
            y_firma = y0 - firma_height - 5

            page.insert_image(
                fitz.Rect(x_firma, y_firma, x_firma + firma_width, y_firma + firma_height),
                stream=firma_img,
                overlay=True
            )

            # Guardar en carpeta "Documentos/Juicios Firmados + nombre original"
            nombre_base = os.path.splitext(os.path.basename(pdf_path))[0]
            documentos_path = os.path.join(os.path.expanduser("~"), "Documents")
            carpeta_destino = os.path.join(documentos_path, f"Juicios Firmados")
            os.makedirs(carpeta_destino, exist_ok=True)
            output_path = os.path.join(carpeta_destino, f"{nombre_base}_firmado.pdf")
            doc.save(output_path)
            doc.close()
            return True, output_path

    doc.close()
    return False, None

def procesar():
    carpeta = carpeta_entry.get()
    firma = firma_entry.get()
    if not carpeta or not firma:
        messagebox.showerror("Error", "Por favor seleccione la carpeta de PDFs y la firma.")
        return

    texto_objetivo = "NOMBRE Y FIRMA COORDINADOR ACADEMICO RESPONSABLE"
    firmados = 0
    fallidos = 0
    no_encontrados = []

    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith(".pdf"):
            ruta_pdf = os.path.join(carpeta, archivo)
            resultado, ruta_salida = firmar_pdf(ruta_pdf, firma, texto_objetivo)
            if resultado:
                firmados += 1
            else:
                fallidos += 1
                no_encontrados.append(archivo)

    # Guardar el historial de fallidos
    if no_encontrados:
        documentos_path = os.path.join(os.path.expanduser("~"), "Documents")
        carpeta_destino = os.path.join(documentos_path, "Juicios Firmados")
        os.makedirs(carpeta_destino, exist_ok=True)
        historial_path = os.path.join(carpeta_destino, "no_encontrados.txt")
        with open(historial_path, "w", encoding="utf-8") as f:
            f.write("PDFs sin texto encontrado:\n")
            for nombre in no_encontrados:
                f.write(f"- {nombre}\n")

    messagebox.showinfo("Completado", f"✅ {firmados} firmados.\n❌ {fallidos} no encontrados.")
    
    # 🔄 Limpiar los campos después de la operación
    carpeta_entry.delete(0, tk.END)
    firma_entry.delete(0, tk.END)




def seleccionar_firma():
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes PNG", "*.png")])
    if ruta:
        firma_entry.delete(0, tk.END)
        firma_entry.insert(0, ruta)

def seleccionar_carpeta():
    ruta = filedialog.askdirectory()
    if ruta:
        carpeta_entry.delete(0, tk.END)
        carpeta_entry.insert(0, ruta)

# Interfaz
root = tk.Tk()
root.title("Firmador de PDFs")

Label(root, text="Carpeta de PDFs:").grid(row=0, column=0, sticky="e")
carpeta_entry = tk.Entry(root, width=50)
carpeta_entry.grid(row=0, column=1)
Button(root, text="Seleccionar", command=seleccionar_carpeta).grid(row=0, column=2)

Label(root, text="Firma (imagen PNG):").grid(row=1, column=0, sticky="e")
firma_entry = tk.Entry(root, width=50)
firma_entry.grid(row=1, column=1)
Button(root, text="Seleccionar", command=seleccionar_firma).grid(row=1, column=2)

Button(root, text="Firmar PDFs", command=procesar).grid(row=2, column=1, pady=20)

root.mainloop()