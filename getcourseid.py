import aiohttp

# 新的 API 地址（根据你提供的请求 URL）
NEW_API_URL = "https://bjce.bjdj.gov.cn/api-course/portal/open/usercourse/listCourse"
# 这个是服务器发送请求返回课程的url
# https://bjce.bjdj.gov.cn/api-course/portal/open/usercourse/listCourse?searchCategoryID=xinshidaishoudufazhan&searchCourseName=&pageSize=16&currentPage=1&searchHasChild=1&lang=zh_CN
# NEW_API_URL="https://bjce.bjdj.gov.cn/#/course/courseResources?activedIndex=3&id=xinshidaishoudufazhan"

# 根据你提供的请求头信息，构造请求头（注意大小写及必填字段）
NEW_HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'connection': 'keep-alive',
    'host': 'bjce.bjdj.gov.cn',
    'referer': 'https://bjce.bjdj.gov.cn/',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'terminal': 'pc',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
    'x-xsrf-token': 'd4a489f4-824b-4548-8862-891406ba0aad'
}

# 如果有其他默认参数，可在这里设置，这里仅说明 GET 方式下固定部分参数
BASE_PARAMS = {
    'searchCategoryID': 'xinshidaishoudufazhan',  # 该参数就是你现在请求的专题ID
    'searchCourseName': '',
    'pageSize': 16,            # 根据实际情况，是否需要调大
    'currentPage': 2,
    'searchHasChild': 1,
    'lang': 'zh_CN'
}


async def Get_course_id(cookie: str, search_category: str, page_size: int, current_page: int):
    """
    根据传入的 cookie、专题ID（search_category）、每页条数和当前页码，从接口获取课程列表数据。
    获取课程的基本信息，包括 courseID、courseName、setType 等字段。
    """
    headers = NEW_HEADERS.copy()
    # 将 cookie 填入 headers 内，注意必须包含所有有效的 Cookie 字段
    headers['cookie'] = cookie

    # 更新查询参数
    params = BASE_PARAMS.copy()
    params.update({
        'searchCategoryID': search_category,  # 传入的专题ID
        'pageSize': page_size,
        'currentPage': current_page
    })
    

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(NEW_API_URL, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"API请求失败，状态码: {response.status}")
                    return []
                json_resp = await response.json(encoding='utf-8')
        except Exception as e:
            print(f"请求过程中出现异常: {e}")
            return []

    # 根据返回的数据格式进行解析，假设最外层为 "data"，为一个列表
    courses = json_resp.get("data", [])
    course_messages = []
    

    for course in courses:
        # 检查必要字段：courseID 和 courseName
        user_name = course.get("userName")
        course_id = course.get("courseID")
        course_name = course.get("courseName")
        set_type = course.get("setType")  # 提取 setType 字段
        if not course_id or not course_name or set_type is None:
            print("课程数据缺少必要字段，跳过此条记录")
            continue

        # 优先使用外层的学习进度；若为空，则尝试从 userCourse 字段中获取
        progress = course.get("learningProgress")
        if progress is None and course.get("userCourse"):
            progress = course["userCourse"].get("learningProgress")
        set_type = course.get("setType")      
        # 优先使用外层的课程时长；若为空，则尝试从 userCourse 字段中获取
        duration = course.get("courseDuration")
        if duration is None and course.get("userCourse"):
            duration = course["userCourse"].get("courseDuration")  # 注意这里对应字段名可能是 courseDuration
            if duration is None:  # 如果外层和 userCourse 均没有 courseDuration，尝试获取 learningDuration
                duration = course["userCourse"].get("learningDuration")
        progress = progress or 0
        # 构建最终返回的课程信息，增加 setType 字段
        if progress < 0.8:  # 仅当 progress 小于 0.8 时才处理
            course_info = {
                "user": user_name,
                "id": course_id,
                "name": course_name.strip(),
                "progress": progress,
                "duration": duration,
                "courseCode": course.get("courseCode"),
                "courseIntroduction": course.get("courseIntroduction"),
                "courseYear": course.get("courseYear"),
                "coverImage": course.get("coverImage"),
                "setType": set_type  # 新增的字段
            }
            course_messages.append(course_info)

        # print(course_messages)
    return course_messages




# 示例调用（请在你的异步主函数中调用）
if __name__ == "__main__":
    import asyncio

    async def main():
        # 请传入实际的 cookie 信息，例如从浏览器复制：
        cookie = "lang=zh_CN; XSRF-TOKEN=d4a489f4-824b-4548-8862-891406ba0aad; SESSION=4161639f-2559-4d1d-9abf-6824904047f3"
        search_category = "zhengzhililun"  # 专题ID
        page_size = 16
        current_page = 1
        courses = await Get_course_id(cookie, search_category, page_size, current_page)
        for c in courses:
            print(c)

    asyncio.run(main())
