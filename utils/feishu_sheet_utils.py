import requests
import pandas as pd
from typing import List, Dict, Optional, Union, Tuple, Any
import os
import time
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
APP_ID = os.getenv("FEISHU_APP_DAODAO_AINEWS_ID")
APP_SECRET = os.getenv("FEISHU_APP_DAODAO_AINEWS_SECRET")


class FeishuSheetUtils:
    """
    飞书 Sheets 工具类（基于官方最新 Sheets API）

    官方文档：
    https://open.larkoffice.com/document/server-docs/docs/sheets-v3/overview

    特点：
    - 自动刷新 tenant_access_token
    - 支持 DataFrame
    - 支持 Sheet 管理
    - 支持 batch_update
    - 统一异常处理
    - 基于官方推荐 API
    """

    BASE_URL = "https://open.feishu.cn/open-apis"

    AUTH_URL = BASE_URL + "/auth/v3/tenant_access_token/internal"

    def __init__(
        self,
        spreadsheet_token: str,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
    ):
        self.spreadsheet_token = spreadsheet_token
        self.app_id = app_id or os.getenv("FEISHU_APP_DAODAO_AINEWS_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_DAODAO_AINEWS_SECRET")

        if not self.app_id or not self.app_secret:
            raise ValueError("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET")

        self._tenant_token = None
        self._token_expire_at = 0

    # =========================================================
    # token
    # =========================================================

    def _refresh_token(self):

        resp = requests.post(
            self.AUTH_URL,
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret,
            },
            timeout=15,
        )

        data = resp.json()

        if data.get("code") != 0:
            raise Exception(f"获取 tenant_access_token 失败: {data}")

        self._tenant_token = data["tenant_access_token"]

        # 官方返回 expire（秒）
        expire = data.get("expire", 7200)

        # 提前 5 分钟刷新
        self._token_expire_at = time.time() + expire - 300

    def _get_token(self):

        if not self._tenant_token or time.time() >= self._token_expire_at:
            self._refresh_token()

        return self._tenant_token

    # =========================================================
    # request
    # =========================================================

    def _headers(self):
        return {
            "Authorization": (f"Bearer {self._get_token()}"),
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params=None,
        json=None,
    ):
        url = f"{self.BASE_URL}/{path.lstrip('/')}"

        resp = requests.request(
            method=method.upper(),
            url=url,
            headers=self._headers(),
            params=params,
            json=json,
            timeout=30,
        )

        try:
            data = resp.json()
        except Exception:
            raise Exception(f"飞书接口返回非 JSON:\n{resp.text}")

        if data.get("code") != 0:
            raise Exception(
                f"飞书 API 错误:\n"
                f"code={data.get('code')}\n"
                f"msg={data.get('msg')}\n"
                f"data={data}"
            )

        return data.get("data", {})

    # =========================================================
    # spreadsheet meta
    # =========================================================

    def get_meta(self):
        """
        获取 文档 元信息
        """

        return self._request(
            "GET",
            f"/sheets/v3/spreadsheets/" f"{self.spreadsheet_token}",
        )

    def list_sheets(self) -> List[Dict]:
        """
        获取 sheet 列表
        """
        data = self._request(
            "GET",
            f"/sheets/v3/spreadsheets/{self.spreadsheet_token}/sheets/query",
        )

        return data.get("sheets", [])

    def get_sheet(
        self,
        sheet_name: str,
    ) -> Optional[Dict]:
        for s in self.list_sheets():
            if s["title"] == sheet_name:
                return s

        return None

    def get_sheet_id(
        self,
        sheet_name: str,
    ) -> Optional[str]:

        sheet = self.get_sheet(sheet_name)

        return sheet["sheet_id"] if sheet else None

    # =========================================================
    # values
    # =========================================================

    # def read(
    #     self,
    #     range_value: str,
    # ) -> Dict:
    #     """
    #     range_value 示例：

    #     Sheet1!A1:C10
    #     """

    #     return self._request(
    #         "GET",
    #         f"/sheets/v2/spreadsheets/"
    #         f"{self.spreadsheet_token}"
    #         f"/values/{range_value}",
    #     )

    # def read_values(
    #     self,
    #     range_value: str,
    # ) -> List[List]:

    #     data = self.read(range_value)

    #     return data.get("valueRange", {}).get("values", [])

    # def write(
    #     self,
    #     range_value: str,
    #     values: List[List],
    # ):
    #     """
    #     覆盖写入
    #     """

    #     return self._request(
    #         "PUT",
    #         f"/sheets/v2/spreadsheets/" f"{self.spreadsheet_token}" f"/values",
    #         json={
    #             "valueRange": {
    #                 "range": range_value,
    #                 "values": values,
    #             }
    #         },
    #     )

    # def append(
    #     self,
    #     range_value: str,
    #     values: List[List],
    # ):
    #     """
    #     追加写入
    #     """

    #     return self._request(
    #         "POST",
    #         f"/sheets/v2/spreadsheets/" f"{self.spreadsheet_token}" f"/values_append",
    #         json={
    #             "valueRange": {
    #                 "range": range_value,
    #                 "values": values,
    #             }
    #         },
    #     )

    # def batch_write(
    #     self,
    #     items: List[Dict],
    # ):
    #     """
    #     示例：

    #     [
    #         {
    #             "range": "Sheet1!A1:B2",
    #             "values": [[1,2],[3,4]]
    #         }
    #     ]
    #     """

    #     value_ranges = []

    #     for item in items:

    #         value_ranges.append(
    #             {
    #                 "range": item["range"],
    #                 "values": item["values"],
    #             }
    #         )

    #     return self._request(
    #         "POST",
    #         f"/sheets/v2/spreadsheets/"
    #         f"{self.spreadsheet_token}"
    #         f"/values_batch_update",
    #         json={"valueRanges": value_ranges},
    #     )

    # def clear(
    #     self,
    #     range_value: str,
    # ):

    #     return self._request(
    #         "POST",
    #         f"/sheets/v2/spreadsheets/" f"{self.spreadsheet_token}" f"/values_clear",
    #         json={"ranges": [range_value]},
    #     )

    # =========================================================
    # dataframe
    # =========================================================

    # def read_df(
    #     self,
    #     range_value: str,
    # ) -> pd.DataFrame:

    #     values = self.read_values(range_value)

    #     if not values:
    #         return pd.DataFrame()

    #     header = values[0]

    #     rows = values[1:]

    #     return pd.DataFrame(
    #         rows,
    #         columns=header,
    #     )

    # def write_df(
    #     self,
    #     range_value: str,
    #     df: pd.DataFrame,
    #     include_header: bool = True,
    # ):

    #     values = []

    #     if include_header:
    #         values.append(df.columns.tolist())

    #     values.extend(df.fillna("").values.tolist())

    #     return self.write(
    #         range_value,
    #         values,
    #     )

    # =========================================================
    # sheet batch update
    # =========================================================

    def sheet_batch_update(
        self,
        requests_data: List[Dict],
    ):
        """
        飞书所有 sheet 结构操作
        都推荐统一走这里
        """

        return self._request(
            "POST",
            f"/sheets/v2/spreadsheets/{self.spreadsheet_token}/sheets_batch_update",
            json={"requests": requests_data},
        )

    # =========================================================
    # sheet operations
    # =========================================================

    def add_sheet(
        self,
        title: str,
        index: int = 0,
    ):
        """
        添加 sheet
        """
        return self.sheet_batch_update(
            [
                {
                    "addSheet": {
                        "properties": {
                            "title": title,
                            "index": index,
                        }
                    }
                }
            ]
        )

    def copy_sheet(self, sheet_id: str, sheet_copy: str):
        """
        复制 sheet
        """
        return self.sheet_batch_update(
            [
                {
                    "copySheet": {
                        "source": {"sheetId": sheet_id},
                        "destination": {"title": sheet_copy},
                    }
                }
            ]
        )

    def delete_sheet(
        self,
        sheet_id: str,
    ):
        return self.sheet_batch_update([{"deleteSheet": {"sheetId": sheet_id}}])

    def rename_sheet(
        self,
        sheet_id: str,
        new_title: str,
    ):
        return self.sheet_batch_update(
            [
                {
                    "updateSheet": {
                        "properties": {
                            "sheetId": sheet_id,
                            "title": new_title,
                        }
                    }
                }
            ]
        )

    # =========================================================
    # dimension
    # =========================================================
    def append_rows(self, range: str, rows_data: List[List]) -> Dict:
        """
        追加多行数据
        文档地址：https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/append-data
        """
        path = f"/sheets/v2/spreadsheets/{self.spreadsheet_token}/values_append?insertDataOption=INSERT_ROWS"
        req_body = {"valueRange": {"range": range, "values": rows_data}}
        return self._request("POST", path, json=req_body)

    def append_row(self, range: str, row_data: List) -> Dict:
        """追加单行数据"""
        return self.append_rows(range, [row_data])


# =========================================================
# example
# =========================================================

if __name__ == "__main__":

    fs = FeishuSheetUtils(spreadsheet_token="ZzgQstUP2h2fHWtCwrXco2kXnyb")

    # 获取 sheet 列表
    # print(fs.list_sheets())
    sheet_id = fs.get_sheet_id("Sheet1")
    print(sheet_id)
    # fs.append_row(f"9a768f!A:B", ["name", "age"])
    fs.append_row(f"9a768f!A:B", ["dao", 18])
    # fs.append_row("Sheet1!A:B", ["tom", 20])

    # 写入
    # fs.write(
    #     "Sheet1!A1:B3",
    #     [
    #         ["name", "age"],
    #         ["dao", 18],
    #         ["tom", 20],
    #     ],
    # )

    # # 读取
    # values = fs.read_values("Sheet1!A1:B10")

    # print(values)

    # # dataframe
    # df = fs.read_df("Sheet1!A1:B10")

    # print(df)
