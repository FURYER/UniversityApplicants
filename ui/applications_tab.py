from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QComboBox, QDateEdit, QListWidgetItem
)
from PySide6.QtCore import Qt, QDate
from db import Session
from models import Application, Applicant, Specialty
from datetime import datetime

class ApplicationsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(22)
        layout.setContentsMargins(40, 30, 40, 30)

        header_layout = QHBoxLayout()
        self.label = QLabel("Заявления")
        self.label.setStyleSheet("font-size: 22px; font-weight: 600; color: #fff;")
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        self.add_button = QPushButton("+ Подать заявление")
        self.add_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #4f8cff; color: #fff; border-radius: 8px;")
        self.add_button.clicked.connect(self.add_application)
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)

        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по абитуриенту или специальности...")
        self.filter_edit.textChanged.connect(self.load_applications)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 16px; background: #23273a; border-radius: 10px; padding: 12px;")
        self.list_widget.itemDoubleClicked.connect(self.edit_application)
        layout.addWidget(self.list_widget)

        self.load_applications()

    def load_applications(self):
        self.list_widget.clear()
        session = Session()
        try:
            query = session.query(Application).join(Applicant).join(Specialty)
            filter_text = self.filter_edit.text().strip().lower()
            if filter_text:
                query = query.filter(
                    (Applicant.last_name.ilike(f"%{filter_text}%")) |
                    (Applicant.first_name.ilike(f"%{filter_text}%")) |
                    (Specialty.name.ilike(f"%{filter_text}%"))
                )
            applications = query.all()
            for a in applications:
                status_text = {
                    'pending': 'Подано',
                    'under_review': 'На рассмотрении',
                    'approved': 'Принято',
                    'rejected': 'Отклонено'
                }.get(a.status, a.status)
                item = QListWidgetItem(
                    f"{a.applicant.last_name} {a.applicant.first_name} -> "
                    f"{a.specialty.name} ({a.specialty.code}) - {status_text}"
                )
                item.setData(Qt.UserRole, a.application_id)
                self.list_widget.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()

    def add_application(self):
        dialog = AddApplicationDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            session = Session()
            try:
                application = Application(**data)
                session.add(application)
                session.commit()
                QMessageBox.information(self, "Успех", "Заявление успешно подано!")
                self.load_applications()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось подать заявление: {e}")
            finally:
                session.close()

    def edit_application(self, item):
        application_id = item.data(Qt.UserRole)
        session = Session()
        try:
            application = session.query(Application).get(application_id)
            if not application:
                QMessageBox.warning(self, "Ошибка", "Заявление не найдено в базе.")
                return
            dialog = EditApplicationDialog(application, self)
            if dialog.exec() == QDialog.Accepted:
                if dialog.deleted:
                    session.delete(application)
                    session.commit()
                    QMessageBox.information(self, "Удаление", "Заявление удалено.")
                else:
                    data = dialog.get_data()
                    for k, v in data.items():
                        setattr(application, k, v)
                    session.commit()
                    QMessageBox.information(self, "Успех", "Данные заявления обновлены!")
                self.load_applications()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить: {e}")
        finally:
            session.close()

class AddApplicationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подать заявление")
        self.setModal(True)
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.applicant_combo = QComboBox()
        self.specialty_combo = QComboBox()
        
        session = Session()
        try:
            applicants = session.query(Applicant).all()
            for a in applicants:
                self.applicant_combo.addItem(f"{a.last_name} {a.first_name}", a.applicant_id)
            
            specialties = session.query(Specialty).all()
            for s in specialties:
                self.specialty_combo.addItem(f"{s.name} ({s.code})", s.specialty_id)
        finally:
            session.close()

        layout.addRow("Абитуриент*:", self.applicant_combo)
        layout.addRow("Специальность*:", self.specialty_combo)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def validate_and_accept(self):
        if not self.applicant_combo.currentData() or not self.specialty_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите абитуриента и специальность.")
            return
        self.accept()

    def get_data(self):
        return {
            'applicant_id': self.applicant_combo.currentData(),
            'specialty_id': self.specialty_combo.currentData(),
            'status': 'pending'
        }

class EditApplicationDialog(QDialog):
    def __init__(self, application, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать заявление")
        self.setModal(True)
        self.application = application
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.status_combo = QComboBox()
        self.status_combo.addItems(['Подано', 'На рассмотрении', 'Принято', 'Отклонено'])
        status_map = {
            'pending': 'Подано',
            'under_review': 'На рассмотрении',
            'approved': 'Принято',
            'rejected': 'Отклонено'
        }
        self.status_combo.setCurrentText(status_map.get(application.status, application.status))

        layout.addRow("Статус:", self.status_combo)

        self.delete_button = QPushButton("Удалить заявление")
        self.delete_button.setStyleSheet("background: #ff5c5c; color: #fff; border-radius: 8px; font-size: 15px; padding: 8px 22px;")
        self.delete_button.clicked.connect(self.delete_application)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        self.buttons.button(QDialogButtonBox.Save).setText("Сохранить")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        layout.addRow(self.delete_button)

        self.deleted = False

    def get_data(self):
        status_map = {
            'Подано': 'pending',
            'На рассмотрении': 'under_review',
            'Принято': 'approved',
            'Отклонено': 'rejected'
        }
        return {
            'status': status_map[self.status_combo.currentText()]
        }

    def delete_application(self):
        reply = QMessageBox.question(
            self, 
            "Подтвердите удаление", 
            f"Удалить заявление: {self.application.applicant.last_name} {self.application.applicant.first_name} -> {self.application.specialty.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.deleted = True
            self.accept() 