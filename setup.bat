CALL venv\Scripts\activate

venv\Scripts\pyinstaller --console --icon="app.ico" --add-data="venv\Lib\site-packages\Selenium;Selenium" video_handler.py