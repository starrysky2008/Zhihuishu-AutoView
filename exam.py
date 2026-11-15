import base64
import json
import time
from openai import OpenAI
from playwright.sync_api import *

with open("apikey.txt", "r") as f:
    apikey = f.read().strip()

CDP_URL = "http://127.0.0.1:9270"
SYSTEM_PROMPT = \
'''
你是一个精通军事理论课程的教师，现在你需要根据用户提供的题目做出解答，所有回答采用json格式
示例输出:
{
    "question":"从2001年起，每年9月的（ ）是我国的全民国防教育日。",
    "choices": ["A"],
    "choice_texts": ["第三个星期六"],
    "reason": "<你对该题的解析>"
}
在做出回答前请反复思考确认，尽可能降低错误率
'''
MODEL = "deepseek-flash"

client = OpenAI(api_key=apikey, base_url="https://api.deepseek.com")

def get_answer(image_data: str):
    response = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages= [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "作答图中题目"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        reasoning_effort="max",
        extra_body={"thinking": {"type": "enabled"}}
    )
    data = json.loads(response.choices[0].message.content)
    return data

def next(page: Page):
    """
    return: 已全部完成?
    """
    locator = page.get_by_text("下一题", exact=True)
    if locator.count() != 0:
        locator.first.click()
        return False
    locator = page.get_by_text("保存", exact=True)
    if locator.count() != 0:
        locator.click()
        return True
    raise RuntimeError("找不到下一题按钮")

def choose(page: Page, choices: str | list[str]):
    def choose_single(page: Page, choice: str):
        page.locator(".examPaper_subject:visible") \
            .first.get_by_text(f"{choice}.").click()
    if type(choices) == str:
        choose_single(page, choices)
        return
    for choice in choices:
        choose_single(page, choice)

def main():
    p = sync_playwright().start()
    browser = p.chromium.connect_over_cdp(CDP_URL)
    # page = browser.contexts[0].pages[0]
    # print("将要作答的页面: " + page.title())
    # print("是否开始? ")
    # ans = input("(Y/N N) ")
    # con = ans == "Y"
    # if not con:
    #     print("退出")
    #     return
    print("当前打开的页面:")
    index = 0
    for page in browser.contexts[0].pages:
        print(f"{index}. {page.title()}")
        index += 1
    index = int(input("要打开的页面编号: "))
    page = browser.contexts[0].pages[index]

    print("开始作答")
    print(f"模型: {MODEL}")

    while True:
        time.sleep(1)
        data = page.locator(".examPaper_subject:visible") \
            .first.screenshot(type="png")
        data = base64.b64encode(data).decode()
        ans = get_answer(data)
        q = ans["question"]
        a = ans["choices"]
        at = ans["choice_texts"]
        rs = ans["reason"]
        print(f"题目: {q}\n" \
              + f"作答选项: {",".join(a)} ({",".join(at)})\n" \
                + f"解析: {rs}\n")
        choose(page, a)
        time.sleep(0.7)
        if next(page):
            print("全部题目已作答，试卷已保存")
            return

if __name__ == "__main__":
    main()