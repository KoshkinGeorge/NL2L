# NL2L

Преобразование текстовых описаний и речи в LaTeX-код

## Описание

Пайплайн предназначен для автоматического преобразования текстовых описаний математических формул (или голосовых команд) в корректный LaTeX-код. Состоит из трёх основных модулей:

1. ASR — распознавание речи
2. MathDetector — выделение математических блоков в тексте на русском языке
3. NL2L — преобразование текстового описания в LaTeX-код (Seq2Seq модель)

Веб-интерфейс на Flask позволяет загружать аудиофайлы или вводить текст вручную и сразу видеть результат с рендерингом формул через MathJax.

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/KoshkinGeorge/NL2L
cd <project-folder>
```

### 2. Установка Python и зависимостей

Минимальная версия Python: 3.8

Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Установка ffmpeg (обязательно для аудио)

Whisper использует ffmpeg для обработки аудио. Установите его:

Ubuntu/Debian: 
```bash
sudo apt update && sudo apt install ffmpeg -y
```

Fedora: 
```bash
sudo dnf install ffmpeg
```

macOS (Homebrew): 
```bash
brew install ffmpeg
```

Windows: 
  1. Скачайте ffmpeg.org
  2. Распакуйте в C:\ffmpeg
  3. Добавьте C:\ffmpeg\bin в PATH (переменные среды)

## Структура проекта

NL2L/\
├── README.md\
├── requirements.txt\
└── src\
    ├── app.py # веб интерфейс на Flask\
    ├── converter\
    │   ├── NL2L.ipynb # ноутбук с пошаговым обучением\
    │   ├── NL2L.py    # модуль, который делает инференс на предобученных весах\
    │   └── nl2l-large\
    │       ├──  ... # предобученные веса\
    ├── detector\
    │   ├── MathDetector.py\
    │   ├── __init__.py\
    │   ├── markers.yaml # набор правил для детектора\
    ├── formal_lang\
    │   ├── lark.py # пример использования грамматики lark\
    │   ├── parser \
    │   │   ├── grammar # файлы lark с описанием правил грамматики\
    │   │   │   ├── math.lark\
    │   │   │   └── terminals.lark\
    │   │   └── transformers # трансформеры, которые преобразуют полученное AST-дерево в Latex\
    │   │       ├── __init__.py \
    │   │       ├── expr.py\
    │   │       ├── terminals.py\
    │   │       └── trig.py\
    │   └── trees # примеры парсинга для наглядности\
    │       ├── parse_tree.png\
    │       ├── parse_tree_1.png\
    │       ├── parse_tree_2.png\
    │       ├── parse_tree_3.png\
    │       ├── parse_tree_4.png\
    │       └── parse_tree_5.png\
    ├── pipeline.py # единый пайплайн\
    ├── templates\
    │   └── index.html # веб-страничка\
    └── utils.py # вспомогательные функции

## Настройка

### 1. Модель NL2L

Веса обученной модели на гитхаб не влезли, а потому загрузите папку src/converter/nl2l-large/ отдельно с моего [гугл диска](https://drive.google.com/file/d/1FzTMHkJyLq6fV_TENrSWVPbtF3NJ-sUv/view?usp=sharing)

## Запуск

### Веб-интерфейс

```bash
python ./src/app.py
```

Откройте браузер: http://localhost:5000

## Требования к системе

Компонент: ОЗУ | Минимум: 8 ГБ | Рекомендуется: 16 ГБ+\
Компонент: Место на диске | Минимум: 10 ГБ | Рекомендуется: 20 ГБ+\
Компонент: GPU (опционально) | Минимум: — | Рекомендуется: NVIDIA с 8+ ГБ VRAM\
Компонент: Python | Минимум: 3.8+ | Рекомендуется: 3.10+

## Контакты

Автор: [Кошкин Георгий, БПИ232]\
Почта: [gakoshkin@edu.hse.ru]\
Проект выполнен в рамках летней практики.
