from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QCheckBox, QScrollArea
from PyQt5.QtCore import Qt
import sys
import yaml

# Liste des images disponibles et des versions Docker Compose
docker_images = ["nginx:alpine", "httpd:alpine", "prometheus", "grafana", "mariadb:latest", "wordpress:php8.3-fpm-alpine", "nextcloud:latest"]
compose_versions = ["3", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8"]

# Dictionnaire pour stocker les services ajoutés
services = {}

class DockerComposeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.dynamic_fields = []  # Liste des champs dynamiques
        self.initUI()

    # Fonctions des templates
    def apply_nginx_template(self):
        self.service_name_entry.setText("nginx_service")
        self.image_dropdown.setCurrentText("nginx:alpine")
        self.container_name_entry.setText("nginx_container")
        self.ports_entry.setText("80:80, 443:443")
        self.volumes_entry.setText("/host/path:/container/path")

    def apply_apache_template(self):
        self.service_name_entry.setText("apache_service")
        self.image_dropdown.setCurrentText("httpd:alpine")
        self.container_name_entry.setText("apache_container")
        self.ports_entry.setText("80:80")
        self.volumes_entry.setText("/host/path:/container/path")

    def apply_prometheus_template(self):
        self.service_name_entry.setText("prometheus_service")
        self.image_dropdown.setCurrentText("prometheus")
        self.container_name_entry.setText("prometheus_container")
        self.ports_entry.setText("9090:9090")
        self.volumes_entry.setText("/host/path:/container/path")

    def apply_grafana_template(self):
        self.service_name_entry.setText("grafana_service")
        self.image_dropdown.setCurrentText("grafana")
        self.container_name_entry.setText("grafana_container")
        self.ports_entry.setText("3000:3000")
        self.volumes_entry.setText("/host/path:/container/path")

    def initUI(self):
        self.setWindowTitle('Docker-Compose Generator')
        self.setStyleSheet("background-color: #2f3336; color: white;")

        # Layout principal
        main_layout = QVBoxLayout()

        # Section des paramètres de base
        version_label = QLabel('Compose Version')
        version_label.setStyleSheet("font-size: 12px;")
        self.version_checkbox = QCheckBox("Use Specific Version")
        self.version_checkbox.setStyleSheet("font-size: 12px;")
        self.version_checkbox.stateChanged.connect(self.toggle_version_dropdown)

        self.version_dropdown = QComboBox()
        self.version_dropdown.addItems(compose_versions)
        self.version_dropdown.setEnabled(False)

        service_name_label = QLabel('Service Name')
        self.service_name_entry = QLineEdit()

        docker_image_label = QLabel('Docker Image')
        self.image_dropdown = QComboBox()
        self.image_dropdown.addItems(docker_images)

        container_name_label = QLabel('Container Name')
        self.container_name_entry = QLineEdit()

        ports_label = QLabel('Ports (comma-separated)')
        self.ports_entry = QLineEdit()

        volumes_label = QLabel('Volumes (comma-separated)')
        self.volumes_entry = QLineEdit()

        # Section des champs dynamiques
        dynamic_label = QLabel('Dynamic Attributes')
        add_dynamic_button = QPushButton('Add Dynamic Attribute')
        add_dynamic_button.clicked.connect(self.add_dynamic_attribute)

        # Scroll Area pour les attributs dynamiques
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.dynamic_widget = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_widget)
        self.scroll_area.setWidget(self.dynamic_widget)

        # Boutons de templates pour remplir automatiquement les champs
        nginx_button = QPushButton('Nginx Template')
        nginx_button.clicked.connect(self.apply_nginx_template)
        apache_button = QPushButton('Apache Template')
        apache_button.clicked.connect(self.apply_apache_template)
        prometheus_button = QPushButton('Prometheus Template')
        prometheus_button.clicked.connect(self.apply_prometheus_template)
        grafana_button = QPushButton('Grafana Template')
        grafana_button.clicked.connect(self.apply_grafana_template)

        # Layout des boutons de templates
        template_layout = QHBoxLayout()
        template_layout.addWidget(nginx_button)
        template_layout.addWidget(apache_button)
        template_layout.addWidget(prometheus_button)
        template_layout.addWidget(grafana_button)

        main_layout.addLayout(template_layout)

        # Boutons pour l'ajout de services et la génération du fichier
        add_service_button = QPushButton('Add Service')
        add_service_button.clicked.connect(self.add_service)

        generate_button = QPushButton('Generate docker-compose.yml')
        generate_button.clicked.connect(self.submit_form)

        clear_button = QPushButton('Clear All Fields')
        clear_button.clicked.connect(self.clear_all_fields)

        # Organisation des layouts
        form_layout = QVBoxLayout()
        form_layout.addWidget(version_label)
        form_layout.addWidget(self.version_checkbox)
        form_layout.addWidget(self.version_dropdown)
        form_layout.addWidget(service_name_label)
        form_layout.addWidget(self.service_name_entry)
        form_layout.addWidget(docker_image_label)
        form_layout.addWidget(self.image_dropdown)
        form_layout.addWidget(container_name_label)
        form_layout.addWidget(self.container_name_entry)
        form_layout.addWidget(ports_label)
        form_layout.addWidget(self.ports_entry)
        form_layout.addWidget(volumes_label)
        form_layout.addWidget(self.volumes_entry)

        form_layout.addWidget(dynamic_label)
        form_layout.addWidget(self.scroll_area)
        form_layout.addWidget(add_dynamic_button)

        button_layout = QVBoxLayout()
        button_layout.addWidget(add_service_button)
        button_layout.addWidget(generate_button)
        button_layout.addWidget(clear_button)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def toggle_version_dropdown(self):
        self.version_dropdown.setEnabled(self.version_checkbox.isChecked())

    def add_dynamic_attribute(self):
        # Création d'un nouveau champ dynamique
        field_layout = QHBoxLayout()

        attribute_name = QLineEdit()
        attribute_name.setPlaceholderText('Attribute Name')
        attribute_value = QLineEdit()
        attribute_value.setPlaceholderText('Attribute Value')
        format_choice = QComboBox()
        format_choice.addItems(['Format 1', 'Format 2'])
        delete_button = QPushButton('Delete')
        
        # Ajout du champ à la liste et gestion de la suppression
        field_layout.addWidget(attribute_name)
        field_layout.addWidget(attribute_value)
        field_layout.addWidget(format_choice)
        field_layout.addWidget(delete_button)
        
        # Ajoute le layout dans la zone dynamique
        self.dynamic_layout.addLayout(field_layout)
        self.dynamic_fields.append((attribute_name, attribute_value, format_choice, field_layout))

        delete_button.clicked.connect(lambda: self.remove_dynamic_attribute(field_layout))

    def remove_dynamic_attribute(self, layout):
        # Code pour supprimer l'attribut dynamique
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
    
        # Retirer l'attribut dynamique de la liste (self.dynamic_fields)
        self.dynamic_fields = [
            item for item in self.dynamic_fields if item[3] != layout
        ]
    
        # Supprimer l'attribut de la liste
        for item in self.dynamic_fields[:]:
            if item[3] == layout:
                self.dynamic_fields.remove(item)

    def add_service(self):
        service_name = self.service_name_entry.text()
        selected_image = self.image_dropdown.currentText()
        container_name = self.container_name_entry.text()
        ports = self.clean_and_format_list(self.ports_entry.text())
        volumes = self.clean_and_format_list(self.volumes_entry.text())
    
        dynamic_attributes = {}
        for name, value, format_choice, layout in self.dynamic_fields:
            if name.text() and value.text():
                if format_choice.currentText() == 'Format 1':
                    # Format 1 : attribut sous forme de liste
                    dynamic_attributes[name.text()] = [value.text()]  # Stocker comme liste pour les ports
                else:
                    # Format 2 : attribut sous forme simple
                    dynamic_attributes[name.text()] = value.text()
    
        service_data = {
            'container_name': container_name,
            'image': selected_image,
            'ports': ports,
            'volumes': volumes
        }
    
        if dynamic_attributes:
            service_data['dynamic_attributes'] = dynamic_attributes
    
        if service_name and selected_image and container_name:
            services[service_name] = service_data
            QMessageBox.information(self, "Info", f"Service {service_name} added!")
            self.clear_entries()
        else:
            QMessageBox.warning(self, "Warning", "Please fill in all fields!")

    def submit_form(self):
        if not services:
            QMessageBox.warning(self, "Warning", "No services added!")
            return
    
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Docker Compose", "", "YAML Files (*.yml)")
        if output_path:
            selected_version = self.version_dropdown.currentText() if self.version_checkbox.isChecked() else None
            self.generate_compose_file(selected_version, services, output_path)
            services.clear()  # Vider les services après génération
            self.clear_all_fields()  # Réinitialiser tous les champs

    def generate_compose_file(self, version, services_data, output_path):
        data = {}
        if version:
            data['version'] = version
        data['services'] = services_data
        with open(output_path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
        QMessageBox.information(self, "Success", f"docker-compose.yml has been created at {output_path}")

    def clean_and_format_list(self, input_str):
        return [item.strip() for item in input_str.split(',') if item.strip()]

    def clear_entries(self):
        self.service_name_entry.clear()
        self.container_name_entry.clear()
        self.ports_entry.clear()
        self.volumes_entry.clear()

    def clear_all_fields(self):
        self.clear_entries()
        self.image_dropdown.setCurrentIndex(0)
        self.version_checkbox.setChecked(False)
        self.version_dropdown.setEnabled(False)
        self.version_dropdown.setCurrentIndex(0)
        # Clear dynamic fields
        for name, value, format_choice, layout in self.dynamic_fields:
            self.remove_dynamic_attribute(layout)
        self.dynamic_fields.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DockerComposeApp()
    ex.show()
    sys.exit(app.exec_())