# Korean Sentence Splitter
# Split Korean text into sentences using heuristic algorithm.
#
# Copyright (C) 2021 Hyun-Woong Ko <kevin.ko@tunib.ai> and Sang-Kil Park <skpark1224@hyundai.com>
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

from collections import defaultdict
from typing import Any
from kss._emoji import _emojis


class Stats(object):
    DEFAULT: int = 0
    DA_EOJEOL: int = 1
    DA_MORPH: int = 2
    YO: int = 3
    JYO: int = 4
    SB: int = 5
    COMMON: int = 6
    EOMI: int = 7


class ID(object):
    NONE: int = 0
    PREV: int = 1 << 0
    CONT: int = 1 << 1
    NEXT: int = 1 << 2
    NEXT1: int = 1 << 3
    NEXT2: int = 1 << 4


yo = {
    "가",
    "감",
    "개",
    "걔",
    "걘",
    "괴",
    "까",
    "깨",
    "껴",
    "꿈",
    "꿔",
    "꿰",
    "끔",
    "낌",
    "나",
    "남",
    "내",
    "냄",
    "놂",
    "놔",
    "눠",
    "늚",
    "대",
    "댐",
    "데",
    "돼",
    "되",
    "됨",
    "둠",
    "듦",
    "듬",
    "따",
    "땀",
    "떠",
    "떼",
    "뜀",
    "뜸",
    "띔",
    "매",
    "메",
    "배",
    "베",
    "봬",
    "뵈",
    "빎",
    "빔",
    "빪",
    "뺌",
    "삠",
    "사",
    "삶",
    "삼",
    "새",
    "서",
    "세",
    "셈",
    "싸",
    "쌈",
    "쌔",
    "써",
    "썲",
    "쎄",
    "쏨",
    "쏴",
    "쓺",
    "씀",
    "앎",
    "암",
    "얘",
    "얜",
    "엶",
    "옮",
    "옴",
    "와",
    "왜",
    "자",
    "재",
    "잼",
    "쟤",
    "쟨",
    "젊",
    "져",
    "졺",
    "줌",
    "줘",
    "짜",
    "째",
    "쪄",
    "쬠",
    "찜",
    "차",
    "채",
    "쳐",
    "춤",
    "춰",
    "캐",
    "커",
    "켜",
    "켬",
    "킴",
    "타",
    "탐",
    "터",
    "텨",
    "튐",
    "틈",
    "팜",
    "패",
    "퍼",
    "펌",
    "펴",
    "폄",
    "품",
    "핌",
    "함",
    "해",
}

jyo = {
    "가",
    "갉",
    "갔",
    "갖",
    "같",
    "갚",
    "개",
    "걔",
    "걷",
    "걸",
    "검",
    "겪",
    "골",
    "곪",
    "곱",
    "괴",
    "굵",
    "굶",
    "굼",
    "굽",
    "긁",
    "긋",
    "길",
    "깊",
    "깎",
    "깠",
    "깨",
    "깼",
    "꺾",
    "껐",
    "꼈",
    "꼽",
    "꽂",
    "꾸",
    "꿇",
    "꿨",
    "꿰",
    "뀌",
    "끊",
    "끌",
    "끓",
    "끼",
    "낚",
    "날",
    "낡",
    "남",
    "났",
    "낮",
    "내",
    "냈",
    "넓",
    "넘",
    "넣",
    "녹",
    "놀",
    "높",
    "놓",
    "놨",
    "누",
    "눕",
    "늙",
    "늦",
    "닦",
    "닫",
    "달",
    "닮",
    "닳",
    "답",
    "닿",
    "대",
    "댔",
    "덜",
    "덥",
    "덮",
    "데",
    "뎄",
    "돋",
    "돌",
    "돕",
    "돼",
    "됐",
    "되",
    "두",
    "뒀",
    "듣",
    "들",
    "딛",
    "딪",
    "따",
    "땄",
    "땋",
    "땠",
    "떨",
    "떴",
    "떼",
    "뛰",
    "뜨",
    "뜯",
    "띄",
    "띠",
    "막",
    "많",
    "말",
    "맑",
    "맞",
    "맡",
    "매",
    "맵",
    "맸",
    "맺",
    "먹",
    "멀",
    "메",
    "멨",
    "몰",
    "묵",
    "묶",
    "묻",
    "묽",
    "뭍",
    "믿",
    "밀",
    "밉",
    "박",
    "받",
    "밝",
    "밟",
    "배",
    "뱄",
    "뱉",
    "벌",
    "벗",
    "베",
    "보",
    "볶",
    "봤",
    "봬",
    "뵀",
    "뵈",
    "붇",
    "불",
    "붉",
    "붓",
    "붙",
    "비",
    "빌",
    "빚",
    "빨",
    "빻",
    "빼",
    "뺐",
    "뻗",
    "뻤",
    "뼜",
    "사",
    "살",
    "삵",
    "샀",
    "새",
    "샌",
    "샛",
    "샜",
    "서",
    "섞",
    "섰",
    "세",
    "셌",
    "속",
    "솎",
    "솟",
    "숨",
    "쉬",
    "쉽",
    "시",
    "식",
    "싣",
    "싫",
    "싶",
    "싸",
    "쌌",
    "쌓",
    "쌔",
    "쌨",
    "써",
    "썩",
    "썰",
    "썼",
    "쎄",
    "쏘",
    "쏟",
    "쏴",
    "쐈",
    "쑤",
    "쓰",
    "쓸",
    "씌",
    "씹",
    "앉",
    "않",
    "알",
    "앓",
    "약",
    "얇",
    "얕",
    "얘",
    "얹",
    "얻",
    "얼",
    "없",
    "엎",
    "엮",
    "열",
    "옅",
    "옛",
    "오",
    "온",
    "옭",
    "옮",
    "옳",
    "와",
    "왔",
    "울",
    "읊",
    "일",
    "읽",
    "잃",
    "입",
    "있",
    "잊",
    "자",
    "작",
    "잡",
    "잤",
    "잦",
    "재",
    "잰",
    "쟀",
    "쟤",
    "적",
    "절",
    "젊",
    "접",
    "젓",
    "졌",
    "졸",
    "좇",
    "좋",
    "주",
    "죽",
    "줍",
    "줬",
    "쥐",
    "지",
    "질",
    "집",
    "짓",
    "짖",
    "짙",
    "짜",
    "짧",
    "짰",
    "째",
    "쨌",
    "쩔",
    "쪘",
    "쬐",
    "찌",
    "찍",
    "찐",
    "찝",
    "찢",
    "차",
    "찼",
    "찾",
    "채",
    "챘",
    "쳐",
    "쳤",
    "추",
    "춥",
    "춰",
    "췄",
    "치",
    "캐",
    "캤",
    "커",
    "컸",
    "켜",
    "켠",
    "켰",
    "크",
    "키",
    "타",
    "탔",
    "터",
    "튀",
    "트",
    "파",
    "팔",
    "팠",
    "패",
    "팼",
    "펐",
    "펴",
    "폈",
    "피",
    "하",
    "핥",
    "했",
    "휘",
    "희",
}

ham = {
    "리",
    "절",
    "용",
    "편",
    "륭",
    "듯",
    "야",
    "족",
    "못",
    "끗",
    "안",
    "천",
    "정",
    "각",
    "실",
    "소",
    "끔",
    "분",
    "이",
    "약",
}

um = {
    "았",
    "었",
    "했",
    "없",
    "좋",
    "있",
    "웠",
    "였",
    "않",
    "같",
    "많",
    "적",
    "겠",
    "찮",
    "났",
    "좁",
    "작",
    "싶",
    "셨",
    "졌",
    "좁",
    "넓",
}


before = {
    # 조사
    "이",
    "가",
    "에서",
    "은",
    "는",
    "을",
    "를",
    "도",
    "에",
    "게",
    "께",
    "한테",
    "로",
    "써",
    "와",
    "과",
    "랑",
    "까지",
    "부터",
    "뿐",
    "만",
    "따라",
    "토록",
    "도록",
    "든지",
    "던지",
    "란",
    "만큼",
    "만치",
    "때",
    # 부사
    "너무",
    "잘",
    "못",
    "빨리",
    "매우",
    "몹시",
    "별로",
    "아까",
    "내일",
    "일찍",
    "금방",
    "이미",
    "이리",
    "저리",
    "아니",
    "과연",
    "설마",
    "제발",
    "정말",
    "결코",
    "가득",
    "히",
    # 대명사
    "나",
    "저",
    "우리",
    "저희",
    "너",
    "너희",
    "당신",
    "그대",
    "그",
    "그녀",
    "분",
    "놈",
    "거",
    "것",
    "여기",
    "저기",
    "쪽",
    "곳",
    "님",
}


def create_dict(d, default: Any = 0):
    return defaultdict(lambda: default, d)


Table = create_dict(
    {
        Stats.DA_EOJEOL:
        # EC, EF 주의 !!
        create_dict(
            {
                "갔": ID.PREV,
                "간": ID.PREV,
                "겠": ID.PREV,
                "겼": ID.PREV,
                "같": ID.PREV,
                "놨": ID.PREV,
                "녔": ID.PREV,
                "니": ID.PREV,
                "논": ID.PREV,
                "낸": ID.PREV,
                "냈": ID.PREV,
                "뒀": ID.PREV,
                "때": ID.PREV,
                "랐": ID.PREV,
                "럽": ID.PREV,
                "렵": ID.PREV,
                "렸": ID.PREV,
                "뤘": ID.PREV,
                "몄": ID.PREV,
                "밌": ID.PREV,
                "볐": ID.PREV,
                "볍": ID.PREV,
                "봤": ID.PREV,
                "섰": ID.PREV,
                "샜": ID.PREV,
                "셨": ID.PREV,
                "싼": ID.PREV,
                "싸": ID.PREV,
                "않": ID.PREV,
                "았": ID.PREV,
                "없": ID.PREV,
                "었": ID.PREV,
                "였": ID.PREV,
                "온": ID.PREV,
                "웠": ID.PREV,
                "이": ID.PREV,
                "인": ID.PREV,
                "있": ID.PREV,
                "진": ID.PREV,
                "졌": ID.PREV,
                "쳤": ID.PREV,
                "췄": ID.PREV,
                "챘": ID.PREV,
                "켰": ID.PREV,
                "켠": ID.PREV,
                "팠": ID.PREV,
                "펐": ID.PREV,
                "폈": ID.PREV,
                "했": ID.PREV,
                "혔": ID.PREV,
                "한": ID.NEXT,
                "가": ID.NEXT,
                "고": ID.NEXT | ID.NEXT2,
                "는": ID.NEXT | ID.NEXT2,
                "라": ID.NEXT,
                "시": ID.NEXT,
                "등": ID.NEXT,
                "던": ID.NEXT,
                "든": ID.NEXT,
                "지": ID.NEXT2,
                "를": ID.NEXT,
                "운": ID.NEXT,  # ~ 다운
                "만": ID.NEXT,  # ~ 하다만
                "며": ID.NEXT | ID.NEXT2,
                "면": ID.NEXT | ID.NEXT1 | ID.NEXT2,
                "서": ID.NEXT2,
                "싶": ID.PREV | ID.NEXT,
                "죠": ID.NEXT,
                "죵": ID.NEXT,
                "쥬": ID.NEXT,
                "하": ID.NEXT1,
                "해": ID.NEXT1,
                "도": ID.NEXT2,
                "": ID.NONE,
            }
        ),
        Stats.DA_MORPH:
        # EC, EF 주의 !!
        create_dict(
            {
                "간": ID.PREV,
                "갈": ID.PREV,
                "갉": ID.PREV,
                "감": ID.PREV,
                "갔": ID.PREV,
                "같": ID.PREV,
                "갚": ID.PREV,
                "개": ID.PREV,
                "걔": ID.PREV,
                "건": ID.PREV,
                "검": ID.PREV,
                "겪": ID.PREV,
                "곤": ID.PREV,
                "골": ID.PREV,
                "곪": ID.PREV,
                "곱": ID.PREV,
                "괴": ID.PREV,
                "군": ID.PREV,
                "굵": ID.PREV,
                "굶": ID.PREV,
                "굽": ID.PREV,
                "긁": ID.PREV,
                "긋": ID.PREV,
                "길": ID.PREV,
                "깊": ID.PREV,
                "까": ID.PREV,
                "깎": ID.PREV,
                "깐": ID.PREV,
                "깠": ID.PREV,
                "깨": ID.PREV,
                "깬": ID.PREV,
                "깼": ID.PREV,
                "꺾": ID.PREV,
                "껐": ID.PREV,
                "꼈": ID.PREV,
                "꼬": ID.PREV,
                "꼽": ID.PREV,
                "꽂": ID.PREV,
                "꾸": ID.PREV,
                "꾼": ID.PREV,
                "꿨": ID.PREV,
                "꿰": ID.PREV,
                "끼": ID.PREV,
                "낀": ID.PREV,
                "나": ID.PREV,
                "낚": ID.PREV,
                "난": ID.PREV,
                "날": ID.PREV,
                "낡": ID.PREV,
                "남": ID.PREV,
                "났": ID.PREV,
                "낮": ID.PREV,
                "내": ID.PREV,
                "낸": ID.PREV,
                "냈": ID.PREV,
                "넓": ID.PREV,
                "넘": ID.PREV,
                "넣": ID.PREV,
                "녹": ID.PREV,
                "논": ID.PREV,
                "놀": ID.PREV,
                "높": ID.PREV,
                "놓": ID.PREV,
                "놨": ID.PREV,
                "누": ID.PREV,
                "눈": ID.PREV,
                "눕": ID.PREV,
                "늘": ID.PREV,
                "늙": ID.PREV,
                "늦": ID.PREV,
                "닦": ID.PREV,
                "단": ID.PREV,
                "닫": ID.PREV,
                "달": ID.PREV,
                "닮": ID.PREV,
                "닳": ID.PREV,
                "담": ID.PREV,
                "답": ID.PREV,
                "닿": ID.PREV,
                "대": ID.PREV,
                "댄": ID.PREV,
                "댔": ID.PREV,
                "덜": ID.PREV,
                "덥": ID.PREV,
                "덮": ID.PREV,
                "데": ID.PREV,
                "덴": ID.PREV,
                "뎄": ID.PREV,
                "돈": ID.PREV,
                "돋": ID.PREV,
                "돌": ID.PREV,
                "돕": ID.PREV,
                "돼": ID.PREV,
                "됐": ID.PREV,
                "되": ID.PREV,
                "된": ID.PREV,
                "두": ID.PREV,
                "둔": ID.PREV,
                "둠": ID.PREV,
                "뒀": ID.PREV,
                "듣": ID.PREV,
                "들": ID.PREV,
                "딛": ID.PREV,
                "딪": ID.PREV,
                "따": ID.PREV,
                "딴": ID.PREV,
                "땄": ID.PREV,
                "땋": ID.PREV,
                "땠": ID.PREV,
                "떨": ID.PREV,
                "떴": ID.PREV,
                "떼": ID.PREV,
                "뗀": ID.PREV,
                "뛰": ID.PREV,
                "뜨": ID.PREV,
                "뜯": ID.PREV,
                "띄": ID.PREV,
                "띈": ID.PREV,
                "띠": ID.PREV,
                "막": ID.PREV,
                "많": ID.PREV,
                "말": ID.PREV,
                "맑": ID.PREV,
                "맞": ID.PREV,
                "맡": ID.PREV,
                "매": ID.PREV,
                "맨": ID.PREV,
                "맵": ID.PREV,
                "맸": ID.PREV,
                "맺": ID.PREV,
                "먹": ID.PREV,
                "멀": ID.PREV,
                "메": ID.PREV,
                "멘": ID.PREV,
                "멨": ID.PREV,
                "몬": ID.PREV,
                "몰": ID.PREV,
                "묵": ID.PREV,
                "묶": ID.PREV,
                "묻": ID.PREV,
                "물": ID.PREV,
                "묽": ID.PREV,
                "뭍": ID.PREV,
                "뭘": ID.PREV,
                "민": ID.PREV,
                "믿": ID.PREV,
                "밀": ID.PREV,
                "밉": ID.PREV,
                "박": ID.PREV,
                "받": ID.PREV,
                "밝": ID.PREV,
                "밟": ID.PREV,
                "배": ID.PREV,
                "밴": ID.PREV,
                "뱄": ID.PREV,
                "뱉": ID.PREV,
                "번": ID.PREV,
                "벌": ID.PREV,
                "벗": ID.PREV,
                "베": ID.PREV,
                "벤": ID.PREV,
                "보": ID.PREV,
                "볶": ID.PREV,
                "본": ID.PREV,
                "봤": ID.PREV,
                "봬": ID.PREV,
                "뵀": ID.PREV,
                "뵈": ID.PREV,
                "뵌": ID.PREV,
                "분": ID.PREV,
                "붇": ID.PREV,
                "불": ID.PREV,
                "붉": ID.PREV,
                "붓": ID.PREV,
                "붙": ID.PREV,
                "비": ID.PREV,
                "빈": ID.PREV,
                "빌": ID.PREV,
                "빚": ID.PREV,
                "빤": ID.PREV,
                "빨": ID.PREV,
                "빻": ID.PREV,
                "빼": ID.PREV,
                "뺀": ID.PREV,
                "뺐": ID.PREV,
                "뻗": ID.PREV,
                "뻤": ID.PREV,
                "뼜": ID.PREV,
                "삔": ID.PREV,
                "사": ID.PREV,
                "산": ID.PREV,
                "살": ID.PREV,
                "삵": ID.PREV,
                "샀": ID.PREV,
                "새": ID.PREV,
                "샌": ID.PREV,
                "샜": ID.PREV,
                "섞": ID.PREV,
                "선": ID.PREV,
                "섰": ID.PREV,
                "세": ID.PREV,
                "셌": ID.PREV,
                "속": ID.PREV,
                "솎": ID.PREV,
                "솟": ID.PREV,
                "숨": ID.PREV,
                "수": ID.PREV,  # ~ 했수다.
                "쉬": ID.PREV,
                "쉰": ID.PREV,
                "쉽": ID.PREV,
                "식": ID.PREV,
                "싣": ID.PREV,
                "싫": ID.PREV,
                "싸": ID.PREV,
                "싼": ID.PREV,
                "쌌": ID.PREV,
                "쌓": ID.PREV,
                "쌔": ID.PREV,
                "쌨": ID.PREV,
                "썩": ID.PREV,
                "썰": ID.PREV,
                "썼": ID.PREV,
                "쎄": ID.PREV,
                "쏘": ID.PREV,
                "쏜": ID.PREV,
                "쏟": ID.PREV,
                "쐈": ID.PREV,
                "쓰": ID.PREV,
                "쓴": ID.PREV,
                "쓸": ID.PREV,
                "씹": ID.PREV,
                "안": ID.PREV,
                "앉": ID.PREV,
                "않": ID.PREV,
                "알": ID.PREV,
                "앓": ID.PREV,
                "약": ID.PREV,
                "얇": ID.PREV,
                "얕": ID.PREV,
                "얘": ID.PREV,
                "언": ID.PREV,
                "얹": ID.PREV,
                "얻": ID.PREV,
                "얼": ID.PREV,
                "없": ID.PREV,
                "엎": ID.PREV,
                "엮": ID.PREV,
                "연": ID.PREV,
                "열": ID.PREV,
                "옅": ID.PREV,
                "오": ID.PREV,
                "온": ID.PREV,
                "옭": ID.PREV,
                "옳": ID.PREV,
                "왔": ID.PREV,
                "울": ID.PREV,
                "읊": ID.PREV,
                "일": ID.PREV,
                "읽": ID.PREV,
                "잃": ID.PREV,
                "입": ID.PREV,
                "있": ID.PREV,
                "잊": ID.PREV,
                "자": ID.PREV,
                "작": ID.PREV,
                "잔": ID.PREV,
                "잡": ID.PREV,
                "잤": ID.PREV,
                "잦": ID.PREV,
                "재": ID.PREV,
                "잰": ID.PREV,
                "쟀": ID.PREV,
                "쟤": ID.PREV,
                "적": ID.PREV,
                "전": ID.PREV,
                "절": ID.PREV,
                "젊": ID.PREV,
                "접": ID.PREV,
                "젓": ID.PREV,
                "졌": ID.PREV,
                "존": ID.PREV,
                "졸": ID.PREV,
                "좁": ID.PREV,
                "좋": ID.PREV,
                "주": ID.PREV,
                "죽": ID.PREV,
                "준": ID.PREV,
                "줍": ID.PREV,
                "줬": ID.PREV,
                "쥐": ID.PREV,
                "진": ID.PREV,
                "질": ID.PREV,
                "집": ID.PREV,
                "짓": ID.PREV,
                "짖": ID.PREV,
                "짙": ID.PREV,
                "짜": ID.PREV,
                "짧": ID.PREV,
                "짰": ID.PREV,
                "째": ID.PREV,
                "짼": ID.PREV,
                "쨌": ID.PREV,
                "쩐": ID.PREV,
                "쩔": ID.PREV,
                "쪘": ID.PREV,
                "쫀": ID.PREV,
                "쬐": ID.PREV,
                "찌": ID.PREV,
                "찍": ID.PREV,
                "찐": ID.PREV,
                "찝": ID.PREV,
                "찢": ID.PREV,
                "차": ID.PREV,
                "찬": ID.PREV,
                "참": ID.PREV,
                "찼": ID.PREV,
                "찾": ID.PREV,
                "채": ID.PREV,
                "챈": ID.PREV,
                "챘": ID.PREV,
                "쳤": ID.PREV,
                "추": ID.PREV,
                "춘": ID.PREV,
                "춥": ID.PREV,
                "췄": ID.PREV,
                "치": ID.PREV,
                "친": ID.PREV,
                "캐": ID.PREV,
                "캤": ID.PREV,
                "컸": ID.PREV,
                "켜": ID.PREV,
                "켠": ID.PREV,
                "켰": ID.PREV,
                "크": ID.PREV,
                "키": ID.PREV,
                "킨": ID.PREV,
                "타": ID.PREV,
                "탄": ID.PREV,
                "탔": ID.PREV,
                "튀": ID.PREV,
                "튄": ID.PREV,
                "트": ID.PREV,
                "튼": ID.PREV,
                "파": ID.PREV,
                "팔": ID.PREV,
                "팠": ID.PREV,
                "패": ID.PREV,
                "팼": ID.PREV,
                "펐": ID.PREV,
                "펴": ID.PREV,
                "편": ID.PREV,
                "폈": ID.PREV,
                "푼": ID.PREV,
                "품": ID.PREV,
                "피": ID.PREV,
                "핀": ID.PREV,
                "핥": ID.PREV,
                "했": ID.PREV,
                "헌": ID.PREV,
                "휘": ID.PREV,
                "희": ID.PREV,
                "겠": ID.PREV,
                "겼": ID.PREV,
                "녔": ID.PREV,
                "니": ID.PREV,
                "때": ID.PREV,
                "랐": ID.PREV,
                "럽": ID.PREV,
                "렵": ID.PREV,
                "렸": ID.PREV,
                "뤘": ID.PREV,
                "몄": ID.PREV,
                "밌": ID.PREV,
                "볐": ID.PREV,
                "볍": ID.PREV,
                "셨": ID.PREV,
                "았": ID.PREV,
                "었": ID.PREV,
                "였": ID.PREV,
                "웠": ID.PREV,
                "이": ID.PREV,
                "인": ID.PREV,
                "혔": ID.PREV,
                "한": ID.NEXT,
                "가": ID.PREV | ID.NEXT,
                "고": ID.NEXT | ID.NEXT2,
                "구": ID.NEXT | ID.NEXT2,
                "는": ID.NEXT | ID.NEXT2,
                "라": ID.NEXT,
                "시": ID.PREV | ID.NEXT,
                "등": ID.NEXT,
                "던": ID.PREV | ID.NEXT,
                "든": ID.PREV | ID.NEXT,
                "지": ID.PREV | ID.NEXT2,
                "를": ID.NEXT,
                "운": ID.PREV | ID.NEXT,  # ~ 다운
                "만": ID.NEXT,
                "며": ID.NEXT | ID.NEXT2,
                "면": ID.NEXT | ID.NEXT1 | ID.NEXT2,
                "서": ID.PREV | ID.NEXT2,
                "싶": ID.PREV | ID.NEXT,
                "죠": ID.NEXT,
                "죵": ID.NEXT,
                "쥬": ID.NEXT,
                "하": ID.PREV | ID.NEXT1,
                "거": ID.PREV | ID.NEXT,
                "해": ID.NEXT1,
                "도": ID.NEXT2,
                "": ID.NONE,
            }
        ),
        Stats.YO: create_dict(
            {
                "겨": ID.PREV,
                "거": ID.PREV,
                "구": ID.PREV,
                "군": ID.PREV,
                "걸": ID.PREV,
                "까": ID.PREV,
                "께": ID.PREV,
                "껴": ID.PREV,
                "네": ID.PREV,
                "나": ID.PREV,
                "니": ID.PREV,
                "데": ID.PREV,
                "든": ID.PREV,
                "려": ID.PREV,
                "서": ID.PREV,
                "세": ID.PREV,
                "아": ID.PREV,
                "어": ID.PREV,
                "워": ID.PREV,
                "에": ID.PREV,
                "예": ID.PREV,
                "을": ID.PREV,
                "져": ID.PREV,
                "줘": ID.PREV,
                "지": ID.PREV,
                "춰": ID.PREV,
                "해": ID.PREV,
                "먼": ID.PREV,
                "만": ID.PREV,
                "고": ID.NEXT2,
                "는": ID.NEXT,
                "라": ID.NEXT1,
                "등": ID.NEXT,
                "를": ID.NEXT,
                "즘": ID.NEXT,
                "소": ID.NEXT,
                "며": ID.NEXT2,
                "면": ID.PREV | ID.NEXT2,
                "하": ID.NEXT1,
                "": ID.NONE,
            }
        ),
        Stats.JYO: create_dict(
            {
                "거": ID.PREV,
                "가": ID.PREV,
                "갔": ID.PREV,
                "겠": ID.PREV,
                "같": ID.PREV,
                "놨": ID.PREV,
                "녔": ID.PREV,
                "냈": ID.PREV,
                "니": ID.PREV,
                "뒀": ID.PREV,
                "았": ID.PREV,
                "르": ID.PREV,
                "랐": ID.PREV,
                "럽": ID.PREV,
                "렵": ID.PREV,
                "렸": ID.PREV,
                "맞": ID.PREV,
                "몄": ID.PREV,
                "밌": ID.PREV,
                "볐": ID.PREV,
                "볍": ID.PREV,
                "봤": ID.PREV,
                "서": ID.PREV,
                "섰": ID.PREV,
                "셨": ID.PREV,
                "샜": ID.PREV,
                "않": ID.PREV,
                "없": ID.PREV,
                "었": ID.PREV,
                "였": ID.PREV,
                "이": ID.PREV,
                "졌": ID.PREV,
                "쳤": ID.PREV,
                "챘": ID.PREV,
                "켰": ID.PREV,
                "팠": ID.PREV,
                "폈": ID.PREV,
                "하": ID.PREV,
                "했": ID.PREV,
                "혔": ID.PREV,
                "고": ID.PREV | ID.NEXT2,
                "는": ID.NEXT,
                "등": ID.NEXT,
                "라": ID.NEXT1,
                "를": ID.NEXT,
                "며": ID.NEXT2,
                "면": ID.PREV | ID.NEXT2,
                "": ID.NONE,
            }
        ),
        Stats.SB:
        # https://www.yeoju.go.kr/history/jsp/Theme/Save_View.jsp?BC_ID=d0400
        create_dict(
            {
                "것": ID.PREV,
                "가": ID.PREV,
                "까": ID.PREV,
                "걸": ID.PREV,
                "껄": ID.PREV,
                "나": ID.PREV,
                "니": ID.PREV,
                "네": ID.PREV,
                "다": ID.PREV,
                "쎄": ID.PREV,
                "래": ID.PREV,
                "데": ID.PREV,
                "지": ID.PREV,
                "든": ID.PREV,
                "덩": ID.PREV,
                "등": ID.PREV,
                "랴": ID.PREV,
                "마": ID.PREV,
                "봐": ID.PREV,
                "서": ID.PREV,
                "셈": ID.PREV,  # ~하셈 (신조어)
                "아": ID.PREV,
                "어": ID.PREV,
                "오": ID.PREV,
                "요": ID.PREV,
                "용": ID.PREV,
                "을": ID.PREV,
                "자": ID.PREV,
                "죠": ID.PREV,
                "쥬": ID.PREV,  # ~했쥬 (사투리)
                "죵": ID.PREV,  # ~했죵 (신조어)
                "고": ID.NEXT2,
                "는": ID.NEXT,
                "라": ID.PREV | ID.NEXT,
                "며": ID.NEXT2,
                "면": ID.NEXT2,
                "하": ID.NEXT1,
                "": ID.NONE,
            }
        ),
        Stats.COMMON: create_dict(
            {
                "ㄱ": ID.CONT,
                "ㄴ": ID.CONT,
                "ㄷ": ID.CONT,
                "ㄹ": ID.CONT,
                "ㅁ": ID.CONT,
                "ㅂ": ID.CONT,
                "ㅅ": ID.CONT,
                "ㅇ": ID.CONT,
                "ㅈ": ID.CONT,
                "ㅊ": ID.CONT,
                "ㅋ": ID.CONT,
                "ㅌ": ID.CONT,
                "ㅍ": ID.CONT,
                "ㅎ": ID.CONT,
                "ㅏ": ID.CONT,
                "ㅑ": ID.CONT,
                "ㅓ": ID.CONT,
                "ㅕ": ID.CONT,
                "ㅗ": ID.CONT,
                "ㅛ": ID.CONT,
                "ㅜ": ID.CONT,
                "ㅠ": ID.CONT,
                "ㅡ": ID.CONT,
                "ㅣ": ID.CONT,
                "^": ID.CONT,
                ";": ID.CONT,
                ".": ID.CONT,
                "?": ID.CONT,
                "!": ID.CONT,
                "~": ID.CONT,
                "…": ID.CONT,
                "": ID.NONE,
            }
        ),
        Stats.EOMI: create_dict(
            {
                "나": ID.NEXT,  # 했다나 뭐라나, 한다나 뭐라나
                "고": ID.NEXT | ID.NEXT2,
                "구": ID.NEXT | ID.NEXT2,
                "라": ID.NEXT,
                "시": ID.NEXT,
                "다": ID.NEXT,
                "등": ID.NEXT,
                "던": ID.NEXT,
                "든": ID.NEXT,
                "지": ID.NEXT2,
                "요": ID.NEXT,  # ~하구요
                "유": ID.NEXT,  # ~하구유
                "용": ID.NEXT,  # ~하군용
                "만": ID.NEXT,
                "은": ID.NEXT | ID.NEXT2,
                "는": ID.NEXT | ID.NEXT2,
                "이": ID.NEXT,
                "가": ID.NEXT,
                "을": ID.NEXT,
                "를": ID.NEXT,
                "의": ID.NEXT,
                "며": ID.NEXT | ID.NEXT2,
                "면": ID.NEXT | ID.NEXT1 | ID.NEXT2,
                "서": ID.NEXT2,
                "싶": ID.NEXT,
                "죠": ID.NEXT,
                "죵": ID.NEXT,
                "쥬": ID.NEXT,
                "하": ID.NEXT1,
                "도": ID.NEXT | ID.NEXT2,
            }
        ),
    },
    default=create_dict({}),
)

unicodes = []
unicodes += ["‍"]  # zero width joiner
unicodes += [
    "︀",
    "︁",
    "︂",
    "︃",
    "︄",
    "︅",
    "︆",
    "︇",
    "︈",
    "︉",
    "︊",
    "︋",
    "︌",
    "︍",
    "︎",
    "️",
]  # variation_selectors 1~16

Table[Stats.COMMON].update({e: ID.CONT for e in _emojis.keys()})
Table[Stats.COMMON].update({e: ID.CONT for e in unicodes})

post_processing_da = list(
    set([f"{x} {_}{y} " for y in ["다"] for _ in yo for x in before])
)
post_processing_yo = list(
    set([f"{x} {_}{y} " for y in ["요"] for _ in yo for x in before])
)
post_processing_jyo = list(
    set([f"{x} {_}{j} " for j in ["죠"] for _ in jyo for x in before])
)
