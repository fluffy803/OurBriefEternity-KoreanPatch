# -*- coding: utf-8 -*-
"""Write tl_korean/zz_extra_strings.rpy: displayed strings the game does not wrap in _().

Ren'Py's Text displayable translates its raw string at display time, so speaker
names (Character("时语")), `text some_list[i]` values and plain `text "..."`
literals pick up these entries even though `translate --strings-only` skips them.
"""
import os

W = os.environ.get("OBE_WORKSPACE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXTRA = [
    # scripts/roles/role.rpy - speaker names
    "同事A", "同事B", "同事C", "房东", "时语", "时语&星弥", "星弥", "服务员", "林小凑",
    "林小凑&星弥", "林小凑&时语", "棕发少女", "银发少女", "人事主管", "摊主",
    # scripts/screens/music.rpy - voice drama list
    "音声 01", "音声 02", "音声 03", "音声 04", "主题曲",
    "下播后的专属时间", "小小作家的休闲时刻", "盛夏·海滩·防晒霜", "清晨·突袭·过往趣事", "永恒星辰下的日常",
    "通关时语线解锁", "通关星弥线解锁", "通关后宫线NE解锁", "通关后宫线GE解锁",
    "时长", "音量",
    # scripts/screens/screen_preferences.rpy - preview lines
    "此处背景为文本框透明度的演示", "此处为文本正常演出时的速度演示", "此处为文本自动模式时的速度演示",
    # scripts/controls/VirtualViewport.rpy - history jump confirm
    "确定要跳转到该处吗？",
]


def main():
    out = os.path.join(W, "tl_korean", "zz_extra_strings.rpy")
    with open(out, "w", encoding="utf-8") as o:
        o.write("﻿translate korean strings:\n\n")
        for s in EXTRA:
            o.write(f'    old "{s}"\n    new "{s}"\n\n')
    print(f"{len(EXTRA)} extra strings -> {out}")


if __name__ == "__main__":
    main()
