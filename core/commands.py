from abc import abstractmethod

import django.apps
from django.core.management import BaseCommand
from django.db import models
from django.utils import timezone

from core.logger import logger as CommonLogger
from core.models import SensitiveFieldMixin
from core.querypie.models import SensitiveFieldModel, Rule


class CommonBaseCommand(BaseCommand):
    command_name = None

    def __init__(self):
        self._init_logger()
        super().__init__()

    def _init_logger(self):
        self.logger = CommonLogger

    def handle(self, *args, **options) -> None:
        start_time = timezone.now()
        self.logger.info("---Start Command---")

        self.run(*args, **options)

        end_time = timezone.now()
        duration = end_time - start_time
        self.logger.info("---End Command (Duration: %s)---", duration)

    @abstractmethod
    def run(self, *args, **options) -> None:
        pass


class QuerypieRuleUpdateBaseCommand(CommonBaseCommand):
    POLICY_NAME = ""
    SENSITIVE_FIELD_NAME = "sensitive_fields"

    # SensitiveFieldModel를 추가해서 사용할 수 있습니다.
    ADDITIONAL_SENSITIVE_MODELS: list[SensitiveFieldModel] = []

    policy_uuid: str = None
    dry_run: bool = True

    def __init__(self):
        super(QuerypieRuleUpdateBaseCommand, self).__init__()
        self.changes = 0

    def add_arguments(self, parser):
        parser.add_argument(
            "--policy-uuid",
            type=str,
            dest="policy_uuid",
            help="Policy UUID",
            required=True,
        )
        parser.add_argument(
            "--dry-run",
            type=bool,
            dest="dry_run",
            help="Dry run with no api call",
            required=False,
            default=True,
        )

    def run(self, *args, **options):
        self.policy_uuid = options["policy_uuid"]
        self.dry_run = options["dry_run"]

        rules = self._get_current_rules()
        self.logger.info(
            f"현재 쿼리파이에 저장되어있는 [{self.POLICY_NAME}]: {len(rules)}"
        )

        sensitive_field_models = self._get_sensitive_field_included_models()
        self.logger.info(
            f"현재 SensitiveFieldModel을 사용한 모델 개수: {len(sensitive_field_models)}"
        )

        self.logger.info("동기화 시작")
        self._sync_rules(rules, sensitive_field_models)
        result_message = (
            f"[{self.POLICY_NAME}] {self.changes}개 테이블의 규칙이 변경되었습니다."
            if self.changes != 0
            else "변경된 내용이 존재하지 않습니다."
        )
        self.logger.info(result_message)
        self.logger.info("동기화 완료")

    def _get_sensitive_field_included_models(self) -> list[SensitiveFieldModel]:
        all_models = django.apps.apps.get_models()
        sensitive_field_mixin_models = list(
            filter(
                lambda model: issubclass(model, SensitiveFieldMixin)
                and issubclass(model, models.Model),
                all_models,
            )
        )
        result = []
        for model in sensitive_field_mixin_models:
            sensitive_fields = getattr(model, self.SENSITIVE_FIELD_NAME, [])
            if not isinstance(sensitive_fields, list):
                sensitive_fields = []
            result.append(
                SensitiveFieldModel(
                    table_name=model._meta.db_table,
                    fields=list(sensitive_fields),
                )
            )

        return result + self.ADDITIONAL_SENSITIVE_MODELS

    def _sync_rules(
        self, current_rules: list[Rule], apply_models: list[SensitiveFieldModel]
    ):
        current_table_rule_dict = {
            rule.get_table_name(): rule
            for rule in current_rules
            if rule.get_table_name() or rule.get_field_names()
        }

        for model in apply_models:
            self.changes += 1
            if (
                model.table_name in current_table_rule_dict
            ):  # 기존에 마스킹 처리되어있던 모델
                rule = current_table_rule_dict.pop(model.table_name)
                if not model.fields:
                    self._delete(rule)
                elif rule.get_field_names() != model.fields:
                    self._update(rule, model)
                else:  # 접근 제한할 필드가 비어있지 않고 현재 설정된 정책과 다르지 않다면 무시한다
                    self.changes -= 1
                    pass
            else:  # 기존에 없던 모델
                self._create(model)

        for remain_rule in current_table_rule_dict.values():
            # 위에서 pop으로 처리하지 않은 rule은 존재하지 않는 table이기 떄문에 삭제한다
            self._delete(remain_rule)

    def _get_current_rules(self) -> list[Rule]:
        return []

    def _create(self, model: SensitiveFieldModel):
        self.logger.info(f"Create rule for {model.table_name}, fields: {model.fields}")

    def _update(self, rule: Rule, model: SensitiveFieldModel):
        self.logger.info(f"Update rule for {model.table_name}, fields: {model.fields}")

    def _delete(self, rule: Rule):
        self.logger.info(f"Delete rule for {rule.get_table_name()}")
