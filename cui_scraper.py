from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os
import time

def scrape_site(start_url, domain):
    visited = set()
    pages_to_visit_set = {start_url}
    pages_to_visit = [start_url]

    # Set up the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    count = 0
    while True:
        try:
            print(count)
            if pages_to_visit:
                current_page = pages_to_visit.pop(0)
                if current_page not in visited:
                    driver.get(current_page)
                    visited.add(current_page)
                    visited.add(f"{current_page}/")
                    print("Navigated to:", current_page)

                    # Wait for JavaScript to load if necessary
                    time.sleep(2)  # Adjust this sleep time as necessary for the site
                
                    # Process the page content
                    text_content = driver.find_element("tag name", "body").text
                    clean_text = text_content.encode('utf-8', 'ignore').decode('utf-8')
                    if not os.path.exists("output_folder"):
                        os.makedirs("output_folder")


                    # Save the text content to a file in the output folder
                    with open(os.path.join("output_folder", f"{count}_data.txt"), "w", encoding='utf-8') as file:
                        # file will probably have some unknown chars so encode it to utf-8 and ignore the unknown chars
                        file.write(current_page + '\n')
                        file.write(clean_text)
                        print("Wrote to file")
                    
                    count += 1
                    # Find all links on the page
                    links = driver.find_elements("tag name", "a")
                    for link in links:
                        href = link.get_attribute('href')
                        #print(href)
                        if href:
                            if domain in href and ('#' not in href) and ('.' not in href[-5:]) and href not in visited and href not in pages_to_visit_set:
                                pages_to_visit.append(href)
                                pages_to_visit_set.add(href)

                    print('Pages to visit length:', len(pages_to_visit))
            else:
                break
        except Exception as e:
            print(e)
    driver.quit()  # Make sure to close the driver

# Example usage
scrape_site('https://www.cui.edu/', 'https://www.cui.edu/')
