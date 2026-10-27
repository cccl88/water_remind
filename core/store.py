"""饮水记录存储：按天记录，JSON 持久化"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from typing import Dict, List

from .config import DATA_PATH


class Store:
    def __init__(self, path: str = DATA_PATH):
        self.path = path
        self.data: Dict = {"days": {}}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.data.setdefault("days", {})
            except Exception:
                self.data = {"days": {}}

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ---------- 记录 ----------
    def _day(self, d: date) -> Dict:
        key = d.isoformat()
        day = self.data["days"].setdefault(key, {"total_ml": 0, "cups": []})
        day.setdefault("total_ml", 0)
        day.setdefault("cups", [])
        return day

    def add(self, ml: int, when: datetime | None = None) -> None:
        when = when or datetime.now()
        day = self._day(when.date())
        day["total_ml"] += ml
        day["cups"].append({"time": when.strftime("%H:%M"), "ml": ml})
        self.save()

    def undo(self) -> bool:
        """撤销今天最后一次记录"""
        day = self._day(date.today())
        if not day["cups"]:
            return False
        last = day["cups"].pop()
        day["total_ml"] = max(0, day["total_ml"] - last.get("ml", 0))
        self.save()
        return True

    def today_total(self) -> int:
        return self._day(date.today())["total_ml"]

    def today_cups(self) -> List[Dict]:
        return self._day(date.today())["cups"]

    def set_total(self, ml: int) -> None:
        day = self._day(date.today())
        day["total_ml"] = max(0, ml)
        self.save()

    # ---------- 统计 ----------
    def last_days(self, n: int = 7):
        """返回最近 n 天 [(日期, 总量)]，按时间正序"""
        today = date.today()
        out = []
        for i in range(n - 1, -1, -1):
            d = today - timedelta(days=i)
            out.append((d, self._day(d)["total_ml"]))
        return out

    def streak(self, goal_ml: int) -> int:
        """连续达标天数（含今天则从今天往前算）"""
        today = date.today()
        count = 0
        cursor = today
        # 今天没达标不算断，从昨天开始回溯
        if self._day(today)["total_ml"] >= goal_ml:
            count += 1
        cursor = today - timedelta(days=1)
        while self._day(cursor)["total_ml"] >= goal_ml:
            count += 1
            cursor -= timedelta(days=1)
            if count > 3650:
                break
        return count
