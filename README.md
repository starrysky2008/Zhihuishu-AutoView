# Zhihuishu-AutoView

## 这是什么?
这是一个可以自动浏览智慧树的小脚本  
~~这里没有人喜欢网课...对吧？~~

## 如何使用
这个脚本需要一个开启cdp的chromium浏览器，如果你有一台linux机器的话可以看看  
[Chromium in Docker](https://github.com/starrysky2008/ChromiumDocker)  
这会给你剩下不少时间  
如果你是windows用户的话。。。  
AI是你的好朋友 :D （不要问我为什么不做跨平台，你不能要求一个大学生做太多事情）  
  
如果你已经准备好了浏览器，那么运行
```bash
pip install --upgrade pip
pip install playwright
playwright install # 这一步可选，鉴于你已经准备了一个浏览器
```
一切就绪之后，打开main.py，找到这一行  
```python
CDP_ADDR = "http://127.0.0.1:9270"
```
把那个9270改成你自己的端口号  
然后运行这个脚本就可以啦 :D
  
## 为什么这东西在我的电脑上用不了?
em正如我所说的，你不能要求一个大学生做太多事情，这个脚本的完成度大概就是刚好能用  
不过我把研究日志也放在这里了，你可以把我的日志和脚本丢给ai，然后让它给你做一个更好的:D