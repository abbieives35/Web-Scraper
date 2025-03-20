import requests
from bs4 import BeautifulSoup as bs
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_driver():
    """Initializes and returns a WebDriver instance."""
    gecko_driver_path = r'C:\New folder\geckodriver.exe'
    firefox_binary_path = r'C:\Users\aives\AppData\Local\Mozilla Firefox\firefox.exe'
    options = Options()
    options.binary_location = firefox_binary_path
    service = Service(executable_path=gecko_driver_path)
    return webdriver.Firefox(service=service, options=options)

def get_grainger_price_selenium(part_number, driver):
    """Scrapes the Grainger website for the specified part number price and unit of measure."""
    try:
        search_url = f"https://www.grainger.com/search?searchQuery={part_number}&searchBar=true"
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)

        try:
            part_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//dd[contains(text(), '{part_number}')]"))
            )
        except:
            return {"error": f"Part number '{part_number}' not found on Grainger."}

        try:
            price_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@data-testid, 'pricing-component')]")  # Updated price path
            ))
            price = price_element.text.strip()
        except:
            return {"error": "Price not found on Grainger."}

        try:
            uom_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(), 'pkg. of') or contains(text(), 'pair') or contains(text(), 'dozen')]")  # Updated UOM path
            ))
            uom = uom_element.text.strip()
        except:
            uom = "N/A"

        return {"part_number": part_number, "price": price, "uom": uom}

    except Exception as e:
        return {"error": f"Grainger Error: {e}"}

def get_western_safety_price_selenium(part_number, driver):
    """Scrapes Western Safety for price and unit of measure."""
    try:
        search_url = f"https://www.westernsafety.com/search?q={part_number}"
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)

        try:
            price_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//p[contains(@class, 'text-xl font-bold')]")
            ))
            price = price_element.text.strip()
        except:
            price = "Not Found"

        try:
            uom_element = driver.find_element(By.XPATH, "//meta[@property='og:title']")
            uom_content = uom_element.get_attribute("content")
            uom = uom_content.split("|")[1].strip() if "|" in uom_content else "Not Found"
        except:
            uom = "Not Found"

        return {"part_number": part_number, "price": price, "uom": uom}

    except Exception as e:
        return {"error": f"Western Safety Error: {e}"}

def get_magid_price_selenium(part_number, driver):
    """Scrapes Magid for price and unit of measure."""
    try:
        search_url = f"https://www.magidglove.com/search?q={part_number}"
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)

        try:
            price_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'price')]")))
            uom_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'product-price-uom')]")))
            return {"part_number": part_number, "price": price_element.text.strip(), "uom": uom_element.text.strip()}
        except:
            return {"error": "Price or UOM not found on Magid."}
    except Exception as e:
        return {"error": f"Magid Error: {e}"}
def get_rs_hughes_price_selenium(part_number, driver):
    """Scrapes RS Hughes for price and unit of measure."""
    try:
        search_url = f"https://www.rshughes.com/search.html?q={part_number}"
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)

        try:
            price_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class, 'product__price') or contains(@class, 'product_price')]")
            ))
            price = price_element.text.strip()
        except:
            price = "Not Found"

        try:
            uom_element = driver.find_element(By.XPATH, "//span[@class='product__unit-desc']")
            uom = uom_element.text.strip()
        except:
            uom = "Not Found"

        return {"part_number": part_number, "price": price, "uom": uom}

    except Exception as e:
        return {"error": f"RS Hughes Error: {e}"}

def search_prices():
    part_number = part_number_entry.get().strip()
    if not part_number:
        result_text.insert(tk.END, "Please enter a part number.\n")
        return
    
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Searching for part number: {part_number}\n")

    driver = setup_driver()
    try:
        results = {
            "Grainger": get_grainger_price_selenium(part_number, driver),
            "Western Safety": get_western_safety_price_selenium(part_number, driver),
            "Magid Glove": get_magid_price_selenium(part_number, driver),
            "RS Hughes": get_rs_hughes_price_selenium(part_number, driver)
        }
    
        for site, result in results.items():
            if "error" in result:
                result_text.insert(tk.END, f"{site}: {result['error']}\n")
            else:
                result_text.insert(tk.END, f"{site} - Part Number: {result['part_number']}, Price: {result['price']}, UOM: {result['uom']}\n")
    
    finally:
        driver.quit()

root = tk.Tk()
root.title("Multi-Site Price & UOM Scraper")
root.geometry("700x500")

tk.Label(root, text="Enter Part Number:", font=("Arial", 12)).pack(pady=5)
part_number_entry = tk.Entry(root, font=("Arial", 12), width=30)
part_number_entry.pack(pady=5)

tk.Button(root, text="Search Prices", font=("Arial", 12), command=search_prices).pack(pady=10)

result_text = scrolledtext.ScrolledText(root, width=80, height=20, font=("Arial", 10))
result_text.pack(pady=10)

root.mainloop()
