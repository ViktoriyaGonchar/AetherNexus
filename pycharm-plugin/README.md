# AetherNexus PyCharm Plugin

Плагин для PyCharm, интегрирующий AetherNexus в IDE.

## Разработка

```bash
# Сборка плагина
./gradlew buildPlugin

# Запуск PyCharm с плагином
./gradlew runIde

# Тестирование
./gradlew test
```

## Установка

1. Соберите плагин: `./gradlew buildPlugin`
2. В PyCharm: `File` → `Settings` → `Plugins` → `Install Plugin from Disk`
3. Выберите файл из `build/distributions/AetherNexus-*.zip`

## Структура

- `src/main/kotlin/com/aethernexus/` - Исходный код
  - `ui/` - UI компоненты
  - `api/` - API клиент
  - `actions/` - Действия плагина
  - `settings/` - Настройки
  - `listeners/` - Слушатели событий

