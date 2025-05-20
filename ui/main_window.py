from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox, QDialog, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox, QHBoxLayout, QTabWidget
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QAction, QIcon
from db import Session
from models import Applicant
from datetime import date
import re

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
                self.list_widget.addItem(f"{a.last_name} {a.first_name} ({a.birth_date})")
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
        # Получаем ФИО и дату, ищем в базе
        text = item.text()
        fio, date_part = text.rsplit('(', 1)
        fio = fio.strip()
        date_str = date_part.replace(')', '').strip()
        last_name, first_name = fio.split(' ', 1)
        session = Session()
        try:
            applicant = session.query(Applicant).filter_by(last_name=last_name, first_name=first_name, birth_date=date_str).first()
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система абитуриентов ВУЗа")
        self.setGeometry(100, 100, 900, 650)
        self.setStyleSheet(DARK_QSS)

        self.tabs = QTabWidget()
        self.tabs.addTab(ApplicantsTab(), "Абитуриенты")
        # TODO: self.tabs.addTab(SpecialtiesTab(), "Специальности") и т.д.
        self.setCentralWidget(self.tabs) 