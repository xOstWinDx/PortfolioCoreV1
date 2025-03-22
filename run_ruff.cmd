@echo off
ruff check --fix --exit-zero
git add -u  # Добавляем измененные файлы в индекс
exit 0