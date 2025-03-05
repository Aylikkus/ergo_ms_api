"""
Модуль для создания новых модулей Django в директории src/external.

Этот модуль предоставляет команду Django для создания новых модулей
с предустановленной структурой файлов и директорий.

Пример использования:
    python manage.py add_module my_new_module

Создает следующую структуру:
    src/external/my_new_module/
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── serializers.py
    ├── tests.py
    ├── methods.py
    ├── scripts.py
    └── migrations/
        └── __init__.py
"""

import os
import logging

from typing import Any, Dict
from textwrap import dedent

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from src.core.utils.auto_api.auto_config import check_app_config_name
from src.core.utils.methods import convert_snake_to_camel

# Настройка логгера
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Команда Django для создания нового модуля.

    Attributes:
        help (str): Описание команды для справки Django.
    """
    help = 'Создание нового модуля в директории src/external'

    def add_arguments(self, parser) -> None:
        """
        Добавляет аргументы командной строки для команды.

        Args:
            parser: Парсер аргументов Django.
        """
        parser.add_argument('names', nargs='+', help='Имена создаваемых модулей (через пробел, например, module1 module2 module3)')

    def create_file_structure(self, module_directory: str, files_to_create: Dict[str, str]) -> None:
        """
        Создает файловую структуру модуля.

        Args:
            module_directory (str): Путь к директории модуля
            files_to_create (Dict[str, str]): Словарь с именами файлов и их содержимым
        """
        for filename, content in files_to_create.items():
            file_path = os.path.join(module_directory, filename)
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content.strip())
                logger.debug(f'Создан файл: {file_path}')
            except IOError as e:
                logger.error(f'Ошибка при создании файла {file_path}: {str(e)}')
                raise CommandError(f'Не удалось создать файл {filename}')

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Выполняет команду создания модуля.

        Args:
            *args: Позиционные аргументы
            **options: Именованные аргументы, включая names

        Raises:
            CommandError: Если модуль уже существует или возникла ошибка при создании
        """
        module_names = options['names']
        logger.info(f'Начало создания модулей: {module_names}')

        external_modules_directory = getattr(settings, 'EXTERNAL_MODULES_DIR', None)

        if not os.path.exists(external_modules_directory):
            os.makedirs(external_modules_directory)
            logger.debug(f'Создана директория: {external_modules_directory}')

        # Создаем иерархию директорий на основе переданных имен
        module_directory = os.path.normpath(os.path.join(external_modules_directory, *module_names))

        # Форматируем список модулей в строку с разделителями через точку
        formatted_module_names = " -> ".join(module_names)
        # Форматируем путь для вывода (заменяем обратные слэши на прямые)
        formatted_path = module_directory.replace("\\", "/")
        
        # В методе handle, где выводится сообщение об ошибке
        if os.path.exists(module_directory):
            logger.error(f'Модуль {module_names[-1]} уже существует: {formatted_path}')
            self.stdout.write(self.style.ERROR(
                f'Модуль {module_names[-1]} с иерархией {formatted_module_names} уже существует по пути: {formatted_path}'
            ))
            return

        # Проверка конфликта имен для конфига
        camel_module_name = convert_snake_to_camel(module_names[-1])
        if check_app_config_name(external_modules_directory, camel_module_name):
            logger.error(f'Конфликт имен: {camel_module_name}Config уже существует')
            self.stdout.write(self.style.ERROR(f'Уже существует модуль c именем класса конфига - {camel_module_name}Config.'))
            self.stdout.write(self.style.ERROR(f'Попробуйте другое название модуля.'))
            return

        try:
            # Создаем все директории в иерархии
            os.makedirs(module_directory)
            os.makedirs(os.path.join(module_directory, 'migrations'))
            logger.debug(f'Создана структура директорий для модуля {module_names}')

            # Создаем файлы в каждой директории
            files_to_create = {
                '__init__.py': '',
                'apps.py': dedent(f"""
                    from django.apps import AppConfig

                    class {camel_module_name}Config(AppConfig):
                        default_auto_field = 'django.db.models.BigAutoField'
                        name = 'src.external.{".".join(module_names)}'
                """),
                'urls.py': dedent("""
                    from django.urls import path

                    urlpatterns = [
                    ]
                """),
                'models.py': dedent("""
                    from django.db import models

                    # Создавайте свои модели здесь
                """),
                'scripts.py': dedent("""
                    # Создавайте свои скрипты здесь
                """),
                'tests.py': dedent("""
                    from django.test import TestCase

                    # Создавайте свои тесты здесь
                """),
                'serializers.py': dedent("""
                    from rest_framework import serializers

                    # Создавайте свои сериализаторы здесь
                """),
                'methods.py': dedent("""
                    # Создавайте свои вспомогательные методы здесь
                """),
                'views.py': dedent("""
                    from django.shortcuts import render

                    # Создавайте свои представления здесь
                """),
                os.path.join('migrations', '__init__.py'): '',
            }

            self.create_file_structure(module_directory, files_to_create)
            
            logger.info(f'Модуль {module_names[-1]} успешно создан')
            self.stdout.write(self.style.SUCCESS(f'Модуль {module_names[-1]} с иерархией {formatted_module_names} успешно создан по пути - {module_directory}'))

        except Exception as e:
            logger.error(f'Ошибка при создании модуля: {str(e)}')
            raise CommandError(f'Не удалось создать модуль: {str(e)}')