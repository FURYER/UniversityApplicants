from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt
from db import Session
from models import Specialty, Application
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class StatisticsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(22)
        layout.setContentsMargins(40, 30, 40, 30)

        # Заголовок
        header_layout = QHBoxLayout()
        self.label = QLabel("Статистика")
        self.label.setStyleSheet("font-size: 22px; font-weight: 600; color: #fff;")
        header_layout.addWidget(self.label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Создаем сетку для графиков
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # График количества заявлений по специальностям
        self.applications_figure = Figure(figsize=(6, 4), facecolor='#181c27')
        self.applications_canvas = FigureCanvas(self.applications_figure)
        grid_layout.addWidget(self.applications_canvas, 0, 0)

        # График проходных баллов
        self.scores_figure = Figure(figsize=(6, 4), facecolor='#181c27')
        self.scores_canvas = FigureCanvas(self.scores_figure)
        grid_layout.addWidget(self.scores_canvas, 0, 1)

        # График конкурса на место
        self.competition_figure = Figure(figsize=(6, 4), facecolor='#181c27')
        self.competition_canvas = FigureCanvas(self.competition_figure)
        grid_layout.addWidget(self.competition_canvas, 1, 0)

        # График статистики по факультетам
        self.faculties_figure = Figure(figsize=(6, 4), facecolor='#181c27')
        self.faculties_canvas = FigureCanvas(self.faculties_figure)
        grid_layout.addWidget(self.faculties_canvas, 1, 1)

        layout.addLayout(grid_layout)
        self.update_statistics()

    def update_statistics(self):
        session = Session()
        try:
            # Получаем данные для графиков
            specialties = session.query(Specialty).all()
            applications = session.query(Application).all()

            # 1. Количество заявлений по специальностям
            self.plot_applications_by_specialty(specialties, applications)

            # 2. Проходные баллы
            self.plot_passing_scores(specialties)

            # 3. Конкурс на место
            self.plot_competition_ratio(specialties, applications)

            # 4. Статистика по факультетам
            self.plot_faculty_statistics(specialties, applications)

        finally:
            session.close()

    def plot_applications_by_specialty(self, specialties, applications):
        ax = self.applications_figure.add_subplot(111)
        ax.clear()
        
        specialty_names = [s.name for s in specialties]
        application_counts = [len([a for a in applications if a.specialty_id == s.specialty_id]) for s in specialties]
        
        bars = ax.bar(specialty_names, application_counts, color='#4f8cff')
        ax.set_title('Количество заявлений по специальностям', color='white', pad=20)
        ax.set_xlabel('Специальности', color='white')
        ax.set_ylabel('Количество заявлений', color='white')
        
        # Настройка внешнего вида
        ax.set_facecolor('#23273a')
        ax.tick_params(colors='white')
        ax.grid(True, color='#3a3f5c', linestyle='--', alpha=0.3)
        
        # Поворот подписей для лучшей читаемости
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.applications_figure.tight_layout()
        self.applications_canvas.draw()

    def plot_passing_scores(self, specialties):
        ax = self.scores_figure.add_subplot(111)
        ax.clear()
        
        specialty_names = [s.name for s in specialties]
        passing_scores = [s.passing_score if s.passing_score else 0 for s in specialties]
        
        bars = ax.bar(specialty_names, passing_scores, color='#4f8cff')
        ax.set_title('Проходные баллы по специальностям', color='white', pad=20)
        ax.set_xlabel('Специальности', color='white')
        ax.set_ylabel('Проходной балл', color='white')
        
        # Настройка внешнего вида
        ax.set_facecolor('#23273a')
        ax.tick_params(colors='white')
        ax.grid(True, color='#3a3f5c', linestyle='--', alpha=0.3)
        
        # Поворот подписей для лучшей читаемости
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.scores_figure.tight_layout()
        self.scores_canvas.draw()

    def plot_competition_ratio(self, specialties, applications):
        ax = self.competition_figure.add_subplot(111)
        ax.clear()
        
        specialty_names = [s.name for s in specialties]
        competition_ratios = []
        
        for specialty in specialties:
            applications_count = len([a for a in applications if a.specialty_id == specialty.specialty_id])
            ratio = applications_count / specialty.seats_available if specialty.seats_available > 0 else 0
            competition_ratios.append(ratio)
        
        bars = ax.bar(specialty_names, competition_ratios, color='#4f8cff')
        ax.set_title('Конкурс на место по специальностям', color='white', pad=20)
        ax.set_xlabel('Специальности', color='white')
        ax.set_ylabel('Количество заявлений на место', color='white')
        
        # Настройка внешнего вида
        ax.set_facecolor('#23273a')
        ax.tick_params(colors='white')
        ax.grid(True, color='#3a3f5c', linestyle='--', alpha=0.3)
        
        # Поворот подписей для лучшей читаемости
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.competition_figure.tight_layout()
        self.competition_canvas.draw()

    def plot_faculty_statistics(self, specialties, applications):
        ax = self.faculties_figure.add_subplot(111)
        ax.clear()
        
        # Группируем специальности по факультетам
        faculty_data = {}
        for specialty in specialties:
            if specialty.faculty not in faculty_data:
                faculty_data[specialty.faculty] = {
                    'specialties': 0,
                    'applications': 0,
                    'seats': 0
                }
            faculty_data[specialty.faculty]['specialties'] += 1
            faculty_data[specialty.faculty]['seats'] += specialty.seats_available
            faculty_data[specialty.faculty]['applications'] += len([a for a in applications if a.specialty_id == specialty.specialty_id])
        
        faculties = list(faculty_data.keys())
        specialty_counts = [data['specialties'] for data in faculty_data.values()]
        application_counts = [data['applications'] for data in faculty_data.values()]
        
        x = np.arange(len(faculties))
        width = 0.35
        
        ax.bar(x - width/2, specialty_counts, width, label='Количество специальностей', color='#4f8cff')
        ax.bar(x + width/2, application_counts, width, label='Количество заявлений', color='#ff5c5c')
        
        ax.set_title('Статистика по факультетам', color='white', pad=20)
        ax.set_xlabel('Факультеты', color='white')
        ax.set_ylabel('Количество', color='white')
        ax.set_xticks(x)
        ax.set_xticklabels(faculties)
        ax.legend(facecolor='#23273a', edgecolor='#3a3f5c', labelcolor='white')
        
        # Настройка внешнего вида
        ax.set_facecolor('#23273a')
        ax.tick_params(colors='white')
        ax.grid(True, color='#3a3f5c', linestyle='--', alpha=0.3)
        
        # Поворот подписей для лучшей читаемости
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.faculties_figure.tight_layout()
        self.faculties_canvas.draw() 