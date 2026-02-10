# Moalog Backend - 프로젝트 분석

## 프로젝트 개요

**Moalog** - 팀 회고록 작성을 도와주는 AI 기반 서비스의 Rust 백엔드. YAPP 27기 Web 3팀 프로젝트.

## 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Rust (Edition 2021) |
| 웹 프레임워크 | Axum 0.7 |
| 비동기 런타임 | Tokio |
| DB | MySQL + SeaORM |
| AI | OpenAI API (gpt-4o-mini, async-openai) |
| 인증 | JWT (jsonwebtoken) + OAuth (카카오/구글) |
| API 문서 | utoipa + Swagger UI |
| PDF | genpdf |
| 검증 | validator |
| 로깅 | tracing |
| HTTP 클라이언트 | reqwest |
| 에러 처리 | thiserror |

## 디렉토리 구조

```
codes/server/src/
├── main.rs                  # 엔트리포인트, 라우터 정의, Swagger 설정
├── lib.rs                   # 라이브러리 루트
├── state.rs                 # AppState { db, config, ai_service }
│
├── config/
│   ├── mod.rs
│   ├── app_config.rs        # AppConfig (환경변수 로드)
│   └── database.rs          # DB 연결 + Auto-Schema + 마이그레이션
│
├── utils/
│   ├── mod.rs
│   ├── error.rs             # AppError enum (~40개 변형)
│   ├── response.rs          # BaseResponse<T>, ErrorResponse
│   ├── jwt.rs               # JWT 생성/검증 (access, refresh, signup)
│   ├── auth.rs              # 인증 유틸
│   ├── cookie.rs            # 쿠키 유틸
│   └── logging.rs           # tracing 초기화
│
├── global/
│   ├── mod.rs
│   └── middleware.rs         # request_id 미들웨어
│
├── domain/
│   ├── mod.rs
│   │
│   ├── auth/                # 인증 도메인
│   │   ├── mod.rs
│   │   ├── handler.rs       # 소셜로그인, 회원가입, 토큰갱신, 로그아웃
│   │   ├── service.rs       # OAuth 코드교환, 유저정보 조회, JWT 발급
│   │   └── dto.rs           # Request/Response DTO
│   │
│   ├── member/              # 회원 도메인
│   │   ├── mod.rs
│   │   ├── handler.rs       # 프로필 조회, 탈퇴
│   │   ├── service.rs       # 회원 비즈니스 로직
│   │   ├── dto.rs
│   │   └── entity/
│   │       ├── mod.rs
│   │       ├── member.rs            # 회원 (email, nickname, social_type, refresh_token)
│   │       ├── member_retro.rs      # 회원-회고 매핑 (status: DRAFT/SUBMITTED/ANALYZED)
│   │       ├── member_retro_room.rs # 회원-회고방 매핑 (role: OWNER/MEMBER, order_index)
│   │       ├── member_response.rs   # 회원-답변 매핑
│   │       └── assistant_usage.rs   # AI 어시스턴트 사용 기록
│   │
│   ├── retrospect/          # 회고 도메인 (핵심)
│   │   ├── mod.rs
│   │   ├── handler.rs       # 30+ API 핸들러
│   │   ├── service.rs       # 회고방/회고/답변/댓글/좋아요/검색/PDF 비즈니스 로직
│   │   ├── dto.rs           # 모든 Request/Response DTO
│   │   └── entity/
│   │       ├── mod.rs
│   │       ├── retro_room.rs        # 회고방 (title, invition_url, invite_code_created_at)
│   │       ├── retrospect.rs        # 회고 (title, insight, retrospect_method, start_time)
│   │       ├── response.rs          # 회고 답변 (question, content)
│   │       ├── response_comment.rs  # 답변 댓글 (content, member_id)
│   │       ├── response_like.rs     # 답변 좋아요 (member_id, response_id)
│   │       └── retro_reference.rs   # 참고자료 (title, url)
│   │
│   ├── ai/                  # AI 서비스
│   │   ├── mod.rs
│   │   ├── service.rs       # OpenAI 호출 (분석, 어시스턴트)
│   │   └── prompt.rs        # 프롬프트 템플릿
│   │
│   └── webhook/             # 웹훅 처리
│       ├── mod.rs
│       ├── discord_handler.rs
│       ├── github_handler.rs
│       └── dto.rs
│
├── event/                   # 이벤트 시스템 (MVP, 미사용)
│   ├── mod.rs
│   ├── event_types.rs       # Event, EventMetadata, Priority, Severity
│   ├── queue.rs             # EventQueue trait
│   ├── file_queue.rs        # FileEventQueue 구현
│   └── trigger.rs           # TriggerFilter, RateLimiter
│
├── monitoring/              # 로그 모니터링 (MVP, 미사용)
│   ├── mod.rs
│   ├── log_watcher.rs       # LogEntry, LogWatcher
│   ├── discord_alert.rs     # DiscordAlert
│   └── processor.rs         # EventProcessor
│
└── automation/              # AI 자동화 안전장치 (MVP)
    ├── mod.rs
    └── safety.rs
```

## 엔티티 (DB 테이블) 관계도

```
member (1) ──┬── (N) member_retro_room ──(N:1)── retro_room
             ├── (N) member_retro ──(N:1)── retrospect ──(N:1)── retro_room
             ├── (N) member_response ──(N:1)── response
             ├── (N) response_comment ──(N:1)── response
             ├── (N) response_like ──(N:1)── response
             └── (N) assistant_usage

retro_room (1) ──(N)── retrospect (1) ──┬── (N) response
                                         └── (N) retro_reference
```

### 엔티티 상세

| 테이블 | 주요 필드 | 설명 |
|--------|----------|------|
| `member` | email, nickname, social_type(KAKAO/GOOGLE), insight_count, refresh_token | 회원 |
| `retro_room` | title(unique, max 20), description, invition_url, invite_code_created_at | 회고방 |
| `retrospect` | title, insight, retrospect_method(KPT/FOUR_L/FIVE_F/PMI/FREE), start_time, retrospect_room_id | 회고 |
| `response` | question, content, retrospect_id | 회고 답변 |
| `response_comment` | content, response_id, member_id | 답변 댓글 |
| `response_like` | member_id, response_id (unique index) | 답변 좋아요 |
| `retro_reference` | title, url, retrospect_id | 참고자료 |
| `member_retro_room` | member_id, retrospect_room_id, role(OWNER/MEMBER), order_index | 회원-회고방 매핑 |
| `member_retro` | member_id, retrospect_id, status(DRAFT/SUBMITTED/ANALYZED), personal_insight, submitted_at | 회원-회고 매핑 |
| `member_response` | member_id, response_id | 회원-답변 매핑 |
| `assistant_usage` | member_id, created_at (인덱스: member_id+created_at) | AI 어시스턴트 사용 기록 |

### Enum 값

| Enum | 값 | 위치 |
|------|----|------|
| `SocialType` | KAKAO, GOOGLE | member.social_type |
| `RetrospectMethod` | KPT, FOUR_L, FIVE_F, PMI, FREE | retrospect.retrospect_method |
| `RetrospectStatus` | DRAFT, SUBMITTED, ANALYZED | member_retro.status |
| `RoomRole` | OWNER, MEMBER | member_retro_room.role |

## API 엔드포인트 (총 ~30개)

### Authentication (6개)

| Method | Path | Handler | 설명 |
|--------|------|---------|------|
| POST | `/api/v1/auth/social-login` | `social_login` | 소셜 로그인 (카카오/구글 인가코드 → JWT) |
| POST | `/api/v1/auth/signup` | `signup` | 회원가입 완료 (signup 토큰 → 닉네임 설정) |
| POST | `/api/v1/auth/token/refresh` | `refresh_token` | 토큰 갱신 (refresh → new access+refresh) |
| POST | `/api/v1/auth/logout` | `logout` | 로그아웃 (refresh token 무효화) |
| POST | `/api/auth/login/email` | `login_by_email` | 이메일 로그인 (개발/테스트용) |
| GET | `/api/auth/test` | `auth_test` | 인증 테스트 |

### RetroRoom (7개)

| Method | Path | Handler | 설명 |
|--------|------|---------|------|
| POST | `/api/v1/retro-rooms` | `create_retro_room` | 회고방 생성 (INV-XXXX-XXXX 초대코드 자동생성) |
| GET | `/api/v1/retro-rooms` | `list_retro_rooms` | 내 회고방 목록 조회 |
| POST | `/api/v1/retro-rooms/join` | `join_retro_room` | 초대코드로 회고방 참여 |
| PATCH | `/api/v1/retro-rooms/order` | `update_retro_room_order` | 회고방 순서 변경 |
| PATCH | `/api/v1/retro-rooms/:retro_room_id/name` | `update_retro_room_name` | 회고방 이름 변경 |
| DELETE | `/api/v1/retro-rooms/:retro_room_id` | `delete_retro_room` | 회고방 삭제 |
| GET | `/api/v1/retro-rooms/:retro_room_id/members` | `list_retro_room_members` | 회고방 멤버 목록 |

### Retrospect (12개)

| Method | Path | Handler | 설명 |
|--------|------|---------|------|
| POST | `/api/v1/retrospects` | `create_retrospect` | 회고 생성 |
| POST | `/api/v1/retrospects/:id/participants` | `create_participant` | 참석자 추가 |
| GET | `/api/v1/retrospects/:id/references` | `list_references` | 참고자료 목록 |
| PUT | `/api/v1/retrospects/:id/drafts` | `save_draft` | 임시저장 |
| GET | `/api/v1/retrospects/:id` | `get_retrospect_detail` | 회고 상세 조회 |
| POST | `/api/v1/retrospects/:id/submit` | `submit_retrospect` | 회고 제출 |
| GET | `/api/v1/retrospects/storage` | `get_storage` | 보관함 (연도별 그룹핑) |
| POST | `/api/v1/retrospects/:id/analysis` | `analyze_retrospective_handler` | AI 종합 분석 |
| GET | `/api/v1/retrospects/search` | `search_retrospects` | 검색 |
| GET | `/api/v1/retrospects/:id/responses` | `list_responses` | 답변 목록 |
| GET | `/api/v1/retrospects/:id/export` | `export_retrospect` | PDF 내보내기 |
| DELETE | `/api/v1/retrospects/:id` | `delete_retrospect` | 회고 삭제 |

### Response & Comment (4개)

| Method | Path | Handler | 설명 |
|--------|------|---------|------|
| GET | `/api/v1/responses/:id/comments` | `list_comments` | 댓글 목록 |
| POST | `/api/v1/responses/:id/comments` | `create_comment` | 댓글 작성 |
| POST | `/api/v1/responses/:id/likes` | `toggle_like` | 좋아요 토글 |

### AI Assistant (1개)

| Method | Path | Handler | 설명 |
|--------|------|---------|------|
| POST | `/api/v1/retrospects/:retro_id/questions/:q_id/assistant` | `assistant_guide` | AI 작성 가이드 |

### Member (2개)

| Method | Path | Handler | 설명 |
|--------|------|---------|------|
| GET | `/api/v1/members/me` | `get_profile` | 내 프로필 조회 |
| POST | `/api/v1/members/withdraw` | `withdraw` | 서비스 탈퇴 |

## 주요 비즈니스 로직

### 회고 방식 5종

각 방식별 기본 질문이 내장되어 있음:

| 방식 | 질문 수 | 설명 |
|------|---------|------|
| KPT | 3개 | Keep-Problem-Try |
| 4L | 4개 | Liked-Learned-Lacked-Longed for |
| 5F | 5개 | Facts-Feelings-Findings-Future-Feedback |
| PMI | 3개 | Plus-Minus-Interesting |
| FREE | 5개 | 자유 형식 |

### 회고 플로우

```
회고방 생성 → 초대코드로 멤버 참여
    → 회고 생성 (방식 선택) → 참석자 추가 → 참고자료 등록
    → 답변 임시저장 (DRAFT) → 답변 제출 (SUBMITTED)
    → AI 종합 분석 (ANALYZED)
    → 댓글/좋아요 → PDF 내보내기
```

### AI 기능

1. **종합 분석** (`analyze_retrospective`): 팀 전체 회고 답변 → 감정 랭킹 3개 + 개인별 미션 3개 생성
2. **어시스턴트** (`generate_assistant_guide`): 질문별 작성 가이드 1~3개 생성 (초기 가이드 / 맞춤 가이드)
3. 모델: `gpt-4o-mini`, temperature 0.7, max_tokens 4000, timeout 30초

### 인증 플로우

```
카카오/구글 인가코드
  → OAuth 코드 교환 (access_token)
  → 유저 정보 조회 (email)
  → DB 조회
    ├── 기존 회원 → access_token + refresh_token 발급
    └── 신규 회원 → signup_token 발급 → 닉네임 설정 → access_token + refresh_token 발급
```

- Access Token: 30분 (기본)
- Refresh Token: 14일 (기본, jti로 고유성 보장)
- Signup Token: 10분 (email + provider 포함)

## 아키텍처 패턴

### 레이어 구조

```
handler (HTTP 요청/응답) → service (비즈니스 로직) → entity (SeaORM 모델/DB)
```

### 응답 형식

```json
{
  "isSuccess": true,
  "code": "COMMON200",
  "message": "성공입니다.",
  "result": { ... }
}
```

에러 시:
```json
{
  "isSuccess": false,
  "code": "RETRO4041",
  "message": "존재하지 않는 회고입니다.",
  "result": null
}
```

### 에러 코드 체계

| 접두사 | 도메인 |
|--------|--------|
| COMMON | 공통 (400, 403, 404, 409, 500) |
| AUTH | 인증 (4001~4005) |
| RETRO | 회고방/회고 (4001~4221) |
| RES | 답변 (4001, 4041) |
| AI | AI 서비스 (4031~5031) |
| SEARCH | 검색 (4001) |
| MEMBER | 회원 (4042) |

### DB 스키마 관리

- SeaORM의 `create_table_from_entity`로 Auto-Schema 지원
- `DB_SCHEMA_UPDATE=true` 환경변수로 활성화
- `apply_migrations()`로 수동 ALTER TABLE (컬럼 추가 등)
- 테이블 생성 순서: 독립 엔티티 → 1단계 의존 → 2단계 의존 (FK 순서)

### CORS 허용 도메인

- `localhost:3000`, `localhost:5173`, `localhost:5174` (개발)
- `moalog.me`, `www.moalog.me`, `moaofficial.kr` (프로덕션)

## 환경변수

```env
# Database
DATABASE_URL=mysql://localhost:3306/retrospect
DB_SCHEMA_UPDATE=false

# Server
SERVER_PORT=8080

# JWT
JWT_SECRET=
JWT_EXPIRATION=1800
REFRESH_TOKEN_EXPIRATION=1209600
SIGNUP_TOKEN_EXPIRATION=600

# Social Login
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
KAKAO_CLIENT_ID=
KAKAO_CLIENT_SECRET=

# AI
OPENAI_API_KEY=

# PDF
PDF_FONT_DIR=./fonts
PDF_FONT_FAMILY=NanumGothic
```

## MVP 모듈 (미사용)

`event/`, `monitoring/`, `automation/` 모듈은 AI 자동화 파이프라인을 위해 구조만 잡혀있으며, `#[allow(dead_code)]`로 표시됨. 이벤트 큐, 로그 감시, Discord 알림, 트리거 필터링 등의 인프라가 준비되어 있음.
