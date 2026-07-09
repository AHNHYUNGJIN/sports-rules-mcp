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
        "fouls": ["위험한 태클 또는 발 들기", "팔꿈치 사용", "고의적 핸드볼", "상대 선수 밀기/잡기"],
        "referee_guide": [
            "주심 1명, 부심 2명으로 구성",
            "파울 판정: 손을 수직으로 들어 방향 지시",
            "간접 프리킥: 한 손을 위로 들어 유지",
            "오프사이드: 깃발을 들고 위치 지시",
            "경고: 옐로카드를 꺼내 위로 들어 보임",
            "퇴장: 레드카드를 꺼내 위로 들어 보임",
        ],
        "modified_for_class": {
            "초등": {"players": "5 vs 5 또는 6 vs 6", "duration": "10분 × 2~3회", "modifications": ["오프사이드 규칙 제거", "골 크기 축소", "4호 또는 소프트볼 사용", "스로인 대신 발로 차서 인바운드"]},
            "중등": {"players": "7 vs 7 또는 8 vs 8", "duration": "15분 × 2회", "modifications": ["오프사이드 간소화 적용", "파울 후 프리킥 시 벽 세우기 생략"]},
            "고등": {"players": "9 vs 9 또는 11 vs 11", "duration": "20분 × 2회", "modifications": ["정식 규칙 최대한 적용"]},
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
        "fouls": ["신체 접촉에 의한 개인 파울", "기술 파울: 비신사적 행동, 심판 항의", "플래그런트 파울: 고의적이고 과도한 신체 접촉"],
        "referee_guide": [
            "주심 2명 (또는 3명) 운영",
            "트래블링: 양손 앞에서 굴리는 동작",
            "더블드리블: 두 손을 위아래로 움직이는 동작",
            "파울: 한 팔을 위로 들고 주먹 쥐기",
            "자유투: 두 팔을 가슴 앞으로 교차",
            "타임아웃: T자 모양으로 양손 표시",
        ],
        "modified_for_class": {
            "초등": {"players": "3 vs 3 또는 4 vs 4", "duration": "5분 × 4회", "modifications": ["드리블 없이 3걸음까지 허용", "24초 타이머 제거", "3점슛 없음", "낮은 골대 사용 (2.6~2.8m)"]},
            "중등": {"players": "4 vs 4 또는 5 vs 5", "duration": "8분 × 4쿼터", "modifications": ["30초 공격 시간 적용", "3점슛 적용"]},
            "고등": {"players": "5 vs 5", "duration": "10분 × 4쿼터", "modifications": ["FIBA 정식 규칙 적용"]},
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
        "fouls": ["4번 터치 (포 히트)", "더블 컨택", "리프팅 (공을 잡아채는 동작)", "네트 터치", "센터라인 완전히 넘기"],
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
            "초등": {"players": "4 vs 4", "duration": "15점 선취 × 3세트", "modifications": ["소프트 배구공 사용", "바운드 1회 허용", "5번 터치까지 허용", "낮은 네트 사용 (1.8~2.0m)"]},
            "중등": {"players": "6 vs 6 또는 4 vs 4", "duration": "15점 선취 × 3세트", "modifications": ["바운드 1회 허용 (선택)", "리베로 규정 간소화"]},
            "고등": {"players": "6 vs 6", "duration": "25점 선취 × 5세트 중 3세트", "modifications": ["정식 규칙 적용"]},
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
        "fouls": ["타석 밖에서 타격", "주자가 베이스를 밟지 않고 진루 (어필 아웃)", "수비 방해", "보크: 투수의 부정 투구 동작"],
        "referee_guide": [
            "주심: 홈플레이트 뒤에서 스트라이크/볼 판정",
            "1루심, 2루심, 3루심: 각 베이스 근처에서 아웃/세이프 판정",
            "스트라이크: 오른손을 옆으로 힘차게 뻗기",
            "아웃: 오른손 주먹을 위로 올리기",
            "세이프: 양팔을 수평으로 벌리기",
            "파울: 양팔을 수평으로 들고 '파울' 선언",
            "홈런: 검지로 원을 그리며 '홈런' 선언",
        ],
        "modified_for_class": {
            "초등": {"players": "6 vs 6", "duration": "3이닝", "modifications": ["티볼 방식 (투수 없이 티 위의 공 타격)", "소프트볼 또는 스펀지볼 사용", "베이스 간격 15m로 축소", "전원 타격 후 교대"]},
            "중등": {"players": "9 vs 9", "duration": "5이닝", "modifications": ["느린 투구 (슬로피치) 적용", "도루 없음", "소프트볼 사용 가능"]},
            "고등": {"players": "9 vs 9", "duration": "7이닝", "modifications": ["정식 야구 규칙 적용 (도루 포함)"]},
        },
    },
    "피클볼": {
        "name": "피클볼", "english": "Pickleball",
        "players": {"official": "단식(1 vs 1) 또는 복식(2 vs 2)", "min": 1},
        "duration": "11점 선취 (2점 차), 2게임 선취",
        "field": "13.4m × 6.1m, 네트 높이 중앙 86cm / 사이드 91cm",
        "basic_rules": [
            "구멍 뚫린 플라스틱 공과 단단한 패들 사용",
            "서브는 반드시 언더핸드로 대각선 서비스 박스로",
            "키친(논볼리존): 네트에서 2.13m 구역, 이 안에서 발리 금지",
            "서브 후 양 팀 모두 반드시 1회 이상 바운드 후 타구 (더블바운스 규칙)",
            "11점 선취 시 게임 승리 (10-10 시 2점 차 선취)",
            "공이 라인에 닿으면 인바운드 (키친 라인 포함)",
        ],
        "fouls": ["키친에서 발리", "오버핸드 서브", "서브가 키친 안에 떨어짐", "네트 터치", "더블바운스 규칙 위반"],
        "referee_guide": [
            "공식 경기: 주심 1명 + 선심, 비공식은 선수들이 자체 판정",
            "인/아웃 콜: 인 → 무선언, 아웃 → '아웃' 선언",
            "폴트 선언: '폴트' 또는 '사이드아웃'",
            "점수 선언: '서브팀 점수 - 상대팀 점수 - 서버 번호 (복식)'",
            "키친 폴트: '키친' 또는 '논볼리존 폴트' 선언",
        ],
        "modified_for_class": {
            "초등": {"players": "복식(2 vs 2)", "duration": "7점 선취", "modifications": ["스펀지/폼 공 사용", "키친 규칙 생략", "바운드 후 타구만 허용", "랠리포인트제 적용"]},
            "중등": {"players": "단식 또는 복식", "duration": "11점 선취", "modifications": ["키친 규칙 적용", "더블바운스 규칙 적용", "랠리포인트제 적용"]},
            "고등": {"players": "단식 또는 복식", "duration": "11점 선취 × 2게임 선취", "modifications": ["정식 피클볼 규칙 적용"]},
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
        "fouls": ["서브 시 공을 숨기거나 몸 뒤에서 타구", "테이블 움직이기", "자유 손이 테이블에 닿기", "연속 2회 타구"],
        "referee_guide": [
            "주심 1명이 테이블 옆에서 진행",
            "득점 선언: '서브팀 점수 - 리시브팀 점수'",
            "렛 선언: '렛' 호칭 후 재서브 지시",
            "에지볼 (테이블 모서리): 득점 인정",
            "서브 폴트: '폴트' 선언 후 상대 득점",
        ],
        "modified_for_class": {
            "초등": {"players": "단식", "duration": "7점 선취", "modifications": ["더 큰 공 사용 (폼볼)", "서브 규칙 간소화", "네트 높이 낮추기"]},
            "중등": {"players": "단식 또는 복식", "duration": "11점 선취 × 5게임", "modifications": ["서브 규칙 기본 적용", "복식 서브 위치 간소화"]},
            "고등": {"players": "단식 또는 복식", "duration": "11점 선취 × 7게임", "modifications": ["정식 규칙 적용"]},
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
        "fouls": ["오버 더 넷 (네트 너머로 라켓이 넘어감)", "네트 터치", "언더핸드 서브 위반", "두 번 연속 치기"],
        "referee_guide": [
            "주심: 네트 기둥 옆 심판석에 위치",
            "득점 선언: '서브팀 점수 - 리시브팀 점수 (서브)'",
            "인: 엄지 들기 또는 라인 방향 손짓",
            "아웃: 양팔 수평으로 벌리기",
            "렛: 양 손바닥을 위로 들기 (재서브)",
        ],
        "modified_for_class": {
            "초등": {"players": "단식 또는 복식", "duration": "11점 선취", "modifications": ["바운드 1회 허용", "서비스 박스 구분 없음", "소프트 셔틀콕 사용"]},
            "중등": {"players": "단식 또는 복식", "duration": "15점 선취 × 3게임", "modifications": ["서브 규칙 간소화", "서비스 폴트 1회 허용"]},
            "고등": {"players": "단식 또는 복식", "duration": "21점 선취 × 3게임", "modifications": ["정식 규칙 적용"]},
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
        ],
        "fouls": ["파울볼 (3번째 파울은 아웃)", "주자가 베이스 밟지 않고 진루", "타구한 공이 1루 도달 전에 잡힘"],
        "referee_guide": [
            "주심은 홈베이스 뒤에 위치",
            "아웃 신호: 오른손 주먹 들어올리기",
            "세이프 신호: 양팔 수평으로 벌리기",
            "파울: '파울' 선언 + 양팔 수평",
        ],
        "modified_for_class": {
            "초등": {"players": "5 vs 5", "duration": "3이닝", "modifications": ["스펀지볼 사용", "베이스 간격 12m로 축소", "아웃 없이 모두 타격 후 교대"]},
            "중등": {"players": "7 vs 7", "duration": "5이닝", "modifications": ["정식 아웃 규칙 적용", "도루 없음"]},
            "고등": {"players": "9 vs 9", "duration": "7이닝", "modifications": ["정식 티볼 규칙 적용"]},
        },
    },
    "테니스": {
        "name": "테니스", "english": "Tennis",
        "players": {"official": "단식(1 vs 1) 또는 복식(2 vs 2)", "min": 1},
        "duration": "남자: 5세트 중 3세트 선취, 여자/학교: 3세트 중 2세트 선취",
        "field": "단식: 23.77m × 8.23m, 복식: 23.77m × 10.97m (네트 높이: 중앙 91.4cm)",
        "basic_rules": [
            "서브: 베이스라인 뒤에서 대각선 서비스 박스로 오버핸드 타구",
            "포인트 계산: 0 → 15 → 30 → 40 → 게임 (듀스 시 2점 차 선취)",
            "6게임 선취 시 세트 승리 (5-5 시 타이브레이크 또는 7-5 선취)",
            "서브 실패 2회(더블폴트) 시 상대 득점",
            "공이 라인에 닿으면 인바운드",
            "네트 맞고 서비스 박스에 들어가면 렛(재서브)",
        ],
        "fouls": ["서브가 서비스 박스 밖에 떨어짐 (폴트)", "서브 시 베이스라인 밟기 (풋폴트)", "공이 2회 바운드 후 타구", "네트 터치", "공을 2번 연속 타구"],
        "referee_guide": [
            "주심: 심판대에서 전체 경기 진행",
            "선심: 각 라인별 인/아웃 판정",
            "아웃 콜: '아웃' 선언 + 한 팔 수평으로 뻗기",
            "폴트: '폴트' 선언",
            "렛: '렛' 선언 후 재서브",
            "점수 선언: 서버 점수 먼저 '15-0', '30-15' 등으로 선언",
        ],
        "modified_for_class": {
            "초등": {"players": "단식 또는 복식", "duration": "4게임 선취 × 3세트", "modifications": ["슬로볼(빨간색 볼) 사용", "코트 크기 1/2로 축소", "드롭 서브 또는 손으로 토스 후 타격", "포인트 1점씩 카운트"]},
            "중등": {"players": "단식 또는 복식", "duration": "6게임 선취 × 3세트", "modifications": ["슬로볼(오렌지색 볼) 또는 일반 볼", "더블폴트 1회 허용", "정식 포인트 계산 적용"]},
            "고등": {"players": "단식 또는 복식", "duration": "6게임 선취 × 3세트 중 2세트", "modifications": ["정식 테니스 규칙 적용"]},
        },
    },
}

LESSON_PLAN_DATA = {
    "축구": {
        "equipment": ["축구공 (학생 2~3명당 1개)", "미니 골대 또는 콘 골대", "콘 (코트 표시용)", "팀 구분 조끼"],
        "safety": [
            "수업 전 운동장 위험 요소(돌, 유리 등) 제거 확인",
            "신발 끈 단단히 묶기 및 정강이 보호대 착용 권장",
            "슬라이딩 태클 금지",
            "충돌 방지를 위한 충분한 활동 공간 확보",
            "더운 날씨: 수분 보충 및 그늘 휴식 보장",
        ],
        "key_skills": ["드리블", "패스 (인사이드킥)", "트래핑", "슈팅", "수비 위치"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "공과 친해지기", "content": "발로 공 굴리기, 세우기, 인사이드킥 기본 자세"},
                {"range": "3~4차시", "topic": "패스와 트래핑", "content": "짝끼리 패스 연습, 발 안쪽으로 트래핑 연습"},
                {"range": "5~6차시", "topic": "슈팅", "content": "콘 골대 향해 슛 연습, 간이 1 vs 1 게임"},
                {"range": "7~8차시", "topic": "미니 게임", "content": "5 vs 5 변형 경기, 규칙 적용 및 팀워크"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "드리블·패스·트래핑 기술 점검 및 교정"},
                {"range": "3~4차시", "topic": "공격 전술", "content": "삼각 패스, 침투 패스, 슈팅 기술 연습"},
                {"range": "5~6차시", "topic": "수비 전술", "content": "1대1 수비, 공간 수비, 수비 대형 이해"},
                {"range": "7~8차시", "topic": "경기 적용", "content": "7 vs 7 경기 운영, 규칙 적용 및 심판 실습"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "포메이션 이해", "content": "4-3-3, 4-4-2 포메이션 및 포지션 역할"},
                {"range": "3~4차시", "topic": "세트피스", "content": "코너킥, 프리킥 전술 연습"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "팀별 전술 적용 경기, 자기 평가"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["드리블 10m 이동 성공 여부", "짝 패스 10회 연속 성공", "경기 참여 태도 및 협동심"],
            "중등": ["드리블 돌기 기록 측정", "패스 정확도 (10회 중 성공 횟수)", "게임 내 규칙 준수 및 포지션 이해"],
            "고등": ["기술 수행 능력 (드리블·패스·슛)", "전술 이해도 및 경기 운영", "협동심·페어플레이·심판 능력"],
        },
    },
    "농구": {
        "equipment": ["농구공 (학생 2~3명당 1개)", "농구 골대 (높이 조절 가능하면 좋음)", "콘 (코트 표시용)", "팀 구분 조끼"],
        "safety": [
            "손가락 부상 주의 — 공을 받을 때 손가락을 펴지 않도록 지도",
            "충돌 방지를 위한 코트 경계 확인",
            "점프 착지 시 무릎 구부리기 지도",
            "팔꿈치 사용 금지 교육",
            "농구화 또는 미끄럼 방지 운동화 착용",
        ],
        "key_skills": ["드리블", "패스 (체스트·바운드·오버헤드)", "레이업슛", "점프슛", "수비 자세"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "드리블 기초", "content": "제자리 드리블, 이동 드리블, 방향 전환"},
                {"range": "3~4차시", "topic": "패스와 캐치", "content": "체스트 패스, 바운드 패스 짝 연습"},
                {"range": "5~6차시", "topic": "슛 연습", "content": "레이업슛 기본 동작, 낮은 골대에서 슛 연습"},
                {"range": "7~8차시", "topic": "3 vs 3 게임", "content": "변형 규칙으로 미니 경기, 팀워크 강조"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "드리블·패스·슛 기술 점검 및 교정"},
                {"range": "3~4차시", "topic": "레이업 & 점프슛", "content": "레이업슛 좌우 연습, 간이 점프슛"},
                {"range": "5~6차시", "topic": "공격·수비 전술", "content": "스크린·픽앤롤, 맨투맨 수비 이해"},
                {"range": "7~8차시", "topic": "5 vs 5 경기", "content": "정식 규칙 경기 운영 및 심판 실습"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "전술 이해", "content": "존 디펜스·맨투맨 비교, 공격 패턴"},
                {"range": "3~4차시", "topic": "특수 기술", "content": "더블팀, 프레스, 패스트 브레이크"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "전술 적용 경기, 영상 분석 (가능 시)"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["드리블 왕복 10m 기록", "패스 정확도 (짝끼리 10회)", "경기 참여 태도"],
            "중등": ["레이업슛 성공률 (10회 중)", "드리블 돌기 기록", "게임 내 규칙 준수·협동심"],
            "고등": ["슛 성공률·기술 완성도", "전술 이해 및 경기 운영", "리더십·협동심·페어플레이"],
        },
    },
    "배구": {
        "equipment": ["배구공 (팀당 2~3개)", "배구 네트 (높이 조절형)", "라인 표시 콘 또는 테이프"],
        "safety": [
            "손목·손가락 부상 주의 — 언더핸드 기본 자세 철저히 교육",
            "점프 착지 시 발목 접질림 주의",
            "네트 기둥 주변 충돌 방지",
            "서브 타구 전 반드시 수비 준비 확인",
            "밀집된 공간에서 백스윙 주의",
        ],
        "key_skills": ["언더핸드 패스 (리시브)", "오버핸드 패스 (토스)", "서브 (언더·플로트)", "스파이크 기초", "블로킹"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "언더핸드 패스", "content": "기본 자세, 짝끼리 언더 패스 연습"},
                {"range": "3~4차시", "topic": "오버핸드 패스", "content": "손 모양 만들기, 오버 패스 짝 연습"},
                {"range": "5~6차시", "topic": "서브", "content": "언더핸드 서브 연습, 네트 넘기기"},
                {"range": "7~8차시", "topic": "소프트 배구 게임", "content": "4 vs 4 변형 경기 (바운드 1회 허용)"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "언더·오버 패스 정확도 점검 및 교정"},
                {"range": "3~4차시", "topic": "서브 & 리시브", "content": "플로트 서브, 3단 연결 (서브→리시브→토스)"},
                {"range": "5~6차시", "topic": "스파이크 기초", "content": "스파이크 도움닫기·타이밍, 간이 스파이크"},
                {"range": "7~8차시", "topic": "6 vs 6 경기", "content": "정식 규칙 경기 운영, 로테이션 적용"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "포지션 역할", "content": "세터·리베로·스파이커 역할 이해"},
                {"range": "3~4차시", "topic": "전술 연습", "content": "조합 공격 (A·B·C 퀵), 수비 대형"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "전술 적용 경기, 자기·동료 평가"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["언더 패스 10회 연속 성공 여부", "서브 성공률 (10회 중)", "경기 참여 태도"],
            "중등": ["3단 연결 성공률", "서브 성공률 및 정확도", "게임 내 규칙 준수·로테이션"],
            "고등": ["기술 완성도 (패스·서브·스파이크)", "전술 이해 및 포지션 역할", "협동심·경기 운영 능력"],
        },
    },
    "야구": {
        "equipment": ["소프트볼 또는 고무공 (학생 2명당 1개)", "배트 (소프트 배트 권장)", "글러브 (1인 1개)", "베이스 4개", "타격 헬멧"],
        "safety": [
            "배트 스윙 반경 3m 이내 접근 금지 철저 교육",
            "타격 시 반드시 헬멧 착용",
            "투구 전 수비 준비 확인 신호 필수",
            "글러브 없이 딱딱한 공 받기 금지",
            "베이스 슬라이딩 시 발목 부상 주의",
        ],
        "key_skills": ["던지기 (오버핸드)", "받기 (글러브 사용)", "타격 (스윙 자세)", "주루 (베이스 밟기)", "수비 위치"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "던지기·받기", "content": "오버핸드 던지기 자세, 짝끼리 캐치볼"},
                {"range": "3~4차시", "topic": "타격 기초", "content": "티볼 스탠드에서 타격 자세, 스윙 연습"},
                {"range": "5~6차시", "topic": "주루", "content": "베이스 밟기, 1~2루 주루 연습"},
                {"range": "7~8차시", "topic": "티볼 게임", "content": "5 vs 5 티볼 경기 (전원 타격 후 교대)"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "캐치볼·타격 자세 점검, 슬로피치 적응"},
                {"range": "3~4차시", "topic": "수비", "content": "포지션별 수비 역할, 송구 연습"},
                {"range": "5~6차시", "topic": "타격 & 주루", "content": "타격 후 주루 연계 연습, 번트 기초"},
                {"range": "7~8차시", "topic": "슬로피치 경기", "content": "9 vs 9 슬로피치 경기, 규칙 적용"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "전술 이해", "content": "타순·포지션 전략, 번트·도루 상황 판단"},
                {"range": "3~4차시", "topic": "투구 & 수비", "content": "기본 투구 연습, 내야 수비 연계"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "7이닝 정식 경기 운영"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["타격 성공률 (10회 중)", "캐치볼 연속 성공 횟수", "경기 참여 태도 및 안전 수칙 준수"],
            "중등": ["타격 정확도 (페어볼 비율)", "수비 포지션 이해 및 송구 정확도", "규칙 준수·주루 판단"],
            "고등": ["타격·수비·주루 기술 완성도", "전술 이해 및 상황 판단", "팀워크·리더십·페어플레이"],
        },
    },
    "피클볼": {
        "equipment": ["피클볼 패들 (1인 1개)", "피클볼 (팀당 2~3개)", "이동식 네트 또는 콘 네트", "라인 표시 테이프 또는 콘"],
        "safety": [
            "패들 스윙 반경 내 타인 접근 주의",
            "빠른 방향 전환 시 발목 부상 주의",
            "키친(논볼리존) 라인 구분 명확히 표시",
            "공이 눈에 맞지 않도록 주의 (안경 착용 권장)",
            "미끄러운 바닥 주의 — 실내 운동화 필수",
        ],
        "key_skills": ["언더핸드 서브", "드라이브 (포핸드·백핸드)", "딩크 (소프트샷)", "발리", "키친 규칙 적용"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "패들과 친해지기", "content": "패들 그립, 공 튀기기, 짝끼리 랠리"},
                {"range": "3~4차시", "topic": "언더핸드 서브", "content": "서브 자세, 네트 넘기기 연습"},
                {"range": "5~6차시", "topic": "랠리 연습", "content": "포핸드·백핸드 기초, 짝 랠리 지속"},
                {"range": "7~8차시", "topic": "복식 게임", "content": "2 vs 2 변형 경기 (키친 규칙 생략)"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "서브·드라이브 점검, 키친 규칙 학습"},
                {"range": "3~4차시", "topic": "딩크 & 발리", "content": "딩크샷 연습, 키친 앞 발리 전술"},
                {"range": "5~6차시", "topic": "더블바운스 규칙 적용", "content": "3rd샷 드롭, 서브 후 전진 전술"},
                {"range": "7~8차시", "topic": "경기 운영", "content": "단식·복식 경기, 정식 점수 계산"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "전술 이해", "content": "스택 전형, 랠리 패턴 분석"},
                {"range": "3~4차시", "topic": "고급 기술", "content": "에로 (ATP), 롤 샷, 어니"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "복식 경기, 전술 적용 자기 평가"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["서브 성공률 (10회 중)", "랠리 지속 횟수 (짝과 함께)", "경기 참여 태도"],
            "중등": ["서브 정확도", "랠리 중 키친 규칙 준수", "경기 운영 및 점수 계산 능력"],
            "고등": ["기술 완성도 (서브·드라이브·딩크)", "전술 이해 및 경기 운영", "협동심·페어플레이"],
        },
    },
    "탁구": {
        "equipment": ["탁구대 (2~3인 1대)", "탁구 라켓 (1인 1개)", "탁구공 (충분히 준비)", "네트"],
        "safety": [
            "라켓 스윙 시 옆 사람 거리 확보",
            "탁구공 바닥에 굴러다닐 때 미끄럼 주의",
            "탁구대 모서리 충돌 주의",
            "라켓 무단 투척 금지 교육",
        ],
        "key_skills": ["포핸드 드라이브", "백핸드 푸시", "서브 (기본)", "스매시", "풋워크"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "라켓과 친해지기", "content": "그립 잡기, 공 튀기기 (바닥·라켓)"},
                {"range": "3~4차시", "topic": "포핸드 기초", "content": "포핸드 드라이브 자세, 짝 랠리"},
                {"range": "5~6차시", "topic": "서브 기초", "content": "간단한 서브 동작, 서브 후 랠리"},
                {"range": "7~8차시", "topic": "단식 게임", "content": "7점 선취 게임, 점수 계산 학습"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "포핸드·백핸드 점검, 자세 교정"},
                {"range": "3~4차시", "topic": "서브 & 리시브", "content": "다양한 서브 연습, 리시브 대응"},
                {"range": "5~6차시", "topic": "스매시 & 풋워크", "content": "스매시 타이밍, 사이드 스텝 연습"},
                {"range": "7~8차시", "topic": "단식·복식 경기", "content": "11점 선취 게임, 복식 서브 순서"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "루프 드라이브", "content": "루프 드라이브 기초, 랠리 전술"},
                {"range": "3~4차시", "topic": "서비스 전술", "content": "변화구 서브, 3구 공격 패턴"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "단식·복식 경기, 전술 적용"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["포핸드 랠리 연속 횟수", "서브 성공 여부", "경기 참여 태도 및 규칙 이해"],
            "중등": ["포핸드·백핸드 정확도", "서브 다양성 및 성공률", "경기 운영 및 점수 계산"],
            "고등": ["기술 완성도 (드라이브·서브·스매시)", "전술 이해 및 경기 운영", "집중력·페어플레이"],
        },
    },
    "배드민턴": {
        "equipment": ["배드민턴 라켓 (1인 1개)", "셔틀콕 (팀당 3~4개)", "배드민턴 네트", "라인 표시 테이프 또는 콘"],
        "safety": [
            "라켓 스윙 시 옆 사람 거리 (최소 1.5m) 확보",
            "셔틀콕이 눈에 맞지 않도록 주의",
            "빠른 방향 전환 시 발목 부상 주의",
            "실내 수업 시 미끄럼 방지 운동화 필수",
            "라켓 무단 투척 금지",
        ],
        "key_skills": ["언더핸드 서브", "클리어 (하이클리어)", "드롭샷", "스매시", "네트샷"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "라켓과 친해지기", "content": "그립, 셔틀콕 띄우기, 간이 랠리"},
                {"range": "3~4차시", "topic": "서브 기초", "content": "언더핸드 서브 자세, 네트 넘기기"},
                {"range": "5~6차시", "topic": "클리어 & 드롭", "content": "하이클리어 기초 동작 연습"},
                {"range": "7~8차시", "topic": "단식·복식 게임", "content": "11점 선취 변형 게임 (바운드 1회 허용)"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "서브·클리어·드롭 기술 점검 및 교정"},
                {"range": "3~4차시", "topic": "스매시 기초", "content": "스매시 타이밍, 점프 스매시 기초"},
                {"range": "5~6차시", "topic": "네트샷 & 풋워크", "content": "헤어핀 샷, 사이드 스텝 연습"},
                {"range": "7~8차시", "topic": "단식·복식 경기", "content": "21점 경기 운영, 심판 실습"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "전술 이해", "content": "단식 코트 공략법, 복식 포지션 역할"},
                {"range": "3~4차시", "topic": "고급 기술", "content": "드라이브, 푸시, 리버스 슬라이스"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "단식·복식 경기, 전술 적용 자기 평가"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["서브 성공률 (10회 중)", "랠리 지속 횟수", "경기 참여 태도"],
            "중등": ["서브·클리어 정확도", "스매시 성공률", "경기 운영 및 규칙 준수"],
            "고등": ["기술 완성도 (서브·스매시·네트샷)", "전술 이해 및 경기 운영", "집중력·협동심·페어플레이"],
        },
    },
    "티볼": {
        "equipment": ["티볼 스탠드 (타자 1명당 1개)", "소프트볼 또는 스펀지볼", "소프트 배트", "베이스 4개", "타격 헬멧"],
        "safety": [
            "배트 스윙 반경 3m 이내 접근 절대 금지",
            "타격 시 반드시 헬멧 착용",
            "수비 위치 확인 후 타격 신호",
            "베이스 간 충돌 방지",
            "소프트 재질 공·배트 사용으로 부상 최소화",
        ],
        "key_skills": ["타격 자세 (스탠스·스윙)", "던지기·받기", "주루 (베이스 밟기)", "수비 위치 이해"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "던지기·받기", "content": "오버핸드 던지기, 짝끼리 캐치볼"},
                {"range": "3~4차시", "topic": "타격 기초", "content": "티 위 공 타격 자세, 스윙 연습"},
                {"range": "5~6차시", "topic": "주루", "content": "1루 주루, 베이스 순서 익히기"},
                {"range": "7~8차시", "topic": "티볼 게임", "content": "5 vs 5 게임 (전원 타격 후 교대)"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "캐치볼·타격 자세 점검 및 교정"},
                {"range": "3~4차시", "topic": "수비", "content": "포지션별 역할, 내야 송구 연습"},
                {"range": "5~6차시", "topic": "타격 & 주루 연계", "content": "타격 후 주루 판단 연습"},
                {"range": "7~8차시", "topic": "티볼 경기", "content": "7 vs 7 정식 경기 운영, 규칙 적용"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "전술 이해", "content": "타순 배치, 포지션 전략"},
                {"range": "3~4차시", "topic": "특수 기술", "content": "번트, 히트앤런 상황 연습"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "9 vs 9 정식 티볼 경기"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["타격 성공률 (10회 중 페어볼)", "캐치볼 성공 횟수", "경기 참여 태도 및 안전 수칙 준수"],
            "중등": ["타격 정확도 (페어볼 비율)", "수비 포지션 이해", "규칙 준수·주루 판단"],
            "고등": ["타격·수비·주루 기술 완성도", "전술 이해 및 상황 판단", "팀워크·리더십"],
        },
    },
    "테니스": {
        "equipment": ["테니스 라켓 (1인 1개)", "테니스공 (학생 2명당 3~4개)", "이동식 네트", "라인 표시 테이프 또는 콘"],
        "safety": [
            "라켓 스윙 반경 내 타인 접근 주의 (최소 2m)",
            "공이 눈에 맞지 않도록 안전 교육",
            "빠른 방향 전환 시 발목 부상 주의",
            "서브 전 상대방 준비 확인 필수",
            "테니스화 또는 미끄럼 방지 운동화 착용",
        ],
        "key_skills": ["포핸드 그라운드스트로크", "백핸드 그라운드스트로크", "서브 (언더·오버핸드)", "발리", "풋워크"],
        "sessions": {
            "초등": [
                {"range": "1~2차시", "topic": "라켓과 친해지기", "content": "그립, 공 튀기기, 짝끼리 랠리 (슬로볼)"},
                {"range": "3~4차시", "topic": "포핸드 기초", "content": "포핸드 스윙 자세, 네트 넘기기"},
                {"range": "5~6차시", "topic": "서브 기초", "content": "드롭 서브 또는 토스 후 타격"},
                {"range": "7~8차시", "topic": "미니 게임", "content": "축소 코트 경기, 1점씩 카운트"},
            ],
            "중등": [
                {"range": "1~2차시", "topic": "기본기 점검", "content": "포핸드·백핸드 자세 점검 및 교정"},
                {"range": "3~4차시", "topic": "서브 & 리턴", "content": "오버핸드 서브 기초, 리턴 연습"},
                {"range": "5~6차시", "topic": "발리 & 스매시", "content": "네트 앞 발리 자세, 오버헤드 스매시"},
                {"range": "7~8차시", "topic": "단식·복식 경기", "content": "6게임 선취 경기, 정식 점수 계산"},
            ],
            "고등": [
                {"range": "1~2차시", "topic": "전술 이해", "content": "베이스라인·네트 전술, 서브앤발리"},
                {"range": "3~4차시", "topic": "고급 기술", "content": "탑스핀·슬라이스, 로브·패싱샷"},
                {"range": "5~6차시", "topic": "실전 경기", "content": "단식·복식 경기, 전술 적용 자기 평가"},
                {"range": "7~8차시", "topic": "리그전 및 평가", "content": "반 내 리그 경기 및 수행평가"},
            ],
        },
        "assessment": {
            "초등": ["포핸드 랠리 지속 횟수", "서브 성공률 (10회 중)", "경기 참여 태도"],
            "중등": ["포핸드·백핸드 정확도", "서브 성공률 및 방향", "경기 운영 및 점수 계산"],
            "고등": ["기술 완성도 (서브·그라운드스트로크·발리)", "전술 이해 및 경기 운영", "집중력·페어플레이"],
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
                    "sport_name": {"type": "string", "description": "종목명 (예: 축구, 농구, 배구, 야구, 피클볼, 탁구, 배드민턴, 티볼, 테니스)"}
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
                    "grade": {"type": "string", "description": "학교급 (초등, 중등, 고등)", "enum": ["초등", "중등", "고등"]},
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
                    "keyword": {"type": "string", "description": "검색 키워드 (예: 네트, 라켓, 이닝)"}
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="generate_lesson_plan",
            description="특정 종목과 학교급에 맞는 체육 수업 계획서를 생성합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "sport_name": {"type": "string", "description": "종목명"},
                    "grade": {"type": "string", "description": "학교급 (초등, 중등, 고등)", "enum": ["초등", "중등", "고등"]},
                    "total_sessions": {"type": "integer", "description": "총 차시 수 (기본값: 8)", "default": 8},
                    "students_count": {"type": "integer", "description": "학생 수 (기본값: 30)", "default": 30},
                },
                "required": ["sport_name", "grade"],
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

    elif name == "generate_lesson_plan":
        sport_name = arguments.get("sport_name", "")
        grade = arguments.get("grade", "중등")
        total_sessions = arguments.get("total_sessions", 8)
        students_count = arguments.get("students_count", 30)

        sport = find_sport(sport_name)
        if not sport:
            return [TextContent(type="text", text=f"'{sport_name}' 종목을 찾을 수 없습니다.")]

        plan = LESSON_PLAN_DATA.get(sport["name"])
        if not plan:
            return [TextContent(type="text", text=f"'{sport_name}' 수업 계획 데이터가 없습니다.")]

        modified = sport["modified_for_class"].get(grade, {})
        sessions = plan["sessions"].get(grade, [])
        assessment = plan["assessment"].get(grade, [])

        lines = [f"# {sport['name']} 체육 수업 계획서 ({grade})\n"]

        lines.append("## 기본 정보\n")
        lines.append(f"| 항목 | 내용 |")
        lines.append(f"|------|------|")
        lines.append(f"| 대상 | {grade} |")
        lines.append(f"| 총 차시 | {total_sessions}차시 |")
        lines.append(f"| 학생 수 | {students_count}명 |")
        lines.append(f"| 경기 인원 | {modified.get('players', '-')} |")
        lines.append(f"| 경기장 | {sport['field']} |\n")

        lines.append("## 학습 목표\n")
        for i, skill in enumerate(plan["key_skills"], 1):
            lines.append(f"{i}. {skill}의 기본 기술을 익히고 경기에 적용할 수 있다.")

        lines.append("\n## 준비물\n")
        for item in plan["equipment"]:
            lines.append(f"- {item}")

        lines.append("\n## ⚠️ 안전 지도 사항\n")
        for safety in plan["safety"]:
            lines.append(f"- {safety}")

        lines.append("\n## 차시별 수업 계획\n")
        lines.append("| 차시 | 주제 | 주요 내용 |")
        lines.append("|------|------|-----------|")
        for s in sessions:
            lines.append(f"| {s['range']} | {s['topic']} | {s['content']} |")

        lines.append("\n## 기본 수업 흐름 (매 차시 50분 기준)\n")
        lines.append("### 도입 (10분)")
        lines.append("- 출석 확인 및 용구 배부")
        lines.append("- 준비운동 (스트레칭 5분 + 동적 워밍업 5분)")
        lines.append("- 전 차시 복습 및 오늘 학습 목표 제시\n")
        lines.append("### 전개 (30분)")
        lines.append(f"- 기능 연습 (15분): {', '.join(plan['key_skills'][:3])} 기술 집중 연습")
        lines.append(f"- 게임 적용 (15분): {modified.get('players', '팀')} {modified.get('duration', '변형 경기')}\n")
        lines.append("### 정리 (10분)")
        lines.append("- 정리운동 (스트레칭 5분)")
        lines.append("- 학습 내용 정리 및 질의응답")
        lines.append("- 다음 차시 예고 및 용구 정리")

        lines.append("\n## 평가 기준\n")
        lines.append("| 평가 항목 | 내용 |")
        lines.append("|-----------|------|")
        for i, item in enumerate(assessment, 1):
            lines.append(f"| 평가 {i} | {item} |")

        lines.append("\n## 변형 규칙 요약\n")
        for mod in modified.get("modifications", []):
            lines.append(f"- {mod}")

        return [TextContent(type="text", text="\n".join(lines))]

    return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
