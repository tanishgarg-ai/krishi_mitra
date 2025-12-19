from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from selenium.webdriver.common.keys import Keys
import time
chrome_options = Options()
# chrome_options.add_argument("--head")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 60)  # 10 seconds wait

driver.get("https://www.myscheme.gov.in/search/category/Agriculture%2CRural%20%26%20Environment")
# Wait until the cards are present instead of sleep
input_box = driver.find_element(By.NAME, "query")
driver.execute_script("arguments[0].setAttribute('value', 'kisan');", input_box)

wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.p-4")))
cards = driver.find_elements(By.CSS_SELECTOR, "div.p-4")
# time.sleep(10)
# print(len(cards))
schemes = []


# click the button
# for x in range(2):
    # path = driver.find_element(By.XPATH, "//svg[@class='ml-2 text-darkblue-900 dark:text-white cursor-pointer']/*[name()='path'][2]")
    # path.click()
    # time.sleep(3)
for i in range(len(cards)):
    time.sleep(0.5)
    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='query']"))
    )

    # clear and type 'kisan'
    search_input.clear()
    search_input.send_keys("kisan")

    # wait until the button becomes clickable
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Search']"))
    )
    search_button.click()
    time.sleep(1)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.p-4")
    print(len(cards))
    try:
        card = cards[i]
        title_tag = card.find_element(By.CSS_SELECTOR, "h2[id^='scheme-name'] a")
        title = title_tag.text
        link = title_tag.get_attribute("href")

        ministry_tag = card.find_elements(By.CSS_SELECTOR, "h2.mt-3")
        ministry = ministry_tag[0].text if ministry_tag else None

        desc_tag = card.find_elements(By.CSS_SELECTOR, "span[aria-label*='Brief description']")
        description = desc_tag[0].text if desc_tag else None

        # Go to scheme page
        driver.get(link)
        # Wait until the details section is present
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#details")))

        try:
            details = driver.find_element(By.CSS_SELECTOR, "div#details").text
            eligibility = driver.find_element(By.CSS_SELECTOR, "div#eligibility").text
            application_process = driver.find_element(By.CSS_SELECTOR, "div#application-process").text
            documents_required = driver.find_element(By.CSS_SELECTOR, "div#documents-required").text
        except:
            details = eligibility = application_process = documents_required = None

        schemes.append({
            "title": title,
            "link": link,
            "ministry": ministry,
            "description": description,
            "details": details,
            "eligibility": eligibility,
            "application_process": application_process,
            "documents_required": documents_required,
        })

        # Go back to main page
        driver.back()
        # Wait until the cards are present again
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.p-4")))

    except Exception as e:
        print("Error:", e)
        continue
# path = driver.find_element(By.XPATH, "//svg[@class='ml-2 text-darkblue-900 dark:text-white cursor-pointer']/*[name()='path'][2]")
# path.click()


driver.quit()

# Save to JSON
with open("schemeas.json", "w", encoding="utf-8") as f:
    json.dump(schemes, f, ensure_ascii=False, indent=4)
    print("sasda")