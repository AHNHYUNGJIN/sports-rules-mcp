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
    "핸드볼": {
        "name": "핸드볼", "english": "Handball",
        "players": {"official": 7, "min": 5},
        "duration": "전반 30분, 후반 30분 (총 60분)",
        "field": "40m × 20m",
        "basic_rules": [
            "공을 손으로 패스하거나 드리블하여 골에 넣으면 득점",
            "드리블 없이 3걸음까지 이동 가능",
            "6m 골 에어리어 안에는 골키퍼만 진입 가능",
            "공격팀은 9m 라인 밖에서 슛",
            "공을 3초 이상 정지 상태로 들고 있으면 패시브플레이",
            "7m 스로 (페널티): 6m 이내 파울 시",
        ],
        "fouls": [
            "6m 에어리어 진입",
            "공 빼앗을 때 상대 팔/몸 잡기",
            "위험한 플레이",
            "3걸음 이상 보행",
            "더블 드리블",
        ],
        "referee_guide": [
            "주심 2명이 양쪽 터치라인에서 진행",
            "파울: 한 팔을 수평으로 들어 방향 지시",
            "7m 스로: 7m 지점 가리키기",
            "경고(옐로카드), 2분 퇴장, 실격(레드카드)",
            "타임아웃: T자 모양 신호",
        ],
        "modified_for_class": {
            "초등": {
                "players": "5 vs 5",
                "duration": "10분 × 2회",
                "modifications": ["소프트 핸드볼 사용", "에어리어 진입 허용", "5걸음까지 허용"],
            },
            "중등": {
                "players": "6 vs 6 또는 7 vs 7",
                "duration": "15분 × 2회",
                "modifications": ["에어리어 규칙 적용", "3걸음 규칙 적용"],
            },
            "고등": {
                "players": "7 vs 7",
                "duration": "20분 × 2회",
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
    "플로어볼": {
        "name": "플로어볼", "english": "Floorball",
        "players": {"official": 6, "min": 4},
        "duration": "20분 × 3피리어드",
        "field": "40m × 20m (펜스 경계)",
        "basic_rules": [
            "가벼운 플라스틱 스틱으로 공을 쳐서 골에 넣으면 득점",
            "스틱은 무릎 아래에서만 사용 (들어올리기 금지)",
            "공을 발로 차거나 손으로 치는 것 금지 (우연한 접촉 제외)",
            "골키퍼는 손, 발, 몸 전체 사용 가능",
            "슬래핑(스틱으로 상대 스틱 치기) 금지",
            "신체 접촉 최소화 (어깨 접촉만 허용)",
        ],
        "fouls": [
            "스틱 들어올리기",
            "발로 공 차기 (의도적)",
            "슬래핑 (상대 스틱 치기)",
            "과도한 신체 접촉",
        ],
        "referee_guide": [
            "주심 2명이 코트 양쪽에서 진행",
            "파울: 휘슬 후 프리히트 위치 지시",
            "2분 퇴장, 5분 퇴장, 경기 퇴장 패널티",
            "패널티샷: 중앙에서 출발 신호",
        ],
        "modified_for_class": {
            "초등": {
                "players": "4 vs 4",
                "duration": "5분 × 3회",
                "modifications": ["소형 골대 사용", "스틱 들어올리기 1회 경고 후 적용", "페널티 없이 프리히트만 적용"],
            },
            "중등": {
                "players": "5 vs 5",
                "duration": "10분 × 3회",
                "modifications": ["기본 파울 규칙 적용", "골키퍼 없이 진행 가능"],
            },
            "고등": {
                "players": "6 vs 6",
                "duration": "15분 × 3피리어드",
                "modifications": ["정식 규칙 적용"],
            },
        },
    },
    "킨볼": {
        "name": "킨볼", "english": "Kin-Ball",
        "players": {"official": "3팀 각 4명 (12명)", "min": "3팀 각 3명"},
        "duration": "3피리어드 × 7분",
        "field": "21m × 21m 정사각형",
        "basic_rules": [
            "3팀이 동시에 경기 (분홍, 회색, 검정 팀)",
            "지름 122cm의 대형 공 사용",
            "서브팀이 '옴니킨 + 수비팀 색깔'을 외치며 공을 타격",
            "지목된 팀이 공을 받아야 함",
            "공이 바닥에 닿으면 나머지 두 팀 각 1점 획득",
            "4명 전원이 공에 닿아야 서브 가능",
        ],
        "fouls": [
            "지목한 팀이 아닌 팀이 공 받기",
            "서브 전 모두가 공에 닿지 않음",
            "경기장 밖으로 공 나가기",
        ],
        "referee_guide": [
            "심판 1~2명으로 진행",
            "득점 선언: 득점한 팀 방향 지시",
            "파울: 휘슬 후 규칙 위반 설명",
            "팀 색깔 확인: 분홍(핑크), 회색(그레이), 검정(블랙)",
        ],
        "modified_for_class": {
            "초등": {
                "players": "3팀 각 3명",
                "duration": "5분 × 3피리어드",
                "modifications": ["터치 횟수 무제한", "서브 규칙 간소화", "전원 터치 규칙 생략"],
            },
            "중등": {
                "players": "3팀 각 4명",
                "duration": "7분 × 3피리어드",
                "modifications": ["전원 터치 규칙 적용", "서브 타격 규칙 적용"],
            },
            "고등": {
                "players": "3팀 각 4명",
                "duration": "7분 × 3피리어드",
                "modifications": ["정식 규칙 적용"],
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
                        "description": "종목명 (예: 축구, 농구, 배구, 배드민턴, 탁구, 핸드볼, 티볼, 플로어볼, 킨볼)",
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
                    "sport_name": {
                        "type": "string",
                        "description": "종목명",
                    },
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
                    "sport_name": {
                        "type": "string",
                        "description": "종목명",
                    }
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
                        "description": "검색 키워드 (예: 네트, 팀, 라켓, 3명)",
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
