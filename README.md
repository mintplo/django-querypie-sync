# Django QueryPie Sync

Django 모델과 QueryPie 간의 데이터 정책 동기화를 자동화하는 사례를 공유하는 예제 프로젝트입니다.

## 주요 기능

- Django와 QueryPie의 통합 예제
- 데이터 정책 동기화 및 검증 커스텀 명령어 제공
- CI/CD 환경에서 데이터 접근 제어를 자동화

## 설치 및 실행

### 1. 사전 준비

- Python 3.11 이상
- Pipenv (Python 패키지 관리 도구)

### 2. 설치 방법

1. 저장소 클론:
   ```bash
   git clone https://github.com/mintplo/django-querypie-sync.git
   cd django-querypie-sync
   ```
2. 가상 환경 생성 및 패키지 설치:
   ```bash
   pipenv install --dev
   ```
3. 환경 활성화:
   ```bash
   pipenv shell
   ```

### 3. 쿼리파이 데이터 정책 동기화 실행 방법 (Only Command)
>[!NOTE]
> dry-run이 default로 설정되어 있으며, `--dry-run=False`로 설정하면 실제 동기화가 진행됩니다.

```bash
python manage.py querypie_access_rule_sync_command --policy-uuid=<POLICY_UUID>
```

**결과 예시:**
```bash
 [2024-11-23T07:16:19.593] [INFO] [commands.py:25] ---Start Command---
 [2024-11-23T07:16:19.594] [INFO] [commands.py:74] 현재 쿼리파이에 저장되어있는 [데이터 접근 정책]: 0
 [2024-11-23T07:16:19.594] [INFO] [commands.py:79] 현재 SensitiveFieldModel을 사용한 모델 개수: 2
 [2024-11-23T07:16:19.594] [INFO] [commands.py:83] 동기화 시작
 [2024-11-23T07:16:19.594] [INFO] [commands.py:149] Create rule for company_employee, fields: ['email', 'phone_number', 'salary']
 [2024-11-23T07:16:19.594] [INFO] [commands.py:149] Create rule for company_department, fields: ['name']
 [2024-11-23T07:16:19.594] [INFO] [commands.py:90] [데이터 접근 정책] 2개 테이블의 규칙이 변경되었습니다.
 [2024-11-23T07:16:19.594] [INFO] [commands.py:91] 동기화 완료
 [2024-11-23T07:16:19.594] [INFO] [commands.py:31] ---End Command (Duration: 0:00:00.000294)---
```
