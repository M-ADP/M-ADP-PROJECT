# MADP Project Service API 문서

## 요약
- Base Path는 `/v1`이며 Health Check는 `/health`입니다.
- `/v1` 이하 모든 엔드포인트는 헤더 `user-id`, `role`이 필요합니다.
- 주요 리소스는 Projects, Ports, DNS이며 공통 응답 형식과 페이지네이션 규칙을 공유합니다.
- 공통 에러는 422(Validation)와 500(Internal Server Error)입니다.

## 목차
- [개요](#개요)
- [공통 응답 형식](#공통-응답-형식)
- [공통 헤더](#공통-헤더)
- [공통 에러](#공통-에러)
- [페이지네이션](#페이지네이션)
- [Health (상태 확인)](#health)
  - [GET /health (서비스 상태)](#get-health)
- [Projects (프로젝트)](#projects)
  - [POST /v1/projects (프로젝트 생성)](#post-v1projects)
  - [GET /v1/projects (프로젝트 목록 조회)](#get-v1projects)
  - [GET /v1/projects/{project_id} (프로젝트 상세 조회)](#get-v1projectsproject_id)
  - [PATCH /v1/projects/{project_id}/name (프로젝트 이름 변경)](#patch-v1projectsproject_idname)
  - [PATCH /v1/projects/{project_id}/resource (프로젝트 리소스 변경)](#patch-v1projectsproject_idresource)
  - [DELETE /v1/projects/{project_id} (프로젝트 삭제)](#delete-v1projectsproject_id)
- [Project Members (프로젝트 멤버)](#project-members)
  - [GET /v1/projects/{project_id}/members (멤버 목록 조회)](#get-v1projectsproject_idmembers)
  - [POST /v1/projects/{project_id}/members (멤버 추가)](#post-v1projectsproject_idmembers)
  - [DELETE /v1/projects/{project_id}/members/{nickname} (멤버 제거)](#delete-v1projectsproject_idmembersnickname)
  - [PATCH /v1/projects/{project_id}/owner (소유권 이전)](#patch-v1projectsproject_idowner)
- [Ports (포트)](#ports)
  - [POST /v1/projects/{project_id}/ports (포트 공개)](#post-v1projectsproject_idports)
  - [GET /v1/projects/{project_id}/ports (포트 목록 조회)](#get-v1projectsproject_idports)
  - [PUT /v1/projects/{project_id}/ports/{port_id} (포트 수정)](#put-v1projectsproject_idportsport_id)
  - [DELETE /v1/projects/{project_id}/ports/{port_id} (포트 삭제)](#delete-v1projectsproject_idportsport_id)
- [DNS (도메인)](#dns)
  - [POST /v1/projects/{project_id}/dns (DNS 생성)](#post-v1projectsproject_iddns)
  - [GET /v1/projects/{project_id}/dns-records (DNS 조회)](#get-v1projectsproject_iddns-records)
  - [DELETE /v1/projects/{project_id}/dns-records/{dns_id} (DNS 삭제)](#delete-v1projectsproject_iddns-recordsdns_id)
  - [PATCH /v1/projects/{project_id}/dns-records/{dns_id} (DNS 서브도메인 변경)](#patch-v1projectsproject_iddns-recordsdns_id)
  - [PATCH /v1/projects/{project_id}/dns-records/{dns_id}/port (DNS에 포트 바인딩)](#patch-v1projectsproject_iddns-recordsdns_idport)

## 개요
- Base Path: `/v1`
- Health Check: `/health`
- 인증/인가: `/v1` 이하 모든 엔드포인트는 헤더 `user-id`, `role` 필요

## 공통 응답 형식

### SuccessResponse
```json
{
  "message": "문자열",
  "data": {}
}
```

### ErrorResponse
```json
{
  "message": "문자열"
}
```

## 공통 헤더
| 헤더 | 타입 | 설명 |
| --- | --- | --- |
| user-id | string | 사용자 식별자 |
| role | string | 사용자 역할 |

## 공통 에러
- 422 Validation Error: 요청 파라미터/바디 유효성 오류 (FastAPI 기본)
- 500 Internal Server Error: 예외 처리되지 않은 오류

## 페이지네이션
### CursorPage
```json
{
  "items": [],
  "has_next": true
}
```

쿼리 파라미터:
- `cursor`: 다음 페이지 커서(이전 페이지 마지막 id)
- `limit`: 한 번에 가져올 개수 (기본 20, 1~100)

## Health
### GET /health
서비스 상태를 확인합니다.

응답 예시:
```json
{
  "status": "healthy",
  "service": "MADP Project Service"
}
```

---

## Projects

### POST /v1/projects
프로젝트 생성

요청 바디:
```json
{
  "name": "string",
  "max_cpu": 0.1,
  "max_memory": 32.0,
  "max_disk": 32.0
}
```

필드:
- `name` (string, 필수): 공백 제거, 최소 1자
- `max_cpu` (float, 선택): 기본 0.1, 0.1~4.0
- `max_memory` (float, 선택): 기본 32.0(MB), 32~4096
- `max_disk` (float, 선택): 기본 32.0(MB), 32~51200

응답 데이터: `ProjectResponse`
```json
{
  "id": "string",
  "user_id": "string",
  "name": "string",
  "max_cpu": 0.1,
  "max_memory": 32.0,
  "max_disk": 32.0
}
```

에러:
- 400: "프로젝트 생성 한도(3개)를 초과했습니다."
- 400: "프로젝트 이름은 고유해야 합니다."

내부 요청 API:
- ProjectResourceClient.create: namespace 생성

---

### GET /v1/projects
프로젝트 목록 조회

쿼리 파라미터: `cursor`, `limit`

응답 데이터: `CursorPage[ProjectListItemResponse]`
```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "my_role": "OWNER|MEMBER",
      "domain": "string|null",
      "deployment_summary": { "running": 0, "warning": 0 },
      "deployment_status": { "state": "RUNNING|STOPPED|FAILED", "message": "string" }
    }
  ],
  "has_next": true
}
```

필드 설명:
- `my_role`: 현재 요청 사용자의 프로젝트 내 역할 (OWNER: 소유자, MEMBER: 멤버)

내부 요청 API:
- DeploymentSummaryClient.get_summary_batch: 프로젝트 배포 요약 배치 조회

---

### GET /v1/projects/{project_id}
프로젝트 상세 조회

응답 데이터: `ProjectDetailResponse`
```json
{
  "id": "string",
  "name": "string",
  "my_role": "OWNER|MEMBER",
  "deployments": [
    {
      "id": "string",
      "name": "string",
      "runtime": "string|null",
      "pod_count": 0,
      "exposed_port": 80,
      "cpu_usage_percent": 0.0,
      "ram_usage_percent": 0.0,
      "health_status": "Healthy|Unhealthy|Stopped"
    }
  ],
  "cpu_usage": [{ "timestamp": "string", "value": 0.0 }],
  "memory_usage": [{ "timestamp": "string", "value": 0.0 }],
  "disk_usage": [{ "timestamp": "string", "value": 0.0 }],
  "network_usage": [{ "timestamp": "string", "value": 0.0 }],
  "traffic_per_hour": [{ "timestamp": "string", "value": 0.0 }],
  "ports": [
    {
      "id": "string",
      "project_id": "string",
      "from_ip": "string",
      "from_port": 80,
      "port_number": 6,
      "protocol": "tcp"
    }
  ]
}
```

필드 설명:
- `my_role`: 현재 요청 사용자의 프로젝트 내 역할 (OWNER: 소유자, MEMBER: 멤버)

에러:
- 404: "프로젝트를 찾을 수 없습니다."

내부 요청 API:
- ProjectResourceClient.get_usage: 최근 7일 리소스 사용량 조회
- DeploymentClient.list_by_project: 프로젝트 배포 목록 조회

---

### PATCH /v1/projects/{project_id}/name
프로젝트 이름 변경

요청 바디:
```json
{
  "name": "string"
}
```

필드:
- `name` (string, 필수): 공백 제거, 최소 1자

응답 데이터: `ProjectResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 400: "프로젝트 이름은 고유해야 합니다."

---

### PATCH /v1/projects/{project_id}/resource
프로젝트 리소스 변경

요청 바디 (모두 선택):
```json
{
  "max_cpu": 0.1,
  "max_memory": 32.0,
  "max_disk": 32.0
}
```

필드:
- `max_cpu` (float, 선택): 0.1~4.0
- `max_memory` (float, 선택): 32~4096 (MB)
- `max_disk` (float, 선택): 32~51200 (MB), 줄이기 불가

응답 데이터: `ProjectResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 400: "디스크 용량은 줄일 수 없습니다."

내부 요청 API:
- ProjectResourceClient.allocate: 리소스 쿼터 재할당

---

### DELETE /v1/projects/{project_id}
프로젝트 삭제

응답 데이터: `ProjectResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 403: "프로젝트 소유자만 프로젝트를 삭제할 수 있습니다."

내부 요청 API:
- ProjectResourceClient.delete: namespace 삭제

---

## Project Members
- 프로젝트 생성자는 최초 OWNER입니다.
- 소유권은 기존 OWNER가 같은 프로젝트의 MEMBER에게만 이전할 수 있습니다.
- 프로젝트 내 OWNER는 항상 1명입니다.

### GET /v1/projects/{project_id}/members
프로젝트 멤버 목록 조회

쿼리 파라미터: `cursor`, `limit`

응답 데이터: `CursorPage[ProjectMemberResponse]`
```json
{
  "items": [
    {
      "user_id": "string",
      "username": "string",
      "profile_image": "string|null",
      "role": "OWNER|MEMBER",
      "joined_at": "2024-01-01T00:00:00Z"
    }
  ],
  "has_next": true
}
```

필드 설명:
- `user_id`: 멤버의 사용자 식별자
- `username`: 멤버의 표시 이름
- `profile_image`: 프로필 이미지 URL (없으면 null)
- `role`: 프로젝트 내 역할 (OWNER: 소유자, MEMBER: 멤버)
- `joined_at`: 프로젝트 참여 일시

에러:
- 404: "프로젝트를 찾을 수 없습니다."

---

### POST /v1/projects/{project_id}/members
프로젝트에 멤버 추가 (사용자 초대)

요청 바디:
```json
{
  "nickname": "string"
}
```

필드:
- `nickname` (string, 필수): 초대할 사용자의 닉네임

응답 데이터: `ProjectMemberResponse`
```json
{
  "user_id": "string",
  "username": "string",
  "profile_image": "string|null",
  "role": "MEMBER",
  "joined_at": "2024-01-01T00:00:00Z"
}
```

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "사용자를 찾을 수 없습니다."
- 400: "이미 프로젝트에 참여 중인 사용자입니다."
- 403: "프로젝트 소유자만 멤버를 추가할 수 있습니다."

내부 요청 API:
- UserClient.get_user: 사용자 정보 조회 (username, profile_image)

---

### DELETE /v1/projects/{project_id}/members/{nickname}
프로젝트에서 멤버 제거

응답 데이터: `ProjectMemberResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "멤버를 찾을 수 없습니다."
- 400: "프로젝트 소유자는 제거할 수 없습니다."
- 403: "프로젝트 소유자만 멤버를 제거할 수 있습니다."

---

### PATCH /v1/projects/{project_id}/owner
프로젝트 소유권 이전

요청 바디:
```json
{
  "target_nickname": "string"
}
```

필드:
- `target_nickname` (string, 필수): 소유권을 이전할 대상 MEMBER 멤버의 닉네임

응답 데이터: `ProjectMemberResponse` (새 OWNER 정보 반환)

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "멤버를 찾을 수 없습니다."
- 400: "소유권은 MEMBER 멤버에게만 이전할 수 있습니다."
- 400: "자기 자신에게 소유권을 이전할 수 없습니다."
- 403: "프로젝트 소유자만 소유권을 이전할 수 있습니다."

---

## Ports

### POST /v1/projects/{project_id}/ports
포트 공개

요청 바디:
```json
{
  "from_ip": "string",
  "from_port": 1,
  "port_number": 6,
  "protocol": "tcp"
}
```

필드:
- `from_ip` (string, 필수): CIDR 또는 IP
- `from_port` (int, 선택): 1~65535
- `port_number` (int, 선택): 0~255 (IANA protocol number)
- `protocol` (string, 선택): tcp/udp/icmp

응답 데이터: `PortResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 400: "프로젝트 내에서 이미 사용 중인 포트입니다."

내부 요청 API:
- ProjectResourceClient.open_port: gateway 자원 생성

---

### GET /v1/projects/{project_id}/ports
포트 목록 조회

쿼리 파라미터: `cursor`, `limit`

응답 데이터: `CursorPage[PortResponse]`

에러:
- 404: "프로젝트를 찾을 수 없습니다."

---

### PUT /v1/projects/{project_id}/ports/{port_id}
포트 수정

요청 바디 (`PortCreate`와 동일):
```json
{
  "from_ip": "string",
  "from_port": 1,
  "port_number": 6,
  "protocol": "tcp"
}
```

필드:
- `from_ip` (string, 필수): CIDR 또는 IP
- `from_port` (int, 선택): 1~65535
- `port_number` (int, 선택): 0~255 (IANA protocol number)
- `protocol` (string, 선택): tcp/udp/icmp

응답 데이터: `PortResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "포트를 찾을 수 없습니다."
- 400: "프로젝트 내에서 이미 사용 중인 포트입니다."

내부 요청 API:
- ProjectResourceClient.update_port: gateway 자원 수정

---

### DELETE /v1/projects/{project_id}/ports/{port_id}
포트 삭제

응답 데이터: `PortResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "포트를 찾을 수 없습니다."

내부 요청 API:
- ProjectResourceClient.close_port: gateway 자원 삭제

---

## DNS

### POST /v1/projects/{project_id}/dns
DNS 생성

요청 바디:
```json
{
  "subdomain": "string"
}
```

필드:
- `subdomain` (string, 필수): 1~63자, 영문/숫자/하이픈, 하이픈 시작/끝 불가

응답 데이터: `DNSResponse`
```json
{
  "id": "string",
  "project_id": "string",
  "dns_name": "subdomain.mdeveloper.platform",
  "state": "PENDING|ACTIVE|FAILED|DELETED",
  "port_id": "string|null"
}
```

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 400: "프로젝트에 이미 DNS가 등록되어 있습니다."
- 400: "이미 사용 중인 DNS 이름입니다."

내부 요청 API:
- ProjectResourceClient.create_dns: ExternalDNS 자원 생성

---

### GET /v1/projects/{project_id}/dns-records
DNS 조회

응답 데이터: `DNSResponse | null`

에러:
- 404: "프로젝트를 찾을 수 없습니다."

---

### DELETE /v1/projects/{project_id}/dns-records/{dns_id}
DNS 삭제

응답 데이터: `DNSResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "DNS를 찾을 수 없습니다."

내부 요청 API:
- ProjectResourceClient.delete_dns: ExternalDNS 자원 삭제

---

### PATCH /v1/projects/{project_id}/dns-records/{dns_id}
DNS 서브도메인 변경

요청 바디:
```json
{
  "subdomain": "string"
}
```

필드:
- `subdomain` (string, 필수): 1~63자, 영문/숫자/하이픈, 하이픈 시작/끝 불가

응답 데이터: `DNSResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "DNS를 찾을 수 없습니다."
- 400: "이미 사용 중인 DNS 이름입니다."

내부 요청 API:
- ProjectResourceClient.update_dns: ExternalDNS 자원 수정

---

### PATCH /v1/projects/{project_id}/dns-records/{dns_id}/port
DNS에 포트 바인딩

요청 바디:
```json
{
  "port_id": "string"
}
```

필드:
- `port_id` (string, 필수): 바인딩할 공개 포트 ID

응답 데이터: `DNSResponse`

에러:
- 404: "프로젝트를 찾을 수 없습니다."
- 404: "DNS를 찾을 수 없습니다."
- 404: "포트를 찾을 수 없습니다."

내부 요청 API:
- ProjectResourceClient.mapping_dns_and_port: ExternalDNS 자원과 gateway 자원 매핑
