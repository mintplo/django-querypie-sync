from pydantic import BaseModel


class SensitiveFieldModel(BaseModel):
    table_name: str
    fields: list[str]


class Rule(BaseModel):
    # https://{QUERYPIE_URL}/api/docs#operation/findRules 200 응답 참조

    uuid: str
    objectType: str  # 어떤 단위의 규칙인지 정의 -> "COLUMN"
    # ["lemonbase", "table_name", "column_name"] or ["/lemonbase/i", "/table_name/i", "/column_name/i"]
    objectPath: list[str]

    def get_table_name(self) -> str | None:
        return self.objectPath[1] if len(self.objectPath) > 0 else None

    def get_field_names(self) -> list[str]:
        fields = self.objectPath[2] if len(self.objectPath) > 1 else None
        if not fields:
            return []

        # /(column_1|column_2|column_3)/i -> ['column_1', 'column_2', 'column_3']
        return fields.replace("/(", "").replace(")/i", "").split("|")
