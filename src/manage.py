"""
Файл содержит основную функцию для запуска Django-приложения.

Он устанавливает переменную окружения DJANGO_SETTINGS_MODULE на 'src.config.patterns.development',
что указывает Django, какие настройки использовать для этого окружения. Затем пытается импортировать
функцию execute_from_command_line из django.core.management и выполняет команду Django,
переданную через аргументы командной строки.
"""

import os
import sys

def main():
    """
    Основная функция для запуска Django-приложения.

    Устанавливает переменную окружения DJANGO_SETTINGS_MODULE на 'src.config.patterns.development',
    что указывает Django, какие настройки использовать для этого окружения. Затем пытается импортировать
    функцию execute_from_command_line из django.core.management и выполняет команду Django,
    переданную через аргументы командной строки.
    """
    
    from src.core.utils.auto_api.auto_config import get_env_deploy_type

    deploy_type = get_env_deploy_type()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', deploy_type)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедитесь, что Django установлен и "
            "доступен в вашей переменной окружения PYTHONPATH. Вы не забыли активировать виртуальное окружение?"
        ) from exc

    execute_from_command_line(sys.argv)

# Если скрипт запущен напрямую, вызываем функцию main
if __name__ == '__main__':
    main()