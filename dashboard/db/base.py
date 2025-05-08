from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class DBClientInterface(ABC):
    @abstractmethod
    def select_from_table(
        self,
        table: str,
        select_columns: Union[str, List[str]] = "*",
        conditions: Optional[Dict] = None,
        limit: Optional[int] = None,
        single: bool = False,
        maybe_single: bool = False,
        order_by: Optional[str] = None,
        desc: bool = False,
    ) -> Union[List[Dict], Dict, None]:
        pass

    @abstractmethod
    def insert_into_table(
        self,
        table: str,
        values: Union[Dict, List[Dict]],
    ) -> Any:
        pass

    @abstractmethod
    def update_table(
        self,
        table: str,
        values: Dict,
        conditions: Dict,
    ) -> Any:
        pass

    @abstractmethod
    def delete_from_table(
        self,
        table: str,
        conditions: Dict,
    ) -> Any:
        pass

    @abstractmethod
    def call_rpc(
        self,
        function_name: str,
        params: Dict,
    ) -> Any:
        pass
