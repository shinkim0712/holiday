# kr-holiday-notion-sync

한국 공휴일(data.go.kr 특일 정보 API)을 Notion 데이터베이스에 매년 자동으로 동기화합니다.

## 필요한 Notion 데이터베이스 속성

| 속성명 | 타입 |
|---|---|
| 이름 | title |
| 날짜 | date |
| 구분 | select (옵션에 "공휴일" 포함) |

## 설정 방법 (자기 자신의 값으로 교체)

1. [notion.so/my-integrations](https://www.notion.so/my-integrations)에서 integration 생성 → 토큰 복사 → 대상 데이터베이스에 연결 초대
2. [data.go.kr](https://www.data.go.kr)에서 "한국천문연구원_특일 정보" API 활용신청 → Decoding 서비스키 복사
3. 이 저장소를 fork하거나 그대로 사용
4. 저장소 Settings → Secrets and variables → Actions에 아래 3개 등록
   - `NOTION_TOKEN`
   - `NOTION_DATABASE_ID`
   - `DATA_GO_KR_KEY`
5. Actions 탭에서 워크플로 수동 실행(Run workflow)으로 테스트

이후 매년 1월 1일 자동 실행됩니다.
