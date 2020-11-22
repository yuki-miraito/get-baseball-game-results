import requests
from bs4 import BeautifulSoup
import re
import json
import sys

# 引数で日時を取得
args = sys.argv
if 2 == len(args):
    pattern = r'[12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])'
    is_date = re.match(pattern, args[1])
    if is_date:
        date = args[1]
    else:
        print('「2020-01-01」の形式で指定してください。')
        sys.exit()
else:
    print("日時を1つだけ指定してください。")
    sys.exit()

# 日時指定した時のurl
# https://baseball.yahoo.co.jp/npb/schedule/?date=2020-07-02
base_url = "https://baseball.yahoo.co.jp/npb/schedule/"
match_date = "?date=" + date
match_date_page_url = base_url + match_date
match_date_page_res = requests.get(match_date_page_url)

match_date_page = BeautifulSoup(match_date_page_res.content, "html.parser")
bb_scores = match_date_page.find_all("section", class_="bb-score")

print("======================================================")

for bb_score in bb_scores:

    # 試合がない日は処理を終える
    no_data = bb_score.find("p", class_="bb-noData")
    if no_data is not None and no_data.string == "試合はありません":
        print("■ " + "2020-11-11の" + no_data.string)
        print("======================================================")
        sys.exit()

    bb_score_title = bb_score.find("h1", class_="bb-socore__title").string
    bb_score_items = bb_score.find_all("li", class_="bb-score__item")

    if bb_score_title == "セ・リーグ":
        central_league_score_items = bb_score_items
    elif bb_score_title == "パ・リーグ":
        pacific_league_score_items = bb_score_items
    else:
        print("データに不整合があります。")
        sys.exit()

def crawling_score_items(score_items):
    for score_item in score_items:
        result_page_url = score_item.find_next("a").get('href')
        result_page_res = requests.get(result_page_url)
        result_page = BeautifulSoup(result_page_res.content, "html.parser")
        bb_main = result_page.find("div", class_="bb-main")

        # 試合日時
        match_date_label = bb_main.find("h1", class_="bb-head01__title").find_next("a").string
        print("■ 試合日")
        print(match_date_label)
        # 球場
        baseball_stadium = bb_main.find("p", class_="bb-gameDescription").text
        print("■ 球場")
        print(baseball_stadium)

        # 試合中止の場合の処理
        game_stats = bb_main.find("span", class_="bb-gameCard__state").string
        game_stats = ''.join(game_stats.split())
        if game_stats != "試合終了":
            team = bb_main.find("h1", class_="bb-head01__title").find("span").string
            reason_for_cancel = bb_main.find("p", class_="bb-paragraph")
            reason_for_cancel = "---" if reason_for_cancel is None else reason_for_cancel.string
            print("■ 対戦チーム")
            print(team)
            print("■ " + game_stats)
            print(reason_for_cancel)
            print("======================================================")
            continue

        # チーム
        score_board = bb_main.find("table", id="ing_brd").find("tbody").find_all("tr")
        first_team = score_board[0].find("td", class_="bb-gameScoreTable__data--team").find_next("a").string
        print("■ 先攻チーム")
        print(first_team)
        second_team = score_board[1].find("td", class_="bb-gameScoreTable__data--team").find_next("a").string
        print("■ 後攻チーム")
        print(second_team)

        # イニング回数
        inning_count = 0
        for score_board_row in score_board:
            scores = score_board_row.find_all("td", class_="bb-gameScoreTable__data")
            for score in scores:
                score_number = score.find(class_="bb-gameScoreTable__score")
                if score_number is None:
                    continue
                elif score_number.string == "X":
                    break
                else:
                    inning_count += 1

        end_of_match = {
            18: "9回裏",
            17: "9回表",
            16: "8回裏",
            15: "8回表",
            14: "7回裏",
            13: "7回表",
            12: "6回裏",
            11: "6回表",
            10: "5回裏",
            9: "5回表",
            8: "4回裏",
            7: "4回表",
            6: "3回裏",
            5: "3回表",
            4: "2回裏",
            3: "2回表",
            2: "1回裏",
            1: "1回表"
        }
        print("■ 試合終了")
        print(end_of_match[inning_count])
        print("■ 回数")
        print(inning_count)

        # 先攻チームスコア
        first_team_score = bb_main.find("span", class_="bb-gameTeam__awayScore").string
        print("■ 先攻チーム得点")
        print(first_team_score)
        # 後攻チームスコア
        second_team_score = bb_main.find("span", class_="bb-gameTeam__homeScore").string
        print("■ 後攻チーム得点")
        print(second_team_score)
        # 合計スコア
        total_score = int(first_team_score) + int(second_team_score)
        print("■ 合計得点")
        print(total_score)

        contents = bb_main.find_all(class_="bb-modCommon01")
        for content in contents:
            bb_head_title = content.find("h1", class_="bb-head02__title")
            if bb_head_title is None:
                continue
            elif bb_head_title.text == "審判":
                # 審判名
                # <br>が存在するので出力する時は .text
                referee_types_tag = content.find_all("th", class_="bb-tableLeft__head")
                referee_types = [referee_type.text for referee_type in referee_types_tag]
                referees_tag = content.find_all("td", class_="bb-tableLeft__data")
                referees = [referee.string for referee in referees_tag]
                print("■ 審判名")
                for i in range(len(referee_types)):
                    print(referee_types[i] + ": " + referees[i])
                print("======================================================")
                break
            else:
                continue

# セ・リーグの試合を繰り返し
print("------------------------------------------------------")
print("▼ セ・リーグ")
print("------------------------------------------------------")
crawling_score_items(central_league_score_items)
# パ・リーグの試合を繰り返し
print("------------------------------------------------------")
print("▼ パ・リーグ")
print("------------------------------------------------------")
crawling_score_items(pacific_league_score_items)
