-- Добавление столбца application_id в таблицу exam_results
ALTER TABLE university.exam_results
ADD COLUMN application_id INTEGER REFERENCES university.applications(application_id) ON DELETE SET NULL;

-- Создание индекса для оптимизации поиска по application_id
CREATE INDEX idx_exam_results_application ON university.exam_results(application_id); 