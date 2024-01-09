from urllib.parse import urlparse
import re
import requests
from bs4 import BeautifulSoup
import random
import whois
import pandas as pd
import joblib

user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]


def _nb_subdomains(url):
    parsed_url = urlparse(url)
    subdomain_number = parsed_url.netloc.split('.')[:-2]

    return len(subdomain_number)


def _path_extension(url):
    extensions_to_check = [".exe", ".html", ".pdf", ".txt"]

    parsed_url = urlparse(url)
    path = parsed_url.path

    for ext in extensions_to_check:
        if path.endswith(ext):
            return 1
    return 0


def _nb_redirection(url):
    max_redirects = 10
    current_url = url
    redirect_count = 0

    while redirect_count < max_redirects:
        try:
            response = requests.head(current_url, allow_redirects=False)
            if 300 <= response.status_code < 400:
                redirect_url = response.headers['Location']
                if not redirect_url.startswith("http"):
                    redirect_url = current_url + redirect_url
                current_url = redirect_url
                redirect_count += 1
            else:
                break
        except requests.exceptions.RequestException:
            break

    return redirect_count


def _req_feats(url):
    data = {
        "nb_hyperlinks": 0,
        "nb_extCSS": 0,
        "external_favicon": 0,
        "links_in_tags": 0,
        "ratio_intMedia": 0,
        "iframe": 0,
        "empty_title": 0,
        "domain_in_title": 0,
        "domain_with_copyright": 0,
        "whois_registered_domain": 0,
    }

    try:
        response = requests.get(url, headers={"User-Agent": random.choice(user_agents_list)})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        hyperlinks = soup.find_all('a')
        external_css_links = [link.get("href") for link in soup.find_all("link", rel="stylesheet")]
        favicon_link = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
        img_tags = soup.find_all('img')
        video_tags = soup.find_all('video')
        total_media_count = len(img_tags) + len(video_tags)
        img_count = len(img_tags)
        iframe_tags = soup.find_all('iframe')
        title_tag = soup.find('title')
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain_info = whois.whois(domain)

        if total_media_count > 0:
            media_ratio = (img_count / total_media_count) * 100
        else:
            media_ratio = 0

        if favicon_link:
            data["external_favicon"] = 1
        else:
            data["external_favicon"] = 0

        if iframe_tags:
            data["iframe"] = 1
        else:
            data["iframe"] = 0

        if title_tag:
            data["empty_title"] = 0
            title_text = title_tag.text.strip()

            if domain in title_text:
                data["domain_in_title"] = 1
            else:
                data["domain_in_title"] = 0
        else:
            data["empty_title"] = 1
            data["domain_in_title"] = 0

        if "©" in domain:
            data["domain_with_copyright"] = 1
        else:
            data["domain_with_copyright"] = 0

        if domain_info.status is not None:
            data["whois_registered_domain"] = 0
        else:
            data["whois_registered_domain"] = 1

        data["nb_hyperlinks"] = len(hyperlinks)
        data["links_in_tags"] = data["nb_hyperlinks"]
        data["nb_extCSS"] = len(external_css_links)
        data["ratio_intMedia"] = media_ratio

    except requests.exceptions.RequestException as e:
        global error
        error = str(e)
        print("Error occured")

    return data, error


def url_prep(url):
    data = {}
    url_tld_list = [".com", ".net", ".org", ".gov", ".edu", ".mil", ".int", ".co.uk", ".fr", ".de", ".jp"]
    shortening_services = {"bit.ly": r"bit\.ly/[\w\d]+", "t.co": r"t\.co/[\w\d]+"}
    ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    data["length_url"] = len(url)

    second_part = url.split("://")[1]
    hostname = second_part.split("/")[0]
    data["length_hostname"] = len(hostname)

    data["nb_dots"] = url.count(".")

    data["nb_hyphens"] = url.count("-")

    data["nb_at"] = url.count("@")

    data["nb_qm"] = url.count("?")
    data["nb_and"] = url.count("&")
    data["nb_eq"] = url.count("=")
    data["nb_tilde"] = url.count("~")
    data["nb_slash"] = url.count("/")
    data["nb_colon"] = url.count(":")
    data["nb_semicolumn"] = url.count(";")
    data["nb_www"] = url.count("www")
    data["nb_com"] = url.count("com")
    data["nb_dslash"] = url.count("//")

    http_number = url.count("http")
    https_number = url.count("https")
    data["http_in_path"] = http_number - https_number
    data["https_token"] = https_number

    num_count = 0
    char_count = 0

    url_split = url.split("://", 1)[1]
    for char in url_split:
        if char.isnumeric():
            num_count += 1
        elif char.isalpha():
            char_count += 1
    if char_count == 0:
        char_count += 1

    data["ratio_digits_url"] = num_count / char_count

    for tld in url_tld_list:
        if tld in url:
            data["tld_in_path"] = 1
            break
        else:
            data["tld_in_path"] = 0

    data["nb_subdomains"] = _nb_subdomains(url)

    for service, pattern in shortening_services.items():
        if re.search(pattern, url):
            data["shortening_service"] = 1
            break
        else:
            data["shortening_service"] = 0

    data["path_extension"] = _path_extension(url)

    if re.search(ip_pattern, url):
        data["ip"] = 1
    else:
        data["ip"] = 0

    data["nb_redirection"] = _nb_redirection(url)

    results, error = _req_feats(url)

    data.update(results)

    return data, error


model = joblib.load("model/phishing.pkl")

# phishing 1
# leg 0
