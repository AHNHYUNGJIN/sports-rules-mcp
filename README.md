# 스포츠 규칙 검색 MCP

체육 수업에서 바로 쓸 수 있는 스포츠 규칙 검색 MCP 서버입니다.

## 지원 종목

축구 · 농구 · 배구 · 배드민턴 · 탁구 · 핸드볼 · 티볼 · 플로어볼 · 킨볼

## 설치

```bash
pip install sports-rules-mcp
```

## Claude Code에 등록

```bash
claude mcp add sports-rules -- python -m sports_rules_mcp
```

## 제공 도구

| 도구 | 설명 |
|------|------|
| `list_sports` | 지원 종목 전체 목록 |
| `get_sport_rules` | 종목별 기본 규칙 + 반칙 |
| `get_modified_rules` | 학교급별 수업용 변형 규칙 (초등/중등/고등) |
| `get_referee_guide` | 심판 방법 및 신호 동작 |
| `search_sports` | 키워드로 종목 검색 |

## 사용 예시

Claude에게 이렇게 물어보세요:

- "배구 중등 수업용 변형 규칙 알려줘"
- "핸드볼 심판 신호 동작 뭐야?"
- "네트 쓰는 종목 검색해줘"
- "초등 축구 몇 명이서 해?"

## 라이선스

MIT
