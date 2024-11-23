import requests
from pydantic import TypeAdapter

from core.commands import QuerypieRuleUpdateBaseCommand
from core.querypie.client import QuerypieAPIBase
from core.querypie.models import Rule, SensitiveFieldModel


class QuerypieAccessRuleAPI(QuerypieAPIBase):
    # https://{QUERYPIE_URL}/api/docs#tag/Policy-API 참조

    policy_uuid: str = None

    def __init__(self, policy_uuid: str):
        self.policy_uuid = policy_uuid

    def get_current_rules(self) -> list[Rule]:
        response = requests.get(
            f"{self.BASE_URL}/policies/{self.policy_uuid}/rules", headers=self.HEADERS
        )
        if not response.ok:
            raise Exception(
                f"현재 정책 조회중 오류 발생 {response.json()['error']['message']}"
            )
        return TypeAdapter(list[Rule]).validate_python(response.json())

    def create_rule(self, table_name, field_names: list[str]):
        response = requests.post(
            f"{self.BASE_URL}/policies/{self.policy_uuid}/data-accesses",
            json={
                "allowedUserUuids": [],
                "objectPath": [
                    self.DATABASE_NAME,
                    table_name,
                    f"/({'|'.join(field_names)})/i",
                ],
                "objectType": "COLUMN",
            },
            headers=self.HEADERS,
        )
        if not response.ok:
            raise Exception(
                f"정책 생성중 오류 발생 {response.json()['error']['message']}"
            )

    def delete_rule(self, rule_uuid):
        response = requests.delete(
            f"{self.BASE_URL}/policies/{self.policy_uuid}/rules/{rule_uuid}",
            headers=self.HEADERS,
        )
        if not response.ok:
            raise Exception(
                f"정책 삭제중 오류 발생 {response.json()['error']['message']}"
            )


class Command(QuerypieRuleUpdateBaseCommand):
    """
    민감 필드를 숨기는 커맨드
    """

    POLICY_NAME = "데이터 접근 정책"

    def _get_current_rules(self) -> list[Rule]:
        if self.dry_run:
            return []

        return QuerypieAccessRuleAPI(policy_uuid=self.policy_uuid).get_current_rules()

    def _create(self, model: SensitiveFieldModel):
        super()._create(model)

        if not self.dry_run:
            QuerypieAccessRuleAPI(policy_uuid=self.policy_uuid).create_rule(
                model.table_name, model.fields
            )

    def _update(self, rule: Rule, model: SensitiveFieldModel):
        super()._update(rule, model)

        if not self.dry_run:
            # Update API에서 컬럼을 수정하는 방법을 제공하지 않기 때문에 삭제 후 재생성
            QuerypieAccessRuleAPI(policy_uuid=self.policy_uuid).delete_rule(rule.uuid)
            QuerypieAccessRuleAPI(policy_uuid=self.policy_uuid).create_rule(
                model.table_name, model.fields
            )

    def _delete(self, rule: Rule):
        super()._delete(rule)

        if not self.dry_run:
            QuerypieAccessRuleAPI(policy_uuid=self.policy_uuid).delete_rule(rule.uuid)
