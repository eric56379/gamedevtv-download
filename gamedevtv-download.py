import os
import re
import time
import json
import subprocess
import sys
import time
import click

# Hiding a warning about pkg_resources caused by seleniumwire.
import warnings
warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API"
)

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# For user input.
def parse_ranges(input_string):
    selected_items = set()
    for part in input_string.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start_str, end_str = part.split('-')
                start = int(start_str)
                end = int(end_str)

                # Ensure start is less than or equal to end for the range to work.
                if start <= end:
                    selected_items.update(range(start, end + 1))
                else:
                    click.echo(f"Invalid range: {part}. Start must be <= end.", err=True)
            except ValueError:
                click.echo(f"Invalid range format: {part}", err=True)
        else:
            try:
                item = int(part)
                selected_items.add(item)
            except ValueError:
                click.echo(f"Invalid item: {part}", err=True)
    return sorted(list(selected_items))

def login(driver):
    element = driver.find_element(By.ID, "email")
    element.send_keys(sys.argv[2])

    element = driver.find_element(By.ID, "password")
    element.send_keys(sys.argv[4])

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Letting the website complete the request.
    time.sleep(5)

def main():
    # Checking usage.
    if len(sys.argv) != 5:
        print("Usage: python3 scrape.py -e [email] -p [password]")
        sys.exit(1)

    elif (sys.argv[1] != "-e" or sys.argv[3] != "-p"):
        print("Usage: python3 scrape.py -e [email] -p [password]")
        sys.exit(1)

    browser_options = Options()
    # browser_options.add_argument("--headless")
    browser_options.add_argument("--disable-dev-shm-usage")
    browser_options.add_argument("--no-sandbox")
    browser_options.add_argument("--disable-gpu")
    browser_options.add_argument("--disable-extensions")
    browser_options.add_argument("--start-maximized")

    # Booting Selenium.
    driver = webdriver.Chrome(options=browser_options)
    wait = WebDriverWait(driver, 20)

    print(f"Logging in as {sys.argv[2]}...")

    url = "https://gamedev.tv/login"
    driver.get(url)

    WebDriverWait(driver, 30).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

    time.sleep(2)

    login(driver)

    # Obtain all courses.
    dashboard_html = driver.page_source
    
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(@data-sentry-source-file, "DashboardPage.tsx")]')))

    html = element.get_attribute("outerHTML")
    all_courses = re.findall(r'href="/courses/([^/]+)/view"', html)

    # Removing duplicates.
    all_courses = list(set(all_courses))

    if (len(all_courses) == 0):
        print("No courses were found on this account. Exiting.")
        exit()

    print("\nThe following courses are available. Make a selection with the courses you wish to download.")
    print("(e.g., '1, 3-6, 8')\n")
    print("==== AVAILABLE COURSES ====")

    for i in range(1, len(all_courses) + 1):
        print(f"{i}: {all_courses[i - 1]}")

    while True:
        try:
            user_input = str(input("\nType the range of courses to download: "))

            selection = parse_ranges(user_input)

            # Getting the courses.
            selection = [course_num - 1 for course_num in selection]
            all_courses = [all_courses[i] for i in selection]
            break

        except Exception as e:
            # print(e)
            print("Invalid argument.")

    # Starting to navigate across all courses.
    for course in all_courses:
        print(f"Starting download for {course}...")
        
        # Creating a directory for this lesson.
        os.makedirs(f"{course}", exist_ok=True)

        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        time.sleep(5)

        driver.get(f"https://gamedev.tv/courses/{course}/view")

        # Waiting for the sidebar to load up.
        lesson_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "player-sidebar")]')
            )
        )

        html_content = lesson_element.get_attribute("outerHTML")

        # Locating all of the URLs of the lesson.
        lesson_regex = re.compile(
            r'''<a[^>]+class="absolute inset-0"[^>]+href="([^"]+?)"''',
            re.IGNORECASE
        )

        lesson_urls = lesson_regex.findall(html_content)
        print(f"Found {len(lesson_urls)} lessons.")

        # Process each lesson.
        i = 0
        prev_url = ""

        for lesson_url in lesson_urls:
            i += 1 
            driver.get(f"https://gamedev.tv{lesson_url}")

            # Force a small wait for request to go through.
            time.sleep(5)

            # Define the timeout and the interval to inform the user of longer loading times.
            elapsed_time = 0
            total_timeout = 30
            check_interval = 10

            while elapsed_time < total_timeout:
                try:
                    # Wait for the playlist.m3u8 request to appear
                    WebDriverWait(driver, check_interval).until(
                        lambda d: any(r.url.endswith("playlist.m3u8") for r in d.requests)
                    )

                    # New request was found.
                    break
                except:
                    # If the WebDriverWait times out, print "Still loading..." and increase elapsed_time.
                    elapsed_time += check_interval
                    print(f"Lesson {i}: Still loading...")

            # If the condition wasn't met and loop exits after total_timeout.
            if elapsed_time >= total_timeout:
                print(f"Timed out waiting for Lesson {i}. This lesson will be skipped.")
                continue

            # Get newest playlist request.
            m3u8_requests = [
                r.url for r in driver.requests
                if r.url.endswith("playlist.m3u8")
            ]

            # New request was found. Prepare it for downloading.
            if m3u8_requests and (prev_url != m3u8_requests[-1]):
                m3u8_url = m3u8_requests[-1]
                prev_url = m3u8_requests[-1]

            # Skip this lesson. It was likely just text and not a video.
            else:
                i -= 1
                continue

            # Download with yt-dlp.
            output_path = f"{course}/Lesson {i}.mp4"

            if os.path.exists(output_path):
                print(f"Lesson {i} is already downloading. Skipping.")

            else:
                print(f"Downloading Lesson {i}...")
                subprocess.run([
                    "yt-dlp", "--no-warnings", "--quiet", "--progress",
                    "-o", f"{output_path}", 
                    m3u8_url
                ])

    # Finished downloading all courses.
    driver.quit()

if __name__ == "__main__":
    main()
