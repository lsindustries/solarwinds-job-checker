import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import sleep

# Adres email na który będą wysyłane powiadomienia
# CONFIG
TO_EMAIL = '' # adres.email@do.ktorego.wysylamy.powiadomienia
SMTP_SERV = '' # adres smtp np smtp.gmail.com
SMTP_EMAIL = '' # adres.email.z.ktorego.wysylamy.powiadomienia
PASSWRD = '' # haslo.do.tego.konta

filename = 'jobs.txt'
url = 'https://jobs.solarwinds.com'

HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }


def file_creator():
    try:
        # Try to open the file for reading
        with open(filename, "r") as file:
            pass
    except FileNotFoundError:
        # If the file doesn't exist, create it
        with open(filename, "w") as file:
            print(f"File '{filename}' created successfully!")


# Funkcja do pobierania aktualnych ofert dla Krakowa
def scrape_jobs():
    url = 'https://jobs.solarwinds.com/jobs/?sw-search=&sw-locations%5B%5D=Krakow%2C+Poland'

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = soup.find_all('tr', {'class': 'job'})
    job_data = []
    for job in jobs:
        title = job.find('td', {'class': 'title'}).text.strip().split("\n")[0].strip()
        location = job.find('p', {'class': 'value'}).text.strip()
        job_id = job.find('td', {'class': 'title'}).text.split(":")[1].strip()
        link = job.find('a')['href']
        job_data.append({'title': title, 'location': location, 'job_id': job_id, 'link': link})
    return job_data


def job_details(url):
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    [div.decompose() for div in soup.find_all("div", {"class": ["content-intro", "content-conclusion"]})]

    job_description = soup.find("div", {"class": "desc"})

    return job_description


# Funkcja do zapisywania danych do pliku
def save_data(job):
    with open(filename, 'a') as file:
        file.write(f"{job['title']}\t{job['location']}\t{job['job_id']}\t{job['link']}\n")


# Funkcja do sprawdzania, czy oferta już istnieje
def is_job_new(job):
    with open(filename, 'r') as file:
        for line in file:
            title, location, job_id, link = line.strip().split('\t')
            if job['title'] == title and job['location'] == location and job['link'] == link and job[
                'job_id'] == job_id:
                return False
    return True


# Funkcja do wysyłania emaili
def send_email(new_jobs):
    if not new_jobs:
        return

    body = '<html><body><h2 style="color:red;">Nowe oferty pracy:</h2>\n\n' + '\n\n'.join(f"""
    <h3>{job['title']} - {job['location']}</h3>\n
    <div style='border-top: 1px solid #c0c0c0;'><p>{url+job['link']}</p>\n
    {job_details(url+job['link'])}</div></body></html>""" for job in new_jobs)
    message = MIMEMultipart()
    message['Subject'] = 'Nowe oferty pracy na SolarWinds Jobs'
    message['From'] = SMTP_EMAIL
    message['To'] = TO_EMAIL
    html_body = MIMEText(body, "html")
    message.attach(html_body)
    with smtplib.SMTP(SMTP_SERV, 587) as smtp:
        smtp.starttls()
        smtp.login(SMTP_EMAIL, PASSWRD)
        smtp.send_message(message)


def main():
    file_creator()
    jobs = scrape_jobs()
    new_jobs = [job for job in jobs if is_job_new(job)]
    if new_jobs:
        [save_data(job) for job in new_jobs]
        send_email(new_jobs)
    print(f"Task done... {len(new_jobs)} new offers found")
    sleep(5)


if __name__ == "__main__":
    main()
