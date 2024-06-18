from tkinter import *
from tkinter import ttk
import requests
import tkintermapview
from bs4 import BeautifulSoup
import psycopg2 as ps

db_params = ps.connect(
    database="mapbook",
    user="postgres",
    password="test",
    host="localhost",
    port="5432"
)

airports = []
employees = []
customers = []
markers = []

class Airport:
    def __init__(self, id, name, location, wspolrzedne):
        self.id = id
        self.name = name
        self.location = location
        self.wspolrzedne = wspolrzedne
        self.marker = map_widget.set_marker(
            float(self.wspolrzedne[0]),
            float(self.wspolrzedne[1]),
            text=f"Lotnisko {self.id} - {self.name}"
        )
        markers.append(self.marker)

class Employee:
    def __init__(self, id, name, surname, position, airport_id, wspolrzedne):
        self.id = id
        self.name = name
        self.surname = surname
        self.position = position
        self.airport_id = airport_id
        self.wspolrzedne = wspolrzedne
        self.marker = map_widget.set_marker(
            float(self.wspolrzedne[0]),
            float(self.wspolrzedne[1]),
            text=f"{self.name} {self.surname} - {self.position}"
        )
        markers.append(self.marker)

class Customer:
    def __init__(self, id, name, surname, airport_id, wspolrzedne):
        self.id = id
        self.name = name
        self.surname = surname
        self.airport_id = airport_id
        self.wspolrzedne = wspolrzedne
        self.marker = map_widget.set_marker(
            float(self.wspolrzedne[0]),
            float(self.wspolrzedne[1]),
            text=f"{self.name} {self.surname}"
        )
        markers.append(self.marker)

def get_coordinates(location) -> list:
    url = f'https://pl.wikipedia.org/wiki/{location}'
    response = requests.get(url)
    response_html = BeautifulSoup(response.text, 'html.parser')
    return [
        float(response_html.select('.latitude')[1].text.replace(",", ".")),
        float(response_html.select('.longitude')[1].text.replace(",", "."))
    ]

def clear_markers() -> None:
    for marker in markers:
        marker.delete()
    markers.clear()

def show_airports() -> None:
    cursor = db_params.cursor()
    sql_show_airports = "SELECT id, name, location, ST_AsText(wspolrzedne) FROM public.airports"
    cursor.execute(sql_show_airports)
    airports_db = cursor.fetchall()
    cursor.close()

    airports.clear()
    listbox_lista_obiektow.delete(0, END)
    for idx, airport in enumerate(airports_db):
        airport_obj = Airport(airport[0], airport[1], airport[2], [airport[3][6:-1].split()[1], airport[3][6:-1].split()[0]])
        airports.append(airport_obj)
        listbox_lista_obiektow.insert(idx, f'Lotnisko {airport[0]} - {airport[1]} {airport[2]}')

def add_airport() -> None:
    name = entry_name.get()
    location = entry_location.get()
    wspolrzedne = get_coordinates(location)

    cursor = db_params.cursor()
    sql_insert_airport = f"""
    INSERT INTO public.airports (name, location, wspolrzedne) 
    VALUES (%s, %s, ST_GeomFromText(%s))
    RETURNING id
    """
    cursor.execute(sql_insert_airport, (name, location, f'POINT({wspolrzedne[1]} {wspolrzedne[0]})'))
    airport_id = cursor.fetchone()[0]
    db_params.commit()
    cursor.close()

    airport = Airport(id=airport_id, name=name, location=location, wspolrzedne=wspolrzedne)
    airports.append(airport)

    show_airports()

    entry_name.delete(0, END)
    entry_location.delete(0, END)
    entry_name.focus()

def remove_airport() -> None:
    i = listbox_lista_obiektow.index(ACTIVE)
    airport = airports[i]

    cursor = db_params.cursor()
    sql_delete_airport = f"DELETE FROM public.airports WHERE id = %s"
    cursor.execute(sql_delete_airport, (airport.id,))
    db_params.commit()
    cursor.close()

    airport.marker.delete()
    markers.remove(airport.marker)
    airports.pop(i)
    show_airports()

def show_airport_details() -> None:
    i = listbox_lista_obiektow.index(ACTIVE)
    airport = airports[i]
    label_name_szczegoly_obiektu_wartosc.config(text=airport.name)
    label_location_szczegoly_obiektu_wartosc.config(text=airport.location)
    map_widget.set_position(float(airport.wspolrzedne[0]), float(airport.wspolrzedne[1]))
    map_widget.set_zoom(12)
    button_update_airport.config(state=NORMAL)
    button_add_airport.config(state=DISABLED)

def update_airport() -> None:
    i = listbox_lista_obiektow.index(ACTIVE)
    airport = airports[i]
    name = entry_name.get()
    location = entry_location.get()
    wspolrzedne = get_coordinates(location)

    cursor = db_params.cursor()
    sql_update_airport = f"""
    UPDATE public.airports 
    SET name = %s, location = %s, wspolrzedne = ST_GeomFromText(%s) 
    WHERE id = %s
    """
    cursor.execute(sql_update_airport, (name, location, f'POINT({wspolrzedne[1]} {wspolrzedne[0]})', airport.id))
    db_params.commit()
    cursor.close()

    airport.name = name
    airport.location = location
    airport.wspolrzedne = wspolrzedne
    airport.marker.delete()
    airport.marker = map_widget.set_marker(
        float(wspolrzedne[0]),
        float(wspolrzedne[1]),
        text=f"Lotnisko {airport.id} - {airport.name}",
    )

    show_airports()
    # button_update_airport.config(state=DISABLED)
    # button_add_airport.config(state=NORMAL)
    entry_name.delete(0, END)
    entry_location.delete(0, END)

def add_employee() -> None:
    name = entry_employee_name.get()
    surname = entry_employee_surname.get()
    position = entry_employee_position.get()
    airport_id = int(entry_employee_airport_id.get())
    wspolrzedne = get_coordinates(entry_employee_location.get())

    cursor = db_params.cursor()
    sql_insert_employee = f"""
    INSERT INTO public.employees (name, surname, position, airport_id, wspolrzedne) 
    VALUES (%s, %s, %s, %s, ST_GeomFromText(%s))
    RETURNING id
    """
    cursor.execute(sql_insert_employee, (name, surname, position, airport_id, f'POINT({wspolrzedne[1]} {wspolrzedne[0]})'))
    employee_id = cursor.fetchone()[0]
    db_params.commit()
    cursor.close()

    employee = Employee(id=employee_id, name=name, surname=surname, position=position, airport_id=airport_id, wspolrzedne=wspolrzedne)
    employees.append(employee)

    entry_employee_name.delete(0, END)
    entry_employee_surname.delete(0, END)
    entry_employee_position.delete(0, END)
    entry_employee_airport_id.delete(0, END)
    entry_employee_location.delete(0, END)

def remove_employee() -> None:
    i = employees_listbox.index(ACTIVE)
    employee = employees[i]

    cursor = db_params.cursor()
    sql_delete_employee = f"DELETE FROM public.employees WHERE id = %s"
    cursor.execute(sql_delete_employee, (employee.id,))
    db_params.commit()
    cursor.close()

    employee.marker.delete()
    markers.remove(employee.marker)
    employees.pop(i)
    show_employees_and_customers()

def add_customer() -> None:
    name = entry_customer_name.get()
    surname = entry_customer_surname_field.get()
    airport_id = int(entry_customer_airport_id.get())
    wspolrzedne = get_coordinates(entry_customer_location.get())

    cursor = db_params.cursor()
    sql_insert_customer = f"""
    INSERT INTO public.customers (name, surname, airport_id, wspolrzedne) 
    VALUES (%s, %s, %s, ST_GeomFromText(%s))
    RETURNING id
    """
    cursor.execute(sql_insert_customer, (name, surname, airport_id, f'POINT({wspolrzedne[1]} {wspolrzedne[0]})'))
    customer_id = cursor.fetchone()[0]
    db_params.commit()
    cursor.close()

    customer = Customer(id=customer_id, name=name, surname=surname, airport_id=airport_id, wspolrzedne=wspolrzedne)
    customers.append(customer)

    entry_customer_name.delete(0, END)
    entry_customer_surname_field.delete(0, END)
    entry_customer_airport_id.delete(0, END)
    entry_customer_location.delete(0, END)

def remove_customer() -> None:
    i = customers_listbox.index(ACTIVE)
    customer = customers[i]

    cursor = db_params.cursor()
    sql_delete_customer = f"DELETE FROM public.customers WHERE id = %s"
    cursor.execute(sql_delete_customer, (customer.id,))
    db_params.commit()
    cursor.close()

    customer.marker.delete()
    markers.remove(customer.marker)
    customers.pop(i)
    show_employees_and_customers()

def show_employees_and_customers() -> None:
    i = listbox_lista_obiektow.index(ACTIVE)
    airport = airports[i]
    cursor = db_params.cursor()

    sql_show_employees = f"SELECT id, name, surname, position, airport_id, ST_AsText(wspolrzedne) FROM public.employees WHERE airport_id = %s"
    cursor.execute(sql_show_employees, (airport.id,))
    employees_db = cursor.fetchall()

    sql_show_customers = f"SELECT id, name, surname, airport_id, ST_AsText(wspolrzedne) FROM public.customers WHERE airport_id = %s"
    cursor.execute(sql_show_customers, (airport.id,))
    customers_db = cursor.fetchall()
    cursor.close()

    employees_listbox.delete(0, END)
    employees.clear()
    for employee in employees_db:
        employee_obj = Employee(
            employee[0], employee[1], employee[2], employee[3],
            employee[4], [employee[5][6:-1].split()[1], employee[5][6:-1].split()[0]]
        )
        employees.append(employee_obj)
        employees_listbox.insert(END, f"{employee[1]} {employee[2]}, {employee[3]}")

    customers_listbox.delete(0, END)
    customers.clear()
    for customer in customers_db:
        customer_obj = Customer(
            customer[0], customer[1], customer[2],
            customer[3], [customer[4][6:-1].split()[1], customer[4][6:-1].split()[0]]
        )
        customers.append(customer_obj)
        customers_listbox.insert(END, f"{customer[1]} {customer[2]}")

def deselect_airport() -> None:
    listbox_lista_obiektow.selection_clear(0, END)
    #clear_markers()
    label_name_szczegoly_obiektu_wartosc.config(text="")
    label_location_szczegoly_obiektu_wartosc.config(text="")
    button_update_airport.config(state=DISABLED)
    button_add_airport.config(state=NORMAL)

root = Tk()
root.title("System zarządzania lotniskami")
root.geometry("1200x1000")

map_widget = tkintermapview.TkinterMapView(root, width=800, height=400)
map_widget.pack(fill="both", expand=True)
map_widget.set_position(52.2296756, 21.0122287)
map_widget.set_zoom(5)

frame = Frame(root)
frame.pack()

label_name = Label(frame, text="Nazwa")
label_name.grid(row=0, column=0)
entry_name = Entry(frame)
entry_name.grid(row=0, column=1)

label_location = Label(frame, text="Miasto")
label_location.grid(row=1, column=0)
entry_location = Entry(frame)
entry_location.grid(row=1, column=1)

button_add_airport = Button(frame, text="Dodaj lotnisko", command=add_airport)
button_add_airport.grid(row=2, column=0)
button_update_airport = Button(frame, text="Zaktualizuj lotnisko", command=update_airport)
button_update_airport.grid(row=2, column=1)
button_update_airport.config(state=DISABLED)
button_remove_airport = Button(frame, text="Usuń lotnisko", command=remove_airport)
button_remove_airport.grid(row=2, column=2)
button_deselect_airport = Button(frame, text="Odznacz lotnisko", command=deselect_airport)
button_deselect_airport.grid(row=2, column=3)

label_employee_name = Label(frame, text="Imię")
label_employee_name.grid(row=3, column=0)
entry_employee_name = Entry(frame)
entry_employee_name.grid(row=3, column=1)

label_employee_surname = Label(frame, text="Nazwisko")
label_employee_surname.grid(row=4, column=0)
entry_employee_surname = Entry(frame)
entry_employee_surname.grid(row=4, column=1)

label_employee_position = Label(frame, text="Stanowisko")
label_employee_position.grid(row=5, column=0)
entry_employee_position = Entry(frame)
entry_employee_position.grid(row=5, column=1)

label_employee_airport_id = Label(frame, text="ID lotnisko")
label_employee_airport_id.grid(row=6, column=0)
entry_employee_airport_id = Entry(frame)
entry_employee_airport_id.grid(row=6, column=1)

label_employee_location = Label(frame, text="Miejscowość")
label_employee_location.grid(row=7, column=0)
entry_employee_location = Entry(frame)
entry_employee_location.grid(row=7, column=1)

button_add_employee = Button(frame, text="Dodaj pracownika", command=add_employee)
button_add_employee.grid(row=8, column=0)
button_remove_employee = Button(frame, text="Usuń pracownika", command=remove_employee)
button_remove_employee.grid(row=8, column=1)

label_customer_name = Label(frame, text="Imię")
label_customer_name.grid(row=9, column=0)
entry_customer_name = Entry(frame)
entry_customer_name.grid(row=9, column=1)

label_customer_surname = Label(frame, text="Nazwisko")
label_customer_surname.grid(row=10, column=0)
entry_customer_surname_field = Entry(frame)
entry_customer_surname_field.grid(row=10, column=1)

label_customer_airport_id = Label(frame, text="ID lotniska")
label_customer_airport_id.grid(row=11, column=0)
entry_customer_airport_id = Entry(frame)
entry_customer_airport_id.grid(row=11, column=1)

label_customer_location = Label(frame, text="Miejscowość")
label_customer_location.grid(row=12, column=0)
entry_customer_location = Entry(frame)
entry_customer_location.grid(row=12, column=1)

button_add_customer = Button(frame, text="Dodaj klienta", command=add_customer)
button_add_customer.grid(row=13, column=0)
button_remove_customer = Button(frame, text="Usuń klienta", command=remove_customer)
button_remove_customer.grid(row=13, column=1)

button_show_employees_and_customers = Button(frame, text="Pokaż klientów i pracowników", command=show_employees_and_customers)
button_show_employees_and_customers.grid(row=14, column=0)

listbox_lista_obiektow = Listbox(frame)
listbox_lista_obiektow.grid(row=0, column=3, rowspan=15)
listbox_lista_obiektow.bind('<<ListboxSelect>>', lambda _: show_airport_details())

label_name_szczegoly_obiektu = Label(root, text="Nazwa: ")
label_name_szczegoly_obiektu.pack()
label_name_szczegoly_obiektu_wartosc = Label(root, text="")
label_name_szczegoly_obiektu_wartosc.pack()

label_location_szczegoly_obiektu = Label(root, text="Miejscowość: ")
label_location_szczegoly_obiektu.pack()
label_location_szczegoly_obiektu_wartosc = Label(root, text="")
label_location_szczegoly_obiektu_wartosc.pack()

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

employees_frame = Frame(notebook)
notebook.add(employees_frame, text="Pracownicy")

customers_frame = Frame(notebook)
notebook.add(customers_frame, text="Klienci")

employees_listbox = Listbox(employees_frame)
employees_listbox.pack(fill=BOTH, expand=True)

customers_listbox = Listbox(customers_frame)
customers_listbox.pack(fill=BOTH, expand=True)

show_airports()

root.mainloop()
