# Установка AetherNexus

## Быстрая установка

### 1. Установка зависимостей бэкенда

```bash
# Перейти в директорию бэкенда
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Или для минимальной установки:
pip install -r requirements-minimal.txt
```

### 2. Установка зависимостей плагина PyCharm

```bash
# Перейти в директорию плагина
cd pycharm-plugin

# Установить зависимости через Gradle
./gradlew build

# Или на Windows:
gradlew.bat build
```

### 3. Запуск бэкенда

```bash
# Из директории backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Установка плагина в PyCharm

#### Способ 1: Из исходников (для разработки)

```bash
cd pycharm-plugin
./gradlew runIde
```

#### Способ 2: Сборка и установка вручную

```bash
cd pycharm-plugin
./gradlew buildPlugin
```

Затем в PyCharm:
1. File → Settings → Plugins
2. Нажмите ⚙️ → Install Plugin from Disk
3. Выберите `pycharm-plugin/build/distributions/AetherNexus-*.zip`

## Требования

- Python 3.10+
- JDK 17+
- Gradle 8.0+
- PyCharm Community 2023.1+

