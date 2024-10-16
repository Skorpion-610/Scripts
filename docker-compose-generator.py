import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import yaml

# Liste des images disponibles et des versions Docker Compose
docker_images = ["nginx:alpine", "prometheus", "grafana" , "mariadb:latest", "wordpress:php8.3-fpm-alpine", "nextcloud:latest"]
compose_versions = ["3", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8"]

# Fonction pour nettoyer et formater les listes (ports, volumes)
def clean_and_format_list(input_str):
    cleaned_list = [item.strip() for item in input_str.split(',') if item.strip()]
    return cleaned_list

# Fonction pour générer le fichier docker-compose.yml
def generate_compose_file(version, services_data, output_path):
    data = {
        'version': version,
        'services': services_data
    }
    with open(output_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
    messagebox.showinfo("Success", f"docker-compose.yml has been created at {output_path}")

# Fonction pour ajouter un service
def add_service():
    service_name = service_name_entry.get()
    selected_image = image_var.get()
    container_name = container_name_entry.get()

    # Nettoyage et formatage des ports et volumes
    ports = clean_and_format_list(ports_entry.get())
    volumes = clean_and_format_list(volumes_entry.get())

    # Ajouter les attributs dynamiques
    dynamic_attributes = {}
    for name, (label, entry, format_choice, row, format1_radio, format2_radio) in dynamic_entries.items():
        value = entry.get()
        if format_choice.get() == 1:  # Format 1
            dynamic_attributes[name] = value
        elif format_choice.get() == 2:  # Format 2
            dynamic_attributes[name] = [value]  # Liste pour le format 2

    if service_name and selected_image and container_name:
        services[service_name] = {
            'container_name': container_name,
            'image': selected_image,
            'ports': ports,
            'volumes': volumes,
            **dynamic_attributes
        }
        messagebox.showinfo("Info", f"Service {service_name} added!")
        clear_dynamic_attributes()  # Effacer uniquement les attributs dynamiques après ajout
        clear_entries()  # Effacer les champs principaux après ajout
    else:
        messagebox.showwarning("Warning", "Please fill in all fields!")

# Fonction pour collecter les données saisies dans l'interface
def submit_form():
    if not services:
        messagebox.showwarning("Warning", "No services added!")
        return

    # Sélectionner l'endroit où enregistrer le fichier docker-compose.yml
    output_path = filedialog.asksaveasfilename(defaultextension=".yml", filetypes=[("YAML files", "*.yml")])
    if output_path:
        selected_version = version_var.get()
        generate_compose_file(selected_version, services, output_path)

# Fonction pour effacer les champs principaux après l'ajout d'un service
def clear_entries():
    service_name_entry.delete(0, tk.END)
    container_name_entry.delete(0, tk.END)
    ports_entry.delete(0, tk.END)
    volumes_entry.delete(0, tk.END)

# Fonction pour ajouter un attribut dynamique
def add_dynamic_attribute():
    attr_name = simpledialog.askstring("Input", "Enter dynamic attribute name:")
    if attr_name:
        row = len(dynamic_entries) + 9  # Commence juste en dessous des champs existants
        
        dynamic_label = tk.Label(root, text=f"{attr_name} (comma-separated)", background=bg_color, fg="white", font=("Helvetica", 10))
        dynamic_label.grid(row=row, column=0, sticky=tk.W)
        
        dynamic_entry = tk.Entry(root, font=("Helvetica", 10))
        dynamic_entry.grid(row=row, column=1)

        # Ajouter des boutons radio pour choisir le format
        format_choice = tk.IntVar(value=1)  # Valeur par défaut : Format 1
        format1_radio = tk.Radiobutton(root, text="Format 1 (key: value)", variable=format_choice, value=1)
        format1_radio.grid(row=row, column=2)
        format2_radio = tk.Radiobutton(root, text="Format 2 (list)", variable=format_choice, value=2)
        format2_radio.grid(row=row, column=3)

        # Enregistrer la référence pour collecter les valeurs plus tard
        dynamic_entries[attr_name] = (dynamic_label, dynamic_entry, format_choice, row, format1_radio, format2_radio)

# Fonction pour effacer uniquement les attributs dynamiques après l'ajout d'un service
def clear_dynamic_attributes():
    for label, entry, format_choice, row, format1_radio, format2_radio in dynamic_entries.values():
        label.grid_forget()  # Cache l'étiquette
        entry.grid_forget()  # Cache l'entrée
        format1_radio.grid_forget()  # Cache le bouton radio Format 1
        format2_radio.grid_forget()  # Cache le bouton radio Format 2
    dynamic_entries.clear()  # Vider le dictionnaire des attributs dynamiques

# Dictionnaire pour stocker les services ajoutés
services = {}
dynamic_entries = {}  # Pour stocker les attributs dynamiques

# Interface graphique avec Tkinter
root = tk.Tk()
root.title("Docker-Compose Generator")

# Thème et style
bg_color = "#2f3336"  # Couleur de fond
button_color = "#3984ac"  # Couleur des boutons
button_text_color = "white"  # Couleur du texte des boutons

root.configure(bg=bg_color)

# Version du fichier docker-compose
tk.Label(root, text="Compose Version", background=bg_color, fg="white", font=("Helvetica", 10)).grid(row=0, column=0, sticky=tk.W)

# Créer un style pour le combobox
style = ttk.Style()
style.configure("TCombobox", foreground="#2f3336", font=("Helvetica", 10))

version_var = tk.StringVar(root)
version_dropdown = ttk.Combobox(root, textvariable=version_var, values=compose_versions, style="TCombobox")
version_dropdown.grid(row=0, column=1)
version_dropdown.current(7)  # Sélectionner par défaut la version 3.7

# Service Name
tk.Label(root, text="Service Name", background=bg_color, fg="white", font=("Helvetica", 10)).grid(row=1, column=0, sticky=tk.W)
service_name_entry = tk.Entry(root, font=("Helvetica", 10))
service_name_entry.grid(row=1, column=1)

# Sélection d'une image Docker depuis un menu déroulant
tk.Label(root, text="Docker Image", background=bg_color, fg="white", font=("Helvetica", 10)).grid(row=2, column=0, sticky=tk.W)
image_var = tk.StringVar(root)
image_dropdown = ttk.Combobox(root, textvariable=image_var, values=docker_images, font=("Helvetica", 10))
image_dropdown.grid(row=2, column=1)
image_dropdown.current(0)  # Sélectionne par défaut la première image

# Nom du conteneur
tk.Label(root, text="Container Name", background=bg_color, fg="white", font=("Helvetica", 10)).grid(row=3, column=0, sticky=tk.W)
container_name_entry = tk.Entry(root, font=("Helvetica", 10))
container_name_entry.grid(row=3, column=1)

# Volumes
tk.Label(root, text="Volumes (comma-separated)", background=bg_color, fg="white", font=("Helvetica", 10)).grid(row=4, column=0, sticky=tk.W)
volumes_entry = tk.Entry(root, font=("Helvetica", 10))
volumes_entry.grid(row=4, column=1)

# Ports
tk.Label(root, text="Ports (comma-separated)", background=bg_color, fg="white", font=("Helvetica", 10)).grid(row=5, column=0, sticky=tk.W)
ports_entry = tk.Entry(root, font=("Helvetica", 10))
ports_entry.grid(row=5, column=1)

# Bouton pour ajouter un attribut dynamique
add_dynamic_button = tk.Button(root, text="Add Dynamic Attribute", command=add_dynamic_attribute, font=("Helvetica", 10), bg=button_color, fg=button_text_color)
add_dynamic_button.grid(row=6, column=0, columnspan=2, pady=10)

# Bouton pour ajouter le service
add_button = tk.Button(root, text="Add Service", command=add_service, font=("Helvetica", 10), bg=button_color, fg=button_text_color)
add_button.grid(row=7, column=0, columnspan=2, pady=10)

# Bouton pour générer le fichier docker-compose.yml
submit_button = tk.Button(root, text="Generate docker-compose.yml", command=submit_form, font=("Helvetica", 10), bg=button_color, fg=button_text_color)
submit_button.grid(row=8, column=0, columnspan=2, pady=10)

# Lancer l'interface
root.mainloop()