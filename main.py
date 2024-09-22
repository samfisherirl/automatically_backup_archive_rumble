""""Overview:

The script automates video uploads to a website using Selenium.
It is structured around two main classes: EnvLoader and VideoUploader.
EnvLoader Class:

Manages environment variables.
Checks if a .env file exists and creates one from a template if it doesn't.
Loads environment variables from the .env file.
get_value method retrieves the value of a specified environment variable.
Ensures necessary configuration details (e.g., login credentials, file paths) are available.
VideoUploader Class:

Handles the video upload process.
Initializes a Selenium WebDriver instance to control a web browser.
login method logs into the Rumble website using credentials from environment variables.
prepare_video_upload method creates a hidden file input element and sets the video file path.
fill_video_details method fills in the video title, description, and sets the video category.
upload_and_finalize method monitors the upload progress and finalizes the upload once it reaches 100%.
Includes methods to interact with checkboxes on the webpage using different techniques.
Utility Functions:

get_my_documents_folder: Retrieves the path to the "My Documents" folder on a Windows system.
find_first_video: Scans a directory for video files with specified extensions and returns the path of the first video file found.
string_to_binary: Converts specific string values to binary (0 or 1).
withScroll, withJavascript, withSel: Helper functions to interact with checkboxes on the webpage using different methods.
Main Execution Block:

Initializes an EnvLoader instance.
Retrieves the folder path from environment variables.
Finds the first video file in the specified folder.
Creates a VideoUploader instance to perform the upload.
perform_upload method orchestrates the entire upload process, ensuring the video is uploaded and the browser is properly cleaned up afterward.
Imports:

Imports necessary modules from Selenium for web automation."""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
from dotenv import load_dotenv
import sys
import os
import ctypes
from ctypes import wintypes

# Function to get the path


def get_my_documents_folder():
    # Constants from the Windows API
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value

    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    return buf.value

class EnvLoader:
    def __init__(self, env_file_path=".env"):
        self.env_file_path = env_file_path
        self.env_template_path = f"{env_file_path}.template"
        self.check_env_file_exists()
        self.load_env()

    def check_env_file_exists(self):
        """
        Verifies if the .env file exists, and if not, it creates one from a template.
        """
        if not os.path.exists(self.env_file_path):
            if os.path.exists(self.env_template_path):
                # Create .env file from template
                with open(self.env_template_path, 'r') as template:
                    template_content = template.read()
                with open(self.env_file_path, 'w') as env_file:
                    env_file.write(template_content)
            else:
                print(f"No .env file or template ({self.env_template_path}) found.")

    def load_env(self):
        """
        Loads environment variables from the .env file.
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Adjust for when the application is frozen to use the executable's directory
            base_path = sys._MEIPASS
            env_path = os.path.join(base_path, self.env_file_path)
            load_dotenv(env_path)
        else:
            load_dotenv(self.env_file_path)

    def get_value(self, key):
        """
        Retrieves value for the specified environment variable key.
        
        :param key: Key of the environment variable
        :return: Value of the environment variable or None if not found
        """
        return os.getenv(key).strip()


def find_first_video(directory_path, file_extensions=['.mp4', '.mov']):
    """
    Scans the specified directory recursively for video files with specified extensions.
    Returns the path of the first video file found.

    :param directory_path: Path of the directory to search in.
    :param file_extensions: List of video file extensions to look for.
    :return: Path of the first video file found, or None if no video file is found.
    """
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in file_extensions):
                return os.path.join(root, file)
    return None


def string_to_binary(input_string):
    """
    Converts specified strings to binary values.
    Returns 0 if input_string is "0", "false", or "False", otherwise 1.
    
    :param input_string: The string to evaluate.
    :return: 0 or 1, as an integer.
    """
    # Normalize the input to lowercase to make the check case-insensitive
    normalized_string = input_string.lower()

    # Check if the input_string meets the criteria
    if normalized_string in ["0", "false"]:
        return 0
    else:
        return 1

def withScroll(driver):
    for checkbox_id in ["crights", "cterms"]:
        checkbox = driver.find_element(By.ID, checkbox_id)
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        checkbox.click()  # Now attempt to click after scrolling into view

def withJavascript(driver):
    for checkbox_id in ["crights", "cterms"]:
        driver.execute_script(f"document.getElementById('{checkbox_id}').click();")

def withSel(driver):
    from selenium.common.exceptions import ElementNotInteractableException
    for checkbox_id in ["crights", "cterms"]:
        retries = 3  # Maximum number of retries
        for _ in range(retries):
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                checkbox.click()
                break  # Exit loop if click is successful
            except ElementNotInteractableException:
                time.sleep(1)  # Wait for 1 second before retrying

def getUrl(driver, open_log):
    a_element = driver.find_element(By.CLASS_NAME, "round-button")  # Adjust the locator as necessary.
    href = a_element.get_attribute("href")
    full_href = driver.current_url + href if not href.startswith("http") else href  # Ensure full URL is captured.
    docs = get_my_documents_folder()
    # Filepath for the log file
    log_file_path = docs + "\\href_log.txt"

    # Check if href exists in the log file
    href_exists = False
    try:
        with open(log_file_path, "r") as file:
            if href in file.read():
                href_exists = True
    except FileNotFoundError:
        # If the file doesn't exist, we'll create it later.
        pass

    # Write to the log file
    if not href_exists:
        current_date = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(log_file_path):
            # Include the href at the top of the file with the current date if it's a new entry
            with open(log_file_path, "r+") as file:
                content = file.read()
                file.seek(0, 0)
                file.write(f"{current_date}, {full_href}\n{content}")  # Add new line at the top
        else:
            with open(log_file_path, "w") as file:
                file.write(f"{current_date}, {full_href}\n")
    else:
        print("Href already exists in the log file.")
    if open_log:
        os.system(log_file_path)


class VideoUploader:
    def __init__(self, video_path, env_loader):
        self.video_path = video_path
        self.env_loader = env_loader
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def login(self):
        self.driver.get("https://rumble.com/upload.php")
        time.sleep(1)  # Adjust based on your internet speed

        email = self.env_loader.get_value('email')
        password = self.env_loader.get_value('password')

        self.driver.find_element(By.CSS_SELECTOR, "#login-username").send_keys(email)
        self.driver.find_element(By.CSS_SELECTOR, "#login-password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "#loginForm > button.login-button.login-form-button.round-button.bg-green").click()

        time.sleep(5)  # Adjust based on network speed and response time

    def prepare_video_upload(self):
        self.driver.execute_script("""
            var fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.id = 'seleniumFileInput';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);
            """)
        file_input = self.driver.find_element(By.ID, "seleniumFileInput")
        file_input.send_keys(self.video_path)
        target_element = self.driver.find_element(By.CSS_SELECTOR, "#Filedata")

        if not (target_element.tag_name.lower() == 'input' and target_element.get_attribute('type') == 'file'):
            print("The target element is not an input of type 'file'. Unable to set the file path directly.")

    def fill_video_details(self):
        current_day_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tit = self.env_loader.get_value('video_title')

        self.driver.find_element(By.CSS_SELECTOR, "#title").send_keys(f'{tit} - {current_day_time}')
        self.driver.find_element(By.CSS_SELECTOR, "#description").send_keys(f"{tit} stream archive")
        self.set_category("Entertainment", "Entertainment Life")

    def set_category(self, primary, secondary):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        p_input = self.driver.find_element(By.CSS_SELECTOR, "input selector for primary category")
        p_input.click()
        p_input.send_keys(f"{primary}\n")

        s_input = self.driver.find_element(By.CSS_SELECTOR, "input selector for secondary category")
        s_input.click()
        s_input.send_keys(f"{secondary}\n")

    def upload_and_finalize(self):
            # Pause the execution to observe the result
        time.sleep(10)  # Adjust the time as needed
        found = False
        counter = 100
        while not found and counter > 0:
            try:
                upload_complete_indicator = self.driver.find_element(
                    By.CSS_SELECTOR, "#form > div > div.upload-video-placeholder.upload-video-placholder--active > div.video-upload-info > div.upload-percent > h2")
                if "100%" in upload_complete_indicator.text:
                    # Click submit button
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "#submitForm")
                    submit_button.click()
                    found = True
                else:
                    time.sleep(10)
                    continue
            except Exception as e:
                print(str(e))
            time.sleep(10)
            counter = - 1
            print(f'looping on upload, waiting for 100% upload\ncounter: {counter}')
        time.sleep(5)
        
        try:
            withScroll(self.driver)
        except Exception as e:
            print(str(e))
        try:
            withJavascript(self.driver)
        except Exception as e:
            print(str(e))
        try:
            withSel(self.driver)
        except Exception as e:
            print(str(e))

        submit_button = self.driver.find_element(By.ID, "submitForm2")
        submit_button.click()
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "#submitForm2")
        submit_button.click()
        time.sleep(2)
        getUrl(self.driver, env_loader.get_value('open_log_when_done'))

        if string_to_binary(env_loader.get_value('delete_when_done')):
            os.remove(self.video_path)
            
    def perform_upload(self):
        try:
            self.login()
            self.prepare_video_upload()
            self.fill_video_details()
            self.upload_and_finalize()
        finally:
            self.cleanup()

    def cleanup(self):
        if self.env_loader.get_value('delete_when_done'):
            os.remove(self.video_path)
        self.driver.quit()
        
        
        
if __name__ == "__main__":
    env_loader = EnvLoader()
    folder = env_loader.get_value("folder_path")
    uploader = VideoUploader(find_first_video(folder), env_loader)
    uploader.perform_upload()
