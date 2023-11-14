import tkinter as tk
from tkinter import ttk, simpledialog
import pandas as pd
from datetime import datetime
import os

class MainMenu:
    def __init__(self, root, menu_file="IDEE\speisekarte.csv"):
        self.root = root
        self.root.title("Golden Seagull - Hauptmenü")
        self.menu_frame = ttk.LabelFrame(self.root, text="Speisekarte")
        self.menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.menu = self.load_menu(menu_file)
        self.create_menu_ui()
        self.tischnummer = None
        self.tip_percentage = 0
        self.order_items = {}
        self.cart = {}
        self.create_order_ui()
        self.create_payment_ui()
        self.orders = pd.DataFrame(columns=["ID", "Datum", "SpeiseID", "Menge", "Status"])
        self.display_menu(self.menu)  # Add this line to display the menu
        self.payment_method = ""


    def load_menu(self, menu_file, encoding="utf-8"):
        if "speisekarte.csv" in os.listdir():
            pass
        else:
            menu_file = "..\IDEE\speisekarte.csv"       
        try:
            menu = pd.read_csv(menu_file, encoding=encoding, index_col=False)
            menu.set_index("ID", inplace=True)
            menu["Preis"] = menu["Preis"].map("{:.2f} €".format)
            pd.set_option('display.max_colwidth', None)
            return menu
        except Exception as e:
            print(f"Fehler beim Laden der Speisekarte: {e}")
            return None


    def create_menu_ui(self):
        self.menu_tree = ttk.Treeview(self.menu_frame, columns=("ID", "Name", "Beschreibung", "Preis", "Kategorie", "Allergene", "Vegetarisch", "Vegan"))
        self.menu_tree.heading("#1", text="ID")
        self.menu_tree.heading("#2", text="Name")
        self.menu_tree.heading("#3", text="Beschreibung")
        self.menu_tree.heading("#4", text="Preis")
        self.menu_tree.heading("#5", text="Kategorie")
        self.menu_tree.heading("#6", text="Allergene")
        self.menu_tree.heading("#7", text="Vegetarisch")
        self.menu_tree.heading("#8", text="Vegan")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14))
        style.configure("Treeview", font=("Arial", 11))
        self.menu_tree.tag_configure("Beschreibung", font=("Arial", 11))

        self.menu_tree.column("#1", width=40, anchor="w")
        self.menu_tree.column("#2", width=200, anchor="w")
        self.menu_tree.column("#3", width=400, anchor="w")
        self.menu_tree.column("#4", width=100, anchor="w")
        self.menu_tree.column("#5", width=100, anchor="w")
        self.menu_tree.column("#6", width=200, anchor="w")
        self.menu_tree.column("#7", width=200, anchor="w")
        self.menu_tree.column("#8", width=100, anchor="w")

        self.menu_tree.bind("<Double-1>", self.add_to_cart)
        self.menu_tree.grid(row=4, column=0, pady=5)

        self.cart_frame = ttk.LabelFrame(self.root, text="Warenkorb")
        self.cart_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.cart_text_var = tk.StringVar()  
        self.cart_text = tk.Text(self.cart_frame, height=10, width=40, wrap=tk.WORD, state=tk.DISABLED)
        self.cart_text.grid(row=1, column=0, padx=5, pady=5)

        remove_button = ttk.Button(self.cart_frame, text="Aus dem Warenkorb entfernen", command=self.remove_from_cart)
        remove_button.grid(row=2, column=0, pady=5)

    def create_order_ui(self):
        self.order_frame = ttk.LabelFrame(self.root, text="Bestellung")
        self.order_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.selected_dish = None

    def display_menu(self, menu):
        self.menu_tree.delete(*self.menu_tree.get_children())

        for index, row in menu.iterrows():
            self.menu_tree.insert("", "end", values=(index, row["Name"], row["Beschreibung"], row["Preis"], row["Kategorie"], row["Allergene"], row["Vegetarisch"], row["Vegan"]))

        self.menu_tree.column("#1", width=40, anchor="w")
        self.menu_tree.column("#2", width=200, anchor="w")
        self.menu_tree.column("#3", width=400, anchor="w")
        self.menu_tree.column("#4", width=100, anchor="w")
        self.menu_tree.column("#5", width=100, anchor="w")
        self.menu_tree.column("#6", width=150, anchor="w")
        self.menu_tree.column("#7", width=150, anchor="w")
        self.menu_tree.column("#8", width=100, anchor="w")

    def add_to_cart(self, event):
        selected_item = self.menu_tree.selection()
        if selected_item:
            dish_id = selected_item[0]  # Extract the first element from the tuple
            print(f"Adding dish to cart: {dish_id}")
            if dish_id in self.cart:
                self.cart[dish_id] += 1
            else:
                self.cart[dish_id] = 1
            print(f"Cart after adding: {self.cart}")
            self.update_invoice()

    def remove_from_cart(self):
        selected_item = self.menu_tree.selection()
        if selected_item:
            dish_id = selected_item[0]
            print(f"Removing dish from cart: {dish_id}")
            if dish_id in self.cart:
                if self.cart[dish_id] > 1:
                    self.cart[dish_id] -= 1
                else:
                    del self.cart[dish_id]
                print(f"Cart after removing: {self.cart}")
                self.update_invoice()

    def place_order(self):
        if self.cart:
            for dish_id, quantity in self.cart.items():
                order = self.create_order(dish_id, quantity)
                if order:
                    self.orders = pd.concat([self.orders, order], ignore_index=True)

            self.cart = {}
            self.update_invoice()

        elif self.selected_dish:
            if self.selected_dish["Name"] not in self.order_items:
                self.order_items[self.selected_dish["Name"]] = {
                    "Name": self.selected_dish["Name"],
                    "Beschreibung": self.selected_dish["Beschreibung"],
                    "Preis": self.selected_dish["Preis"],
                    "Menge": 1
                }
            else:
                self.order_items[self.selected_dish["Name"]]["Menge"] += 1
            self.update_invoice()

    def update_invoice(self):
        invoice = self.generate_invoice()
        self.cart_text.config(state=tk.NORMAL)
        self.cart_text.delete(1.0, tk.END)
        self.cart_text.insert(tk.END, invoice)
        self.cart_text.config(state=tk.DISABLED)

        total_price = sum(
            self.menu.loc[dish_id, "Preis"] * quantity if dish_id in self.menu.index else 0
            for dish_id, quantity in self.cart.items()
        )
        self.total_label.config(text=f"Gesamtsumme: {total_price:.2f} €")

    def generate_invoice(self):
        total = 0
        invoice_text = ""
        net_price = 0
        tax_rate = 0.19

        for dish_id, quantity in self.cart.items():
            dish_data = self.menu_tree.item(dish_id, "values")
            name = dish_data[1]
            beschreibung = dish_data[2]
            preis = dish_data[3]

            try:
                price_float = float(preis.split(" €")[0])
                total += price_float * quantity
                net_price += price_float * quantity
                invoice_text += f"{name} x{quantity}: {beschreibung} ({preis})\n"
            except ValueError:
                print(f"Invalid 'preis' value for {name}: {preis}")

        tax_amount = total * tax_rate
        total_price = total + tax_amount
        if self.tip_percentage > 0:
            total_price += self.tip_percentage

        invoice_text += "-----------------------------\n"
        invoice_text += f"MwSt.: {tax_amount:.2f} €\n"
        invoice_text += f"Gesamtpreis: {total_price:.2f} €\n"
        if self.tip_percentage > 0:
            invoice_text += f"Trinkgeld: {self.tip_percentage:.2f} €\n"
        invoice_text += "=============================\n"
        invoice_text += f"Vielen Dank für ihren Besuch in der Goldenen Möwe!\n"
        return invoice_text

    def create_order(self, speiseID, menge):
        if self.validate_order({speiseID: menge}):
            order = pd.DataFrame(columns=["ID", "Datum", "SpeiseID", "Menge", "Status"])
            order = order.append({"ID": len(self.orders) + 1, "Datum": datetime.now(), "SpeiseID": speiseID,
                                  "Menge": menge, "Status": "offen"}, ignore_index=True)
            self.orders = pd.concat([self.orders, order], ignore_index=True)
            return order
        else:
            return None

    def validate_order(self, order_details):
        for item_id in order_details.keys():
            if item_id not in self.menu.index:
                return False
        return True

    def cancel_order(self, order_id):
        self.orders.loc[self.orders["ID"] == order_id, "Status"] = "storno"

    def set_tischnummer(self):
        self.tischnummer = simpledialog.askinteger("Tischnummer", "Bitte geben Sie die Tischnummer ein:", parent=self.root)

    def ask_for_tip_amount(self):
        tip_options = [5, 10, 15]
        
        # Create a custom dialog
        tip_dialog = simpledialog.Toplevel(self.root)
        tip_dialog.title("Trinkgeld")
        
        # Add buttons for predefined tip percentages
        for tip_percentage in tip_options:
            button = ttk.Button(tip_dialog, text=f"{tip_percentage}%", command=lambda p=tip_percentage: self.set_tip_percentage(p))
            button.pack(pady=5)
        
        # Add a button for custom tip amount
        custom_button = ttk.Button(tip_dialog, text="Eigener Betrag", command=self.ask_custom_tip_amount)
        custom_button.pack(pady=5)
        
        # Wait for the user to make a choice
        tip_dialog.wait_window()
        
    def ask_custom_tip_amount(self):
        tip_choice = simpledialog.askfloat("Trinkgeld", "Bitte geben Sie den Trinkgeldbetrag ein:", parent=self.root)
        if tip_choice is not None:
            self.set_tip_percentage(tip_choice)

    def set_tip_percentage(self, percentage):
        self.tip_percentage = percentage / 100


    def create_payment_ui(self):
        self.payment_frame = ttk.LabelFrame(self.root, text="Bezahlung")
        self.payment_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        self.pay_button = ttk.Button(self.payment_frame, text="Bezahlen", command=self.process_payment)
        self.pay_button.grid(row=0, column=0, pady=5)

    def process_payment(self):
        # Ask if the customer wants to give a tip
        tip_response = tk.messagebox.askyesno("Trinkgeld", "Möchten Sie Trinkgeld geben?")
        
        if tip_response:
            # If yes, ask for the tip amount
            tip_amount = self.ask_for_tip_amount()
        else:
            tip_amount = 0

        # Calculate the total price including tip
        total_price = self.calculate_total_price(tip_amount)

        # Display the payment window
        payment_window = tk.Toplevel(self.root)
        payment_window.title("Zahlung")

        # Ask for payment method
        payment_label = tk.Label(payment_window, text="Wählen Sie eine Zahlungsmethode:")
        payment_label.grid(row=0, column=0, padx=10, pady=10)

        payment_options = ["Bar", "Karte", "Gutschein", "ApplePay/GooglePay", "PayPal"]
        payment_var = tk.StringVar(payment_window, value=payment_options[0])
        payment_dropdown = ttk.Combobox(payment_window, values=payment_options, textvariable=payment_var)
        payment_dropdown.grid(row=0, column=1, padx=10, pady=10)

        confirm_button = ttk.Button(payment_window, text="Bestätigen", command=lambda: self.complete_payment(payment_window, total_price, payment_var))
        confirm_button.grid(row=1, column=0, columnspan=2, pady=10)



    def complete_payment(self, payment_window, total_price, payment_var):
        self.payment_method = payment_var.get()
        payment_window.destroy()

        tip_message = f"Trinkgeld: {self.tip_percentage * total_price:.2f} €\n" if self.tip_percentage > 0 else ""
        confirmation_message = f"Ihre Bestellung wurde erfolgreich bezahlt.\n{tip_message}Gesamtpreis: {total_price:.2f} €\nZahlungsmethode: {self.payment_method}"

        payment_result = simpledialog.askstring("Bezahlung abgeschlossen", confirmation_message)

        if payment_result:
            if payment_result.lower() == "storno":
                self.cancel_order(self.orders["ID"].iloc[-1])  # Storniere die letzte Bestellung
                status_message = "storniert"
            else:
                status_message = "erfolgreich"
            self.display_order_status(status_message)
        else:
            print("Zahlung storniert.")

    def display_order_status(self, payment_method):
        status_window = tk.Toplevel(self.root)
        status_window.title("Bestellstatus")

        if payment_method.lower() == "storno":
            status_label = tk.Label(status_window, text=f"Ihre letzte Bestellung wurde {payment_method}.")
        else:
            status_label = tk.Label(status_window, text=f"Ihre letzte Bestellung wurde {payment_method}.")

        status_label.pack()
    
    def calculate_total_price(self, tip_amount):
        total = sum(
            float(self.menu.loc[dish_id, "Preis"].split(" ")[0].replace(",", ".")) * quantity
            if dish_id in self.menu.index else 0
            for dish_id, quantity in self.cart.items()
        )
        
        total += total * tip_amount
        print(f"Total after tip: {total}")
        
        return total

if __name__ == "__main__":
    root = tk.Tk()
    main_menu = MainMenu(root)
    root.mainloop()