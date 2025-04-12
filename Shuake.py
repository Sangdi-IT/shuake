from playwright.async_api import async_playwright
from PIL import Image
from getcourseid import Get_course_id
from DrissionPage import ChromiumPage
from io import BytesIO
import asyncio as asynioc
import cv2
import asyncio
import re
import random
import time
from dotenv import load_dotenv
import os


class Shuake:
    async def start(self):
        async with async_playwright() as playwright:
            self.browser = await playwright.chromium.launch(channel='chrome', headless=False, args=['--mute-audio'])
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            await self.page.goto("https://bjce.bjdj.gov.cn/#/")
            await self.login()

            # Wait for navigation or load complete
            await self.page.wait_for_event("framenavigated", timeout=60000)

            try:
                await self.check_user_core()
            except Exception as e:
                print(f"调用 check_user_core 方法失败，错误信息：{e}")
            
            try:
                status = await self.start_shuake()
                if status:
                    await self.browser.close()
            except Exception as e:
                print(f"网络异常，错误信息：{e}，请再次运行！")

    async def login(self):
        load_dotenv(override=True)  # 强制重新加载

        # 提供可选用户列表
        users = [
            {"name": os.getenv("LOGIN_USER1"), "username": os.getenv("LOGIN_USERNAME1"), "password": os.getenv("LOGIN_PASSWORD1")},
            {"name": os.getenv("LOGIN_USER2"), "username": os.getenv("LOGIN_USERNAME2"), "password": os.getenv("LOGIN_PASSWORD2")},
            {"name": os.getenv("LOGIN_USER3"), "username": os.getenv("LOGIN_USERNAME3"), "password": os.getenv("LOGIN_PASSWORD3")},
        ]

        # 打印用户列表供选择
        print("请选择要登录的用户:")
        for i, user in enumerate(users):
            print(f"{i + 1}. {user['name']}")

        # 用户输入选择
        try:
            choice = int(input("请输入对应的数字选择用户: ")) - 1
            if choice < 0 or choice >= len(users):
                print("无效的选择，退出登录流程。")
                return

            selected_user = users[choice]
            print(f"已选择用户: {selected_user['name']}")

            # 开始登录流程
            await self.page.wait_for_load_state('networkidle')  # Ensure the page has fully loaded

            # Locate and click the login button
            login_button = await self.page.wait_for_selector('//span[text()="请登录"]', timeout=16000)
            await login_button.click()

            await self.page.wait_for_load_state('networkidle')  # Wait again after navigation

            login_option = await self.page.wait_for_selector('//div[text()="登录"]', timeout=16000)
            await login_option.click()

            # Locate the username input field
            username_input = await self.page.wait_for_selector('[placeholder="请输入账号"]', timeout=16000)
            if username_input:
                await username_input.fill(selected_user["username"])
            else:
                print("用户名输入框未找到，请检查选择器。")
                return

            # Locate the password input field
            password_input = await self.page.wait_for_selector('[placeholder="请输入密码"]', timeout=16000)
            if password_input:
                await password_input.fill(selected_user["password"])
            else:
                print("密码输入框未找到，请检查选择器。")
                return

            # Locate and click the login button
            wxlogin_button = await self.page.wait_for_selector('//span[text()="微信认证登录"]', timeout=16000)
            await wxlogin_button.click()
            print(f"用户 {selected_user['name']} 登录成功！")

        except Exception as e:
            print(f"登录过程中发生错误：{e}")
    async def check_user_core(self):
        try:
            await self.page.wait_for_load_state('load')
            
            mandatory_div = await self.page.wait_for_selector('div.iv-row-left-bottom-div2')
            mandatory_score_element = await mandatory_div.query_selector('span[style="font-size: 40px; font-weight: 600;"]')
            mandatory_label_element = await mandatory_div.query_selector('p[style="font-size: 18px; line-height: normal;"]')
            
            mandatory_score = await mandatory_score_element.inner_text() if mandatory_score_element else "N/A"
            mandatory_label = await mandatory_label_element.inner_text() if mandatory_label_element else "N/A"
            print(f"必修学时: {mandatory_score}")
            
            optional_div = await self.page.wait_for_selector('div.iv-row-left-bottom-div3')
            optional_score_element = await optional_div.query_selector('span[style="font-size: 40px; font-weight: 600;"]')
            optional_label_element = await optional_div.query_selector('p[style="font-size: 18px; line-height: normal;"]')
            
            optional_score = await optional_score_element.inner_text() if optional_score_element else "N/A"
            optional_label = await optional_label_element.inner_text() if optional_label_element else "N/A"
            print(f"选修学时: {optional_score}")
        except Exception as e:
            print(f"提取用户学时信息失败，错误信息：{e}")
    
    async def get_course_link(self):
        # await self.page.goto("https://bjce.bjdj.gov.cn/#/course/courseResources?activedIndex=3&id=xinshidaishoudufazhan")
        # await self.page.goto("https://bjce.bjdj.gov.cn/#/course/courseResources?activedIndex=1&id=zhengzhililun")
        # await self.page.goto("https://bjce.bjdj.gov.cn/#/course/courseResources?activedIndex=4&id=zonghesuzhi")
        # 加载环境变量
        load_dotenv()
        # 从 .env 文件读取 URL 和频道 ID
        course_url = os.getenv("COURSE_URL", "https://bjce.bjdj.gov.cn/#/course/courseResources?activedIndex=4&id=zonghesuzhi")
        channel_id = os.getenv("CHANNEL_ID", "zonghesuzhi")
        await self.page.goto(course_url)
        cookies = await self.context.cookies()
        cookies = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        
        container = await self.page.wait_for_selector('div.iv-template-every > ul')
        course_items = await container.query_selector_all('li[data-v-d50a91fc]')
        rowlength = len(course_items)

        # API Call (assuming get_course_id is properly defined elsewhere)
        uncompleted_courses = await Get_course_id(cookies, channel_id, rowlength, 1)
        return uncompleted_courses
    
    async def start_shuake(self):
        """进入未完成课程，不处理播放"""
        uncompleted_courses = await self.get_course_link()
        completed_courses = []
        print(f"本链接剩余课程{len(uncompleted_courses)}门")

        # 依次进入未完成课程
        while uncompleted_courses:
            current_course = uncompleted_courses.pop(0)
            course_id = current_course.get("id")
            course_name = current_course.get("name")
            progress = current_course.get("progress") or 0
            set_type = current_course.get("setType")

            print(f"尝试进入课程: 《{course_name}》，进度: {progress}")

            try:
                success = await self.simulate_click_to_play_course(course_name,set_type)
                if not success:
                    print(f"课程《{course_name}》进入失败，跳过此课程。")
                    await self.close_and_return_to_main_window()
                    continue  # 进入失败，继续下一个课程
                completed_courses.append(current_course)
                print(f"成功完成课程: 《{course_name}》")
            except Exception as e:
                print(f"进入课程《{course_name}》时发生错误：{e}")
                await self.close_and_return_to_main_window()
                continue  # 发生异常，重置状态后继续下一个课程

        print("所有课程已进入完毕！")
        # await self.close_and_return_to_main_window()
    async def simulate_click_to_play_course(self, course_name, set_type):
        """选择课程并点击‘开始学习’或‘继续学习’按钮"""
        try:
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # 确保页面完全加载

            # 查找课程名称
            course_item = await self.page.query_selector(f"div.iv-zhezhao-courseName:text-is('{course_name}')")
            if not course_item:
                print(f"未找到课程《{course_name}》，请检查 HTML 结构。")
                return False

            # 获取课程的 li 元素
            li_element = await course_item.evaluate_handle("el => el.closest('li')")
            await li_element.hover()
            await asyncio.sleep(1)  # 确保按钮渲染完成

            # 仅选择当前课程的学习按钮
            buttons = await li_element.query_selector_all("span:text-is('开始学习'), span:text-is('继续学习')")
            # print(f"课程《{course_name}》的学习按钮数量: {len(buttons)}")

            for button in buttons:
                if await button.is_visible():  # 仅点击可见的按钮
                    await button.click()
                    # print(f"成功点击学习按钮，进入课程《{course_name}》")
                    break
            # 等待新窗口打开
            previous_url = self.page.url
            await asyncio.sleep(2)  # 等待新窗口渲染
            all_pages = self.context.pages
            if len(all_pages) > 1:
                new_page = all_pages[-1]  # 获取最新打开的窗口
                await new_page.wait_for_load_state()
                self.page = new_page  # 切换到新窗口
                print(f"已切换到新窗口，开始学习《{course_name}》")
            elif self.page.url != previous_url:
               print("检测到页面 URL 变化，当前仍在原窗口")
            else:
                print("未检测到新窗口或 URL 变化，请检查页面逻辑")
            
            # 根据课程类型执行不同的播放逻辑
            if set_type == 1:
                await self.monitor_course_progress(course_name)  # 单课程
            elif set_type == 3:
                await self.play_series_sections()  # 系列课程

            # 课程播放完成后关闭窗口并返回主页面
            await self.close_and_return_to_main_window()
            return True

        except Exception as e:
            print(f"进入课程《{course_name}》时发生错误：{e}")
            
            # 发生错误时，确保返回主页面并继续执行下一个课程
            await self.close_and_return_to_main_window()
            return False  # 表示失败，调用者可以决定是否尝试下一个课程

    async def close_and_return_to_main_window(self):
        all_pages = self.context.pages  # 获取所有窗口
        if len(all_pages) > 1:
            # print(f"关闭当前窗口，并切换回主课程页面。")
            await self.page.close()  # 关闭当前窗口
            
            # 等待窗口关闭后切换
            await asyncio.sleep(1)  # 让浏览器处理关闭窗口动作
            self.page = all_pages[0]  # 切换到主窗口
            print("已切换回主课程页面窗口。")
            print("============================下一节课============================")
        else:
            print("未检测到新窗口，无需切换。")
    
    async def fetch_course_sections(self):
        await self.page.wait_for_load_state('networkidle')

        sections = await self.page.query_selector_all("ul.iv-course-play-detail-menu-item > li")
        completed_sections = []
        uncompleted_sections = []

        for section in sections:
            # 提取进度
            progress_element = await section.query_selector("div.ivu-chart-circle-inner span")
            progress_text = await progress_element.inner_text() if progress_element else "0%"
            progress = int(progress_text.strip("%")) if progress_text.strip("%").isdigit() else 0

            # 提取标题（系列课程带“第X集”）
            title_element = await section.query_selector("p.iv-course-play-detail-menu-title")
            title = await title_element.inner_text() if title_element else "未知标题"
            # 分类小节
            section_data = {"title": title, "progress": progress, "element": section}
            if progress >= 100:
                completed_sections.append(section_data)
            else:
                uncompleted_sections.append(section_data)

        return completed_sections, uncompleted_sections

    async def play_series_sections(self):
        # 初始化队列
        await self.page.wait_for_load_state('networkidle')
        completed_sections, uncompleted_sections = await self.fetch_course_sections()
        # print(uncompleted_sections)
        while uncompleted_sections:
            # 选择一个未完成的小节课
            current_section = uncompleted_sections.pop(0)
            title = current_section["title"]
            section_element = current_section["element"]
            # 点击小节课切换到对应页面
            await section_element.click()
            await asyncio.sleep(6)  # 确保页面切换完成
            print(f"开始学习小节课: {title}")
            # # 点击播放按钮
            # play_button = await self.page.query_selector("xg-start.xgplayer-start")
            # if play_button:
            #     await play_button.click()
            #     print(f"已点击播放按钮，正在播放: {title}")
            # 监控播放状态
            await self.monitor_course_progress(title)
            # 标记为已完成
            completed_sections.append(current_section)
            print(f"完成学习小节课: {title}")
        print("系列课程学习完成！")
        # 系列课程学习完成后，关闭当前窗口并返回原窗口
        await self.close_and_return_to_main_window()

    async def monitor_course_progress(self, course_name):
        print("监控播放状态中...")
        
        total_timeout = 3600  # 设置最大监控时间为1小时
        start_time = time.time()
        last_activity_time = start_time
        activity_interval = 1500 # 25分钟

        while time.time() - start_time < total_timeout:
            is_paused = await self.page.evaluate("document.querySelector('video')?.paused")
            video_duration = await self.page.evaluate("document.querySelector('video')?.duration")
            current_time = await self.page.evaluate("document.querySelector('video')?.currentTime")

            if is_paused:
                play_button = await self.page.query_selector("xg-start.xgplayer-start")
                if play_button:
                    await play_button.click()
                    print("检测到视频暂停，尝试点击播放按钮...恢复播放成功")
            # 检测是否播放结束
            progress = await self.page.evaluate("document.querySelector('video')?.currentTime / document.querySelector('video')?.duration")
            if progress and progress >= 0.99:
                print(f"{course_name}播放完成。")
                break
            await asyncio.sleep(10)  # 每隔10秒检查一次
            # 如果视频暂停，可能已经播放完毕
            if is_paused and current_time >= video_duration - 1:
                print(f"{course_name} 播放完成，关闭页面并返回主界面。")
                await self.close_and_return_to_main_window()
                break

            # 检查是否需要模拟用户活动
            if time.time() - last_activity_time >= activity_interval:
                await self.simulate_user_activity()
                last_activity_time = time.time()

            await asyncio.sleep(10)

        # 如果超时未退出，则强制返回主页面
        if time.time() - start_time >= total_timeout:
            print("播放超时，尝试重新启动课程。")
            await self.close_and_return_to_main_window()

    async def simulate_user_activity(self):
        """模拟一次用户活动，防止掉线"""
        print("开始模拟用户活动...")
        activity_type = random.choice(["mouse_move", "scroll"])
        
        if activity_type == "mouse_move":
            x, y = random.randint(10, 50), random.randint(10, 50)
            await self.page.mouse.move(x, y)
            print(f"模拟鼠标移动到 ({x}, {y})")

        elif activity_type == "scroll":
            scroll_distance = random.randint(-10, 10)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            print(f"模拟页面滚动：滚动距离 {scroll_distance}")

        print("用户活动模拟完成。")