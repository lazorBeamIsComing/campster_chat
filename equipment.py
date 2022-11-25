import os
import sys
import urllib.request
import json

from kocrawl.editor.base_editor import BaseEditor
import re

from kocrawl.answerer.base_answerer import BaseAnswerer

#EquipmentSearcher에서 사용-------------------------------------------------------------

client_id = "so4SUp0qUra21tmlGhLd"
client_secret = "pZT9M7IrIo"


#--------------------------------------------------------------------------------------


class EquipmentSearcher:

    def __init__(self):
        self.data_dict = {
            # 데이터를 담을 딕셔너리 구조를 정의합니다.
            'name': [], 'tel': [],
            'context': [], 'category': [],
            'address': [], 'thumUrl': []
        }

    def _make_query(self, category: str, brand: str) -> str:


        query = ' '.join([category, brand])
        #query = category

        print(query)
        return query

    def search_naver_shopping(self, location: str, travel: str):
        query = self._make_query(location, travel)

        encText = urllib.parse.quote(query)
        url = "https://openapi.naver.com/v1/search/shop?display=5&query=" + encText  # JSON 결과
        # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()

        data_dict = [{}]
        # 리스트 + 딕셔너리

        if (rescode == 200):
            response_body = response.read()
            # print(response_body.decode('utf-8'))
            json_data = json.loads(response_body.decode('utf-8'))
            if(len(json_data['items'])!= 0):
                for i in range(5):
                    temp_dict = {"title": json_data["items"][i]["title"],
                                 "link": json_data["items"][i]["link"],
                                 "image": json_data["items"][i]["image"],
                                 "lprice": json_data["items"][i]["lprice"],
                                 "category1": json_data["items"][i]["category1"],
                                 "category2": json_data["items"][i]["category2"],
                                 "category3": json_data["items"][i]["category3"],
                                 "brand": json_data["items"][i]["brand"]
                             }
                    data_dict.append(temp_dict)
            else:
                data_dict.append({"notfound": "해당 정보에 해당하는 물건이 없어요."})
            #print(data_dict[1].values())
            # print(response_body.decode('utf-8'))

        else:
            print("Error Code:" + rescode)

        return data_dict



class EquipmentEditor(BaseEditor):

    def edit_map(self, location: str, place: str, result: dict) -> dict:
        """
        join_dict를 사용하여 딕셔너리에 있는 string 배열들을
        하나의 string으로 join합니다.
        :param location: 지역
        :param place: 장소
        :param result: 데이터 딕셔너리
        :return: 수정된 딕셔너리
        """

        for i in range(5):

            result[i] = self.join_dict(result[i], "title")
            result[i] = self.join_dict(result[i], "link")
            result[i] = self.join_dict(result[i], "image")
            result[i] = self.join_dict(result[i], 'lprice')

            #if isinstance(result['context'], str):
                #result['context'] = re.sub(' ', ', ', result['context'])

        return result

class EquipmentAnswerer():

    def map_form(self, category: str, brand: str, result: list) -> tuple:
        """
        여행지 출력 포맷
        :param location: 지역
        :param place: 장소
        :param result: 데이터 딕셔너리
        :return: 출력 메시지
        """
        msg_tuple = ["", "",""]
        for i in range(3):

            result[i+1]['title'] = re.sub("<b>", "", result[i+1]['title'])
            result[i + 1]['title'] = re.sub("</b>", "", result[i + 1]['title'])

            msg = f"{result[i + 1]['category1']} - {result[i + 1]['category2']} - {result[i + 1]['category3']} \n"
            msg += f"\'{category}\' 카테고리의 {i + 1}번째 검색결과입니다.\n"
            msg += f"\'{result[i + 1]['brand']}\' 브랜드의 \n"
            msg += f"\'{result[i+1]['title']}\' \n"
            msg += f"최저가 : {result[i+1]['lprice']}원 \n"
            msg += f"바로가기 : {result[i+1]['link']}\n"
            msg += "{{"
            msg += result[i+1]['image']
            msg += "}} \n\n"
            msg_tuple[i] += msg

        return msg_tuple


class EquipmentCrawler:

    def request(self, category: str, brand: str) -> str:
        """
        지도를 크롤링합니다.
        (try-catch로 에러가 나지 않는 함수)
        :param category: 장비의 카테고리
        :param brand: 브랜드
        :return: 해당 장비
        """

        try:
            return self.request_debug(category, brand)

        except Exception:
            return "해당 장비는 알 수 없습니다."

    def request_debug(self, category: str, brand: str) -> tuple:
        result_dict = EquipmentSearcher().search_naver_shopping(category, brand)

        #result = EquipmentEditor().edit_map(category, brand, result_dict)
        if 'notfound' in result_dict[1].keys():
            return {
                'state':'NOT_FOUND',
                'answer':result_dict[1]['notfound']
            }

        #return result, result_dict
        temp_result = {
            'input': [],
            'intent': 'equipment',
            'entity': [],
            'state': 'SUCCESS',
            'answer': result_dict[1]
        }


        return temp_result