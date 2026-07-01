# Создаём папку проекта
mkdir marketing_analytics_project
cd marketing_analytics_project

# Создаём виртуальное окружение
python -m venv venv

# Активируем (Windows)
venv\Scripts\activate
# Или (Mac/Linux)
source venv/bin/activate

# Устанавливаем пакеты
pip install pandas numpy matplotlib seaborn plotly scipy statsmodels jupyter openpyxl