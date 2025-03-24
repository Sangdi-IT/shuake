from progressbar import ProgressBar, Percentage, Bar
from playwright.async_api import async_playwright
from config.config import USER_NUMBER, USER_PASSWD, COURSER_LINK
from getcourseid import Get_course_id
from PIL import Image
from io import BytesIO
import asyncio as asynioc
import cv2
import re


class Shuake:
    # 定义异步方法 start，用于启动整个流程
    async def start(self):
        # 使用 async_playwright 上下文管理器确保资源自动清理
        async with async_playwright() as playwright:
            # 启动 Chromium 浏览器
            # 设置 channel 为 'chrome'（使用谷歌浏览器），headless=True 表示无头模式（不显示界面），并静音音频
            self.browser = await playwright.chromium.launch(channel='chrome', headless=True, args=['--mute-audio'])

            # 创建一个新的浏览器上下文，允许隔离浏览器会话
            self.context = await self.browser.new_context()

            # 创建一个新的页面对象
            self.page = await self.context.new_page()

            # 跳转到指定的 URL（目标网页）
            # await self.page.goto("https://www.hngbwlxy.gov.cn/#/")
            await self.page.goto("https://bjce.bjdj.gov.cn/#/")

            # 调用 login 方法，进行登录操作
            await self.login()
            # 确保页面完全加载或触发导航
            await self.page.wait_for_event("framenavigated", timeout=60000)
            print("登录完成...")

            # 调用 check_user_core 方法，检查用户的核心信息或状态
            print("即将执行查询分数check_user_core函数")
            # await self.page.wait_for_load_state('networkidle')  # 页面加载完成
            try:
                print("即将执行 check_user_core 方法...")
                await self.check_user_core()
            except Exception as e:
                print(f"调用 check_user_core 方法失败，错误信息：{e}")
                # 输出页面内容用于调试
                page_content = await self.page.content()
                print("当前页面内容：")
                print(page_content)



            try:
                # 调用 start_shuake 方法，开始刷课流程（或类似功能），并获取其状态
                status = await self.start_shuake()

                # 如果返回的状态为 True，关闭浏览器
                if status:
                    await self.browser.close()
            except:
                # 捕获异常（如网络问题），打印错误信息
                print("网络异常！请再次运行！")


    async def login(self):
        # 等待并选择页面上的登录按钮（通过 CSS 选择器定位）
        # login_button = await self.page.wait_for_selector(
        #     'body > div > div.main-bg-top.ng-scope > div:nth-child(1) > div > div > ul > div.grid_9.searchInput > a'
        # )
        await self.page.wait_for_load_state('networkidle')  # 等待页面加载完成
        # 如果 class 不是唯一的，基于文本内容定位会更稳妥。Playwright 支持 XPath，可以通过文本值选择：
        login_button = await self.page.wait_for_selector('//span[text()="请登录"]')

        # 点击登录按钮以触发登录弹窗或页面跳转
        await login_button.click()

        # 点击“请登录”之后选择登录方式
        await self.page.wait_for_load_state('networkidle')  # 等待页面网络请求空闲
        login_option = await self.page.wait_for_selector('//div[text()="登录"]')
        await login_option.click()
        # await self.page.screenshot(path="before_click.png")  # 点击前截图
        # await login_option.click()
        # await self.page.screenshot(path="after_click.png")   # 点击后截图

        # 等待加载登陆页面
        await self.page.wait_for_load_state('networkidle')

        # 定位输入文本框
        username_input = await self.page.wait_for_selector('[placeholder="请输入账号"]')
        # 输入用户账号
        await username_input.fill('40911915')
        # print("Usernumber entered successfully")

        # 定位密码文本框
        username_input = await self.page.wait_for_selector('[placeholder="请输入密码"]')
        # 输入密码
        await username_input.fill('wangjian0.0')
        # print("Userpassword entered successfully:{USER_PASSWD}")


        await self.page.wait_for_load_state('networkidle')
        wxlogin_button = await self.page.wait_for_selector('//span[text()="微信认证登录"]')
        await wxlogin_button.click()
        # 等待服务端响应---必要的
        await self.page.wait_for_load_state('networkidle')
        current_url = self.page.url
        print(f"当前页面 URL：{current_url}")

    async def check_user_core(self):
        try:
            print("正在执行查询分数函数...")
            # 确保页面加载完成
            await self.page.wait_for_load_state('load')
            print("页面加载完成，开始查找积分元素...")

            # 定位学分元素
            # 提取必修学时
            mandatory_div = await self.page.wait_for_selector('div.iv-row-left-bottom-div2')
            mandatory_score_element = await mandatory_div.query_selector('span[style="font-size: 40px; font-weight: 600;"]')
            mandatory_score = await mandatory_score_element.inner_text()  # 使用 await
            mandatory_label_element = await mandatory_div.query_selector('p[style="font-size: 18px; line-height: normal;"]')
            mandatory_label = await mandatory_label_element.inner_text()  # 使用 await
            print(f"必修学时: {mandatory_label} - {mandatory_score}")

            # 提取选修学时
            optional_div = await self.page.wait_for_selector('div.iv-row-left-bottom-div3')
            optional_score_element = await optional_div.query_selector('span[style="font-size: 40px; font-weight: 600;"]')
            optional_score = await optional_score_element.inner_text()  # 使用 await
            optional_label_element = await optional_div.query_selector('p[style="font-size: 18px; line-height: normal;"]')
            optional_label = await optional_label_element.inner_text()  # 使用 await
            print(f"选修学时: {optional_label} - {optional_score}")
        except Exception as e:
            print(f"函数内部出现异常，错误信息：{e}")
            # 输出页面 HTML 内容用于调试
            # page_content = await self.page.content()
            # print(page_content)

    async def get_course_link(self):
        # 1. 跳转到课程链接页面，确保页面加载完成
        await self.page.goto("https://bjce.bjdj.gov.cn/#/course/courseResources?activedIndex=3&id=xinshidaishoudufazhan")
        page_content = await self.page.content()
        print("当前页面内容：")
        print(page_content)

        # 2. 获取浏览器的 Cookie 信息，用于后续 HTTP 请求中验证身份或维持会话
        cookies = await self.context.cookies()
        # 将 Cookie 转换为键值对格式的字符串，用于构造请求头
        cookies = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        print("这是Cookies:")
        print(cookies)

        # 3. 从课程链接中提取频道 ID，通常用于区分课程分类或频道
        # 使用 split() 提取 'id' 后面的部分
        channelId = COURSER_LINK.split("id=")[-1]
        print(f"提取的结果是：{channelId}")

        # 4. 获取页面上显示的课程总数
        # 等待包裹课程列表的 div 加载完成
        container = await self.page.wait_for_selector('div.iv-template-every > ul')

        # 在容器内查找所有课程 li 元素
        course_items = await container.query_selector_all('li[data-v-d50a91fc]')

        # 统计课程数量
        rowlength = len(course_items)
        print(f"总共有 {rowlength} 个课程")

        # 源代码里面的# 定位课程总数的元素，通过选择器提取文本内容
        # rowlength = await self.page.wait_for_selector(
        #     'body > div > div.container_24.clear-fix.ng-scope > div.grid_18.pad_left_20 > div > div > div.allCourse.mar_top_20 > div:nth-child(5) > div > div > div.page-total > span > strong'
        # )
        # # 获取课程总数的文本内容（通常是数字）
        # rowlength = await rowlength.inner_text()

        # 5. 调用 `Get_course_id` 方法，传入所需参数获取课程 ID 和相关信息
        # 包括 Cookie、频道 ID、总课程数量和分页参数
        course_messages = await Get_course_id(cookies, channelId, rowlength, 1)

        # 6. 返回所有课程的信息
        return course_messages


    async def get_captcha_image(self):
        img = await self.page.wait_for_selector('#drag > canvas.undefined')
        bounding_box = await img.bounding_box()
        left = round(bounding_box['x'])
        top = round(bounding_box['y'])
        right = round(left + bounding_box['width'])
        down = round(top + bounding_box['height'])

        screenshot = await self.page.screenshot()
        screenshot = Image.open(BytesIO(screenshot))
        captcha = screenshot.crop((left, top, right, down))
        captcha_path = './images/captcha.png'
        with open(captcha_path, 'wb') as f:
            captcha.save(f, format='png')
        f.close()
        return captcha_path

    async def get_captcha_position(self):
        status = False
        while status is False:
            captcha_path = await self.get_captcha_image()
            imageSrc = captcha_path
            image = cv2.imread(imageSrc)
            # GaussianBlur方法进行图像模糊化/降噪操作。
            # 它基于高斯函数（也称为正态分布）创建一个卷积核（或称为滤波器），该卷积核应用于图像上的每个像素点。
            blurred = cv2.GaussianBlur(image, (5, 5), 0, 0)
            # Canny方法进行图像边缘检测
            # image: 输入的单通道灰度图像。
            # threshold1: 第一个阈值，用于边缘链接。一般设置为较小的值。
            # threshold2: 第二个阈值，用于边缘链接和强边缘的筛选。一般设置为较大的值
            canny = cv2.Canny(blurred, 200, 400)  # 轮廓
            # findContours方法用于检测图像中的轮廓,并返回一个包含所有检测到轮廓的列表。
            # contours(可选): 输出的轮廓列表。每个轮廓都表示为一个点集。
            # hierarchy(可选): 输出的轮廓层次结构信息。它描述了轮廓之间的关系，例如父子关系等。
            contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # 遍历检测到的所有轮廓的列表
            for contour in contours:
                # contourArea方法用于计算轮廓的面积
                area = cv2.contourArea(contour)
                # arcLength方法用于计算轮廓的周长或弧长
                length = cv2.arcLength(contour, True)
                # 如果检测区域面积在
                # 计算轮廓的边界矩形，得到坐标和宽高
                if 20 < area < 30 and 230 < length < 300:
                    # 计算轮廓的边界矩形，得到坐标和宽高
                    # x, y: 边界矩形左上角点的坐标。
                    # w, h: 边界矩形的宽度和高度。

                    x, y, w, h = cv2.boundingRect(contour)
                    # 在目标区域上画一个红框看看效果
                    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    # cv2.imwrite("images/111.jpg", image)
                    status = True
                    return x

            refresh_pic_button = await self.page.wait_for_selector('#drag > div.refreshIcon')
            await refresh_pic_button.click()

    async def move_to_slider(self):
        x_move_position = await self.get_captcha_position()
        slider = await self.page.wait_for_selector('#drag > div.sliderContainer > div > div')
        slider_position = await slider.bounding_box()
        await slider.hover()
        await self.page.mouse.down()
        await self.page.mouse.move(slider_position['x'] + x_move_position + 30, slider_position['y'] + 2, steps=5)
        await self.page.mouse.up()

        await asynioc.sleep(1)
        class_attribute = await self.page.locator('//*[@id="drag"]/div[2]').get_attribute('class')
        if class_attribute == 'sliderContainer sliderContainer_success':
            return True
        else:
            return False

    async def wait_for_jwplayer(self, selector):
        while True:
            try:
                player = await self.page.wait_for_selector(
                    "body > div > div > div > div.sigle-video.ng-scope > div.sigle-video-bg > div")
                await player.hover()
                jwplayer = await self.page.wait_for_selector(selector)
                if jwplayer:
                    break
                else:
                    await asynioc.sleep(1)
            except Exception as e:
                await asynioc.sleep(1)

        return jwplayer

    async def start_shuake(self):
        # 获取课程链接及相关信息，返回包含课程 ID 和课程名称的字典列表
        course_messages = await self.get_course_link()

        # 遍历所有课程信息（每个信息是一个字典）
        for course_message in course_messages:
            for course_id, course_name in course_message.items():  # 解包课程 ID 和课程名称
                # 构造课程详情页面的 URL
                course_url = f"https://www.hngbwlxy.gov.cn/#/courseCenter/courseDetails?Id={str(course_id)}&courseType=video"
                await self.page.goto(course_url)  # 跳转到课程详情页面
                await asynioc.sleep(2)  # 等待页面加载

                # 检查课程的学习进度，通过选择器提取进度信息
                course_status = await self.page.wait_for_selector(
                    'body > div > div:nth-child(3) > div.container_24 > div > div > div.cpurseDetail.grid_24 > div.c-d-course.clearfix > div > div.course-progress > span.progress-con.ng-binding'
                )
                course_status = await course_status.inner_text()  # 获取学习进度文本
                # 如果课程学习进度已达到 100%，跳过本课程
                if course_status == "100.0%":
                    print(f" {course_name} 课程已学完，将为您选择下一个课程！")
                    continue
                else:
                    # 构造课程播放页面的 URL
                    course_play_url = f"https://www.hngbwlxy.gov.cn/#/play/play?Id={str(course_id)}"
                    await self.page.goto(course_play_url)  # 跳转到课程播放页面
                    try:
                        # 检查是否已达到每日学习的学分上限
                        study_status = await self.page.wait_for_selector('#ban-study', timeout=4000)
                        if study_status:  # 如果元素存在，学分已满
                            print("今日学习的学分已经够 5 分，不需要再学习了！")
                            return True
                    except:
                        print("正在自动选择下一门课程！")

                    # 点击弹框的确认按钮，进入学习状态
                    tan_box = await self.page.wait_for_selector('#msBox > div.msBtn > span')
                    await tan_box.click()

                    # 验证滑动验证码是否通过，重复执行直到通过验证
                    check = await self.move_to_slider()
                    while check is False:
                        await self.get_captcha_position()  # 获取验证码位置
                        check = await self.move_to_slider()  # 重新滑动

                    print(f"{course_name} 课程开始学习！")

                    # 等待课程播放器加载
                    course_progress = await self.wait_for_jwplayer(
                        "#myplayer_controlbar > span.jwgroup.jwcenter > span.jwslider.jwtime > span.jwrail.jwsmooth > span.jwprogressOverflow"
                    )

                    # 初始化进度条，用于显示学习进度
                    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()
                    while True:
                        # 获取播放器的进度样式（第一次获取）
                        style1 = await course_progress.get_attribute("style")
                        width1 = next(
                            (s.split(":")[1].strip() for s in style1.split(";") if s.split(":")[0].strip() == "width"),
                            None
                        )

                        # 等待 1.5 秒后再获取播放器进度样式（第二次获取）
                        await asynioc.sleep(1.5)
                        style2 = await course_progress.get_attribute("style")
                        width2 = next(
                            (s.split(":")[1].strip() for s in style2.split(";") if s.split(":")[0].strip() == "width"),
                            None
                        )

                        # 将进度样式百分比提取为数字并更新进度条
                        width_num = float(width2.strip('%'))
                        pbar.update(width_num)

                        # 如果进度条未变化且宽度为 0.0，学习结束
                        if (width1 == width2) and width_num == 0.0:
                            pbar.finish()  # 完成进度条
                            break

                # 等待 10 秒后重新加载课程页面，准备学习下一个课程
                await self.page.goto(COURSER_LINK)
                await self.page.reload()
                await asynioc.sleep(12)

        # 当所有课程学习完毕时，打印完成信息并返回
        print("当前 URL 下的课程已经全部学习完毕！")
        return True

