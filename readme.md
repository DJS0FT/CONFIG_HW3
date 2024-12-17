# Конвертер Конфигураций в TOML

Конвертер конфигураций на Python, который преобразует файлы конфигурации с пользовательским синтаксисом в формат [TOML](https://toml.io/en/). Этот инструмент предназначен для парсинга файлов конфигурации, обработки переменных, массивов и выполнения операций, таких как `len` и `concat`.

## Содержание

- [Особенности](#особенности)
- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
  - [Базовое преобразование](#базовое-преобразование)
  - [Вывод в файл](#вывод-в-файл)
- [Синтаксис Файла Конфигурации](#синтаксис-файла-конфигурации)
  - [Переменные](#переменные)
  - [Массивы](#массивы)
  - [Операции](#операции)
  - [Комментарии](#комментарии)
- [Тестирование](#тестирование)
  - [Создание Тестовых Файлов](#создание-тестовых-файлов)
  - [Запуск Автоматизированных Тестов](#запуск-автоматизированных-тестов)
- [Примеры](#примеры)
- [Вклад](#вклад)
- [Лицензия](#лицензия)

## Особенности

- **Присваивание Переменных:** Определение констант с целочисленными, строковыми или массивными значениями.
- **Массивы:** Поддержка массивов, содержащих целые числа, строки или смешанные типы.
- **Операции:** Выполнение операций, таких как `len` (длина) и `concat` (конкатенация строк).
- **Комментарии:** Обработка однострочных комментариев, начинающихся с `#` или `*`, а также многострочных комментариев, заключённых между `{{!--` и `--}}`.
- **Обработка Ошибок:** Предоставление понятных сообщений об ошибках при синтаксических и вычислительных ошибках.
- **Гибкий Вывод:** Вывод конвертированного TOML в консоль или запись в указанный файл.
- **Автоматизированное Тестирование:** Включает тестовые случаи для проверки функциональности.

## Требования

- **Python 3.6+**: Убедитесь, что у вас установлен Python. Вы можете скачать его с [официального сайта](https://www.python.org/downloads/).

## Установка

1. **Клонирование Репозитория**

   ```bash
   git clone https://github.com/вашеимя/config-to-toml-converter.git
   cd config-to-toml-converter