import requests
from bs4 import BeautifulSoup

def numberCrawler(url, data, header):

    response = requests.post(url, data=data, headers=header)
    return response

def data_processing(response):
    soup = BeautifulSoup(response.text, 'html.parser')

    tags = soup.tr.stripped_strings
    info_list = []
    info_str = ''
    for i, tag in enumerate(tags):
        if i > 15:
            if (i-15) % 9 != 1 and (i-15) % 9 != 0:
                info_str += tag + '|'
            if (i-15) % 9 == 0:
                info_str += tag
                info_list.append(info_str)
                info_str = ''

    return  info_list

def main():
    file = r'E:\SDUT_students'
    url = r'http://210.44.176.116/cjcx/xhcx_list.php'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

    shool_num = [151, 161, 171]
    for num in shool_num:
        data = {'post_xuehao': num}
        response = numberCrawler(url, data, header)
        text_list = data_processing(response)
        text = '\n'.join(text_list)
        with open(file, 'a+') as f:
            f.write(text)

if __name__ == '__main__':
    main()