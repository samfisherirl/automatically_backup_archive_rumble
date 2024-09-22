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


def simulate_drag_and_drop(video_path, env_loader):
    # Set up the Chrome driver and open the target URL
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://rumble.com/upload.php")
    # body > main > div > section > div.login-third-party > button.login-google.round-button.bg-grey
    # Wait for the page elements to load
    time.sleep(1)  # Adjust based on your internet speed
    # Locate the email input, click it, and enter the email address
    email_input = driver.find_element(By.CSS_SELECTOR, "#login-username")
    email_input.click()
    email_input.send_keys(env_loader.get_value('email'))  # Replace with your actual email

    # Locate the password input, click it, and enter the password
    password_input = driver.find_element(By.CSS_SELECTOR, "#login-password")
    password_input.click()
    password_input.send_keys(env_loader.get_value('password'))  # Replace with your actual password
    login_button = driver.find_element(By.CSS_SELECTOR, "#loginForm > button.login-button.login-form-button.round-button.bg-green")
    login_button.click()

    # Wait a moment for the login process to complete
    time.sleep(5)  # Adjust based on network speed and response time


    # Locate the source element (in this case, it's the video file we will drag)
    # For simulating drag-and-drop, we need to create a dummy file input as Selenium cannot directly interact with desktop elements
    driver.execute_script("""
    var fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.id = 'seleniumFileInput';
    fileInput.style.display = 'none';
    document.body.appendChild(fileInput);
    """)
    file_input = driver.find_element(By.ID, "seleniumFileInput")
    file_input.send_keys(video_path)  # Provide the real local video path here

    # Locate the target element where the file will be dropped
    target_element = driver.find_element(By.CSS_SELECTOR, "#Filedata")

    if target_element.tag_name.lower() == 'input' and target_element.get_attribute('type') == 'file':
        target_element.send_keys(video_path)
    else:
        print("The target element is not an input of type 'file'. Unable to set the file path directly.")
    time.sleep(3)
    # Get the current day and time in a desired format
    current_day_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formats date and time as "Year-Month-Day Hour:Minute:Second"

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait a moment for the page to adjust after scrolling
    time.sleep(2)
    tit = env_loader.get_value('video_title')
    # Enter the current day and time in the title input field
    title_input = driver.find_element(By.CSS_SELECTOR, "#title")
    title_input.send_keys(f'{tit} - {current_day_time}')

    # Enter data in the description textarea
    description_input = driver.find_element(By.CSS_SELECTOR, "#description")
    description_input.send_keys(f"{tit} stream archive")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait a moment for the page to adjust after scrolling
    time.sleep(2)

    # Scroll down the page
    # Selecting "Entertainment" from the first dropdown
    entertainment_input = driver.find_element(By.CSS_SELECTOR, "#form > div > div.video-details.form-wrap > div.form-wrap > div:nth-child(1) > div > input.select-search-input")
    entertainment_input.click()
    entertainment_input.send_keys("Entertainment\n")  # Simulate typing and pressing enter

    # Wait for the dropdown to react to the previous input (optional, depends on the site's responsiveness)
    time.sleep(1)

    # Selecting "Entertainment Life" from the second dropdown
    entertainment_life_input = driver.find_element(By.CSS_SELECTOR, "#form > div > div.video-details.form-wrap > div.form-wrap > div:nth-child(2) > div > input.select-search-input")
    entertainment_life_input.click()
    entertainment_life_input.send_keys("Entertainment Life\n")  # Simulate typing and pressing enter

    # Pause the execution to observe the result
    time.sleep(10)  # Adjust the time as needed
    notFound = True
    counter = 100
    while notFound and counter > 0:
        try:
            upload_complete_indicator = driver.find_element(By.CSS_SELECTOR, "#form > div > div.upload-video-placeholder.upload-video-placholder--active > div.video-upload-info > div.upload-percent > h2")
            if "100%" in upload_complete_indicator.text:
                # Click submit button
                submit_button = driver.find_element(By.CSS_SELECTOR, "#submitForm")
                submit_button.click()
                notFound = False
            else:
                time.sleep(10)
        except Exception as e:
            time.sleep(10)
            print(str(e))
        counter =- 1
    time.sleep(2)

    try:
        withScroll(driver)
    except Exception as e:
        print(str(e))
    try:
        withJavascript(driver)
    except Exception as e:
        print(str(e))
    try:
        withSel(driver)
    except Exception as e:
        print(str(e))

    submit_button = driver.find_element(By.ID, "submitForm2")
    submit_button.click()
    submit_button = driver.find_element(By.CSS_SELECTOR, "#submitForm2")
    submit_button.click() 
    time.sleep(2)
    getUrl(driver, env_loader.get_value('open_log_when_done'))
    
    if string_to_binary(env_loader.get_value('delete_when_done')):
        os.remove(video_path)
    time.sleep(100)
    
if __name__ == "__main__":
    env_loader = EnvLoader()
    folder = env_loader.get_value("folder_path")
    simulate_drag_and_drop(find_first_video(folder), env_loader)
