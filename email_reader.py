# pylint: disable=missing-function-docstring,missing-module-docstring
import io
import re

def convert_to_seconds(timestamp):
    if timestamp == '':
        return 0
    secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(timestamp.split('.'))))
    return secs


def parse_email(mail):
    try:
        url = re.match("(https?://[^\s]+)", mail).group(0)
        url = re.sub("&list=.*", "", url)
        till = re.match(".*till ([0-9]{1,2}.[0-9]{1,2})", mail)
        if till is None:
            till = 0
        else:
            till = till.group(1)
            till = convert_to_seconds(till)
        return url, till
    except:
        return  "",0


def read_email():
    email_content = []
    print("Paste the email below:")
    try:
        while True:
            line = input()
            email_content.append(line)
    except KeyboardInterrupt:
        pass

    return email_content


def print_found_urls(urls, logger):
    logger.info(f"1. Found the following URIs, {len(urls)} in total:")
    for i in urls:
        logger.info(i)


def parse_all_email_lines(email_content):
    urls = []
    for line in email_content:
        with io.open('email.txt', 'a', encoding='utf-8') as f:
            f.write(line + "\n")
        url, till = parse_email(line)
        if url != '':
            urls.append((url, till))
    return urls


def find_urls_in_email(email_content, logger):
    urls = parse_all_email_lines(email_content)
    #urls = list(filter(None, urls))
    for url in urls:
        logger.info("Downloading %s", url)
    return urls


def get_urls_in_email(logger):
    email_content = read_email()
    urls = find_urls_in_email(email_content, logger)
    print_found_urls(urls, logger)
    return urls
