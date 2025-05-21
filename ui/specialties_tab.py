from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QLineEdit, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QListWidgetItem, QComboBox
from PySide6.QtCore import Qt
from db import Session
from models import Specialty, EntranceExam

class SpecialtiesTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(22)
        layout.setContentsMargins(40, 30, 40, 30)

        header_layout = QHBoxLayout()
        self.label = QLabel("Специальности")
        self.label.setStyleSheet("font-size: 22px; font-weight: 600; color: #fff;")
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        
        self.exams_button = QPushButton("Управление экзаменами")
        self.exams_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #23273a; color: #fff; border-radius: 8px;")
        self.exams_button.clicked.connect(self.manage_exams)
        header_layout.addWidget(self.exams_button)
        
        self.add_button = QPushButton("+ Добавить специальность")
        self.add_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #4f8cff; color: #fff; border-radius: 8px;")
        self.add_button.clicked.connect(self.add_specialty)
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)

        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Фильтр по названию или коду...")
        self.filter_edit.textChanged.connect(self.load_specialties)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 16px; background: #23273a; border-radius: 10px; padding: 12px;")
        self.list_widget.itemDoubleClicked.connect(self.edit_specialty)
        layout.addWidget(self.list_widget)

        self.load_specialties()

    def load_specialties(self):
        self.list_widget.clear()
        session = Session()
        try:
            query = session.query(Specialty)
            filter_text = self.filter_edit.text().strip().lower()
            if filter_text:
                query = query.filter((Specialty.name.ilike(f"%{filter_text}%")) | (Specialty.code.ilike(f"%{filter_text}%")))
            specialties = query.all()
            for s in specialties:
                item = QListWidgetItem(
                    f"{s.name} ({s.code})\n"
                    f"Факультет: {s.faculty} | "
                    f"Мест: {s.seats_available} | "
                    f"Проходной балл: {s.passing_score if s.passing_score else 'Не указан'} | "
                    f"Стоимость: {s.tuition_fee if s.tuition_fee else 'Не указана'} ₽"
                )
                item.setData(Qt.UserRole, s.specialty_id)
                self.list_widget.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()

    def add_specialty(self):
        dialog = AddSpecialtyDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            session = Session()
            try:
                specialty = Specialty(**data)
                session.add(specialty)
                session.commit()
                QMessageBox.information(self, "Успех", "Специальность успешно добавлена!")
                self.load_specialties()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить специальность: {e}")
            finally:
                session.close()

    def edit_specialty(self, item):
        specialty_id = item.data(Qt.UserRole)
        session = Session()
        try:
            specialty = session.query(Specialty).get(specialty_id)
            if not specialty:
                QMessageBox.warning(self, "Ошибка", "Специальность не найдена в базе.")
                return
            dialog = EditSpecialtyDialog(specialty, self)
            if dialog.exec() == QDialog.Accepted:
                if dialog.deleted:
                    session.delete(specialty)
                    session.commit()
                    QMessageBox.information(self, "Удаление", "Специальность удалена.")
                else:
                    data = dialog.get_data()
                    for k, v in data.items():
                        setattr(specialty, k, v)
                    session.commit()
                    QMessageBox.information(self, "Успех", "Данные специальности обновлены!")
                self.load_specialties()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить: {e}")
        finally:
            session.close()

    def manage_exams(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите специальность для управления экзаменами.")
            return
        item = selected_items[0]
        specialty_id = item.data(Qt.UserRole)
        session = Session()
        try:
            specialty = session.query(Specialty).get(specialty_id)
            if specialty:
                dialog = EntranceExamsDialog(specialty, self)
                dialog.exec()
        finally:
            session.close()

class AddSpecialtyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить специальность")
        self.setModal(True)
        layout = QFormLayout(self)
        layout.setSpacing(14)

        self.name = QLineEdit()
        self.code = QLineEdit()
        self.faculty = QLineEdit()
        self.seats_available = QLineEdit()
        self.tuition_fee = QLineEdit()
        self.passing_score = QLineEdit()
        self.study_form = QComboBox()
        self.study_form.addItems(["Очная", "Заочная", "Очно-заочная"])

        layout.addRow("Название*:", self.name)
        layout.addRow("Код*:", self.code)
        layout.addRow("Факультет*:", self.faculty)
        layout.addRow("Количество мест*:", self.seats_available)
        layout.addRow("Форма обучения*:", self.study_form)
        layout.addRow("Стоимость обучения:", self.tuition_fee)
        layout.addRow("Проходной балл:", self.passing_score)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def validate_name(self):
        value = self.name.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите название специальности.")
            return False
        return True

    def validate_code(self):
        value = self.code.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите код специальности.")
            return False
        session = Session()
        exists = session.query(Specialty).filter_by(code=value).first()
        session.close()
        if exists:
            QMessageBox.warning(self, "Ошибка", "Специальность с таким кодом уже существует.")
            return False
        return True

    def validate_faculty(self):
        value = self.faculty.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите название факультета.")
            return False
        return True

    def validate_seats(self):
        value = self.seats_available.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите количество мест.")
            return False
        try:
            seats = int(value)
            if seats <= 0:
                QMessageBox.warning(self, "Ошибка", "Количество мест должно быть положительным числом.")
                return False
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное число мест.")
            return False
        return True

    def validate_tuition_fee(self):
        value = self.tuition_fee.text().strip()
        if value:
            try:
                fee = int(value)
                if fee < 0:
                    QMessageBox.warning(self, "Ошибка", "Стоимость обучения не может быть отрицательной.")
                    return False
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректную стоимость обучения.")
                return False
        return True

    def validate_passing_score(self):
        value = self.passing_score.text().strip()
        if value:
            try:
                score = int(value)
                if score < 0 or score > 100:
                    QMessageBox.warning(self, "Ошибка", "Проходной балл должен быть от 0 до 100.")
                    return False
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректный проходной балл.")
                return False
        return True

    def validate_and_accept(self):
        valid = (
            self.validate_name() and
            self.validate_code() and
            self.validate_faculty() and
            self.validate_seats() and
            self.validate_tuition_fee() and
            self.validate_passing_score()
        )
        if not valid:
            return
        self.accept()

    def get_data(self):
        study_form_map = {
            "Очная": "full_time",
            "Заочная": "part_time",
            "Очно-заочная": "distance"
        }
        return {
            'name': self.name.text().strip(),
            'code': self.code.text().strip(),
            'faculty': self.faculty.text().strip(),
            'seats_available': int(self.seats_available.text().strip()),
            'study_form': study_form_map[self.study_form.currentText()],
            'tuition_fee': int(self.tuition_fee.text().strip()) if self.tuition_fee.text().strip() else None,
            'passing_score': int(self.passing_score.text().strip()) if self.passing_score.text().strip() else None
        }

class EditSpecialtyDialog(QDialog):
    def __init__(self, specialty, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать специальность")
        self.setModal(True)
        self.specialty = specialty
        layout = QFormLayout(self)
        layout.setSpacing(14)

        self.name = QLineEdit(specialty.name)
        self.code = QLineEdit(specialty.code)
        self.faculty = QLineEdit(specialty.faculty)
        self.seats_available = QLineEdit(str(specialty.seats_available))
        self.tuition_fee = QLineEdit(str(specialty.tuition_fee) if specialty.tuition_fee else "")
        self.passing_score = QLineEdit(str(specialty.passing_score) if specialty.passing_score else "")
        self.study_form = QComboBox()
        self.study_form.addItems(["Очная", "Заочная", "Очно-заочная"])
        # Установить текущее значение по technical value
        tech_to_rus = {"full_time": "Очная", "part_time": "Заочная", "distance": "Очно-заочная"}
        if specialty.study_form:
            rus_val = tech_to_rus.get(specialty.study_form, "Очная")
            idx = self.study_form.findText(rus_val, Qt.MatchFixedString)
            if idx >= 0:
                self.study_form.setCurrentIndex(idx)

        layout.addRow("Название*:", self.name)
        layout.addRow("Код*:", self.code)
        layout.addRow("Факультет*:", self.faculty)
        layout.addRow("Количество мест*:", self.seats_available)
        layout.addRow("Форма обучения*:", self.study_form)
        layout.addRow("Стоимость обучения:", self.tuition_fee)
        layout.addRow("Проходной балл:", self.passing_score)

        self.delete_button = QPushButton("Удалить специальность")
        self.delete_button.setStyleSheet("background: #ff5c5c; color: #fff; border-radius: 8px; font-size: 15px; padding: 8px 22px;")
        self.delete_button.clicked.connect(self.delete_specialty)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        self.buttons.button(QDialogButtonBox.Save).setText("Сохранить")
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        layout.addRow(self.delete_button)

        self.deleted = False

    def validate_name(self):
        value = self.name.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите название специальности.")
            return False
        return True

    def validate_code(self):
        value = self.code.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите код специальности.")
            return False
        session = Session()
        exists = session.query(Specialty).filter(
            Specialty.code == value,
            Specialty.specialty_id != self.specialty.specialty_id
        ).first()
        session.close()
        if exists:
            QMessageBox.warning(self, "Ошибка", "Специальность с таким кодом уже существует.")
            return False
        return True

    def validate_faculty(self):
        value = self.faculty.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите название факультета.")
            return False
        return True

    def validate_seats(self):
        value = self.seats_available.text().strip()
        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите количество мест.")
            return False
        try:
            seats = int(value)
            if seats <= 0:
                QMessageBox.warning(self, "Ошибка", "Количество мест должно быть положительным числом.")
                return False
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное число мест.")
            return False
        return True

    def validate_tuition_fee(self):
        value = self.tuition_fee.text().strip()
        if value:
            try:
                fee = int(value)
                if fee < 0:
                    QMessageBox.warning(self, "Ошибка", "Стоимость обучения не может быть отрицательной.")
                    return False
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректную стоимость обучения.")
                return False
        return True

    def validate_passing_score(self):
        value = self.passing_score.text().strip()
        if value:
            try:
                score = int(value)
                if score < 0 or score > 100:
                    QMessageBox.warning(self, "Ошибка", "Проходной балл должен быть от 0 до 100.")
                    return False
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректный проходной балл.")
                return False
        return True

    def validate_and_accept(self):
        valid = (
            self.validate_name() and
            self.validate_code() and
            self.validate_faculty() and
            self.validate_seats() and
            self.validate_tuition_fee() and
            self.validate_passing_score()
        )
        if not valid:
            return
        self.accept()

    def get_data(self):
        study_form_map = {
            "Очная": "full_time",
            "Заочная": "part_time",
            "Очно-заочная": "distance"
        }
        return {
            'name': self.name.text().strip(),
            'code': self.code.text().strip(),
            'faculty': self.faculty.text().strip(),
            'seats_available': int(self.seats_available.text().strip()),
            'study_form': study_form_map[self.study_form.currentText()],
            'tuition_fee': int(self.tuition_fee.text().strip()) if self.tuition_fee.text().strip() else None,
            'passing_score': int(self.passing_score.text().strip()) if self.passing_score.text().strip() else None
        }

    def delete_specialty(self):
        reply = QMessageBox.question(self, "Подтвердите удаление", f"Удалить специальность: {self.specialty.name}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.deleted = True
            self.accept()

class EntranceExamsDialog(QDialog):
    def __init__(self, specialty, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Вступительные экзамены - {specialty.name}")
        self.setModal(True)
        self.specialty = specialty
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # Список экзаменов
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-size: 15px; background: #23273a; border-radius: 10px; padding: 12px;")
        self.list_widget.itemDoubleClicked.connect(self.edit_exam)
        layout.addWidget(self.list_widget)

        # Форма добавления
        form_layout = QFormLayout()
        self.subject = QLineEdit()
        self.min_score = QLineEdit()
        
        form_layout.addRow("Предмет*:", self.subject)
        form_layout.addRow("Минимальный балл*:", self.min_score)
        layout.addLayout(form_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить экзамен")
        self.add_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #4f8cff; color: #fff; border-radius: 8px;")
        self.add_button.clicked.connect(self.add_exam)
        buttons_layout.addWidget(self.add_button)

        self.close_button = QPushButton("Закрыть")
        self.close_button.setStyleSheet("font-size: 15px; padding: 8px 22px; background: #23273a; color: #fff; border-radius: 8px;")
        self.close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_button)
        layout.addLayout(buttons_layout)

        self.load_exams()

    def load_exams(self):
        self.list_widget.clear()
        session = Session()
        try:
            exams = session.query(EntranceExam).filter_by(specialty_id=self.specialty.specialty_id).all()
            for exam in exams:
                item = QListWidgetItem(
                    f"{exam.subject}\n"
                    f"Минимальный балл: {exam.min_score}"
                )
                item.setData(Qt.UserRole, exam.exam_id)
                self.list_widget.addItem(item)
        finally:
            session.close()

    def edit_exam(self, item):
        exam_id = item.data(Qt.UserRole)
        session = Session()
        try:
            exam = session.query(EntranceExam).get(exam_id)
            if not exam:
                QMessageBox.warning(self, "Ошибка", "Экзамен не найден в базе.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать экзамен")
            dialog.setModal(True)
            layout = QFormLayout(dialog)

            subject = QLineEdit(exam.subject)
            min_score = QLineEdit(str(exam.min_score))

            layout.addRow("Предмет*:", subject)
            layout.addRow("Минимальный балл*:", min_score)

            buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
            buttons.button(QDialogButtonBox.Save).setText("Сохранить")
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec() == QDialog.Accepted:
                new_subject = subject.text().strip()
                new_min_score = min_score.text().strip()

                if not new_subject:
                    QMessageBox.warning(self, "Ошибка", "Введите название предмета.")
                    return

                try:
                    new_min_score = int(new_min_score)
                    if new_min_score < 0 or new_min_score > 100:
                        QMessageBox.warning(self, "Ошибка", "Минимальный балл должен быть от 0 до 100.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Введите корректный минимальный балл.")
                    return

                exam.subject = new_subject
                exam.min_score = new_min_score
                session.commit()
                self.load_exams()
                QMessageBox.information(self, "Успех", "Экзамен успешно обновлен!")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить экзамен: {e}")
        finally:
            session.close()

    def add_exam(self):
        subject = self.subject.text().strip()
        min_score = self.min_score.text().strip()

        if not subject:
            QMessageBox.warning(self, "Ошибка", "Введите название предмета.")
            return

        try:
            min_score = int(min_score)
            if min_score < 0 or min_score > 100:
                QMessageBox.warning(self, "Ошибка", "Минимальный балл должен быть от 0 до 100.")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректный минимальный балл.")
            return

        session = Session()
        try:
            exam = EntranceExam(
                specialty_id=self.specialty.specialty_id,
                subject=subject,
                min_score=min_score
            )
            session.add(exam)
            session.commit()
            self.subject.clear()
            self.min_score.clear()
            self.load_exams()
            QMessageBox.information(self, "Успех", "Экзамен успешно добавлен!")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить экзамен: {e}")
        finally:
            session.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.list_widget.currentItem():
            item = self.list_widget.currentItem()
            exam_id = item.data(Qt.UserRole)
            reply = QMessageBox.question(
                self,
                "Подтвердите удаление",
                f"Удалить экзамен: {item.text()}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                session = Session()
                try:
                    exam = session.query(EntranceExam).get(exam_id)
                    if exam:
                        session.delete(exam)
                        session.commit()
                        self.load_exams()
                        QMessageBox.information(self, "Успех", "Экзамен успешно удален!")
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Не удалось удалить экзамен: {e}")
                finally:
                    session.close()
        else:
            super().keyPressEvent(event) 