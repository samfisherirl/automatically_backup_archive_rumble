CALL venv\Scripts\activate

venv\Scripts\pyinstaller --noconfirm --console --icon="app.ico" --add-data="venv\Lib\site-packages\Selenium;Selenium" rumble_video_archive.py