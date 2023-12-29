import tkinter as tk
import cv2
import threading
import math
import pandas as pd
from pyzbar import pyzbar
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

# Conecta con la base de datos SQLite
engine = create_engine('sqlite:///productos.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_barra = Column(String)
    nombre_producto = Column(String)
    rubro = Column(String)

# Crear la tabla si no existe
Base.metadata.create_all(engine)

# Establecer la conexión a la base de datos
baseDatos = pd.read_sql(session.query(Producto).statement, session.bind)

# Crear un DataFrame vacío con especificación de columnas
columnas = ['id', 'codigo_barra', 'nombre_producto', 'rubro']
ventaActual = pd.DataFrame(columns=columnas)

class InterfazGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz Gráfica")

        self.root.option_add("*Font", "helvetica 14")

        # Crear y ubicar el Entry y la Listbox en el mismo widget Frame
        frame_entry_lista = tk.Frame(self.root)
        frame_entry_lista.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")


        self.entrada_texto = tk.Entry(frame_entry_lista, width=30)
        self.entrada_texto.pack(side="top", pady=(0, 10), fill="x")
        

        # AGREGADO PARA BÚSQUEDA
        # Vincular la función de búsqueda a la tecla "Enter" en la entrada de texto
        self.entrada_texto.bind("<Return>", lambda event: self.actualizar_resultados())
        # Vincular la función de búsqueda a la liberación de una tecla en la entrada de texto
        self.entrada_texto.bind("<KeyRelease>", lambda event: self.actualizar_resultados())


        self.lista = tk.Listbox(frame_entry_lista, height=5, width=30)
        self.lista.pack(side="top", fill="both", expand=True)

        self.lista.bind("<Double-Button-1>", self.agregar_a_venta_actual)


        # Crear y ubicar los dos frames a la derecha con labels
        frame_derecha = tk.Frame(self.root)
        frame_derecha.grid(row=0, column=4, padx=5)

        # Llamada al método para crear la etiqueta 'Total'
        self.label_total = tk.Label(frame_derecha, text="Total: 0.00")
        self.label_total.pack(side="top", anchor="n", padx=5, pady=10)
        self.crear_frame_con_etiqueta(frame_derecha, "Vuelto: ")

        # Crear y ubicar las tres listas a la derecha con etiquetas encima
        self.frame_lista_1, self.lista1 = self.crear_frame_con_etiqueta_y_lista("Nombre")
        self.frame_lista_1.grid(row=0, column=1, padx=1, pady=5, sticky="nsew")

        self.frame_lista_2, self.lista2 = self.crear_frame_con_etiqueta_y_lista("Categoria")
        self.frame_lista_2.grid(row=0, column=2, padx=1, pady=5, sticky="nsew")

        self.frame_lista_3, self.lista3 = self.crear_frame_con_etiqueta_y_lista("Precio")
        self.frame_lista_3.grid(row=0, column=3, padx=1, pady=5, sticky="nsew")

        # Configurar la expansión de las filas y columnas
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_columnconfigure(4, weight=1)
        
        # Agregar un botón en la esquina inferior derecha
        boton = tk.Button(self.root, text="NUEVA\nVENTA", height=2, width=20,command=self.nueva_venta)
        boton.grid(row=2, column=3, padx=10, pady=(0, 0), sticky="se", rowspan=2, columnspan=2)

        # Llamar al método para ejecutar la captura de video
        self.ejecutar_captura()

    def crear_frame_con_etiqueta(self, frame, texto_etiqueta):
        etiqueta = tk.Label(frame, text=texto_etiqueta)
        etiqueta.pack(side="top", anchor="n", padx=5, pady=10)

    def crear_frame_con_etiqueta_y_lista(self, texto_etiqueta):
        frame = tk.Frame(self.root)

        # Etiqueta
        etiqueta = tk.Label(frame, text=texto_etiqueta)
        etiqueta.pack(side="top")

        # Lista
        lista = tk.Listbox(frame, height=20, width=20)
        lista.pack(side="top", fill="both", expand=True)

        # Guardar la referencia a la lista en el propio frame
        frame.lista = lista

        return frame, lista

    def buscar_por_nombre(self, nombre):
        if nombre == "":
            return sorted(baseDatos["nombre_producto"])
        else:
            filtered_names = baseDatos[baseDatos["nombre_producto"].str.contains(nombre, case=False)]
            return filtered_names["nombre_producto"].tolist()



    def actualizar_resultados(self, *args):
        nombre_a_buscar = self.entrada_texto.get()
        resultados = self.buscar_por_nombre(nombre_a_buscar)

        self.lista.delete(0, tk.END)

        for resultado in resultados:
            self.lista.insert(tk.END, resultado)

    def agregar_a_venta_actual(self, event):
        # Obtener el índice del elemento seleccionado
        indice_seleccionado = self.lista.curselection()

        if indice_seleccionado:
            # Obtener el nombre seleccionado
            nombre_seleccionado = self.lista.get(indice_seleccionado[0])

            # Buscar la información en baseDatos para el nombre seleccionado
            resultado = baseDatos[baseDatos["nombre_producto"] == nombre_seleccionado]

            if not resultado.empty:
                primera_fila = resultado.iloc[0]

                # Agregar la fila al DataFrame ventaActual
                global ventaActual  # Agregado para indicar que estamos usando la variable global
                ventaActual = ventaActual._append(primera_fila, ignore_index=True)

                # Actualizar las listas en la interfaz gráfica
                self.frame_lista_1.lista.insert(tk.END, primera_fila.codigo_barra)
                self.frame_lista_2.lista.insert(tk.END, primera_fila.nombre_producto)
                self.frame_lista_3.lista.insert(tk.END, primera_fila.rubro)

                # suma_precio = round(ventaActual['precio'].sum(), 2)
                # self.label_total.config(text=f"Total: {suma_precio}")


    def nueva_venta(self):
        # Declarar 'ventaActual' como global
        global ventaActual

        # Generar el archivo de venta antes de reiniciar la ventaActual
        self.generar_archivo_venta()

        # Reiniciar DataFrame ventaActual
        ventaActual = pd.DataFrame(columns=['id', 'codigo_barra', 'nombre_producto', 'rubro'])

        # Actualizar la etiqueta de total
        self.label_total.config(text="Total: 0.00")

        # Limpiar listas en la interfaz gráfica
        self.lista.delete(0, tk.END)
        self.frame_lista_1.lista.delete(0, tk.END)
        self.frame_lista_2.lista.delete(0, tk.END)
        self.frame_lista_3.lista.delete(0, tk.END)

    #def generar_archivo_venta(self): //"TICKET"
        # Obtener la fecha y hora actual para usar en el nombre del archivo
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Crear el nombre del archivo con el formato "Venta_YYYYMMDD_HHMMSS.txt"
        nombre_archivo = f"Venta_{fecha_actual}.txt"

        try:
            # Abrir el archivo en modo de escritura
            with open(nombre_archivo, 'w') as archivo:
                # Escribir la cabecera
                archivo.write("-------------------------------\n")
                archivo.write("                       Venta\n")

                # Escribir la información de la venta actual
                for index, row in ventaActual.iterrows():
                    # Agregar el producto en una línea nueva
                    archivo.write(f"{row['codigo_barra']} - {row['nombre_producto']} - {row['rubro']}\n")

                # Escribir la línea de separación
                archivo.write("-------------------------------\n")
                print(f"[INFO] Archivo de venta generado: {nombre_archivo}")

        except Exception as e:
            print(f"[ERROR] Error al generar el archivo de venta: {e}")



        

    def ejecutar_captura(self):
        def capture():
            cap = cv2.VideoCapture(0)

            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    barcodes = pyzbar.decode(frame)
                    for barcode in barcodes:
                        barcodeData = int(barcode.data.decode("utf-8").strip())
                        cantidad_digitos = int(math.log10(barcodeData)) + 1

                        if cantidad_digitos == 13:
                            resultado = baseDatos.loc[baseDatos['codigo_barra'] == str(barcodeData)]



                            if not resultado.empty:
                                # Imprimir información sobre el código de barras encontrado
                                print("[INFO] Found {} barcode: {}".format(barcode.type, barcodeData))
                                # Pausar automáticamente después de encontrar un código
                                paused = True

                                primeraFila = resultado.iloc[0]

                                # Actualizar las listas en la interfaz gráfica
                                self.frame_lista_1.lista.insert(tk.END, primeraFila.codigo_barra)
                                self.frame_lista_2.lista.insert(tk.END, primeraFila.nombre_producto)
                                self.frame_lista_3.lista.insert(tk.END, primeraFila.rubro)

                                # suma_precio = round(ventaActual['precio'].sum(), 2)
                                # self.label_total.config(text=f"Total: {suma_precio}")

                                # Agregar la fila al DataFrame
                                ventaActual.loc[len(ventaActual)] = primeraFila
                                ventaActual.reset_index(drop=True, inplace=True)

                                

                        else:
                            # Si el código de barras no tiene 13 dígitos, no realizar acciones adicionales
                            print("[INFO] Invalid barcode: {}".format(barcodeData))


            cap.release()

        # Crear un hilo para la captura de video
        capture_thread = threading.Thread(target=capture)
        capture_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGrafica(root)
    root.mainloop()