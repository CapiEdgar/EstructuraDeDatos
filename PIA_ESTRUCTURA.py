import datetime
import sqlite3
from sqlite3 import Error
import sys
import pandas as pd
from rich.console import Console
from rich.table import Table
#-----------------------------------------------------------------------------------------------------------------------------------
sqlite3.register_adapter(datetime.date, lambda x: x.strftime("%m/%d/%Y"))
try:
    with sqlite3.connect("BaseEvidencia3.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS pacientes \
        (clave INTEGER PRIMARY KEY, apellido_paterno TEXT NOT NULL, apellido_materno TEXT, nombre TEXT NOT NULL, \
        fecha_nacimiento DATE NOT NULL, sexo TEXT NOT NULL);")
        cursor.execute("CREATE TABLE IF NOT EXISTS citas \
        (folio INTEGER PRIMARY KEY, clave INTEGER NOT NULL, fecha_cita DATE NOT NULL, turno TEXT NOT NULL, \
        realizada INTEGER,estatura REAL, peso REAL, hora TEXT, presion_sistolica REAL, presion_diastolica REAL, diagnostico TEXT, FOREIGN KEY(clave) REFERENCES pacientes(clave));")
except Error as e:
    print (e)
except Exception:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
#-----------------------------------------------------------------------------------------------------------------------------------
def registrarp():
    print("\nRegistrar nuevo paciente")

    # Solicitar apellido paterno y validar que solo contenga letras
    while True:
        apellido_paterno = input("Ingrese apellido paterno (o escriba salir para finalizar el proceso): ").strip()
        if apellido_paterno.lower() == "salir":
            print("Regresando al menú principal...")
            return

        caracteres = apellido_paterno.replace(" ","")
        if not caracteres.isalpha(): #.isalpha() si tiene solo letras regresa True, pero si tiene espacios o numeros regresa False
            print("Error: El apellido paterno solo puede contener letras. Intente nuevamente.")
            continue
        break

    # Solicitar apellido materno y validar que solo contenga letras
    while True:
        apellido_materno = input("Ingrese apellido materno (opcional o escriba salir para finalizar el proceso): ")
        if not apellido_materno:
            break
        if apellido_materno.lower() == "salir":
            print("Regresando al menú principal...")
            return

        caracteres = apellido_materno.replace(" ","")
        if not caracteres.isalpha():
            print("Error: El apellido materno solo puede contener letras. Intente nuevamente.")
            continue
        break

    # Solicitar nombre y validar que solo contenga letras
    while True:
        nombre = input("Ingrese su nombre (o escriba salir para finalizar el proceso): ")
        if nombre.lower() == "salir":
            print("Regresando al menú principal...")
            return
        caracteres = nombre.replace(" ","")

        if not caracteres.isalpha(): #.isalpha() si tiene solo letras regresa True, pero si tiene espacios o numeros regresa False
            print("Error: El nombre solo puede contener letras. Intente nuevamente.")
            continue
        break

    # Validar fecha de nacimiento
    while True:

        fecha_nacimiento = input("Ingrese fecha de nacimiento (mm/dd/yyyy) (o escriba salir para finalizar el proceso): ")
        if fecha_nacimiento.lower() == "salir":
            print("Regresando al menú principal...")
            return
        try:
            fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%m/%d/%Y").date()
            fecha_nacimiento_formato_db = fecha_nacimiento.strftime("%Y-%m-%d")
            # Validar que la fecha de nacimiento sea menor a la fecha actual
            fecha_actual = datetime.date.today()

            if fecha_nacimiento > fecha_actual:
                print("Error: La fecha de nacimiento no puede ser mayor a la fecha actual. Intente nuevamente.")
                continue

            break
        except ValueError:
            print("Error: Formato de fecha incorrecto (mm/dd/yyyy). Intente nuevamente.")



    while True:
        sexo = input("Ingrese sexo del paciente (H)ombre, (M)ujer (o escriba salir para finalizar el proceso): ").upper()
        if sexo.upper() == "SALIR":
                print("Regresando al menú principal...")
                return
        if sexo in ['H', 'M', '']:
            break
        else:
            print("Error: Opción no válida. Ingrese 'H' para Hombre, 'M' para Mujer (o escriba salir para finalizar el proceso)")

    if not sexo:
        sexo = 'N'
        print("No se ha proporcionado el sexo del paciente.")

    try:
        with sqlite3.connect("BaseEvidencia3.db") as conn:
            cursor = conn.cursor()
            valores = (apellido_paterno.upper(), apellido_materno.upper(), nombre.upper(), fecha_nacimiento_formato_db, sexo.upper())
            cursor.execute("INSERT INTO pacientes(apellido_paterno, apellido_materno, nombre, fecha_nacimiento, sexo) VALUES(?,?,?,?,?)", valores)
            print(f"La clave asignada fue {cursor.lastrowid}")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    finally:
        conn.close()
#----------------------------------------------------------------------------------------------------------------------------------
def calcular_edad(fecha_nacimiento, clave_paciente ,detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES):
    try:
        with sqlite3.connect("BaseEvidencia3.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fecha_nacimiento FROM pacientes WHERE clave =?", (clave_paciente,))
            # Convertir la fecha de nacimiento a un objeto de tipo datetime
            fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, '%m-%d-%y')
            
            # Obtener la fecha actual
            fecha_actual = datetime.datetime.now()
            
            # Calcular la diferencia de años entre la fecha actual y la fecha de nacimiento
            edad = fecha_actual.year - fecha_nacimiento.year
            
            # Ajustar la edad si aún no ha pasado el cumpleaños en el año actual
            if fecha_actual.month < fecha_nacimiento.month or (fecha_actual.month == fecha_nacimiento.month and fecha_actual.day < fecha_nacimiento.day):
                edad -= 1
            
            return edad
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    finally:
        conn.close()
#------------------------PROGRAMAR CITA-----------------------------------------------------------------------------------------------------------
def obtener_fecha_cita():
    hoy = datetime.date.today()
    fecha_cita = hoy  # Inicializar fecha_cita con la fecha actual
    limite_inferior = hoy + datetime.timedelta(days=1)  # Sugerimos al menos un día después del día actual
    limite_superior = hoy + datetime.timedelta(days=60)  # Sugerimos un máximo de 60 días desde el día actual

    fecha_mas_distante = limite_superior  # Fecha más distante permitida


    while True:
        str_fecha = input("Fecha que desea la cita (mm/dd/aaaa) o escriba salir para finalizar el proceso: ")
        if str_fecha.lower() == "salir":
            return str_fecha
        fecha = str_fecha
        try:
            fecha_cita = datetime.datetime.strptime(fecha, "%m/%d/%Y").date()
            if fecha_cita < limite_inferior:
                print("Error: La fecha de la cita debe ser al menos un día después del día actual.")
                print(f"Sugerencia: La fecha más temprana posible es {limite_inferior.strftime('%m/%d/%Y')}.")
                continue
            elif fecha_cita > limite_superior:
                print("Error: La fecha de la cita no puede ser mayor a 60 días respecto de la fecha actual.")
                print(f"Sugerencia: La fecha más distante posible es {fecha_mas_distante.strftime('%m/%d/%Y')}.")
                continue
            elif fecha_cita.weekday() == 6:  # Domingo
                print("La fecha de la cita no puede ser un Domingo ya que no tenemos servicio ese día.")
                print("Se sugiere programarla para el sábado inmediato antes de la fecha deseada.")
                confirmacion = input("¿Desea programar la cita para el sábado anterior? (Sí/No): ").lower()
                if confirmacion == 'si' or confirmacion == 'sí':
                    fecha_cita -= datetime.timedelta(days=1)
                    print(f"Fecha de la cita programada para : {fecha_cita}")  # Restar un día para ajustar al sábado anterior
                else:
                    continue
            break
        except ValueError:
            print("Error: Formato de fecha incorrecto (mm/dd/aaaa). Intente nuevamente.")

        # Actualizamos la fecha más distante posible si la fecha ingresada está dentro de los límites
        if fecha_cita > fecha_mas_distante:
            fecha_mas_distante = fecha_cita

    return fecha_cita
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def obtener_turno():
    while True:
        str_turno = input("Ingrese turno de la cita (1 – mañana, 2- mediodía, 3 - tarde) o escriba salir para finalizar el proceso: ").upper()
        if str_turno == "SALIR":
                print("Regresando al menú principal...")
                return str_turno
        turno = str_turno
        if turno in ['1', '2', '3']:
            if turno == '1':
                return "MAÑANA"
            elif turno == '2':
                return "MEDIODÍA"
            else:
                return "TARDE"
        else:
            print("Error: El turno de la cita debe ser 1, 2 o 3.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def clave_paciente_existe(clave_paciente):
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('BaseEvidencia3.db')
    cursor = conn.cursor()

    # Buscar el paciente con la clave proporcionada
    cursor.execute("SELECT 1 FROM pacientes WHERE clave = ?", (clave_paciente,))
    data = cursor.fetchone()

    # Cerrar la conexión
    conn.close()

    # Si data es None, entonces no se encontró ningún paciente con esa clave
    return data is not None
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def verificador_de_pacientes():
    # Verificar si hay pacientes registrados
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect('BaseEvidencia3.db')
    cursor = conn.cursor()

    # Contar el número de registros en la tabla de pacientes
    cursor.execute("SELECT COUNT(*) FROM pacientes")
    num_pacientes = cursor.fetchone()[0]

    # Verificar si hay pacientes registrados
    if num_pacientes == 0:
        print("Error: No hay pacientes registrados. Registre al menos un paciente antes de usar este proceso.")
        return True
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def programar_cita():
    verificador_de_pacientes()
    conn = sqlite3.connect('BaseEvidencia3.db')
    cursor = conn.cursor()

    console = Console()

    print("\nProgramar nueva cita\n")

    # Mostrar lista de pacientes existentes

    cursor.execute("SELECT clave, apellido_paterno, apellido_materno, nombre FROM pacientes")
    pacientes = cursor.fetchall()
    column_names = ['Clave', 'Apellido Paterno', 'Apellido Materno', 'Nombre']
    pacientes_df = pd.DataFrame(pacientes, columns=column_names)

    # Ordenar pacientes alfabéticamente por apellido paterno
    pacientes_df = pacientes_df.sort_values(by='Apellido Paterno')

    # Use Rich Table to print the patients list
    table = Table(title="Pacientes Existentes")
    for column in column_names:
        table.add_column(column, justify="center", style="cyan")

    # Agregar filas a la tabla
    for _, row in pacientes_df.iterrows():
        table.add_row(str(row['Clave']), str(row['Apellido Paterno']), str(row['Apellido Materno']), str(row['Nombre']))

    console.print(table)


    while True:
        clave_paciente = input("Ingrese clave del paciente (o escriba salir para finalizar el proceso): ")
        if clave_paciente.upper() == "SALIR":
            print("Regresando al menú de Gestión de Citas...")
            return
        try:
            clave_paciente = int(clave_paciente)
        except ValueError:
            print("Error: La clave del paciente debe ser un número.")
            continue

        # Usar la función para verificar si existe un paciente
        if not clave_paciente_existe(clave_paciente):
            print("Error: La clave del paciente no existe.")
        else:
            break

    fecha_cita = obtener_fecha_cita()
    try:
        if fecha_cita.lower() == "salir":
            return
    except Exception:
        pass

    fecha_cita_formato_db = fecha_cita.strftime("%Y-%m-%d")  # Convertir fecha a formato "YYYY-MM-DD"

    turno = obtener_turno()
    try:
        if turno.lower() == "salir":
            return
    except Exception:
        pass

    # Check for duplicate appointments
    cursor.execute("SELECT 1 FROM citas WHERE clave =? AND fecha_cita =? AND turno =?", (clave_paciente, fecha_cita_formato_db, turno))
    data = cursor.fetchone()

    # Si no hay citas duplicadas, entonces agrega la nueva cita
    if data is None:
        # Generate a unique folio number and insert the new appointment into the citas table
        cursor.execute("INSERT INTO citas(folio, clave, fecha_cita, turno, realizada) SELECT COALESCE(MAX(folio), 0) + 1,?,?,?,'NO' FROM citas", (clave_paciente, fecha_cita_formato_db, turno))
        conn.commit()

        cursor.execute("SELECT MAX(folio) FROM citas")
        folio = cursor.fetchone()[0]

        console.print(f"El folio asignado fue {str(folio)}. Cita programada con exito", style="green")

    else:
        console.print("Error: Ya existe una cita programada para este paciente en esta fecha y turno.", style="red")

    # Close the database connection
    conn.close()
#------------------------REALIZAR CITA-----------------------------------------------------------------------------------------------------------
def obtener_peso():
    while True:
        entrada = input("Ingrese peso del paciente en kilogramos (máximo 500) (o escriba salir para finalizar el proceso): ").strip()
        if entrada.upper() == "SALIR":
            print("Regresando al menú...")
            return None

        if entrada.isdigit():
            peso = float(entrada)
            if 1 <= peso <= 500:
                return peso
            else:
                print("Error: Peso fuera de lo normal... Este debe estar entre 1 y 500 kg.")
        else:
            print("Error: Por favor, ingrese un valor numérico válido.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def obtener_estatura():
    while True:
        entrada = input("Ingrese estatura del paciente en centímetros (máximo 300) (o escriba salir para finalizar el proceso): ").strip()
        if entrada.upper() == "SALIR":
            print("Regresando al menú...")
            return None

        if entrada.isdigit():
            estatura = float(entrada)
            if 1 <= estatura <= 300:
                return estatura
            else:
                print("Error: Estatura fuera de lo normal... Esta debe estar entre 1 y 300 cm.")
        else:
            print("Error: Por favor, ingrese un valor numérico válido.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def obtener_presion_sistolica():
    while True:
        entrada = input("Ingrese el valor de la presión sistólica (mmHg, entre 60 y 250) (o escriba salir para finalizar el proceso): ").strip()
        if entrada.upper() == "SALIR":
            print("Regresando al menú...")
            return None

        if entrada.isdigit():
            presion = float(entrada)
            if 60 <= presion <= 250:
                return presion
            else:
                print("Error: Presión sistólica fuera de lo normal... Esta debe estar entre 60 y 250 mmHg.")
        else:
            print("Error: Por favor, ingrese un valor numérico válido.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def obtener_presion_diastolica():
    while True:
        entrada = input("Ingrese el valor de la presión diastólica (mmHg, entre 40 y 150) (o escriba salir para finalizar el proceso): ").strip()
        if entrada.upper() == "SALIR":
            print("Regresando al menú...")
            return None

        if entrada.isdigit():
            presion = float(entrada)
            if 40 <= presion <= 150:
                return presion
            else:
                print("Error: Presión diastólica fuera de lo normal... Esta debe estar entre 40 y 150 mmHg.")
        else:
            print("Error: Por favor, ingrese un valor numérico válido.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def realizar_cita():
    conn = sqlite3.connect('BaseEvidencia3.db')
    cursor = conn.cursor()

    console = Console()

    cursor.execute("SELECT * FROM citas WHERE realizada = 'NO'")
    citas_pendientes = cursor.fetchall()

    if not citas_pendientes:
        console.print("Error: No hay citas registradas. Programe al menos una cita antes de realizar una cita.", style="red")
        conn.close()
        return
    else:
        console.print("Realizar cita programada\n")

    df_citas = pd.read_sql_query("SELECT * FROM citas WHERE realizada = 'NO'", conn)


    df_citas['fecha_cita'] = df_citas['fecha_cita'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))
    table = Table(title="Citas Pendientes")
    table.add_column("Folio", justify="center", style="cyan")
    table.add_column("Fecha Cita", justify="center", style="cyan")
    table.add_column("Turno", justify="center", style="cyan")
    for row in df_citas[['folio', 'fecha_cita', 'turno']].values:
        table.add_row(*[str(cell) for cell in row])
    console.print(table)

    while True:
        folio = input("Ingrese folio de la cita o presione Enter para regresar al menú de gestión de citas (o escriba salir para finalizar el proceso): ").strip()
        if folio.upper() == "SALIR":
            console.print("Regresando al menú...")
            conn.close()
            return
        try:
            folio = int(folio)
        except ValueError:
            console.print("Error: El folio de la cita debe ser un número.", style="red")
            continue

        cursor.execute("SELECT * FROM citas WHERE folio = ?", (folio,))
        cita = cursor.fetchone()

        if not cita:
            console.print("Error: El folio de la cita no existe.", style="red")
            continue

        clave_paciente = cita[1]
        cursor.execute("SELECT nombre, fecha_nacimiento FROM pacientes WHERE clave = ?", (clave_paciente,))
        paciente_info = cursor.fetchone()

        if not paciente_info:
            console.print("Error: La clave del paciente no existe.", style="red")
            continue

        nombre_paciente = paciente_info[0]
        fecha_nacimiento = datetime.datetime.strptime(paciente_info[1], '%Y-%m-%d')
        console.print(f"Atendiendo a paciente: {nombre_paciente} (Clave: {clave_paciente})\n")

        # Verificar si la cita ya ha sido realizada
        if cita[4] == 'SI':
            console.print("Error: Esta cita ya ha sido realizada.", style="red")
            conn.close()
            return

        peso = obtener_peso()
        if not peso:
            conn.close()
            return
        estatura = obtener_estatura()
        if not estatura:
            conn.close()
            return
        presion_sistolica = obtener_presion_sistolica()
        if not presion_sistolica:
            conn.close()
            return
        presion_diastolica = obtener_presion_diastolica()
        if not presion_diastolica:
            conn.close()
            return
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        # Solicitar y validar el diagnóstico del paciente
        while True:
            diagnostico = input("Ingrese el diagnóstico del paciente (máximo 200 caracteres) (o escriba salir para finalizar el proceso): ").strip()
            if diagnostico.upper() == "SALIR":
                console.print("Regresando al menú...")
                conn.close()
                return
            if diagnostico:
                if len(diagnostico) <= 200:
                    break
                else:
                    console.print("Error: El diagnóstico debe tener como máximo 200 caracteres.", style="red")
            else:
                console.print("Error: El diagnóstico no puede estar vacío.", style="red")

        # Calcular la edad del paciente en la fecha actual
        fecha_actual = datetime.date.today()
        edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

        # Actualizar la cita como realizada y registrar los datos obtenidos
        cursor.execute("UPDATE citas SET realizada = 'SI', peso = ?, estatura = ?, presion_sistolica = ?, presion_diastolica = ?, hora = ?, diagnostico = ? WHERE folio = ?", (peso, estatura, presion_sistolica, presion_diastolica, hora, diagnostico, folio))

        console.print(f"Cita realizada exitosamente para el paciente {nombre_paciente} (Clave: {clave_paciente}) con folio {folio}.", style="green")
        conn.commit()
        conn.close()
        break
#----------------CANCELAR CITA------------------------------------------------------------------------------------------------------------------
def cancelar_cita():
    while True:
        print("\nSubmenú Cancelar Cita:")
        print("1. Cancelar cita por Paciente")
        print("2. Cancelar cita por Fecha")
        print("3. Salir al menú de Gestion de citas")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            cancelar_cita_por_paciente()
        elif opcion == '2':
            cancelar_cita_por_fecha()
        elif opcion == '3':
            return
        else:
            print("Opción no válida. Intente de nuevo.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def cancelar_cita_por_paciente():
    console = Console()

    conn = sqlite3.connect('BaseEvidencia3.db')
    cursor = conn.cursor()

    cursor.execute("SELECT p.clave, p.apellido_paterno, p.apellido_materno,p.nombre FROM pacientes AS p LEFT JOIN citas AS c ON p.clave = c.clave WHERE c.realizada = 'NO' GROUP BY p.clave, p.apellido_paterno, p.apellido_materno, p.nombre")
    pacientes = cursor.fetchall()
    column_names = ['Clave', 'Apellido Paterno', 'Apellido Materno', 'Nombre']
    pacientes_df = pd.DataFrame(pacientes, columns=column_names)

    if pacientes_df.empty:
        console.print("Error: No hay pacientes con citas pendientes.", style="red")
        return


    # Use Rich Table to print the patients list
    table = Table(title="Pacientes Existentes con Citas Pendientes")
    for column in column_names:
        table.add_column(column, justify="center", style="cyan")
    for row in pacientes:
        table.add_row(*[str(cell) for cell in row])  # Convert each cell to string
    console.print(table)

    while True:
        # Solicitar la clave del paciente
        clave = input("Ingrese la clave del paciente (o 'salir' para regresar al menú): ")
        if clave.lower() == 'salir':
            return  None# Exit the function and return to the menu
        if not clave.isdigit():
            console.print("Error: La clave debe ser un número entero.", style="red")
            continue
        clave = int(clave)
        break



    try:
        # Leer los datos de la tabla de pacientes en un DataFrame de pandas
        df_pacientes = pd.read_sql_query("SELECT * FROM pacientes WHERE clave =?", conn, params=(clave,))

        if df_pacientes.empty:
            console.print("Error: No se encontró ningún paciente con esa clave.", style="red")
            return

        nombre_completo = df_pacientes.iloc[0]['nombre'] + ' ' + df_pacientes.iloc[0]['apellido_paterno'] + ' ' + df_pacientes.iloc[0]['apellido_materno']

        console.print(f"\nCitas programadas para el paciente {nombre_completo}:")

        # Leer los datos de la tabla de citas en un DataFrame de pandas
        df_citas = pd.read_sql_query("SELECT * FROM citas WHERE clave =? AND realizada = 'NO'", conn, params=(clave,))

        if df_citas.empty:
            console.print("No hay citas registradas para este paciente.")
            return

        # Convertir la columna 'fecha_cita' a un formato más legible
        df_citas['fecha_cita'] = df_citas['fecha_cita'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

        # Mostrar las citas programadas para el paciente

        table = Table(title="Citas Programadas")
        table.add_column("Folio", justify="center", style="white")
        table.add_column("Fecha Cita", justify="center", style="white")
        table.add_column("Turno", justify="center", style="white")
        for row in df_citas[['folio', 'fecha_cita', 'turno']].values:
            table.add_row(*[str(cell) for cell in row])
        console.print(table)

        # Solicitar el folio de la cita a cancelar
        while True:
            folio_cita = input("\nIngrese el folio de la cita a cancelar (o 'salir' para regresar al menú): ")
            if folio_cita.lower() == 'salir':
                return  # Exit the function and return to the menu
            if not folio_cita.isdigit():
                console.print("Error: El folio de la cita debe ser un número entero.", style="red")
                continue
            folio_cita = int(folio_cita)
            break

        # Verificar si la cita existe
        if folio_cita not in df_citas['folio'].values:
            console.print("Error: La cita con ese folio no existe.", style="red")
            return

        # Solicitar confirmación para cancelar la cita
        while True:
            confirmacion = input(f"¿Está seguro de que desea cancelar la cita con folio {folio_cita} para {nombre_completo}? (S/N) ").strip().upper()
            if confirmacion == 'S':
                # Aquí pondrías la lógica para cancelar la cita
                break
            elif confirmacion == 'N':
                print("Cancelación de cita abortada.")
                return
            else:
                print("Por favor, responda solo con 'S' para sí o 'N' para no.")

        # Eliminar la cita de la base de datos
        cursor = conn.cursor()
        cursor.execute("DELETE FROM citas WHERE folio =? AND realizada = 'NO'", (folio_cita,))
        conn.commit()
        console.print(f"La cita con folio {folio_cita} ha sido cancelada.", style="green")

    finally:
        # Cerrar la conexión
        conn.close()
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def cancelar_cita_por_fecha():
    console = Console()

    while True:
        console.print('\n[bold white]Búsqueda de una cita por fecha[/bold white]')
        # Mostrar todas las citas donde realizada = 'NO'
        conn = sqlite3.connect('BaseEvidencia3.db')
        try:
            df_citas = pd.read_sql_query("SELECT * FROM citas WHERE realizada ='NO'", conn)

            if df_citas.empty:
                console.print("[bold red]Error: No hay citas programadas.[/bold red]")
                return

            df_citas['fecha_cita'] = df_citas['fecha_cita'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

            table = Table(show_header=True, header_style="bold white")
            table.add_column("Folio")
            table.add_column("Fecha de Cita")
            table.add_column("Turno")

            for _, row in df_citas.iterrows():
                table.add_row(str(row['folio']), str(row['fecha_cita']), row['turno'])

            console.print("\n[bold]Citas programadas :[/bold]")
            console.print(table)

            fecha_cita = input('Ingrese fecha de la cita (mm/dd/aaaa) o "salir" para regresar al menú: ')
            if fecha_cita.lower() == 'salir':
                return  # Exit the function and return to the menu

            fecha_cita = datetime.datetime.strptime(fecha_cita, "%m/%d/%Y").date()
            fecha_cita_formateada = fecha_cita.strftime("%Y-%m-%d")  # Convertir fecha a formato "YYYY-MM-DD"

            # Leer los datos de la tabla de citas en un DataFrame de pandas
            df_citas_fecha = pd.read_sql_query("SELECT * FROM citas WHERE realizada ='NO' AND fecha_cita =?", conn, params=(fecha_cita_formateada,))

            if df_citas_fecha.empty:
                console.print("[bold red]Error: No hay citas registradas para esa fecha.[/bold red]")
                return

            # Mostrar las citas programadas para la fecha
            table_fecha = Table(show_header=True, header_style="bold white")
            table_fecha.add_column("Folio")
            table_fecha.add_column("Clave")
            table_fecha.add_column("Turno")
            table_fecha.add_column("Nombre del Paciente")

            # Unir la tabla de citas con la tabla de pacientes
            df_citas_fecha = pd.merge(df_citas_fecha, pd.read_sql_query("SELECT clave, nombre FROM pacientes", conn), on='clave')

            for _, row in df_citas_fecha.iterrows():
                table_fecha.add_row(str(row['folio']), str(row['clave']), row['turno'], row['nombre'])

            console.print(f"\n[bold]Citas programadas para la fecha {fecha_cita}[/bold]\n")
            console.print(table_fecha)

            # Solicitar el folio de la cita a cancelar
            while True:
                folio_cita = input("\nIngrese el folio de la cita a cancelar (o 'salir' para regresar al menú): ")
                if folio_cita.lower() == 'salir':
                    return  # Exit the function and return to the menu
                if not folio_cita.isdigit():
                    console.print("[bold red]Error: El folio de la cita debe ser un número entero.[/bold red]")
                    continue
                folio_cita = int(folio_cita)
                break

            # Verificar si la cita existe
            if folio_cita not in df_citas_fecha['folio'].values:
                console.print("[bold red]Error: La cita con ese folio no existe.[/bold red]")
                return

            while True:
                confirmacion = input(f"¿Está seguro de que desea cancelar la cita con folio {folio_cita} ? (S/N) ").strip().upper()
                if confirmacion == 'S':
                    # Aquí pondrías la lógica para cancelar la cita
                    break
                elif confirmacion == 'N':
                    print("Cancelación de cita abortada.")
                    return
                else:
                    print("Por favor, responda solo con 'S' para sí o 'N' para no.")


            # Cancelar la cita
            # Actualizar la tabla de citas en la base de datos
            cursor = conn.cursor()
            cursor.execute("DELETE FROM citas WHERE folio =? AND realizada = 'NO'", (folio_cita,))
            conn.commit()
            console.print(f"La cita con folio {folio_cita} ha sido cancelada.")

        except ValueError:
            console.print("[bold red]Error: La fecha debe tener el formato mm/dd/aaaa.[/bold red]")
        finally:
            # Cerrar la conexión
            conn.close()

#-------REPORTES PACIENTES----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def reporte_de_citas_por_periodo():
    console = Console()

    while True:
        console.print('\n[bold white]Reporte de citas por período[/bold white]')

        fecha_inicio_str = input('Fecha de inicio (mm/dd/yyyy) o "salir" para regresar al menú de reportes: ')
        if fecha_inicio_str.lower() == 'salir':
            return  

        fecha_fin_str = input('Fecha de fin (mm/dd/yyyy) o "salir" para regresar al menú de reportes: ')
        if fecha_fin_str.lower() == 'salir':
            return  

        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%m/%d/%Y").date()
            fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%m/%d/%Y").date()

            if fecha_inicio > fecha_fin:
                console.print("[bold red]Error: La fecha de inicio no puede ser posterior a la fecha de fin.[/bold red]")
                continue

            # Convertir las fechas a formato YYYY-MM-DD
            fecha_inicio_formateada = fecha_inicio.strftime("%Y-%m-%d")
            fecha_fin_formateada = fecha_fin.strftime("%Y-%m-%d")

            conn = sqlite3.connect('BaseEvidencia3.db')
            try:
                cursor = conn.cursor()

                cursor.execute("SELECT c.*, p.nombre FROM citas c INNER JOIN pacientes p ON c.clave = p.clave WHERE c.fecha_cita BETWEEN ? AND ?", (fecha_inicio_formateada, fecha_fin_formateada))
                citas = cursor.fetchall()

                column_names = ['Folio', 'Clave paciente', 'Fecha de cita', 'Turno', 'Realizada', 'Estatura', 'Peso', 'Hora', 'Presión sistólica', 'Presión diastólica', 'Diagnóstico', 'Paciente']

                df = pd.DataFrame(citas, columns=column_names)
                
                # Apply date format to 'Fecha de cita' column
                df['Fecha de cita'] = df['Fecha de cita'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))
                
                if df.empty:
                    console.print("[white]No hay citas registradas en ese rango de fechas.[/white]")
                else:
                    table = Table(show_header=True, header_style="bold white")
                    for col in ['Folio', 'Clave paciente', 'Fecha de cita', 'Turno', 'Realizada']:
                        table.add_column(col, style="white")
                    
                    for _, row in df.iterrows():
                        table.add_row(str(row['Folio']), str(row['Clave paciente']), row['Fecha de cita'], row['Turno'], row['Realizada'])

                    console.print("\n[bold white]Listado de citas entre[/bold white]", fecha_inicio_str, "[bold white]y[/bold white]", fecha_fin_str, "\n")
                    console.print(table)

            except sqlite3.Error as e:
                console.print("[bold red]Error:[/bold red]", e)
            finally:
                # Cerrar la conexión
                conn.close()

            return df  # Devuelve el DataFrame df al final de la función

        except ValueError:
            console.print("[bold red]Error:[/bold red] La fecha debe tener el formato mm/dd/yyyy.")


#------------------------------------------------------------------
def reporte_de_citas_por_paciente():
    console = Console()

    while True:
        conn = sqlite3.connect('BaseEvidencia3.db')
        cursor = conn.cursor()

        cursor.execute("SELECT clave, apellido_paterno, apellido_materno, nombre FROM pacientes")
        pacientes = cursor.fetchall()
        column_names = ['Clave', 'Apellido Paterno', 'Apellido Materno', 'Nombre']

        table = Table(title="Pacientes Existentes")
        for column in column_names:
            table.add_column(column, justify="center", style="cyan")
        for row in pacientes:
            table.add_row(*[str(cell) for cell in row])  # Convert each cell to string
        console.print(table)

        clave_paciente_str = input("Ingrese la clave del paciente (o ingrese 'salir' para volver al menú de reportes de citas): ")

        if clave_paciente_str.upper() == "SALIR":
            conn.close()
            return None
        
        try:
            clave_paciente = int(clave_paciente_str)
            df_pacientes = pd.read_sql_query("SELECT * FROM pacientes WHERE clave =?", conn, params=(clave_paciente,))

            if df_pacientes.empty:
                console.print("Error: No se encontró ningún paciente con esa clave.", style="red")
                console.print("Intente nuevamente o ingrese 'salir' para volver al menú de reportes de citas.", style="bold red")
                conn.close()
                continue

            cursor.execute("SELECT * FROM citas WHERE clave =?", (clave_paciente,))
            citas = cursor.fetchall()

            if citas:
                console.print("\nListado de citas para el paciente con clave", clave_paciente, style='bold blue')
                df = pd.DataFrame(citas, columns=['Folio', 'Clave', 'Fecha de cita', 'Turno', 'Realizada', 'Estatura', 'Peso', 'Hora', 'Presión sistólica', 'Presión diastólica', 'Diagnóstico'])
                df['Fecha de cita'] = df['Fecha de cita'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

                # Create a Rich Table
                table = Table(title="Citas del paciente", style='bold white')
                table.add_column("Folio", justify="center", style="white", no_wrap=True)
                table.add_column("Fecha de cita", justify="center", style="white", no_wrap=True)
                table.add_column("Turno", justify="center", style="white", no_wrap=True)
                table.add_column("Realizada", justify="center", style="white", no_wrap=True)

                for index, cita in df.iterrows():
                    table.add_row(str(cita['Folio']), cita['Fecha de cita'], cita['Turno'], cita['Realizada'])

                console.print(table)

                for index, cita in df.iterrows():
                    if cita['Realizada'] == 'SI':
                        console.print("La cita con folio {} ya ha sido realizada.".format(cita['Folio']), style='bold green')
                        ver_expediente = input("¿Desea ver el expediente de esta cita con folio {}? (s/n): ".format(cita['Folio'])).lower()
                        while ver_expediente not in ['s', 'n']:
                            console.print("Error: Por favor, responda solo con 's' o 'n'.", style='bold red')
                            ver_expediente = input("¿Desea ver el expediente de esta cita con folio {}? (s/n): ".format(cita['Folio'])).lower()
                        if ver_expediente == 's':
                            expediente = {
                                'Estatura': cita['Estatura'],
                                'Peso': cita['Peso'],
                                'Hora': cita['Hora'],
                                'Presión arterial': '{:03}/{:03}'.format(int(round(float(cita['Presión sistólica']))), int(round(float(cita['Presión diastólica'])))),
                                'Diagnóstico': cita['Diagnóstico']
                            }

                            # Create a Rich Table for the expediente
                            table_expediente = Table(title="Expediente de la cita", style='bold white')
                            table_expediente.add_column("Datos", justify="center", style="white", no_wrap=True)
                            table_expediente.add_column("", justify="center", style="white", no_wrap=True)

                            for key, value in expediente.items():
                                table_expediente.add_row(key, str(value))

                            console.print(table_expediente)
                return df  # Return the DataFrame
            else:
                console.print("\nNo se encontraron citas para el paciente con clave", clave_paciente, style='bold red')
            conn.close()

        except ValueError:
            console.print("Error: Por favor, ingrese un número entero válido para la clave del paciente.", style="red")
            conn.close()


#-----------------EXPORTAR EN CSV O EXCEL----------------------------------------------------------------------
def exportar_reporte(df, formato):
    while True:
        formato = formato.lower()
        if formato == 'c':
            df.to_csv('reporte_citas.csv', index=False)
            print("El reporte ha sido exportado en formato CSV.")
            break
        elif formato == 'e':
            df.to_excel('reporte_citas.xlsx', index=False)
            print("El reporte ha sido exportado en formato Excel.")
            break
        elif formato =='salir':
            break
        else:
            print("Formato no reconocido. Por favor ingrese 'c' para CSV o 'e' para Excel. (o escriba 'salir' para cancelar esta opcion):")
            formato = input("Ingrese el formato para exportar ('c' para CSV, 'e' para Excel) (o escriba 'salir' para cancelar esta opcion): ")
#-------------------------------------------------------
def reporte_de_citas():
    while True:
        print('\n Menu de Reportes de Citas')
        print('1. Reporte de citas por periodo.')
        print('2. Reporte de citas por paciente.')
        print('3. Regresar al Menu.\n')

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            df = reporte_de_citas_por_periodo()
            if df is not None and not df.empty:
                exportar = input("¿Desea exportar el reporte? (s/n): ")
                if exportar.lower() == 's':
                    formato = input("Ingrese 'c' para exportar en CSV o 'e' para exportar en Excel(o escriba 'salir' para volver al menu de Estadisticos demograficos): ")
                    exportar_reporte(df, formato)
        elif opcion == "2":
            df = reporte_de_citas_por_paciente()
            if df is not None and not df.empty:
                exportar = input("¿Desea exportar el reporte? (s/n): ")
                if exportar.lower() == 's':
                    formato = input("Ingrese 'c' para exportar en CSV o 'e' para exportar en Excel(o escriba 'salir' para volver al menu de Estadisticos demograficos): ")
                    exportar_reporte(df, formato)
            

        elif opcion == "3":
            return
        else:
            print("Opción inválida. Por favor seleccione una opción válida.")
#-----------------------------------------------------
def mostrar_listado_pacientes():
    console = Console()

    with sqlite3.connect('BaseEvidencia3.db') as conn:
        try:
            pacientes_df = pd.read_sql_query("SELECT * FROM pacientes", conn)

            # Verificar si hay pacientes registrados
            if pacientes_df.empty:
                console.print("[bold red]No hay pacientes registrados.[/bold red]")
                return None

            # Formatear la fecha de nacimiento
            pacientes_df['fecha_nacimiento'] = pacientes_df['fecha_nacimiento'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))
            pacientes_df.columns = ['Clave', 'Apellido Paterno', 'Apellido Materno', 'Nombre', 'Fecha de Nacimiento', 'Sexo']

            # Crear tabla para mostrar los pacientes
            table = Table(show_header=True, header_style="bold white")
            for col in pacientes_df.columns:
                table.add_column(col)

            # Agregar filas a la tabla
            for _, row in pacientes_df.iterrows():
                table.add_row(str(row['Clave']), row['Apellido Paterno'], row['Apellido Materno'], row['Nombre'], row['Fecha de Nacimiento'], row['Sexo'])

            console.print(table)
            return pacientes_df
        except sqlite3.Error as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
#-----------------------------------------------------
#-----------------------------------------------------

def buscar_por_clave():
    console= Console()
    while True:
        clave_paciente = input('Clave del paciente (o escriba salir para finalizar el proceso): ').strip()

        if clave_paciente.lower() == "salir":
            print("Regresando al menú principal...")
            return None

        try:
            clave_paciente = int(clave_paciente)
        except ValueError:
            print("Error: La clave del paciente debe ser un número entero. Intente nuevamente.")
            continue

        conn = sqlite3.connect('BaseEvidencia3.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pacientes WHERE clave = ?", (clave_paciente,))
        paciente = cursor.fetchone()

        if paciente:
            print("\nInformación del paciente:")

            paciente_df = pd.DataFrame([paciente], columns=['Clave', 'Apellido paterno', 'Apellido materno', 'Nombre', 'Fecha de nacimiento', 'Sexo'])
            paciente_df['Fecha de nacimiento'] = paciente_df['Fecha de nacimiento'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

            # Create a table using Rich Table
            table = Table(title="Paciente")
            table.add_column("Clave", justify="center")
            table.add_column("Apellido paterno", justify="center")
            table.add_column("Apellido materno", justify="center")
            table.add_column("Nombre", justify="center")
            table.add_column("Fecha de nacimiento", justify="center")
            table.add_column("Sexo", justify="center")
            for index, paciente in paciente_df.iterrows():
                table.add_row(str(paciente["Clave"]), paciente["Apellido paterno"], paciente["Apellido materno"], paciente["Nombre"], paciente["Fecha de nacimiento"], paciente["Sexo"])
            console.print(table)

            cursor.execute("SELECT COUNT(*) FROM citas WHERE clave =?", (clave_paciente,))
            citas_count = cursor.fetchone()[0]

            if citas_count > 0:
                consultar_detalles = input("\n¿Desea consultar más detalles del paciente? (s/n): ").lower()
                if consultar_detalles == 's':
                    cursor.execute("SELECT * FROM citas WHERE clave =?", (clave_paciente,))
                    citas = cursor.fetchall()
                    if citas:
                        print("\nListado de citas para el paciente con clave", clave_paciente)
                        df = pd.DataFrame(citas, columns=['Folio', 'Clave', 'Fecha de cita', 'Turno', 'Realizada','Estatura', 'Peso', 'Hora', 'Presión sistólica', 'Presión diastólica', 'Diagnóstico'])
                        df['Fecha de cita'] = df['Fecha de cita'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

                        # Create a table using Rich Table
                        table = Table(title="Citas")
                        table.add_column("Folio", justify="center")
                        table.add_column("Fecha de cita", justify="center")
                        table.add_column("Turno", justify="center")
                        table.add_column("Realizada", justify="center")
                        for index, cita in df.iterrows():
                            table.add_row(str(cita["Folio"]), cita["Fecha de cita"], cita["Turno"], cita["Realizada"])
                        console.print(table)

                        for index, cita in df.iterrows():
                            if cita['Realizada'] == 'SI':
                                console.print("La cita con folio {} ya ha sido realizada.".format(cita['Folio']), style='bold green')
                                ver_expediente = input("¿Desea ver el expediente de esta cita con folio {}? (s/n): ".format(cita['Folio']))
                                if ver_expediente.lower() == 's':
                                    expediente = {
                                        'Estatura': cita['Estatura'],
                                        'Peso': cita['Peso'],
                                        'Hora': cita['Hora'],
                                        'Presión arterial': '{:03}/{:03}'.format(int(round(float(cita['Presión sistólica']))), int(round(float(cita['Presión diastólica'])))),
                                        'Diagnóstico': cita['Diagnóstico']
                                    }

                                    # Create a Rich Table for the expediente
                                    table_expediente = Table(title="Expediente de la cita", style='bold white')
                                    table_expediente.add_column("Datos", justify="center", style="white", no_wrap=True)
                                    table_expediente.add_column("", justify="center", style="white", no_wrap=True)

                                    for key, value in expediente.items():
                                        table_expediente.add_row(key, str(value))

                                    console.print(table_expediente)

                        return df



                else:
                    console.print("\nNo se consultaron más detalles del paciente.", style="bold red")
                    return None
            else:
                console.print("\nNo hay citas registradas para este paciente.", style="bold red")
                break
                    

        else:
            console.print("No se encontró ningún paciente con esa clave.", style="bold red")
            continue

    conn.close()



def buscar_paciente_por_nombre_y_apellidos():
    console = Console()

    while True:
        print('\nBúsqueda de un paciente por sus apellidos y nombre')

        apellido_paterno = input('Apellido paterno (o ingrese "salir" para regresar al menu de reportes de pacientes): ').upper()
        if apellido_paterno == 'SALIR':
            return None

        nombre = input('Nombre (o ingrese "salir" para regresar al menu de reportes de pacientes): ').upper()
        if nombre == 'SALIR':
            return None
        conn = sqlite3.connect('BaseEvidencia3.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pacientes WHERE apellido_paterno =? AND nombre =?", (apellido_paterno, nombre))
        paciente = cursor.fetchone()

        if paciente:
            print("\nInformación del paciente:")

            paciente_df = pd.DataFrame([paciente], columns=['Clave', 'Apellido paterno', 'Apellido materno', 'Nombre', 'Fecha de nacimiento', 'Sexo'])
            paciente_df['Fecha de nacimiento'] = paciente_df['Fecha de nacimiento'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

            # Create a table using Rich Table
            table = Table(title="Paciente")
            table.add_column("Clave", justify="center")
            table.add_column("Apellido paterno", justify="center")
            table.add_column("Apellido materno", justify="center")
            table.add_column("Nombre", justify="center")
            table.add_column("Fecha de nacimiento", justify="center")
            table.add_column("Sexo", justify="center")
            for index, paciente in paciente_df.iterrows():
             table.add_row(str(paciente["Clave"]), paciente["Apellido paterno"], paciente["Apellido materno"], paciente["Nombre"], paciente["Fecha de nacimiento"], paciente["Sexo"])
            console.print(table)

            cursor.execute("SELECT COUNT(*) FROM citas WHERE clave =?", (paciente.iloc[0],))
            citas_count = cursor.fetchone()[0]

            if citas_count > 0:
                consultar_detalles = input("\n¿Desea consultar más detalles del paciente? (s/n): ").lower()
                if consultar_detalles == 's':
                    cursor.execute("SELECT * FROM citas WHERE clave =?", (paciente.iloc[0],))
                    citas = cursor.fetchall()
                    if citas:
                        print("\nListado de citas para el paciente con clave", paciente.iloc[0])
                        df = pd.DataFrame(citas, columns=['Folio', 'Clave', 'Fecha de cita', 'Turno', 'Realizada','Estatura', 'Peso', 'Hora', 'Presión sistólica', 'Presión diastólica', 'Diagnóstico'])
                        df['Fecha de cita'] = df['Fecha de cita'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d/%Y'))

                        # Create a table using Rich Table
                        table = Table(title="Citas")
                        table.add_column("Folio", justify="center")
                        table.add_column("Fecha de cita", justify="center")
                        table.add_column("Turno", justify="center")
                        table.add_column("Realizada", justify="center")
                        for index, cita in df.iterrows():
                            table.add_row(str(cita["Folio"]), cita["Fecha de cita"], cita["Turno"], cita["Realizada"])
                        console.print(table)

                        for index, cita in df.iterrows():
                            if cita['Realizada'] == 'SI':
                                console.print("La cita con folio {} ya ha sido realizada.".format(cita['Folio']), style='bold green')
                                ver_expediente = input("¿Desea ver el expediente de esta cita con folio {}? (s/n): ".format(cita['Folio']))
                                if ver_expediente.lower() == 's':
                                    expediente = {
                                        'Estatura': cita['Estatura'],
                                        'Peso': cita['Peso'],
                                        'Hora': cita['Hora'],
                                        'Presión arterial': '{:03}/{:03}'.format(int(round(float(cita['Presión sistólica']))), int(round(float(cita['Presión diastólica'])))),
                                        'Diagnóstico': cita['Diagnóstico']
                                    }

                                    # Create a Rich Table for the expediente
                                    table_expediente = Table(title="Expediente de la cita", style='bold white')
                                    table_expediente.add_column("Datos", justify="center", style="white", no_wrap=True)
                                    table_expediente.add_column("", justify="center", style="white", no_wrap=True)

                                    for key, value in expediente.items():
                                        table_expediente.add_row(key, str(value))

                                    console.print(table_expediente)
                                    #print("\nDiagnóstico: {}".format(cita['Diagnóstico'])) #De esta manera se imprime por separado el diagnostico.
                        return df

                else:
                    console.print("\nNo se consultaron más detalles del paciente.", style="bold red")
                    break
            else:
                console.print("\nNo hay citas registradas para este paciente.", style="bold red")
                return None

        else:
            console.print("No se encontró ningún paciente con esos apellidos y nombre.", style="bold red")

            continue

        
        conn.close()

#-----------REPORTE PACIENTES------------------------------------------
def reporte_de_pacientes():
    while True:
        print('\nMenú de Reportes de Pacientes')
        print('1. Mostrar listado con todos los pacientes.')
        print('2. Búsqueda de un paciente por su clave.')
        print('3. Búsqueda de un paciente por sus apellidos y nombre.')
        print('4. Regresar al Menú de Consultas y Reportes.\n')

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            df=mostrar_listado_pacientes()
            if df is not None:
                exportar = input("¿Desea exportar el reporte? (s/n): ")
                if exportar.lower() == 's':
                    formato = input("Ingrese 'c' para exportar en CSV o 'e' para exportar en Excel(o escriba 'salir' para cancelar esta opcion): ")
                    exportar_reporte(df, formato)
        elif opcion == "2":
            df=buscar_por_clave()
            if df is not None:
                exportar = input("¿Desea exportar el reporte? (s/n): ")
                if exportar.lower() == 's':
                    formato = input("Ingrese 'c' para exportar en CSV o 'e' para exportar en Excel(o escriba 'salir' para cancelar esta opcion): ")
                    exportar_reporte(df, formato)
        elif opcion == "3":
            df=buscar_paciente_por_nombre_y_apellidos()
            if df is not None:
                exportar = input("¿Desea exportar el reporte? (s/n): ")
                if exportar.lower() == 's':
                    formato = input("Ingrese 'c' para exportar en CSV o 'e' para exportar en Excel(o escriba 'salir' para cancelar esta opcion): ")
                    exportar_reporte(df, formato)
        elif opcion == "4":
            return
        else:
            print("Opción inválida. Por favor seleccione una opción válida.")
#------------ESTADISTICOS DEMOGRAFICOS-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def estadisticos_demograficos():
    while True:
        print('\nEstadísticos Demográficos')
        print('1. Por Edad')
        print('2. Por Sexo')
        print('3. Por Edad y Sexo')
        print('4. Salir al menú de Consultas y Reportes')

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            estadisticos_por_edad()
        elif opcion == "2":
            estadisticos_por_sexo()
        elif opcion == "3":
            estadisticos_por_sexo_y_edad()
        elif opcion == "4":
            return
        else:
            print("Opción inválida. Por favor seleccione una opción válida.")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def calcular_estadisticos(df):
    # Calcular los estadísticos demográficos
    conteo = df['estatura'].count()
    minimo = df['estatura'].min()
    maximo = df['estatura'].max()
    media = df['estatura'].mean()
    mediana = df['estatura'].median()
    desviacion_estandar = df['estatura'].std()

    conteo_peso = df['peso'].count()
    minimo_peso = df['peso'].min()
    maximo_peso = df['peso'].max()
    media_peso = df['peso'].mean()
    mediana_peso = df['peso'].median()
    desviacion_estandar_peso = df['peso'].std()

    conteo_presion_sistolica = df['presion_sistolica'].count()
    minimo_presion_sistolica = df['presion_sistolica'].min()
    maximo_presion_sistolica = df['presion_sistolica'].max()
    media_presion_sistolica = df['presion_sistolica'].mean()
    mediana_presion_sistolica = df['presion_sistolica'].median()
    desviacion_estandar_presion_sistolica = df['presion_sistolica'].std()

    conteo_presion_diastolica = df['presion_diastolica'].count()
    minimo_presion_diastolica = df['presion_diastolica'].min()
    maximo_presion_diastolica = df['presion_diastolica'].max()
    media_presion_diastolica = df['presion_diastolica'].mean()
    mediana_presion_diastolica = df['presion_diastolica'].median()
    desviacion_estandar_presion_diastolica = df['presion_diastolica'].std()

    df_estadisticos = pd.DataFrame({
        'Estadístico': ['Conteo', 'Mínimo', 'Máximo', 'Media', 'Mediana', 'Desviación estándar'],
        'Estatura': [conteo, minimo, maximo, media, mediana, desviacion_estandar],
        'Peso': [conteo_peso, minimo_peso, maximo_peso, media_peso, mediana_peso, desviacion_estandar_peso],
        'Presion Sistolica':[conteo_presion_sistolica, minimo_presion_sistolica, maximo_presion_sistolica, media_presion_sistolica, mediana_presion_sistolica, desviacion_estandar_presion_sistolica],
        'Presion Diastolica':[conteo_presion_diastolica, minimo_presion_diastolica, maximo_presion_diastolica, media_presion_diastolica, mediana_presion_diastolica, desviacion_estandar_presion_diastolica]
    })

    return df_estadisticos

#---------------Función iloc-----------------------------------------------------------------------------------------------------------------
def estadisticos_grupo(df_grupo):
    if df_grupo.empty:
        print("No hay pacientes en este grupo.")
    else:
        for col in ['estatura', 'peso', 'presion_sistolica', 'presion_diastolica']:
            df_grupo.loc[:, col] = df_grupo[col].astype(float)
        estadisticos = calcular_estadisticos(df_grupo)
        return estadisticos
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def estadisticos_por_edad():
    console = Console()
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Estadístico")
    table.add_column("Estatura")
    table.add_column("Peso")
    table.add_column("Presión Sistólica")
    table.add_column("Presión Diastólica")

    while True:
        try:
            edad_minima = int(input("Ingrese la edad mínima a analizar (o ingrese 0 para regresar al menú de estadísticos demográficos): "))
            if edad_minima == 0:
                return
            if edad_minima < 0:
                print("Error: La edad mínima no puede ser un número negativo.")
                continue
            
            while True:
                edad_maxima = int(input("Ingrese la edad máxima a analizar (o ingrese 0 para regresar al menú de estadísticos demográficos): "))
                if edad_maxima == 0:
                    return
                if edad_maxima < 0:
                    print("Error: La edad máxima no puede ser un número negativo.")
                    continue

                if edad_minima > edad_maxima:
                    print("Error: La edad mínima no puede ser mayor que la edad máxima.")
                    continue
                break

        except ValueError:
            print("Error: Las edades deben ser números enteros.")
            continue
        try:
            # Conectar a la base de datos SQLite
            conn = sqlite3.connect('BaseEvidencia3.db')

            # Consulta SQL para unir las tablas 'pacientes' y 'citas' y calcular la edad
            query = f"""
            SELECT *,
                   CAST((strftime('%Y', 'now') - strftime('%Y', fecha_nacimiento)) - (strftime('%m-%d', 'now') < strftime('%m-%d', fecha_nacimiento)) AS INTEGER) AS edad
            FROM citas
            JOIN pacientes ON citas.clave = pacientes.clave
            """

            # Leer los datos de la consulta en un DataFrame de pandas
            df = pd.read_sql_query(query, conn)

            # Filtrar el DataFrame por edad
            df_filtrado = df[(df['edad'] >= edad_minima) & (df['edad'] <= edad_maxima)].copy()
            
            # Verificar si el DataFrame está vacío
            if df_filtrado.empty:
                print("No se encontraron pacientes en el rango de edad especificado.")
                break
            
            # Convertir la columna 'estatura' a tipo numérico
            df_filtrado['estatura'] = df_filtrado['estatura'].astype(float)
            df_filtrado['peso'] = df_filtrado['peso'].astype(float)
            df_filtrado['presion_sistolica'] = df_filtrado['presion_sistolica'].astype(float)
            df_filtrado['presion_diastolica'] = df_filtrado['presion_diastolica'].astype(float)

            # Calcular estadísticos demográficos
            df_estadisticos = calcular_estadisticos(df_filtrado)

            
            for index, row in df_estadisticos.iterrows():
              table.add_row(
                 str(row['Estadístico']),
                 str(row['Estatura']),
                 str(row['Peso']),
                 str(row['Presion Sistolica']),
                 str(row['Presion Diastolica'])
             )

            console.print(table)

            # Preguntar al usuario si desea exportar los datos
            while True:
                exportar = input("¿Desea exportar estos datos? (s/n): ").lower()
                if exportar == 's':
                    formato = input("Ingrese el formato para exportar ('c' para CSV, 'e' para Excel)(o escriba 'salir' para volver al menu de Estadisticos demograficos):: ")
                    exportar_reporte(df_estadisticos, formato)
                    break
                if exportar == 'n':
                    break
                else:
                    print("Error: Por favor ingrese 's' para sí o 'n' para no.")
                continue



        except ValueError:
            print("Error: Las edades deben ser números enteros.")
        except sqlite3.Error as e:
            print("Error:", e)

        break
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def estadisticos_por_sexo():
    console = Console()
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Estadístico")
    table.add_column("Estatura")
    table.add_column("Peso")
    table.add_column("Presión Sistólica")
    table.add_column("Presión Diastólica")
    try:
        conn = sqlite3.connect('BaseEvidencia3.db')
        df_pacientes = pd.read_sql_query("SELECT * FROM pacientes", conn)
        df_citas = pd.read_sql_query("SELECT * FROM citas", conn)
        df = pd.merge(df_citas, df_pacientes, on='clave')

        # for sexo in ['H', 'M', 'N']:
        #     print(f"\nEstadísticos para el sexo {sexo}:")
        #     df_filtrado = df[df['sexo'] == sexo]
        #     estadisticos = estadisticos_grupo(df_filtrado)
        #     if estadisticos is not None:
        #         for index, row in estadisticos.iterrows():
        #             table.add_row(
        #                 str(row['Estadístico']),
        #                 str(row['Estatura']),
        #                 str(row['Peso']),
        #                 str(row['Presion Sistolica']),
        #                 str(row['Presion Diastolica'])
        #             )
        #         console.print(table)

        # Filtrar el DataFrame por sexo
        df_filtrado_M = df[df['sexo'] == 'H']
        df_filtrado_F = df[df['sexo'] == 'M']
        df_filtrado_N = df[df['sexo'] == 'N']

        # Calcular los estadísticos demográficos para cada sexo
        
        table1 = calcular_estadisticos(df_filtrado_M)
        table2 = calcular_estadisticos(df_filtrado_F)
        table3 = calcular_estadisticos(df_filtrado_N)

        print("\nEstadísticos para el sexo masculino:")
        console.print(table1)
        print("\nEstadísticos para el sexo femenino:")
        console.print(table2)
        print("\nEstadísticos para el sexo no definido:")
        console.print(table3)

        while True:
            exportar = input("¿Desea exportar estos datos? (s/n): ").lower()
            if exportar in ['s', 'n']:
                if exportar == 's':
                    formato = input("Ingrese el formato para exportar ('c' para CSV, 'e' para Excel)(o escriba 'salir' para volver al menu de Estadisticos demograficos):: ")
                    for sexo in ['H', 'F', 'N']:
                        df_filtrado = df[df['sexo'] == sexo]
                        estadisticos = estadisticos_grupo(df_filtrado)
                        if estadisticos is not None:
                            exportar_reporte(estadisticos, formato)
                break
            else:
                print("Error: Por favor ingrese 's' para sí o 'n' para no.")
                continue

    except ValueError:
        print("Error: Las edades deben ser números enteros.")
    except sqlite3.Error as e:
        print("Error:", e)     
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def estadisticos_por_sexo_y_edad():
    console = Console()
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Estadístico")
    table.add_column("Estatura")
    table.add_column("Peso")
    table.add_column("Presión Sistólica")
    table.add_column("Presión Diastólica")

    while True:
        try:
            edad_minima = int(input("Ingrese la edad mínima a analizar (o ingrese 0 para regresar al menú de estadísticos demográficos): "))
            if edad_minima == 0:
                return
            if edad_minima < 0:
                print("Error: La edad mínima no puede ser un número negativo.")
                continue
            
            while True:
                edad_maxima = int(input("Ingrese la edad máxima a analizar (o ingrese 0 para regresar al menú de estadísticos demográficos): "))
                if edad_maxima == 0:
                    return
                if edad_maxima < 0:
                    print("Error: La edad máxima no puede ser un número negativo.")
                    continue

                if edad_minima > edad_maxima:
                    print("Error: La edad mínima no puede ser mayor que la edad máxima.")
                    continue
                break

        except ValueError:
            print("Error: Las edades deben ser números enteros.")
            continue

        try:
            # Conectar a la base de datos SQLite
            conn = sqlite3.connect('BaseEvidencia3.db')

            # Consulta SQL para obtener la edad de los pacientes
            query = f"""
            SELECT *,
                   CAST((strftime('%Y', 'now') - strftime('%Y', fecha_nacimiento)) - (strftime('%m-%d', 'now') < strftime('%m-%d', fecha_nacimiento)) AS INTEGER) AS edad
            FROM pacientes
            """
            
            # Leer los datos de la consulta en un DataFrame de pandas
            df_pacientes = pd.read_sql_query(query, conn)
            
            # Leer los datos de la tabla de citas en un DataFrame de pandas
            df_citas = pd.read_sql_query("SELECT * FROM citas", conn)

            # Unir los dos DataFrames en uno solo
            df = pd.merge(df_citas, df_pacientes, on='clave')

            # Filtrar el DataFrame por sexo y edad
            df_filtrado_H = df[(df['sexo'] == 'H') & (df['edad'] >= edad_minima) & (df['edad'] <= edad_maxima)].copy()
            df_filtrado_M = df[(df['sexo'] == 'M') & (df['edad'] >= edad_minima) & (df['edad'] <= edad_maxima)].copy()
            df_filtrado_N = df[(df['sexo'] == 'N') & (df['edad'] >= edad_minima) & (df['edad'] <= edad_maxima)].copy()

            if df_filtrado_H.empty:
                print("No hay pacientes masculinos en el rango de edad especificado.")
            else:
                df_filtrado_H = df[df['sexo'] == 'H']

                # Calcular los estadísticos demográficos para el sexo masculino
                estadisticos_H = calcular_estadisticos(df_filtrado_H)
                print("\nEstadísticos para el sexo masculino:")
                console.print(estadisticos_H)

            if df_filtrado_M.empty:
                print("No hay pacientes femeninos en el rango de edad especificado.")
            else:
                df_filtrado_M = df[df['sexo'] == 'M']
                
                # Calcular los estadísticos demográficos para el sexo femenino
                estadisticos_M = calcular_estadisticos(df_filtrado_M)
                print("\nEstadísticos para el sexo femenino:")
                console.print(estadisticos_M)
            if df_filtrado_N.empty:
                print("No hay pacientes no definidos en el rango de edad especificado.")
            else:
                df_filtrado_N = df[df['sexo'] == 'N']
                # Calcular los estadísticos demográficos para el sexo no definido
                estadisticos_N = calcular_estadisticos(df_filtrado_N)

                # Imprimir los estadísticos demográficos para el sexo no definido
                print("\nEstadísticos para el sexo no definido:")

                console.print(table)

            # Preguntar al usuario si desea exportar los datos
            while True:
                exportar = input("¿Desea exportar estos datos? (s/n): ").lower()
                if exportar == 's':
                    formato= input("Ingrese el formato para exportar ('c' para CSV, 'e' para Excel)(o escriba 'salir' para volver al menu de Estadisticos demograficos):: ")
                    if not df_filtrado_H.empty:    
                        exportar_reporte(estadisticos_H, formato)
                    if not df_filtrado_M.empty:
                        exportar_reporte(estadisticos_M, formato)
                    if not df_filtrado_N.empty:
                        exportar_reporte(estadisticos_N, formato)
                    break
                elif exportar == 'n':
                    break
                else:
                    print("Error: Por favor ingrese 's' para sí o 'n' para no.")
                    continue
                

        except ValueError:
            print("Error: Las edades deben ser números enteros.")
        except sqlite3.Error as e:
            print("Error:", e)
            break
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def consultas_reportes():
    while True:
        print('\n Menu de Consultas y Reportes')
        print('1. Reporte de citas')
        print('2. Reporte de pacientes')
        print('3. Estadísticos Demográficos')
        print('4. Regresar al Menú Principal')

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            reporte_de_citas()
        elif opcion == "2":
            reporte_de_pacientes()
        elif opcion == "3":
            estadisticos_demograficos()
        elif opcion == "4":
            return
        else:
            print("Opción inválida. Por favor seleccione una opción válida.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def gestion_citas():
    conn = sqlite3.connect('BaseEvidencia3.db')
    cursor = conn.cursor()    
    cursor.execute("SELECT * FROM citas")
    citas = cursor.fetchall()
    while True:
        print("\nGestión de Citas:")
        print("1. Programar Cita")
        print("2. Realizar Cita")
        print("3. Cancelar Cita")
        print("4. Regresar al Menú Principal\n")

        opcion_citas = input("Seleccione una opción: ")

        if opcion_citas == '1':
            programar_cita()
        elif opcion_citas == '2':
            realizar_cita()
        elif opcion_citas == '3':
            if not citas:
             print("Error: No hay citas registradas. Programe al menos una cita antes de realizar una cita.")
             return
            else:
             cancelar_cita()
        elif opcion_citas == '4':
            break
        else:
            print("Opción no válida. Intente de nuevo.")
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def mostrar_menu():
    print('\nMenu Principal: ')
    print('1. Registrar Paciente')
    print('2. Gestión de Citas')
    print('3. Consultas y Reportes')
    print('4. Salir.\n')

mostrar_menu()
while True:
    opcion = input('Seleccione una opción: ')
    if not opcion:
        print("Error. Vuelve A Intentarlo")
        continue

    match opcion:
        case '1':
            registrarp()
            mostrar_menu()
        case '2':
            if verificador_de_pacientes():
                mostrar_menu()
                continue
            else:
                gestion_citas()
                mostrar_menu()
        case '3':
            if verificador_de_pacientes():
                mostrar_menu()
                continue
            else:
                consultas_reportes()
                mostrar_menu()
        case '4':
            confirmacion = input('¿Está seguro que desea salir? (S/N): ')
            if confirmacion.lower() == 's':
                break
            else:
                mostrar_menu()