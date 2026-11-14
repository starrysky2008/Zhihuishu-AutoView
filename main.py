from playwright.sync_api import *
import time
import re
import sys

CDP_ADDR = "http://127.0.0.1:9270"

def consider(playing, dialog_show, is_finished):
    """
    判断当前播放器状态
    返回值:
        1: 正常播放
        2: 答题
        3: 暂停
        4: 完成播放
    """
    if playing:
        return 1
    if dialog_show:
        return 2
    if is_finished:
        return 4
    return 3

def play(page: Page):
    print("切换播放状态...")
    page.locator("#vjs_container").hover()
    time.sleep(1)
    page.locator("#playButton").click()
    return True

def answer(page: Page):
    print("开始弹窗作答")
    def choose(dialog: Locator, choice: str):
        element = dialog.first.get_by_text(choice)
        if element.count() == 0:
            return False
        if not element.first.is_visible():
            return False
        element.first.click()

    dialog = page.get_by_role("dialog")
    if dialog.count() == 0:
        return False

    choices = ["A.", "B.", "C.", "D."]
    for choice in choices:
        choose(dialog, choice)
        time.sleep(0.7)
    choose(dialog, "关闭")
    return True

def next_chapter(page: Page):
    print("开始切换章节...")
    current = page.locator(".current_play").locator(".hour").inner_text()
    major = int(current.split(".")[0])
    minor = int(current.split(".")[1])
    def try_click(page: Page, chapter: str):
        print(f"尝试切换至{chapter}")
        element = page.locator(".box-right").locator(".el-scrollbar__view").get_by_text(chapter, exact=True)
        if element.count() == 0:
            return False
        element.first.click()
        return True
    minor += 1
    res = try_click(page, f"{major}.{minor}")
    if res:
        print("完成切换")
        time.sleep(5) # 等待视频加载
        return True
    # 尝试major+1
    major += 1
    minor = 1
    res = try_click(page, f"{major}.{minor}")
    if res:
        print("完成切换")
        time.sleep(5)
        return True
    # 未完成就是全部播放完毕
    return False

def react(page: Page, status: int):
    """
    根据consider提供的状态做出响应
    返回: bool, 操作是否成功
    """
    if status == 4:
        res = next_chapter(page)
        if not res:
            print("未找到下一章，判定为完成播放，退出")
            sys.exit(0)
        return res

    if status == 2:
        return answer(page)

    if status == 3:
        return play(page)
    
def main():
    # 上下文，通过stop()关闭
    process = sync_playwright().start()
    browser = process.chromium.connect_over_cdp(CDP_ADDR, timeout=5000)

    # 这里默认context0的第一个页面是播放器，实际情况可能不是，但我是懒狗
    page = browser.contexts[0].pages[0]
    if re.match(r".*studyvideoh5.zhihuishu.com/stuStudy.+", page.url) == None:
        print("第一个页面非播放器页面，退出")
        return

    last_state = -1

    while True:
        playing = page.locator("#playButton").get_attribute("class") == "pauseButton"
        chapter = page.locator(".current_play").locator(".hour").inner_text()
        dialog_show = page.get_by_role("dialog").first.is_visible()
        is_finished = page.locator(".current_play").locator(".time_icofinish").count() != 0
        state = consider(
                playing, dialog_show, is_finished
            )

        if state != last_state or state != 1:
            print("当前状态: " + \
                ("播放中" if playing else "暂停") + "\n" + \
                f"章节: {chapter}\n" + \
                f"状态判断: {state}")
            
            react(page, state)
            print()

        last_state = state

        time.sleep(5)



if __name__ == "__main__":
    main()