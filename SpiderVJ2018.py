from json import decoder
from datetime import datetime

import requests
import sqlite3

def header():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
    return headers

def loginCrawler(url, data, header):    # 爬虫登陆
    login_url = url + r'/user/login'
    session = requests.session()
    session.post(login_url, data=data, headers=header())
    return session

flag = False    # 标记比赛密码，防止比赛密码错误导致死循环

def contestLogin(url, contest_id, session):     # 比赛登陆
    login_url = url + r'/contest/login/' + contest_id
    passwd = 'gongbutangjuan'
    data = {'password': passwd}
    session.post(login_url, data=data, headers=header())
    global flag
    flag = True
    contestCrawler(url, contest_id, session)

def contestCrawler(url, contest_id, session):   # 爬取比赛中的 rank 榜
    try:
        contest_url = url + r'/contest/rank/single/' + contest_id
        response = session.get(contest_url)
        response.raise_for_status()
        json_dict = response.json()

        time = json_dict['length'] / 1000
        submit = {}

        for sub in json_dict['submissions']:
            if sub[2] == 1:
                # 比赛成绩的 Rank
                if sub[3] <= time:
                    if not submit.get(str(sub[0])):
                        submit[str(sub[0])] = 1
                    else:
                        submit[str(sub[0])] += 1

        match_list = []
        for k, v in json_dict['participants'].items():
            if submit.get(k) and len(v[1]) >= 8:
                match_list.append((v[0], v[1], submit[k]))

        return match_list

    except decoder.JSONDecodeError:
        if not flag:
            contestLogin(url, contest_id, session)
        else:
            print("比赛密码错误，请更新数据库中比赛 id = " + contest_id + " 的密码")
            raise

def finalContest(url, contest_id, session): # 爬取补题后的 rank 榜
    contest_url = url + r'/contest/rank/single/' + contest_id
    response = session.get(contest_url)
    response.raise_for_status()
    json_dict = response.json()
    submit = {}
    for sub in json_dict['submissions']:
        if sub[2] == 1:
            # 获取补题后的 Rank
            if not submit.get(str(sub[0])):
                submit[str(sub[0])] = 1
            else:
                submit[str(sub[0])] += 1

    final_list = []
    for k, v in json_dict['participants'].items():
        if submit.get(k) and len(v[1]) >= 8:
            final_list.append((v[0], v[1], submit[k]))

    return final_list

def contestData(db_file):
    connect = sqlite3.connect(db_file, timeout=30)
    cursor = connect.cursor()
    sql = 'SELECT contest_id, is_gain, begin_date FROM vj_contest'
    contest = cursor.execute(sql)

    contest_dict = {}
    now_date = datetime.now().strftime('%Y-%m-%d')
    for info in contest:
        delta = now_date - datetime.strptime(info[2], '%Y-%m-%d')
        if 0 < delta.days <= 30:
            contest_dict[info[0]] = info[1]

    cursor.close()
    contest.close()
    return contest_dict


def database(db_file, info_list, flag):    # 存入数据库
    connect = sqlite3.connect(db_file, timeout=30)
    cursor = connect.cursor()
    sql = 'INSERT INTO '
    contest = cursor.execute(sql)

def main():
    url = r'https://cn.vjudge.net'
    data = {'username': 'sdutacm', 'password': 'sdutacm'}
    db_file = r'E:\Django\db.sqlite3'
    # contest = contestData(db_file)
    contest = {'242359': True}
    session = loginCrawler(url, data, header)
    for contest_id, is_gain in contest.items():
        try:
            if not is_gain:
                match_list = contestCrawler(url, contest_id, session)
                # database(db_file, match_list, True)
                print(match_list)
            final_list = finalContest(url, contest_id, session)
            print(final_list)
        except:
            print('发生未知错误！')

    # database(id, title, match_list, final_list)

if __name__ == "__main__":
    main()