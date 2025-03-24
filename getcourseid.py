import requests
import asyncio

url = "https://bjce.bjdj.gov.cn/api-course/portal/open/usercourse/listCourse?searchCategoryID=xinshidaishoudufazhan&searchCourseName=&pageSize=16&currentPage=1&searchHasChild=1&lang=zh_CN"

headers = {
    'Connection': 'close',
    'sec-ch-ua': '";Not A Brand";v="99", "Chromium";v="88"',
    'Accept': 'application/json, text/plain, */*',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Origin': 'https://bjce.bjdj.gov.cn',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://bjce.bjdj.gov.cn/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cookie': ''
}

# data = {
#     'page': '1',
#     'rows': '9',
#     'sort': 'Sort',
#     'order': 'desc',
#     'courseType': '',
#     'channelId': '975',
#     'title': '',
#     'titleNav': '课程中心',
#     'wordLimt': '35',
#     'teacher': '',
#     'flag': 'all',
#     'isSearch': '0',
#     'channelCode': '',
#     'isImportant': ''
# }

data = {
    "userCourseID": 0,
    "courseID": "a80ecea6-03a7-11f0-ab59-ee18dce1c88f",
    "userID": 0,
    "userName": 0,
    "joinDate": 0,
    "passState": 0,
    "passTarget": 0,
    "passDate": 0,
    "learningProgress": 0,
    "learningDuration": 0,
    "learningHour": 0,
    "state": 0,
    "sourceType": 0,
    "sourceID": 0,
    "totalLearningDuration": 0,
    "learningDetails": 0,
    "course": 0,
    "pcUserCourse": 0,
    "courseDuration": 0,
    "passNum": 0,
    "passedWay": 0,
    "courseType": 0,
    "year": 0,
    "obtainHoursType": 0,
    "playLength": 0,
    "socre": 0,
    "latestOperateDate": 0,
    'channlId':'',
    "rows":'',
    'page':''
}


async def Get_course_id(cookie: str, channel_id: str, rowlength: str, page_num: int):
    # 设置请求头中的 Cookie，确保请求可以携带用户会话信息
    headers['Cookie'] = cookie

    # 设置 POST 请求的请求体参数，包括频道 ID、每页的行数和当前页码
    data['channelId'] = channel_id  # 课程所属频道 ID，用于过滤课程分类
    data['rows'] = rowlength  # 每页课程条目数量，控制分页的行数
    data['page'] = str(page_num)  # 当前页码，获取分页数据

    # 发送 POST 请求以获取课程数据
    response = requests.post(url, headers=headers, data=data)

    # 解析返回的 JSON 数据，提取课程列表信息
    ListData = response.json()['Data']['ListData']  # 课程列表位于返回数据的 ListData 字段

    # 初始化课程信息列表，用于存储提取的课程 ID 和名称
    course_messages = []

    # 遍历课程列表，提取每门课程的 ID 和名称
    for course in ListData:
        course_message = {}
        id = course["Id"]  # 获取课程的唯一 ID
        name = course["Name"].strip()  # 获取课程名称，并去除首尾空白字符
        course_message[id] = name  # 以 ID 为键，名称为值存储课程信息
        course_messages.append(course_message)  # 将课程信息字典添加到列表中
    # 打印课程列表
    print("课程列表：")
    for course in course_messages:
        print(course)   

    # 返回课程信息列表，供后续调用
    return course_messages
