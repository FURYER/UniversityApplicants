from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from db import Session
from models import Specialty, Application
import plotly.graph_objs as go
import plotly.io as pio
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

        # WebEngineView для plotly-графиков
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        self.update_statistics()

    def update_statistics(self):
        session = Session()
        try:
            specialties = session.query(Specialty).all()
            applications = session.query(Application).all()
            html = self.generate_statistics_html(specialties, applications)
            self.webview.setHtml(html)
        finally:
            session.close()

    def generate_statistics_html(self, specialties, applications):
        # 1. Количество заявлений по специальностям
        specialty_names = [s.name for s in specialties]
        application_counts = [len([a for a in applications if a.specialty_id == s.specialty_id]) for s in specialties]
        fig1 = go.Figure(data=[go.Bar(x=specialty_names, y=application_counts, marker_color='#4f8cff')])
        fig1.update_layout(
            title={
                'text': 'Количество заявлений по специальностям',
                'y':0.92, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top',
                'font': dict(size=22, color='white', family='Segoe UI, Arial, sans-serif')
            },
            xaxis_title=dict(text='Специальности', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            yaxis_title=dict(text='Количество заявлений', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            plot_bgcolor='#23273a', paper_bgcolor='#181c27', font_color='white',
            margin=dict(l=60, r=30, t=70, b=60), height=350, bargap=0.25,
            legend=dict(bgcolor='#23273a', bordercolor='#3a3f5c', borderwidth=1, font=dict(size=14, color='white'))
        )

        # 2. Проходные баллы по специальностям
        passing_scores = [s.passing_score if s.passing_score else 0 for s in specialties]
        fig2 = go.Figure(data=[go.Bar(x=specialty_names, y=passing_scores, marker_color='#4f8cff')])
        fig2.update_layout(
            title={
                'text': 'Проходные баллы по специальностям',
                'y':0.92, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top',
                'font': dict(size=22, color='white', family='Segoe UI, Arial, sans-serif')
            },
            xaxis_title=dict(text='Специальности', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            yaxis_title=dict(text='Проходной балл', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            plot_bgcolor='#23273a', paper_bgcolor='#181c27', font_color='white',
            margin=dict(l=60, r=30, t=70, b=60), height=350, bargap=0.25,
            legend=dict(bgcolor='#23273a', bordercolor='#3a3f5c', borderwidth=1, font=dict(size=14, color='white'))
        )

        # 3. Конкурс на место по специальностям
        competition_ratios = []
        for specialty in specialties:
            applications_count = len([a for a in applications if a.specialty_id == specialty.specialty_id])
            ratio = applications_count / specialty.seats_available if specialty.seats_available > 0 else 0
            competition_ratios.append(ratio)
        fig3 = go.Figure(data=[go.Bar(x=specialty_names, y=competition_ratios, marker_color='#4f8cff')])
        fig3.update_layout(
            title={
                'text': 'Конкурс на место по специальностям',
                'y':0.92, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top',
                'font': dict(size=22, color='white', family='Segoe UI, Arial, sans-serif')
            },
            xaxis_title=dict(text='Специальности', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            yaxis_title=dict(text='Количество заявлений на место', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            plot_bgcolor='#23273a', paper_bgcolor='#181c27', font_color='white',
            margin=dict(l=60, r=30, t=70, b=60), height=350, bargap=0.25,
            legend=dict(bgcolor='#23273a', bordercolor='#3a3f5c', borderwidth=1, font=dict(size=14, color='white'))
        )

        # 4. Статистика по факультетам
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
        application_counts_fac = [data['applications'] for data in faculty_data.values()]
        fig4 = go.Figure()
        fig4.add_bar(x=faculties, y=specialty_counts, name='Количество специальностей', marker_color='#4f8cff')
        fig4.add_bar(x=faculties, y=application_counts_fac, name='Количество заявлений', marker_color='#ff5c5c')
        fig4.update_layout(
            barmode='group',
            title={
                'text': 'Статистика по факультетам',
                'y':0.92, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top',
                'font': dict(size=22, color='white', family='Segoe UI, Arial, sans-serif')
            },
            xaxis_title=dict(text='Факультеты', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            yaxis_title=dict(text='Количество', font=dict(size=16, color='white', family='Segoe UI, Arial, sans-serif')),
            plot_bgcolor='#23273a', paper_bgcolor='#181c27', font_color='white',
            margin=dict(l=60, r=30, t=70, b=60), height=350, bargap=0.25,
            legend=dict(bgcolor='#23273a', bordercolor='#3a3f5c', borderwidth=1, font=dict(size=14, color='white'))
        )

        # Генерируем HTML для всех графиков с карточками и стилями
        html = '''
        <html><head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        body {{ background: #181c27; margin: 0; padding: 0; }}
        .plot-card {{
            background: #23273a;
            border-radius: 18px;
            box-shadow: 0 2px 16px 0 #00000033;
            padding: 18px 12px 12px 12px;
            margin-bottom: 32px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }}
        </style>
        </head><body>
        <div class="plot-card">{fig1}</div>
        <div class="plot-card">{fig2}</div>
        <div class="plot-card">{fig3}</div>
        <div class="plot-card">{fig4}</div>
        </body></html>
        '''.format(
            fig1=pio.to_html(fig1, include_plotlyjs='cdn', full_html=False, config={'displayModeBar': False}, default_width='100%', default_height='350px'),
            fig2=pio.to_html(fig2, include_plotlyjs=False, full_html=False, config={'displayModeBar': False}, default_width='100%', default_height='350px'),
            fig3=pio.to_html(fig3, include_plotlyjs=False, full_html=False, config={'displayModeBar': False}, default_width='100%', default_height='350px'),
            fig4=pio.to_html(fig4, include_plotlyjs=False, full_html=False, config={'displayModeBar': False}, default_width='100%', default_height='350px')
        )
        return html 