# Importujeme knihovny, které budeme používat
import requests  # Pro stahování obsahu webových stránek
from bs4 import BeautifulSoup  # Pro zpracování HTML kódu stránky
import time  # Pro přidání pauzy mezi požadavky (respekt k serveru)

# Nastavíme základní URL adresu, kde hledáme nabídky práce s klíčovými slovy "python junior"
base_url = "https://www.jobs.cz/prace/?q%5B%5D=python%20junior"

def get_total_pages(soup):
    """
    Funkce, která zjistí, kolik je celkem stránek s výsledky vyhledávání.
    Argument 'soup' je objekt, který reprezentuje HTML kód stránky.
    """
    # Najdeme HTML element <nav> s třídou "Pagination", který obsahuje odkazy na stránky
    pagination = soup.find("nav", class_="Pagination")
    
    # Pokud stránkování na stránce není (např. jen jedna stránka výsledků), vrátíme 1
    if not pagination:
        return 1

    # Najdeme všechny odkazy na jednotlivé stránky (jsou v elementech <a> s třídou "Pagination__page")
    pages = pagination.find_all("a", class_="Pagination__page")
    page_numbers = []  # Sem budeme ukládat čísla stránek

    # Projdeme všechny nalezené odkazy a zkusíme z nich získat číslo stránky
    for page in pages:
        try:
            num = int(page.text.strip())  # Převedeme text na číslo
            page_numbers.append(num)  # Přidáme číslo do seznamu
        except ValueError:
            # Pokud text není číslo (např. šipka "další"), přeskočíme to
            continue

    # Pokud jsme našli nějaká čísla stránek, vrátíme to největší (poslední stránku)
    if page_numbers:
        return max(page_numbers)
    else:
        # Pokud žádná čísla nejsou, vrátíme 1 (jen jedna stránka)
        return 1

def scrape_page(page_num, output_file):
    """
    Funkce pro stažení a zpracování jedné stránky výsledků.
    page_num - číslo stránky, kterou chceme stáhnout
    output_file - název souboru, kam budeme ukládat výsledky
    """
    # Vytvoříme URL adresu s parametrem stránkování
    url = f"{base_url}&page={page_num}"
    print(f"Stahuji stránku {page_num}: {url}")

    try:
        # Pošleme požadavek na stránku
        response = requests.get(url)
        # Zkontrolujeme, jestli byl požadavek úspěšný (status code 200)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Pokud nastala chyba (např. stránka neexistuje nebo není připojení), vypíšeme ji a vrátíme False
        print(f"Chyba při stahování stránky {page_num}: {e}")
        return False

    # Vytvoříme objekt BeautifulSoup pro snadné zpracování HTML kódu
    soup = BeautifulSoup(response.text, "html.parser")
    # Najdeme všechny inzeráty na stránce - jsou v elementech <article> s třídou "SearchResultCard"
    job_listings = soup.find_all("article", class_="SearchResultCard")

    # Pokud na stránce nejsou žádné inzeráty, vypíšeme to a vrátíme False
    if not job_listings:
        print(f"Na stránce {page_num} nebyly nalezeny žádné inzeráty.")
        return False

    # Otevřeme soubor pro zápis v režimu 'a' (append), aby se nové záznamy přidaly za stávající obsah
    with open(output_file, "a", encoding="utf-8") as file:
        # Projdeme každý nalezený inzerát
        for job in job_listings:
            # Zkusíme najít název pozice v elementu <h2>
            title_element = job.find("h2")
            title = title_element.text.strip() if title_element else "Název neuveden"

            # Najdeme odkaz na detail inzerátu v tagu <a> uvnitř inzerátu
            link_element = job.find("a")
            # Odkaz je relativní, proto přidáme doménu jobs.cz
            link = link_element["href"] if link_element and link_element.has_attr('href') else "Odkaz nenalezen"

            # Najdeme název firmy v <div> s třídou "SearchResultCard__company"
            company_element = job.find("span", translate="no")
            company = company_element.text.strip() if company_element else "Firma neuvedena"

            # Najdeme lokalitu v <span> s atributem data-label="location"
            location_element = job.find("li", attrs={"data-test": "serp-locality"})
            location = location_element.text.strip() if location_element else "Lokalita neuvedena"

            # Vypíšeme informace do konzole pro kontrolu
            print(f"Pozice: {title}")
            print(f"Firma: {company}")
            print(f"Lokalita: {location}")
            print(f"Odkaz: {link}")
            print("-" * 30)

            # Zapíšeme informace do souboru, každý inzerát oddělíme čarou
            file.write(f"Pozice: {title}\n")
            file.write(f"Firma: {company}\n")
            file.write(f"Lokalita: {location}\n")
            file.write(f"Odkaz: {link}\n")
            file.write("-" * 30 + "\n")

    # Pokud vše proběhlo v pořádku, vrátíme True
    return True

def main():
    """
    Hlavní funkce, která spustí celý proces.
    """
    output_file = "Python_nabidky.txt"  # Název souboru, kam se budou ukládat data

    try:
        with open(output_file, 'w') as soubor:
            # Tím, že do souboru nic nezapíšete, zůstane po zavření prázdný
            pass
        print(f"Obsah souboru '{output_file}' byl úspěšně smazán.")
    except IOError as e:
        print(f"Nastala chyba při práci se souborem: {e}")

    # Pokud chcete začít vždy s prázdným souborem, odkomentujte následující řádek:
    # open(output_file, "w", encoding="utf-8").close()

    try:
        # Stáhneme první stránku, abychom zjistili počet všech stránek
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Nepodařilo se stáhnout první stránku: {e}")
        return

    # Vytvoříme BeautifulSoup objekt z první stránky
    soup = BeautifulSoup(response.text, "html.parser")
    # Zjistíme, kolik je celkem stránek
    total_pages = get_total_pages(soup)
    print(f"Celkový počet stránek: {total_pages}")

    # Projdeme všechny stránky od 1 do poslední
    for page_num in range(1, total_pages + 1):
        success = scrape_page(page_num, output_file)
        if not success:
            # Pokud nastala chyba nebo stránka je prázdná, ukončíme procházení
            print(f"Ukončuji procházení na stránce {page_num} kvůli chybě nebo prázdné stránce.")
            break
        # Pauza 1 sekunda, abychom server nezatěžovali příliš rychlými požadavky
        time.sleep(1)

# Tento blok zajistí, že funkce main() poběží, když spustíte tento skript
if __name__ == "__main__":
    main()
