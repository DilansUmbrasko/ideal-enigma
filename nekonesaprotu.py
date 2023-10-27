import PyPDF2
import csv
import pathlib
from tabulate import tabulate
import re

def nordpool_cenas(nordpool_csv, target_date):
    with open(nordpool_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            ts_start = row[0]
            if ts_start.startswith(target_date):
                return float(row[2])
    return None

def extract_electricity_quantity(text):
    pattern = r"Elektroenerģija (\d{1,3}(?: \d{3})*,\d{2}) kWh"
    match = re.search(pattern, text)
    if match:
        electricity_quantity = match.group(1)
        electricity_quantity = float(electricity_quantity.replace(' ', '').replace(',', '.'))
        return electricity_quantity
    else:
        return None

def main():
    nordpool_csv = 'nordpool.csv'
    adrese = pathlib.Path("invoices")
    visi_faili = list(adrese.glob("*.pdf"))

    data = []
    
    for f in range(len(visi_faili)):
        row = []
        pdf_file = PyPDF2.PdfReader(open(visi_faili[f], "rb"))
        page2 = pdf_file.pages[1]

        text2 = page2.extract_text()

        pos1 = text2.find("Apjoms Mērv. Cena,")
        per = text2[pos1 - 23:pos1]
        row.append(per)

        pdf_date = per.split("-")[0].strip()
        nordpool_price = nordpool_cenas(nordpool_csv, pdf_date)

        if nordpool_price is not None:
            row.append(nordpool_price)

            electricity_quantity = extract_electricity_quantity(text2)
            if electricity_quantity is not None:
                row.append(electricity_quantity)
            else:
                row.append(None)

            total_cost = float(per.split("EUR")[0].split()[-1].replace(',', '.'))

            if electricity_quantity is not None:
                savings_or_cost = total_cost - (electricity_quantity * nordpool_price)
            else:
                savings_or_cost = None

            if savings_or_cost is not None:
                if savings_or_cost > 0:
                    result = f"Savings: {savings_or_cost:.1f} EUR"
                elif savings_or_cost < 0:
                    result = f"Additional Costs: {abs(savings_or_cost):.1f} EUR"
                else:
                    result = "No Savings or Costs"
                row.append(result)
            else:
                row.append(None)

            data.append(row)

    print(tabulate(data, headers=["Periods", "Nordpool Price", "Electricity Quantity", "Savings / Costs"], tablefmt="github"))

if __name__ == "__main__":
    main()