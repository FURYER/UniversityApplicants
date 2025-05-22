from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox, QDialog, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox, QHBoxLayout, QTabWidget, QComboBox, QListWidgetItem, QFileDialog, QGridLayout
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QAction, QIcon
from db import Session
from models import Applicant, Specialty, EntranceExam, EducationDocument, ExamResult, Application
from datetime import date
import re
import os
import shutil
from .applications_tab import ApplicationsTab
from .specialties_tab import SpecialtiesTab
from .statistics_tab import StatisticsTab

DARK_QSS = """
QWidget {
    background-color: #181c27;
    color: #e0e6f0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 15px;
}
QLabel {
    color: #e0e6f0;
    font-size: 16px;
}
QPushButton {
    background-color: #23273a;
    color: #e0e6f0;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 500;
    border: 1px solid #23273a;
    transition: background 0.2s;
}
QPushButton:hover {
    background-color: #2e334a;
    border: 1px solid #3a3f5c;
}
QPushButton:pressed {
    background-color: #1a1e2b;
}
QLineEdit, QDateEdit {
    background-color: #23273a;
    color: #e0e6f0;
    border: 1.5px solid #23273a;
    border-radius: 7px;
    padding: 6px 10px;
    font-size: 15px;
}
QLineEdit:focus, QDateEdit:focus {
    border: 1.5px solid #4f8cff;
    background-color: #23273a;
}
QListWidget {
    background-color: #23273a;
    color: #e0e6f0;
    border-radius: 8px;
    font-size: 15px;
    padding: 8px;
}
QDialog {
    background-color: #202432;
    border-radius: 12px;
}
QDialog QLabel {
    font-size: 15px;
}
QDialog QLineEdit, QDialog QDateEdit {
    background-color: #23273a;
    color: #e0e6f0;
    border: 1.5px solid #23273a;
    border-radius: 7px;
    padding: 6px 10px;
    font-size: 15px;
}
QDialog QLineEdit:focus, QDialog QDateEdit:focus {
    border: 1.5px solid #4f8cff;
}
QDialog QPushButton {
    min-width: 90px;
}
QDialogButtonBox {
    button-layout: 0;
}
QScrollBar:vertical {
    background: #23273a;
    width: 12px;
    margin: 0px 0px 0px 0px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #3a3f5c;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* --- Стили для вкладок --- */
QTabWidget::pane {
    border: none;
    background: #181c27;
}
QTabBar::tab {
    background: #23273a;
    color: #e0e6f0;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 140px;
    min-height: 32px;
    margin-right: 2px;
    padding: 8px 18px 6px 18px;
    font-size: 15px;
}
QTabBar::tab:selected {
    background: #23273a;
    color: #4f8cff;
    font-weight: 600;
}
QTabBar::tab:!selected {
    background: #202432;
    color: #b0b6c6;
}
QTabBar::tab:hover {
    background: #2e334a;
    color: #4f8cff;
}
QTabBar {
    background: #181c27;
    border-bottom: 1.5px solid #23273a;
}

/* --- Стили для календаря --- */
QCalendarWidget {
    background-color: #23273a;
    color: #e0e6f0;
    border-radius: 10px;
    border: 1.5px solid #23273a;
}
QCalendarWidget QToolButton {
    background: #23273a;
    color: #e0e6f0;
    border: none;
    font-size: 15px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 6px;
}
QCalendarWidget QToolButton:hover {
    background: #2e334a;
    color: #4f8cff;
}
QCalendarWidget QMenu {
    background: #23273a;
    color: #e0e6f0;
    border-radius: 8px;
}
QCalendarWidget QSpinBox {
    background: #23273a;
    color: #e0e6f0;
    border: 1px solid #23273a;
    border-radius: 6px;
}
QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #23273a;
}
QCalendarWidget QAbstractItemView {
    background-color: #23273a;
    color: #e0e6f0;
    selection-background-color: #4f8cff;
    selection-color: #fff;
    border-radius: 6px;
}
QCalendarWidget QAbstractItemView:enabled {
    background-color: #23273a;
    color: #e0e6f0;
}
QCalendarWidget QAbstractItemView:disabled {
    color: #888;
}
QCalendarWidget QTableView {
    border-radius: 6px;
}
QCalendarWidget QHeaderView {
    background: #23273a;
    color: #b0b6c6;
    font-weight: 500;
}
QCalendarWidget QTableView QTableCornerButton::section {
    background: #23273a;
}
QCalendarWidget QTableView::item:selected {
    background: #4f8cff;
    color: #fff;
}
QCalendarWidget QWidget {
    background: #23273a;
    color: #e0e6f0;
}
QCalendarWidget QTableView QHeaderView::section {
    background: #23273a;
    color: #b0b6c6;
    font-weight: 500;
}
"""

class AddApplicantDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить абитуриента")
        self.setModal(True)
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.middle_name = QLineEdit()
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate.currentDate())
        self.passport_number = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QLineEdit()

        self.error_labels = {}
        for field in ["first_name", "last_name", "middle_name", "passport_number", "email", "phone"]:
            self.error_labels[field] = QLabel()
            self.error_labels[field].setStyleSheet("color: #ff5c5c; font-size: 13px;")
            self.error_labels[field].setVisible(False)

        layout.addRow("Имя*:", self.first_name)
        layout.addRow("", self.error_labels["first_name"])
        layout.addRow("Фамилия*:", self.last_name)
        layout.addRow("", self.error_labels["last_name"])
        layout.addRow("Отчество:", self.middle_name)
        layout.addRow("", self.error_labels["middle_name"])
        layout.addRow("Дата рождения*:", self.birth_date)
        layout.addRow("Паспорт*:", self.passport_number)
        layout.addRow("", self.error_labels["passport_number"])
        layout.addRow("Email:", self.email)
        layout.addRow("", self.error_labels["email"])
        layout.addRow("Телефон:", self.phone)
        layout.addRow("", self.error_labels["phone"])
        layout.addRow("Адрес:", self.address)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        # Мгновенная валидация
        self.first_name.textChanged.connect(self.validate_first_name)
        self.last_name.textChanged.connect(self.validate_last_name)
        self.passport_number.textChanged.connect(self.validate_passport)
        self.email.textChanged.connect(self.validate_email)
        self.phone.textChanged.connect(self.validate_phone)

    def validate_first_name(self):
        value = self.first_name.text().strip()
        if not value:
            self.error_labels["first_name"].setText("Имя обязательно для заполнения.")
            self.error_labels["first_name"].setVisible(True)
            return False
        if not re.match(r'^[А-Яа-яA-Za-z]{2,}$', value):
            self.error_labels["first_name"].setText("Имя: только буквы, минимум 2 символа.")
            self.error_labels["first_name"].setVisible(True)
            return False
        self.error_labels["first_name"].setVisible(False)
        return True

    def validate_last_name(self):
        value = self.last_name.text().strip()
        if not value:
            self.error_labels["last_name"].setText("Фамилия обязательна для заполнения.")
            self.error_labels["last_name"].setVisible(True)
            return False
        if not re.match(r'^[А-Яа-яA-Za-z]{2,}$', value):
            self.error_labels["last_name"].setText("Фамилия: только буквы, минимум 2 символа.")
            self.error_labels["last_name"].setVisible(True)
            return False
        self.error_labels["last_name"].setVisible(False)
        return True

    def validate_middle_name(self):
        value = self.middle_name.text().strip()
        if value and not re.match(r'^[А-Яа-яA-Za-z]{2,}$', value):
            self.error_labels["middle_name"].setText("Отчество: только буквы, минимум 2 символа.")
            self.error_labels["middle_name"].setVisible(True)
            return False
        self.error_labels["middle_name"].setVisible(False)
        return True

    def validate_passport(self):
        value = self.passport_number.text().strip()
        if not value:
            self.error_labels["passport_number"].setText("Паспорт обязателен для заполнения.")
            self.error_labels["passport_number"].setVisible(True)
            return False
        if not re.match(r'^[A-Za-zА-Яа-я0-9]{6,20}$', value):
            self.error_labels["passport_number"].setText("Паспорт: только буквы и цифры, 6-20 символов.")
            self.error_labels["passport_number"].setVisible(True)
            return False
        session = Session()
        exists = session.query(Applicant).filter_by(passport_number=value).first()
        session.close()
        if exists:
            self.error_labels["passport_number"].setText("Паспорт уже существует.")
            self.error_labels["passport_number"].setVisible(True)
            return False
        self.error_labels["passport_number"].setVisible(False)
        return True

    def validate_email(self):
        value = self.email.text().strip()
        if value and not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', value):
            self.error_labels["email"].setText("Некорректный email.")
            self.error_labels["email"].setVisible(True)
            return False
        if value:
            session = Session()
            exists = session.query(Applicant).filter_by(email=value).first()
            session.close()
            if exists:
                self.error_labels["email"].setText("Email уже существует.")
                self.error_labels["email"].setVisible(True)
                return False
        self.error_labels["email"].setVisible(False)
        return True

    def validate_phone(self):
        value = self.phone.text().strip()
        if value and not re.match(r'^\+?\d{10,15}$', value):
            self.error_labels["phone"].setText("Телефон: только цифры, допускается +, 10-15 символов.")
            self.error_labels["phone"].setVisible(True)
            return False
        self.error_labels["phone"].setVisible(False)
        return True

    def validate_birth_date(self):
        value = self.birth_date.date().toPython()
        if value > date.today():
            QMessageBox.warning(self, "Ошибка", "Дата рождения не может быть в будущем.")
            return False
        if value.year < 1900:
            QMessageBox.warning(self, "Ошибка", "Дата рождения не может быть раньше 1900 года.")
            return False
        return True

    def validate_and_accept(self):
        valid = (
            self.validate_first_name() and
            self.validate_last_name() and
            self.validate_middle_name() and
            self.validate_passport() and
            self.validate_email() and
            self.validate_phone() and
            self.validate_birth_date()
        )
        if not valid:
            return
        self.accept()

    def get_data(self):
        return {
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'middle_name': self.middle_name.text().strip(),
            'birth_date': self.birth_date.date().toPython(),
            'passport_number': self.passport_number.text().strip(),
            'email': self.email.text().strip(),
            'phone': self.phone.text().strip(),
            'address': self.address.text().strip(),
        }

class EditApplicantDialog(QDialog):
    def __init__(self, applicant, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать абитуриента")
        self.setModal(True)
        self.applicant = applicant
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.first_name = QLineEdit(applicant.first_name)
        self.last_name = QLineEdit(applicant.last_name)
        self.middle_name = QLineEdit(applicant.middle_name or "")
        self.birth_date = QDateEdit()
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate(applicant.birth_date.year, applicant.birth_date.month, applicant.birth_date.day))
        self.passport_number = QLineEdit(applicant.passport_number)
        self.email = QLineEdit(applicant.email or "")
        self.phone = QLineEdit(applicant.phone or "")
        self.address = QLineEdit(applicant.address or "")

        self.error_labels = {}
        for field in ["first_name", "last_name", "middle_name", "passport_number", "email", "phone"]:
            self.error_labels[field] = QLabel()
            self.error_labels[field].setStyleSheet("color: #ff5c5c; font-size: 13px;")
            self.error_labels[field].setVisible(False)

        layout.addRow("Имя*:", self.first_name)
        layout.addRow("", self.error_labels["first_name"])
        layout.addRow("Фамилия*:", self.last_name)
        layout.addRow("", self.error_labels["last_name"])
        layout.addRow("Отчество:", self.middle_name)
        layout.addRow("", self.error_labels["middle_name"])
        layout.addRow("Дата рождения*:", self.birth_date)
        layout.addRow("Паспорт*:", self.passport_number)
        layout.addRow("", self.error_labels["passport_number"])
        layout.addRow("Email:", self.email)
        layout.addRow("", self.error_labels["email"])
        layout.addRow("Телефон:", self.phone)
        layout.addRow("", self.error_labels["phone"])
        layout.addRow("Адрес:", self.address)

        self.delete_button = QPushButton("Удалить абитуриента")
        self.delete_button.setStyleSheet("background: #ff5c5c; color: #fff; border-radius: 8px; font-size: 15px; padding: 8px 22px;")
        self.delete_button.clicked.connect(self.delete_applicant)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        self.buttons.button(QDialogButtonBox.Save).setText("Сохранить")
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        layout.addRow(self.delete_button)

        # Мгновенная валидация
        self.first_name.textChanged.connect(self.validate_first_name)
        self.last_name.textChanged.connect(self.validate_last_name)
        self.passport_number.textChanged.connect(self.validate_passport)
        self.email.textChanged.connect(self.validate_email)
        self.phone.textChanged.connect(self.validate_phone)

        self.deleted = False

    def validate_first_name(self):
        value = self.first_name.text().strip()
        if not value:
            self.error_labels["first_name"].setText("Имя обязательно для заполнения.")
            self.error_labels["first_name"].setVisible(True)
            return False
        if not re.match(r'^[А-Яа-яA-Za-z]{2,}$', value):
            self.error_labels["first_name"].setText("Имя: только буквы, минимум 2 символа.")
            self.error_labels["first_name"].setVisible(True)
            return False
        self.error_labels["first_name"].setVisible(False)
        return True

    def validate_last_name(self):
        value = self.last_name.text().strip()
        if not value:
            self.error_labels["last_name"].setText("Фамилия обязательна для заполнения.")
            self.error_labels["last_name"].setVisible(True)
            return False
        if not re.match(r'^[А-Яа-яA-Za-z]{2,}$', value):
            self.error_labels["last_name"].setText("Фамилия: только буквы, минимум 2 символа.")
            self.error_labels["last_name"].setVisible(True)
            return False
        self.error_labels["last_name"].setVisible(False)
        return True

    def validate_middle_name(self):
        value = self.middle_name.text().strip()
        if value and not re.match(r'^[А-Яа-яA-Za-z]{2,}$', value):
            self.error_labels["middle_name"].setText("Отчество: только буквы, минимум 2 символа.")
            self.error_labels["middle_name"].setVisible(True)
            return False
        self.error_labels["middle_name"].setVisible(False)
        return True

    def validate_passport(self):
        value = self.passport_number.text().strip()
        if not value:
            self.error_labels["passport_number"].setText("Паспорт обязателен для заполнения.")
            self.error_labels["passport_number"].setVisible(True)
            return False
        if not re.match(r'^[A-Za-zА-Яа-я0-9]{6,20}$', value):
            self.error_labels["passport_number"].setText("Паспорт: только буквы и цифры, 6-20 символов.")
            self.error_labels["passport_number"].setVisible(True)
            return False
        session = Session()
        exists = session.query(Applicant).filter(
            Applicant.passport_number == value,
            Applicant.applicant_id != self.applicant.applicant_id
        ).first()
        session.close()
        if exists:
            self.error_labels["passport_number"].setText("Паспорт уже существует.")
            self.error_labels["passport_number"].setVisible(True)
            return False
        self.error_labels["passport_number"].setVisible(False)
        return True

    def validate_email(self):
        value = self.email.text().strip()
        if value and not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', value):
            self.error_labels["email"].setText("Некорректный email.")
            self.error_labels["email"].setVisible(True)
            return False
        if value:
            session = Session()
            exists = session.query(Applicant).filter(
                Applicant.email == value,
                Applicant.applicant_id != self.applicant.applicant_id
            ).first()
            session.close()
            if exists:
                self.error_labels["email"].setText("Email уже существует.")
                self.error_labels["email"].setVisible(True)
                return False
        self.error_labels["email"].setVisible(False)
        return True

    def validate_phone(self):
        value = self.phone.text().strip()
        if value and not re.match(r'^\+?\d{10,15}$', value):
            self.error_labels["phone"].setText("Телефон: только цифры, допускается +, 10-15 символов.")
            self.error_labels["phone"].setVisible(True)
            return False
        self.error_labels["phone"].setVisible(False)
        return True

    def validate_birth_date(self):
        value = self.birth_date.date().toPython()
        if value > date.today():
            QMessageBox.warning(self, "Ошибка", "Дата рождения не может быть в будущем.")
            return False
        if value.year < 1900:
            QMessageBox.warning(self, "Ошибка", "Дата рождения не может быть раньше 1900 года.")
            return False
        return True

    def validate_and_accept(self):
        valid = (
            self.validate_first_name() and
            self.validate_last_name() and
            self.validate_middle_name() and
            self.validate_passport() and
            self.validate_email() and
            self.validate_phone() and
            self.validate_birth_date()
        )
        if not valid:
            return
        self.accept()

    def get_data(self):
        return {
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'middle_name': self.middle_name.text().strip(),
            'birth_date': self.birth_date.date().toPython(),
            'passport_number': self.passport_number.text().strip(),
            'email': self.email.text().strip(),
            'phone': self.phone.text().strip(),
            'address': self.address.text().strip(),
        }

    def delete_applicant(self):
        reply = QMessageBox.question(self, "Подтвердите удаление", f"Удалить абитуриента: {self.applicant.last_name} {self.applicant.first_name}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.deleted = True
            self.accept()

class ApplicantsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(22)
        layout.setContentsMargins(40, 30, 40, 30)

        header_layout = QHBoxLayout()
        self.label = QLabel("Абитуриенты")
        self.label.setStyleSheet("font-size: 22px; font-weight: 600; color: #fff;")
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        
        self.documents_button = QPushButton("Документы")
        self.documents_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #23273a; color: #fff; border-radius: 8px;")
        self.documents_button.clicked.connect(self.manage_documents)
        header_layout.addWidget(self.documents_button)
        
        self.exams_button = QPushButton("Результаты экзаменов")
        self.exams_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #23273a; color: #fff; border-radius: 8px;")
        self.exams_button.clicked.connect(self.manage_exam_results)
        header_layout.addWidget(self.exams_button)
        
        self.add_button = QPushButton("+ Добавить абитуриента")
        self.add_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #4f8cff; color: #fff; border-radius: 8px;")
        self.add_button.clicked.connect(self.add_applicant)
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)

        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по фамилии или имени...")
        self.filter_edit.textChanged.connect(self.load_applicants)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 16px; background: #23273a; border-radius: 10px; padding: 12px;")
        self.list_widget.itemDoubleClicked.connect(self.edit_applicant)
        layout.addWidget(self.list_widget)

        self.load_applicants()

    def load_applicants(self):
        self.list_widget.clear()
        session = Session()
        try:
            query = session.query(Applicant)
            filter_text = self.filter_edit.text().strip().lower()
            if filter_text:
                query = query.filter((Applicant.last_name.ilike(f"%{filter_text}%")) | (Applicant.first_name.ilike(f"%{filter_text}%")))
            applicants = query.all()
            for a in applicants:
                item = QListWidgetItem(f"{a.last_name} {a.first_name} ({a.birth_date})")
                item.setData(Qt.UserRole, a.applicant_id)
                self.list_widget.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()

    def add_applicant(self):
        dialog = AddApplicantDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            session = Session()
            try:
                applicant = Applicant(**data)
                session.add(applicant)
                session.commit()
                QMessageBox.information(self, "Успех", "Абитуриент успешно добавлен!")
                self.load_applicants()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить абитуриента: {e}")
            finally:
                session.close()

    def edit_applicant(self, item):
        applicant_id = item.data(Qt.UserRole)
        session = Session()
        try:
            applicant = session.query(Applicant).get(applicant_id)
            if not applicant:
                QMessageBox.warning(self, "Ошибка", "Абитуриент не найден в базе.")
                return
            dialog = EditApplicantDialog(applicant, self)
            if dialog.exec() == QDialog.Accepted:
                if dialog.deleted:
                    session.delete(applicant)
                    session.commit()
                    QMessageBox.information(self, "Удаление", "Абитуриент удалён.")
                else:
                    data = dialog.get_data()
                    for k, v in data.items():
                        setattr(applicant, k, v)
                    session.commit()
                    QMessageBox.information(self, "Успех", "Данные абитуриента обновлены!")
                self.load_applicants()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить: {e}")
        finally:
            session.close()

    def manage_documents(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите абитуриента для управления документами.")
            return
        item = selected_items[0]
        applicant_id = item.data(Qt.UserRole)
        session = Session()
        try:
            applicant = session.query(Applicant).get(applicant_id)
            if applicant:
                dialog = EducationDocumentsDialog(applicant, self)
                dialog.exec()
        finally:
            session.close()

    def manage_exam_results(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите абитуриента для управления результатами экзаменов.")
            return
        item = selected_items[0]
        applicant_id = item.data(Qt.UserRole)
        session = Session()
        try:
            applicant = session.query(Applicant).get(applicant_id)
            if applicant:
                dialog = ExamResultsDialog(applicant, self)
                dialog.exec()
        finally:
            session.close()

class EducationDocumentsDialog(QDialog):
    def __init__(self, applicant, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Документы об образовании - {applicant.last_name} {applicant.first_name}")
        self.setModal(True)
        self.applicant = applicant
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Список документов
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 15px; background: #23273a; border-radius: 10px; padding: 12px;")
        self.list_widget.itemDoubleClicked.connect(self.edit_document)
        layout.addWidget(self.list_widget)

        # Форма добавления
        form_layout = QFormLayout()
        self.document_type = QComboBox()
        self.document_type.addItems(['Аттестат о среднем общем образовании', 'Диплом о среднем профессиональном образовании', 'Диплом о высшем образовании'])
        self.document_number = QLineEdit()
        self.issue_date = QDateEdit()
        self.issue_date.setCalendarPopup(True)
        self.issue_date.setDate(QDate.currentDate())
        self.issuing_organization = QLineEdit()
        self.scan_path = QLineEdit()
        self.scan_path.setReadOnly(True)
        
        form_layout.addRow("Тип документа*:", self.document_type)
        form_layout.addRow("Номер документа*:", self.document_number)
        form_layout.addRow("Дата выдачи*:", self.issue_date)
        form_layout.addRow("Организация*:", self.issuing_organization)
        form_layout.addRow("Скан документа:", self.scan_path)
        layout.addLayout(form_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить документ")
        self.add_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #4f8cff; color: #fff; border-radius: 8px;")
        self.add_button.clicked.connect(self.add_document)
        buttons_layout.addWidget(self.add_button)

        self.upload_button = QPushButton("Загрузить скан")
        self.upload_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #23273a; color: #fff; border-radius: 8px;")
        self.upload_button.clicked.connect(self.upload_scan)
        buttons_layout.addWidget(self.upload_button)

        self.close_button = QPushButton("Закрыть")
        self.close_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #23273a; color: #fff; border-radius: 8px;")
        self.close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_button)
        layout.addLayout(buttons_layout)

        self.load_documents()

    def load_documents(self):
        self.list_widget.clear()
        session = Session()
        try:
            documents = session.query(EducationDocument).filter_by(applicant_id=self.applicant.applicant_id).all()
            for doc in documents:
                item = QListWidgetItem(
                    f"{doc.document_type}\n"
                    f"Номер: {doc.document_number} | "
                    f"Дата: {doc.issue_date} | "
                    f"Организация: {doc.issuing_organization}"
                )
                item.setData(Qt.UserRole, doc.document_id)
                self.list_widget.addItem(item)
        finally:
            session.close()

    def upload_scan(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите скан документа",
            "",
            "Изображения (*.png *.jpg *.jpeg *.pdf)"
        )
        if file_path:
            self.scan_path.setText(file_path)

    def add_document(self):
        document_type = self.document_type.currentText()
        document_number = self.document_number.text().strip()
        issue_date = self.issue_date.date().toPython()
        issuing_organization = self.issuing_organization.text().strip()
        scan_path = self.scan_path.text().strip()

        if not document_number:
            QMessageBox.warning(self, "Ошибка", "Введите номер документа.")
            return
        if not issuing_organization:
            QMessageBox.warning(self, "Ошибка", "Введите название организации.")
            return

        session = Session()
        try:
            # Если есть скан, копируем его в папку uploads
            final_scan_path = None
            if scan_path:
                uploads_dir = os.path.join(os.getcwd(), 'uploads', 'education_documents')
                os.makedirs(uploads_dir, exist_ok=True)
                filename = f"{self.applicant.applicant_id}_{document_number}_{os.path.basename(scan_path)}"
                final_scan_path = os.path.join(uploads_dir, filename)
                shutil.copy2(scan_path, final_scan_path)

            document = EducationDocument(
                applicant_id=self.applicant.applicant_id,
                document_type=document_type,
                document_number=document_number,
                issue_date=issue_date,
                issuing_organization=issuing_organization,
                scan_path=final_scan_path
            )
            session.add(document)
            session.commit()
            self.document_number.clear()
            self.issuing_organization.clear()
            self.scan_path.clear()
            self.load_documents()
            QMessageBox.information(self, "Успех", "Документ успешно добавлен!")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить документ: {e}")
        finally:
            session.close()

    def edit_document(self, item):
        document_id = item.data(Qt.UserRole)
        session = Session()
        try:
            document = session.query(EducationDocument).get(document_id)
            if not document:
                QMessageBox.warning(self, "Ошибка", "Документ не найден в базе.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать документ")
            dialog.setModal(True)
            layout = QFormLayout(dialog)

            document_type = QComboBox()
            document_type.addItems(['Аттестат о среднем общем образовании', 'Диплом о среднем профессиональном образовании', 'Диплом о высшем образовании'])
            document_type.setCurrentText(document.document_type)
            document_number = QLineEdit(document.document_number)
            issue_date = QDateEdit()
            issue_date.setCalendarPopup(True)
            issue_date.setDate(QDate(document.issue_date.year, document.issue_date.month, document.issue_date.day))
            issuing_organization = QLineEdit(document.issuing_organization)
            scan_path = QLineEdit(document.scan_path or "")
            scan_path.setReadOnly(True)

            layout.addRow("Тип документа*:", document_type)
            layout.addRow("Номер документа*:", document_number)
            layout.addRow("Дата выдачи*:", issue_date)
            layout.addRow("Организация*:", issuing_organization)
            layout.addRow("Скан документа:", scan_path)

            upload_button = QPushButton("Загрузить новый скан")
            upload_button.clicked.connect(lambda: self.upload_scan_for_edit(scan_path))
            layout.addRow(upload_button)

            buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
            buttons.button(QDialogButtonBox.Save).setText("Сохранить")
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec() == QDialog.Accepted:
                new_document_type = document_type.currentText()
                new_document_number = document_number.text().strip()
                new_issue_date = issue_date.date().toPython()
                new_issuing_organization = issuing_organization.text().strip()
                new_scan_path = scan_path.text().strip()

                if not new_document_number:
                    QMessageBox.warning(self, "Ошибка", "Введите номер документа.")
                    return
                if not new_issuing_organization:
                    QMessageBox.warning(self, "Ошибка", "Введите название организации.")
                    return

                # Если есть новый скан, копируем его
                if new_scan_path and new_scan_path != document.scan_path:
                    uploads_dir = os.path.join(os.getcwd(), 'uploads', 'education_documents')
                    os.makedirs(uploads_dir, exist_ok=True)
                    filename = f"{self.applicant.applicant_id}_{new_document_number}_{os.path.basename(new_scan_path)}"
                    final_scan_path = os.path.join(uploads_dir, filename)
                    shutil.copy2(new_scan_path, final_scan_path)
                    new_scan_path = final_scan_path

                document.document_type = new_document_type
                document.document_number = new_document_number
                document.issue_date = new_issue_date
                document.issuing_organization = new_issuing_organization
                if new_scan_path:
                    document.scan_path = new_scan_path

                session.commit()
                self.load_documents()
                QMessageBox.information(self, "Успех", "Документ успешно обновлен!")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить документ: {e}")
        finally:
            session.close()

    def upload_scan_for_edit(self, scan_path_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите скан документа",
            "",
            "Изображения (*.png *.jpg *.jpeg *.pdf)"
        )
        if file_path:
            scan_path_edit.setText(file_path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.list_widget.currentItem():
            item = self.list_widget.currentItem()
            document_id = item.data(Qt.UserRole)
            reply = QMessageBox.question(
                self,
                "Подтвердите удаление",
                f"Удалить документ: {item.text()}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                session = Session()
                try:
                    document = session.query(EducationDocument).get(document_id)
                    if document:
                        # Удаляем файл скана, если он есть
                        if document.scan_path and os.path.exists(document.scan_path):
                            os.remove(document.scan_path)
                        session.delete(document)
                        session.commit()
                        self.load_documents()
                        QMessageBox.information(self, "Успех", "Документ успешно удален!")
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Не удалось удалить документ: {e}")
                finally:
                    session.close()
        else:
            super().keyPressEvent(event)

class ExamResultsDialog(QDialog):
    def __init__(self, applicant, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Результаты экзаменов - {applicant.last_name} {applicant.first_name}")
        self.setModal(True)
        self.applicant = applicant
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Список результатов
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 15px; background: #23273a; border-radius: 10px; padding: 12px;")
        self.list_widget.itemDoubleClicked.connect(self.edit_result)
        layout.addWidget(self.list_widget)

        # Форма добавления
        form_layout = QFormLayout()
        self.application_combo = QComboBox()
        session = Session()
        self.applications = session.query(Application).filter_by(applicant_id=self.applicant.applicant_id).all()
        for app in self.applications:
            specialty = app.specialty.name if app.specialty else "?"
            self.application_combo.addItem(f"{specialty}", app.application_id)
        session.close()
        self.exam_type = QComboBox()
        self.exam_type.addItems(['ЕГЭ', 'Вступительный экзамен'])
        self.subject = QLineEdit()
        self.score = QLineEdit()
        self.exam_date = QDateEdit()
        self.exam_date.setCalendarPopup(True)
        self.exam_date.setDate(QDate.currentDate())
        
        form_layout.addRow("Заявление*:", self.application_combo)
        form_layout.addRow("Тип экзамена*:", self.exam_type)
        form_layout.addRow("Предмет*:", self.subject)
        form_layout.addRow("Балл*:", self.score)
        form_layout.addRow("Дата экзамена*:", self.exam_date)
        layout.addLayout(form_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить результат")
        self.add_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #4f8cff; color: #fff; border-radius: 8px;")
        self.add_button.clicked.connect(self.add_result)
        buttons_layout.addWidget(self.add_button)

        self.close_button = QPushButton("Закрыть")
        self.close_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #23273a; color: #fff; border-radius: 8px;")
        self.close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_button)
        layout.addLayout(buttons_layout)

        self.load_results()

    def load_results(self):
        self.list_widget.clear()
        session = Session()
        try:
            # Получаем все application_id для этого абитуриента
            application_ids = [a.application_id for a in session.query(Application).filter_by(applicant_id=self.applicant.applicant_id).all()]
            if application_ids:
                results = session.query(ExamResult).filter(ExamResult.application_id.in_(application_ids)).all()
            else:
                results = []
            for result in results:
                item = QListWidgetItem(
                    f"{getattr(result, 'exam_type', '')}: {result.subject}\n"
                    f"Балл: {result.score} | "
                    f"Дата: {result.exam_date}"
                )
                item.setData(Qt.UserRole, result.result_id)
                self.list_widget.addItem(item)
        finally:
            session.close()

    def add_result(self):
        application_id = self.application_combo.currentData()
        exam_type = self.exam_type.currentText()
        subject = self.subject.text().strip()
        score = self.score.text().strip()
        exam_date = self.exam_date.date().toPython()

        if not application_id:
            QMessageBox.warning(self, "Ошибка", "Выберите заявление.")
            return
        if not subject:
            QMessageBox.warning(self, "Ошибка", "Введите название предмета.")
            return

        try:
            score = int(score)
            if score < 0 or score > 100:
                QMessageBox.warning(self, "Ошибка", "Балл должен быть от 0 до 100.")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректный балл.")
            return

        session = Session()
        try:
            result = ExamResult(
                application_id=application_id,
                exam_type=exam_type,
                subject=subject,
                score=score,
                exam_date=exam_date
            )
            session.add(result)
            session.commit()
            self.subject.clear()
            self.score.clear()
            self.load_results()
            QMessageBox.information(self, "Успех", "Результат экзамена успешно добавлен!")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить результат: {e}")
        finally:
            session.close()

    def edit_result(self, item):
        result_id = item.data(Qt.UserRole)
        session = Session()
        try:
            result = session.query(ExamResult).get(result_id)
            if not result:
                QMessageBox.warning(self, "Ошибка", "Результат не найден в базе.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать результат")
            dialog.setModal(True)
            layout = QFormLayout(dialog)

            exam_type = QComboBox()
            exam_type.addItems(['ЕГЭ', 'Вступительный экзамен'])
            exam_type.setCurrentText(result.exam_type)
            subject = QLineEdit(result.subject)
            score = QLineEdit(str(result.score))
            exam_date = QDateEdit()
            exam_date.setCalendarPopup(True)
            exam_date.setDate(QDate(result.exam_date.year, result.exam_date.month, result.exam_date.day))

            layout.addRow("Тип экзамена*:", exam_type)
            layout.addRow("Предмет*:", subject)
            layout.addRow("Балл*:", score)
            layout.addRow("Дата экзамена*:", exam_date)

            buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
            buttons.button(QDialogButtonBox.Save).setText("Сохранить")
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec() == QDialog.Accepted:
                new_exam_type = exam_type.currentText()
                new_subject = subject.text().strip()
                new_score = score.text().strip()
                new_exam_date = exam_date.date().toPython()

                if not new_subject:
                    QMessageBox.warning(self, "Ошибка", "Введите название предмета.")
                    return

                try:
                    new_score = int(new_score)
                    if new_score < 0 or new_score > 100:
                        QMessageBox.warning(self, "Ошибка", "Балл должен быть от 0 до 100.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Введите корректный балл.")
                    return

                result.exam_type = new_exam_type
                result.subject = new_subject
                result.score = new_score
                result.exam_date = new_exam_date
                session.commit()
                self.load_results()
                QMessageBox.information(self, "Успех", "Результат экзамена успешно обновлен!")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить результат: {e}")
        finally:
            session.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.list_widget.currentItem():
            item = self.list_widget.currentItem()
            result_id = item.data(Qt.UserRole)
            reply = QMessageBox.question(
                self,
                "Подтвердите удаление",
                f"Удалить результат: {item.text()}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                session = Session()
                try:
                    result = session.query(ExamResult).get(result_id)
                    if result:
                        session.delete(result)
                        session.commit()
                        self.load_results()
                        QMessageBox.information(self, "Успех", "Результат экзамена успешно удален!")
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Не удалось удалить результат: {e}")
                finally:
                    session.close()
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система абитуриентов ВУЗа")
        self.setGeometry(100, 100, 1200, 800)  # Увеличиваем размер окна для графиков
        self.setStyleSheet(DARK_QSS)

        self.tabs = QTabWidget()
        self.applicants_tab = ApplicantsTab()
        self.specialties_tab = SpecialtiesTab()
        self.applications_tab = ApplicationsTab()
        self.statistics_tab = StatisticsTab()
        self.tabs.addTab(self.applicants_tab, "Абитуриенты")
        self.tabs.addTab(self.specialties_tab, "Специальности")
        self.tabs.addTab(self.applications_tab, "Заявления")
        self.tabs.addTab(self.statistics_tab, "Статистика")
        self.setCentralWidget(self.tabs)
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if self.tabs.tabText(index) == "Статистика":
            self.statistics_tab.update_statistics()