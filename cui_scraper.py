from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import re

#normalize url to make sure we don't visit the same page twice because of a small difference in the url
def normalize_url(url):
    return re.sub(r'^https?://(www\.)?', '', url.rstrip('/').lower())

def scrape_site(start_url, domain):
    start_time = time.time()
    visited = set()
    pages_to_visit_set = {normalize_url(start_url)}
    pages_to_visit = [start_url]

    # Set up the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    action = ActionChains(driver)
    wait = WebDriverWait(driver, 3)
    count = 0
    while True:
        try:
            page_time = time.time()
            if pages_to_visit:
                current_page = pages_to_visit.pop(0)
                normalized_current = normalize_url(current_page)
                if normalized_current not in visited:

                    driver.get(current_page)
                    if normalize_url(driver.current_url) in visited:
                        print('Already visited:', current_page)
                        continue

                    visited.add(normalized_current)
                    visited.add(normalized_current + '/')  # Handle both with and without trailing slash
                    print("Navigated to:", current_page)

                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    
                    # Activate all dropdowns with the class 'togglebutton'
                    
                    dropdowns = driver.find_elements(By.CLASS_NAME, 'togglebutton')
                    for dropdown in dropdowns:
                        action.move_to_element(dropdown).click().perform()
                        time.sleep(1)

                    # Get the innerText of the body or any specific element
                    body_element = driver.find_element(By.TAG_NAME, "body")
                    text_content = body_element.get_attribute("innerText")

                    if not os.path.exists("output_folder"):
                        os.makedirs("output_folder")

                    # Save the text content to a file in the output folder
                    with open(os.path.join("output_folder", f"{count}_data.txt"), "w", encoding='utf-8') as file:
                        file.write(current_page + '\n')
                        file.write(text_content)
                        print("Wrote to file")
                    
                    count += 1
                    # Find all links on the page
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute('href')
                        if href:
                            normalized_href = normalize_url(href)
                            
                            if domain in href and ('#' not in normalized_href) and ('.' not in normalized_href[-5:]) and normalized_href not in visited and normalized_href not in pages_to_visit_set:
                                pages_to_visit.append(href)
                                pages_to_visit_set.add(normalized_href)

                    print('Pages to visit length:', len(pages_to_visit))
                    print("Time elapsed:", time.time() - page_time, "seconds")
            else:
                print("FINISHED", time.time() - start_time, "seconds")
                break
        except Exception as e:
            print(f"Error processing {current_page}: {e}")
    driver.quit()  # Make sure to close the driver

def clean_folder():
    content_set = {}
    files = os.listdir("output_folder")
    files.sort(key=lambda x: int(x[:-9]))

    for i, file in enumerate(files):
        #print(i, file)
        with open(os.path.join("output_folder", file), "r", encoding='utf-8') as f:
            #first_line = f.readline()
            content = f.read()
            f.close()
            #print(first_line)
            """main_content = content[content.index('\n'):]
            if main_content in content_set:
                #os.remove(os.path.join("output_folder", file))
                print("Removing file, already exists:", file, "in", content_set[main_content])
                #next iteration
                os.remove(os.path.join("output_folder", file))
                continue
            content_set[main_content] = file"""
            
            """if first_line[:20] != "https://www.cui.edu/" or '?' in first_line or '#' in first_line:
                os.remove(os.path.join("output_folder", file))
                print("Deleted:", file, first_line)"""
            """if "coachs-playbook" in first_line:
                os.remove(os.path.join("output_folder", file))
                print("Deleted:", file, first_line)"""
            """if "/post/" in first_line or '/news/' in first_line:
                os.remove(os.path.join("output_folder", file))
                print("Deleted:", file, first_line)"""
            footer = """Concordia University Irvine is a private, Christian university that is ranked nationally among the "Top Performers on Social Mobility" universities by U.S. News & World Report. Concordia is accredited by WASC Senior College and University Commission (WSCUC) and serves over 5,000 students annually.

Concordia University Irvine
1530 Concordia West
Irvine, CA, USA 92612

(949) 854-8002
info@cui.edu

© 1998-2024 Concordia University Irvine | Privacy Statement | Terms of Use | Accessibility"""
            """if footer in content:
                with open(os.path.join("output_folder", file), "w", encoding='utf-8') as f:
                    f.write(content[:content.index(footer)])
                print('Removed footer from:', file)"""
            #os.rename(os.path.join("output_folder", file), os.path.join("output_folder", f"{i}_data.txt"))
            if len(content) > 5000:
                overlap = 1000
                chunks = [content[i:i+5000] for i in range(0, len(content)-overlap, 5000-overlap)]
                for j, chunk in enumerate(chunks):
                    with open(os.path.join("output_folder", f"{file[:-9]}_{j}_data.txt"), "w", encoding='utf-8') as f:
                        f.write(chunk)
                        f.close()
            

if __name__ == '__main__':

    #scrape_site('https://www.cui.edu/', 'https://www.cui.edu/')
    #NOTES
    #Maybe add the site that contained the url? could make a cool visual with the data.
    clean_folder()

    pass