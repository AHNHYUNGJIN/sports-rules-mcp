#!/usr/bin/env python3
"""체육 수업용 스포츠 규칙 검색 MCP 서버"""

import json
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

SPORTS_DATABASE = {
    "축구": {
        "name": "축구", "english": "Soccer",
        "players": {"official": 11, "min": 7},
        "duration": "전반 45분, 후반 45분 (총 90분)",
        "field": "105m × 68m",
        "basic_rules": [
            "손과 팔을 제외한 신체 부위로 공을 다룬다 (골키퍼 제외)",
            "공이 골라인을 완전히 넘어가면 득점",
            "오프사이드: 상대 진영에서 공보다 앞에 있고 수비수가 1명 이하일 때",
            "파울 시 직접/간접 프리킥 또는 페널티킥 부여",
            "경고(옐로카드) 2회 또는 레드카드 시 퇴장",
            "스로인: 공이 터치라인 밖으로 나가면 양손으로 머리 위에서 던짐",
            "골킥: 공격팀이 골라인 밖으로 보내면 수비팀 골킥",
            "코너킥: 수비팀이 골라인 밖으로 보내면 공격팀 코너킥",
        ],
        "fouls": [
            "위험한 태클 또는 발 들기",
            "팔꿈치 사용",
            "고의적 핸드볼",
            "상대 선수 밀기/잡기",
        ],
        "referee_guide": [
            "주심 1명, 부심 2명으로 구성",
            "파울 판정: 손을 수직으로 들어 방향 지시",
            "간접 프리킥: 한 손을 위로 들어 유지",
            "오프사이드: 깃발을 들고 위치 지시",
            "경고: 옐로카드를 꺼내 위로 들어 보임",
            "퇴장: 레드카드를 꺼내 위로 들어 보임",
        ],
        "modified_for_class": {
            "초등": {
                "players": "5 vs 5 또는 6 vs 6",
                "duration": "10분 × 2~3회",
                "modifications": ["오프사이드 규칙 제거", "골 크기 축소", "4호 또는 소프트볼 사용", "스로인 대신 발로 차서 인바운드"],
            },
            "중등": {
                "players": "7 vs 7 또는 8 vs 8",
                "duration": "15분 × 2회",
                "modifications": ["오프사이드 간소화 적용", "파울 후 프리킥 시 벽 세우기 생략"],
            },
            "고등": {
                "players": "9 vs 9 또는 11 vs 11",
                "duration": "20분 × 2회",
                "modifications": ["정식 규칙 최대한 적용"],
            },
        },
    },
    "농구": {
        "name": "농구", "english": "Basketball",
        "players": {"official": 5, "min": 5},
        "duration": "10분 × 4쿼터 (FIBA 기준)",
        "field": "28m × 15m",
        "basic_rules": [
            "공을 드리블하거나 패스하여 상대 바스켓에 넣으면 득점",
            "2점슛: 3점선 안쪽, 3점슛: 3점선 바깥쪽, 자유투: 1점",
            "드리블 없이 3걸음 이상 이동 시 트래블링",
            "드리블 중 두 손으로 잡았다가 다시 드리블하면 더블드리블",
            "공격 시간 제한: 24초 이내 슛 시도",
            "3초 이상 페인트 존에 머물면 바이올레이션",
            "개인 파울 5회 시 퇴장 (FIBA 기준)",
        ],
        "fouls": [
            "신체 접촉에 의한 개인 파울",
            "기술 파울: 비신사적 행동, 심판 항의",
            "플래그런트 파울: 고의적이고 과도한 신체 접촉",
        ],
        "referee_guide": [
            "주심 2명 (또는 3명) 운영",
            "트래블링: 양손 앞에서 굴리는 동작",
            "더블드리블: 두 손을 위아래로 움직이는 동작",
            "파울: 한 팔을 위로 들고 주먹 쥐기",
            "자유투: 두 팔을 가슴 앞으로 교차",
            "타임아웃: T자 모양으로 양손 표시",
        ],
        "modified_for_class": {
            "초등": {
                "players": "3 vs 3 또는 4 vs 4",
                "duration": "5분 × 4회",
                "modifications": ["드리블 없이 3걸음까지 허용", "24초 타이머 제거", "3점슛 없음", "낮은 골대 사용 (2.6~2.8m)"],
            },
            "중등": {
                "players": "4 vs 4 또는 5 vs 5",
                "duration": "8분 × 4쿼터",
                "modifications": ["30초 공격 시간 적용", "3점슛 적용"],
            },
            "고등": {
                "players": "5 vs 5",
                "duration": "10분 × 4쿼터",
                "modifications": ["FIBA 정식 규칙 적용"],
            },
        },
    },
    "배구": {
        "name": "배구", "english": "Volleyball",
        "players": {"official": 6, "min": 6},
        "duration": "5세트 중 3세트 선취 (1~4세트: 25점, 5세트: 15점)",
        "field": "18m × 9m (네트 높이: 남 2.43m, 여 2.24m)",
        "basic_rules": [
            "한 팀이 공을 3번 이내로 터치하여 상대 코트로 넘겨야 함",
            "같은 선수가 연속 2번 터치 불가 (블로킹 제외)",
            "공이 바닥에 닿으면 득점 (랠리포인트제)",
            "서브권을 얻으면 시계방향으로 로테이션",
            "네트 터치 시 실점",
            "리베로는 백코트에서만 플레이, 서브 불가",
        ],
        "fouls": [
            "4번 터치 (포 히트)",
            "더블 컨택",
            "리프팅 (공을 잡아채는 동작)",
            "네트 터치",
            "센터라인 완전히 넘기",
        ],
        "referee_guide": [
            "주심: 네트 기둥 위 심판대에 위치",
            "부심: 주심 반대편 기둥 옆에 위치",
            "득점: 한 손 들어 득점팀 방향 지시",
            "서브 신호: 팔을 수평으로 들어 방향 지시",
            "네트 파울: 손을 네트 위에서 흔들기",
            "포 히트: 한 손 펴서 4 표시",
            "로테이션 신호: 한 손으로 원을 그리기",
        ],
        "modified_for_class": {
            "초등": {
                "players": "4 vs 4",
                "duration": "15점 선취 × 3세트",
                "modifications": ["풍선 배구 또는 소프트 배구공 사용", "바운드 1회 허용", "5번 터치까지 허용", "낮은 네트 사용 (1.8~2.0m)"],
            },
            "중등": {
                "players": "6 vs 6 또는 4 vs 4",
                "duration": "15점 선취 × 3세트",
                "modifications": ["바운드 1회 허용 (선택)", "리베로 규정 간소화"],
            },
            "고등": {
                "players": "6 vs 6",
                "duration": "25점 선취 × 5세트 중 3세트",
                "modifications": ["정식 규칙 적용"],
            },
        },
    },
    "야구": {
        "name": "야구", "english": "Baseball",
        "players": {"official": 9, "min": 9},
        "duration": "9이닝 (공격·수비 각 3아웃씩)",
        "field": "내야 베이스 간격 27.4m, 홈~2루 38.8m 다이아몬드",
        "basic_rules": [
            "투수가 던진 공을 타자가 쳐서 진루, 홈베이스를 밟으면 1점 득점",
            "3스트라이크: 타자 아웃 (삼진)",
            "4볼: 타자 1루 진루 (볼넷)",
            "타구가 페어지역에 떨어지면 페어, 파울라인 밖이면 파울",
            "공중에 뜬 공을 수비가 잡으면 타자 아웃 (플라이 아웃)",
            "1루에 공이 타자보다 먼저 도달하면 아웃 (땅볼 아웃)",
            "주자를 공으로 터치하면 아웃 (태그 아웃)",
            "3아웃이 되면 공수 교대, 9이닝 후 득점이 많은 팀 승리",
            "홈런: 타구가 파울라인 안쪽으로 외야 펜스를 넘어가면 전 주자 득점",
        ],
        "fouls": [
            "타석 밖에서 타격",
            "주자가 베이스를 밟지 않고 진루 (어필 아웃)",
            "수비 방해 (디플렉션)",
            "주자가 송구를 방해",
            "보크: 투수의 부정 투구 동작 (주자 1루 진루)",
        ],
        "referee_guide": [
            "주심: 홈플레이트 뒤에서 스트라이크/볼 판정",
            "1루심, 2루심, 3루심: 각 베이스 근처에서 아웃/세이프 판정",
            "스트라이크: 오른손을 옆으로 힘차게 뻗기",
            "아웃: 오른손 주먹을 위로 올리기",
            "세이프: 양팔을 수평으로 벌리기",
            "파울: 양팔을 수평으로 들고 '파울' 선언",
            "볼: 별도 신호 없이 '볼' 선언",
            "홈런: 검지로 원을 그리며 '홈런' 선언",
        ],
        "modified_for_class": {
            "초등": {
                "players": "6 vs 6",
                "duration": "3이닝",
                "modifications": [
                    "티볼 방식 (투수 없이 티 위의 공 타격)",
                    "소프트볼 또는 스펀지볼 사용",
                    "베이스 간격 15m로 축소",
                    "3아웃 대신 전원 타격 후 교대",
                ],
            },
            "중등": {
                "players": "9 vs 9",
                "duration": "5이닝",
                "modifications": [
                    "느린 투구 (슬로피치) 적용",
                    "도루 없음",
                    "소프트볼 사용 가능",
                ],
            },
            "고등": {
                "players": "9 vs 9",
                "duration": "7이닝",
                "modifications": ["정식 야구 규칙 적용 (도루 포함)"],
            },
        },
    },
    "피클볼": {
        "name": "피클볼", "english": "Pickleball",
        "players": {"official": "단식(1 vs 1) 또는 복식(2 vs 2)", "min": 1},
        "duration": "11점 선취 (2점 차), 2게임 선취",
        "field": "13.4m × 6.1m (배드민턴 복식 코트와 동일), 네트 높이 86cm(중앙 86cm, 사이드 91cm)",
        "basic_rules": [
            "구멍 뚫린 플라스틱 공과 단단한 패들(라켓) 사용",
            "서브는 반드시 언더핸드로 대각선 서비스 박스로",
            "서브 시 두 발이 베이스라인 뒤에 있어야 함",
            "키친(논볼리존): 네트에서 2.13m 구역, 이 안에서는 발리(바운드 없이 타구) 금지",
            "서브 후 양 팀 모두 반드시 1회 이상 바운드 후 타구해야 함 (더블바운스 규칙)",
            "11점 선취 시 게임 승리 (10-10 시 2점 차 선취)",
            "서브권이 있는 팀만 득점 가능 (사이드아웃 방식, 비공식 랠리포인트 방식도 사용)",
            "공이 라인에 닿으면 인바운드 (키친 라인 포함)",
        ],
        "fouls": [
            "키친에서 발리 (발이 키친 안에 있을 때 공중 타구)",
            "오버핸드 서브",
            "서브가 키친 안에 떨어짐 (키친 라인 포함)",
            "네트 터치",
            "공이 아웃 라인 밖에 떨어짐",
            "더블바운스 규칙 위반 (서브 직후 바운드 없이 타구)",
        ],
        "referee_guide": [
            "공식 경기: 주심 1명 + 선심, 비공식은 선수들이 자체 판정",
            "인/아웃 콜: 인 → 아무 말 없음, 아웃 → '아웃' 선언",
            "폴트 선언: '폴트' 또는 '사이드아웃'",
            "점수 선언: '서브팀 점수 - 상대팀 점수 - 서버 번호 (복식)'",
            "키친 폴트: '키친' 또는 '논볼리존 폴트' 선언",
        ],
        "modified_for_class": {
            "초등": {
                "players": "복식(2 vs 2)",
                "duration": "7점 선취",
                "modifications": [
                    "스펀지/폼 공 사용",
                    "키친 규칙 생략",
                    "바운드 1회 후 타구 허용 (발리 금지)",
                    "랠리포인트제 적용 (서브권 상관없이 득점)",
                ],
            },
            "중등": {
                "players": "단식 또는 복식",
                "duration": "11점 선취",
                "modifications": [
                    "키친 규칙 적용",
                    "더블바운스 규칙 적용",
                    "랠리포인트제 적용",
                ],
            },
            "고등": {
                "players": "단식 또는 복식",
                "duration": "11점 선취 × 2게임 선취",
                "modifications": ["정식 피클볼 규칙 적용"],
            },
        },
    },
    "탁구": {
        "name": "탁구", "english": "Table Tennis",
        "players": {"official": "단식(1 vs 1) 또는 복식(2 vs 2)", "min": 1},
        "duration": "7게임 중 4게임 선취 (각 게임 11점)",
        "field": "274cm × 152.5cm × 높이 76cm 테이블",
        "basic_rules": [
            "서브: 공을 손바닥 위에 놓고 위로 던진 후 타구, 네트 넘겨 상대 코트로",
            "11점 선취 시 게임 승리 (10-10 시 2점 차 선취)",
            "2포인트마다 서브 교대",
            "공이 테이블 끝 라인에 닿으면 인바운드",
            "네트 맞고 넘어가면 렛(재서브)",
        ],
        "fouls": [
            "서브 시 공을 숨기거나 몸 뒤에서 타구",
            "테이블 움직이기",
            "자유 손이 테이블에 닿기",
            "연속 2회 타구",
        ],
        "referee_guide": [
            "주심 1명이 테이블 옆에서 진행",
            "득점 선언: '서브팀 점수 - 리시브팀 점수'",
            "렛 선언: '렛' 호칭 후 재서브 지시",
            "에지볼 (테이블 모서리): 득점 인정",
            "서브 폴트: '폴트' 선언 후 상대 득점",
        ],
        "modified_for_class": {
            "초등": {
                "players": "단식",
                "duration": "7점 선취",
                "modifications": ["더 큰 공 사용 (폼볼)", "서브 규칙 간소화 (올려치기 허용)", "네트 높이 낮추기"],
            },
            "중등": {
                "players": "단식 또는 복식",
                "duration": "11점 선취 × 5게임",
                "modifications": ["서브 규칙 기본 적용", "복식 서브 위치 간소화"],
            },
            "고등": {
                "players": "단식 또는 복식",
                "duration": "11점 선취 × 7게임",
                "modifications": ["정식 규칙 적용"],
            },
        },
    },
    "배드민턴": {
        "name": "배드민턴", "english": "Badminton",
        "players": {"official": "단식(1 vs 1) 또는 복식(2 vs 2)", "min": 1},
        "duration": "3게임 중 2게임 선취 (각 게임 21점)",
        "field": "단식: 13.4m × 5.18m, 복식: 13.4m × 6.1m",
        "basic_rules": [
            "셔틀콕이 상대 코트 바닥에 닿으면 득점 (랠리포인트제)",
            "서브는 허리 아래에서 언더핸드로 대각선 방향으로",
            "21점 선취 시 게임 승리 (20-20 시 2점 차 선취, 최대 30점)",
            "네트 터치 시 실점",
            "셔틀콕이 라인에 닿으면 인바운드",
        ],
        "fouls": [
            "오버 더 넷 (네트 너머로 라켓이 넘어감)",
            "네트 터치",
            "언더핸드 서브 위반 (허리 위에서 서브)",
            "두 번 연속 치기",
        ],
        "referee_guide": [
            "주심: 네트 기둥 옆 심판석에 위치",
            "득점 선언: '서브팀 점수 - 리시브팀 점수 (서브)'",
            "인: 엄지 들기 또는 라인 방향 손짓",
            "아웃: 양팔 수평으로 벌리기",
            "렛: 양 손바닥을 위로 들기 (재서브)",
        ],
        "modified_for_class": {
            "초등": {
                "players": "단식 또는 복식",
                "duration": "11점 선취",
                "modifications": ["바운드 1회 허용", "서비스 박스 구분 없음", "소프트 셔틀콕 사용"],
            },
            "중등": {
                "players": "단식 또는 복식",
                "duration": "15점 선취 × 3게임",
                "modifications": ["서브 규칙 간소화", "서비스 폴트 1회 허용"],
            },
            "고등": {
                "players": "단식 또는 복식",
                "duration": "21점 선취 × 3게임",
                "modifications": ["정식 규칙 적용"],
            },
        },
    },
    "티볼": {
        "name": "티볼", "english": "T-ball",
        "players": {"official": 9, "min": 6},
        "duration": "5이닝 또는 시간 제한",
        "field": "베이스 간 18m (축소 야구장)",
        "basic_rules": [
            "타자는 티(고정 받침대) 위의 공을 타격",
            "공을 타격 후 1루 방향으로 뛰어 진루",
            "수비팀은 공을 잡아 베이스에 던지거나 태그하여 아웃",
            "3아웃 시 공수 교대",
            "홈베이스까지 돌아오면 1점 득점",
            "타구가 파울라인 밖으로 나가면 파울",
        ],
        "fouls": [
            "파울볼 (3번째 파울은 아웃)",
            "주자가 베이스 밟지 않고 진루",
            "타구한 공이 1루 도달 전에 잡힘",
        ],
        "referee_guide": [
            "주심은 홈베이스 뒤에 위치",
            "아웃 신호: 오른손 주먹 들어올리기",
            "세이프 신호: 양팔 수평으로 벌리기",
            "파울: '파울' 선언 + 양팔 수평",
        ],
        "modified_for_class": {
            "초등": {
                "players": "5 vs 5",
                "duration": "3이닝",
                "modifications": ["소프트볼 또는 스펀지볼 사용", "베이스 간격 12m로 축소", "아웃 없이 모두 타격 후 교대"],
            },
            "중등": {
                "players": "7 vs 7",
                "duration": "5이닝",
                "modifications": ["정식 아웃 규칙 적용", "도루 없음"],
            },
            "고등": {
                "players": "9 vs 9",
                "duration": "7이닝",
                "modifications": ["정식 티볼 규칙 적용"],
            },
        },
    },
    "테니스": {
        "name": "테니스", "english": "Tennis",
        "players": {"official": "단식(1 vs 1) 또는 복식(2 vs 2)", "min": 1},
        "duration": "남자: 5세트 중 3세트 선취, 여자/학교: 3세트 중 2세트 선취",
        "field": "단식: 23.77m × 8.23m, 복식: 23.77m × 10.97m (네트 높이: 중앙 91.4cm, 사이드 107cm)",
        "basic_rules": [
            "서브: 베이스라인 뒤에서 대각선 서비스 박스로 오버핸드 타구",
            "포인트 계산: 0 → 15 → 30 → 40 → 게임 (듀스 시 2점 차 선취)",
            "6게임 선취 시 세트 승리 (5-5 시 타이브레이크 또는 7-5 선취)",
            "서브는 게임마다 교대, 서브 실패 2회(더블폴트) 시 상대 득점",
            "공이 라인에 닿으면 인바운드",
            "네트 맞고 서비스 박스에 들어가면 렛(재서브)",
            "공이 바운드 전에 또는 1회 바운드 후 타구",
            "복식: 서브는 한 팀 선수가 번갈아 가며 진행",
        ],
        "fouls": [
            "서브가 서비스 박스 밖에 떨어짐 (폴트)",
            "서브 시 베이스라인 밟기 (풋폴트)",
            "공이 2회 바운드 후 타구",
            "네트 터치",
            "공을 2번 연속 타구",
            "공이 아웃라인 밖에 떨어짐",
        ],
        "referee_guide": [
            "주심: 심판대에서 전체 경기 진행",
            "선심: 각 라인별 인/아웃 판정",
            "아웃 콜: '아웃' 선언 + 한 팔 수평으로 뻗기",
            "폴트: '폴트' 선언",
            "렛: '렛' 선언 후 재서브",
            "점수 선언: 서버 점수 먼저 '15-0', '30-15' 등으로 선언",
            "듀스: '듀스' 선언, 이후 '어드밴티지 서버/리시버'",
        ],
        "modified_for_class": {
            "초등": {
                "players": "단식 또는 복식",
                "duration": "4게임 선취 × 3세트",
                "modifications": [
                    "스펀지볼 또는 슬로볼(빨간색 볼) 사용",
                    "코트 크기 1/2로 축소",
                    "서브 대신 드롭 서브 또는 손으로 토스 후 타격",
                    "포인트 계산 간소화: 1점씩 카운트",
                ],
            },
            "중등": {
                "players": "단식 또는 복식",
                "duration": "6게임 선취 × 3세트",
                "modifications": [
                    "슬로볼(오렌지색 볼) 또는 일반 볼 사용",
                    "더블폴트 1회 허용 후 두 번째 폴트만 실점",
                    "포인트 계산 정식 적용",
                ],
            },
            "고등": {
                "players": "단식 또는 복식",
                "duration": "6게임 선취 × 3세트 중 2세트",
                "modifications": ["정식 테니스 규칙 적용"],
            },
        },
    },
}


def find_sport(sport_name: str):
    if sport_name in SPORTS_DATABASE:
        return SPORTS_DATABASE[sport_name]
    for key, sport in SPORTS_DATABASE.items():
        if sport_name in key or key in sport_name:
            return sport
        if sport_name.lower() in sport.get("english", "").lower():
            return sport
    return None


app = Server("sports-rules-mcp")


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="list_sports",
            description="지원하는 스포츠 종목 목록을 반환합니다",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_sport_rules",
            description="특정 스포츠 종목의 기본 규칙, 반칙 정보를 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "sport_name": {
                        "type": "string",
                        "description": "종목명 (예: 축구, 농구, 배구, 야구, 피클볼, 탁구, 배드민턴, 티볼, 테니스)",
                    }
                },
                "required": ["sport_name"],
            },
        ),
        Tool(
            name="get_modified_rules",
            description="학교 체육 수업에 맞게 변형된 규칙을 조회합니다 (학교급별 인원, 시간, 변형 사항)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sport_name": {"type": "string", "description": "종목명"},
                    "grade": {
                        "type": "string",
                        "description": "학교급 (초등, 중등, 고등)",
                        "enum": ["초등", "중등", "고등"],
                    },
                },
                "required": ["sport_name", "grade"],
            },
        ),
        Tool(
            name="get_referee_guide",
            description="특정 스포츠의 심판 방법, 위치, 신호 동작을 조회합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "sport_name": {"type": "string", "description": "종목명"}
                },
                "required": ["sport_name"],
            },
        ),
        Tool(
            name="search_sports",
            description="키워드로 스포츠 종목을 검색합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "검색 키워드 (예: 네트, 라켓, 이닝)",
                    }
                },
                "required": ["keyword"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "list_sports":
        lines = ["## 지원 스포츠 종목 목록\n"]
        for sport in SPORTS_DATABASE.values():
            p = sport["players"]["official"]
            lines.append(f"- **{sport['name']}** ({sport['english']}) | 선수: {p}명 | 경기장: {sport['field']}")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "get_sport_rules":
        sport_name = arguments.get("sport_name", "")
        sport = find_sport(sport_name)
        if not sport:
            return [TextContent(type="text", text=f"'{sport_name}' 종목을 찾을 수 없습니다. list_sports 도구로 지원 종목을 확인하세요.")]

        lines = [f"## {sport['name']} ({sport['english']}) 기본 규칙\n"]
        lines.append(f"**선수 수:** {sport['players']['official']}명")
        lines.append(f"**경기 시간:** {sport['duration']}")
        lines.append(f"**경기장:** {sport['field']}\n")
        lines.append("### 기본 규칙")
        for i, rule in enumerate(sport["basic_rules"], 1):
            lines.append(f"{i}. {rule}")
        lines.append("\n### 반칙 (파울)")
        for foul in sport["fouls"]:
            lines.append(f"- {foul}")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "get_modified_rules":
        sport_name = arguments.get("sport_name", "")
        grade = arguments.get("grade", "중등")
        sport = find_sport(sport_name)
        if not sport:
            return [TextContent(type="text", text=f"'{sport_name}' 종목을 찾을 수 없습니다.")]

        modified = sport["modified_for_class"].get(grade)
        if not modified:
            return [TextContent(type="text", text=f"{grade} 변형 규칙 정보가 없습니다.")]

        lines = [f"## {sport['name']} — {grade} 수업용 변형 규칙\n"]
        lines.append(f"**인원:** {modified['players']}")
        lines.append(f"**시간:** {modified['duration']}\n")
        lines.append("### 변형 사항")
        for mod in modified["modifications"]:
            lines.append(f"- {mod}")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "get_referee_guide":
        sport_name = arguments.get("sport_name", "")
        sport = find_sport(sport_name)
        if not sport:
            return [TextContent(type="text", text=f"'{sport_name}' 종목을 찾을 수 없습니다.")]

        lines = [f"## {sport['name']} 심판 방법\n"]
        for guide in sport["referee_guide"]:
            lines.append(f"- {guide}")
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "search_sports":
        keyword = arguments.get("keyword", "").lower()
        results = []
        for sport in SPORTS_DATABASE.values():
            if keyword in json.dumps(sport, ensure_ascii=False).lower():
                results.append(f"- **{sport['name']}** ({sport['english']})")

        if results:
            text = f"## '{keyword}' 검색 결과\n\n" + "\n".join(results)
        else:
            text = f"'{keyword}'에 해당하는 종목을 찾을 수 없습니다."
        return [TextContent(type="text", text=text)]

    return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
