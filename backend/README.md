# AetherNexus Backend

Backend сервис для AetherNexus - интеллектуальной системы знаний.

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env с вашими настройками

# Запуск
python main.py
```

## Структура

- `app/api/v1/endpoints/` - API endpoints
- `app/core/` - Конфигурация и логирование
- `app/services/` - Бизнес-логика
- `app/models/` - Модели данных

## API Документация

После запуска доступна по адресу: http://localhost:8000/api/docs

