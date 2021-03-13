# -*-coding:utf-8-*-

import base64
import requests
import configparser
from prettytable import PrettyTable


class App:
    __GET_USER_CENTER_INFO_URL = 'https://gate.lagou.com/v1/neirong/edu/member/getMemberCenterInfo'
    __GET_USER_ALL_COURSES_URL = 'https://gate.lagou.com/v1/neirong/kaiwu/getAllCoursePurchasedRecordForPC'
    __GET_USER_ALL_COURSES_DETAILS_URI_PARTIAL = 'https://gate.lagou.com/v1/neirong/kaiwu/getCourseLessons?courseId='
    __REQ_PARTIAL_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Cookie': None,
        'Referer': 'https://kaiwu.lagou.com/',
        'Origin': 'https://kaiwu.lagou.com',
        'Sec-fetch-dest': 'empty',
        'Sec-fetch-mode': 'cors',
        'Sec-fetch-site': 'same-site',
        'x-l-req-header': '{deviceType:1}'
    }
    __GET_USER_LESSON_DETAIL_URI_PARTIAL = 'https://gate.lagou.com/v1/neirong/kaiwu/getCourseLessonDetail?lessonId='

    __all_courses = []

    __request_freq = -1

    def __convert_html_to_pdf(self, html, f_pdf):
        pass

    def login(self):
        config = configparser.ConfigParser()

        try:
            config.read("config.ini")
        except:
            print("=>读取config.ini文件失败")
            return False

        if config['app']['cookie'] is None:
            print("=>登录失败, Cookie编码为空")
            return False

        if config['app']['request_freq'] is None:
            print("=>获取请求速率失败, 可能没有正确配置")
            return False

        try:
            self.__REQ_PARTIAL_HEADERS['Cookie'] = base64.b64decode(s=config['app']['cookie']).decode(encoding='utf-8')
            self.__request_freq = config['app']['request_freq']
        except:
            print("=>Base64解码失败")
            return False
        return True

    def get_member_center_info(self):
        ret = requests.get(url=self.__GET_USER_CENTER_INFO_URL, headers=self.__REQ_PARTIAL_HEADERS)

        if ret.status_code == 200:
            content = ret.json()
            table = PrettyTable()
            table.field_names = ['昵称', 'ID', '已购课程数']
            table.align['昵称'] = "l"
            table.align['ID'] = "l"
            table.align['已购课程数'] = "l"
            table.add_row(
                [
                    content['content']['nickName'],
                    content['content']['memberId'],
                    content['content']['joinCourseCount']
                ]
            )
            print(table)
        else:
            print('=>请求出错')

    def list_all_courses(self):

        ret = requests.get(url=self.__GET_USER_ALL_COURSES_URL, headers=self.__REQ_PARTIAL_HEADERS)

        if ret.status_code == 200:
            content = ret.json()
            b_status = content['state']

            if str(b_status) == '1':
                print("=>登录成功, 你的基本信息如下: ")
            else:
                print("=>" + content['message'])
                return

            table = PrettyTable()
            table.field_names = ['专栏名称', '学习进度', '专栏更新进度', '专栏ID']
            table.align['专栏名称'] = "l"
            table.align['学习进度'] = "l"
            table.align['专栏更新进度'] = "l"
            table.align['专栏ID'] = "l"
            courses = content['content']['allCoursePurchasedRecord'][0]['courseRecordList']
            for course in courses:
                table.add_row([course['name'], course['lastLearnLessonName'], course['updateProgress'], course['id']])
                self.__all_courses.append(str(course['id']))
            print(table)
        else:
            print('=>请求出错')

    def show_usage_info(self):

        print("LaGou Downloader")
        print("- Version: v1.0.0")
        print("- Chrome Driver: OK")
        print("- FFmpeg: OK")
        print("- Python: OK")

        table = PrettyTable()
        table.field_names = ['命令', '作用']
        table.align['命令'] = "l"
        table.align['作用'] = "l"
        table.add_row(['pdf', '保存专栏为PDF'])
        table.add_row(['all', '保存专栏的全部数据, 包括PDF和音视频'])
        table.add_row(['help', '显示帮助信息'])
        table.add_row(['list', '列出已经购买的全部课程'])
        table.add_row(['quit', '退出'])
        table.add_row(['login', '登陆拉勾教育'])
        table.add_row(['video', '保存专栏为视频'])
        table.add_row(['audio', '保存专栏为音频'])
        table.add_row(['detail', '获取专栏详细信息'])
        print(table)

    def get_course_detail(self, op_type):
        i_course_id = input("=>请输入专栏ID: ")

        if i_course_id is None:
            print("=>输入的ID不正确")
            return

        if i_course_id not in self.__all_courses:
            print("=>输入的ID没有购买, 如果已经购买, 执行list命令将会刷新缓存的专栏列表")
            return

        ret = requests.get(url=self.__GET_USER_ALL_COURSES_DETAILS_URI_PARTIAL + i_course_id,
                           headers=self.__REQ_PARTIAL_HEADERS)

        if ret.status_code == 200:
            content = ret.json()
            state = content['state']

            if str(state) == '1':
                sections = content['content']['courseSectionList']
                course_name = content['content']['courseName']

                table = PrettyTable()
                table.field_names = ['专栏ID', '专栏名称', '章节ID', '章节名称', '课程ID', '课程名称', '视频ID', '音频ID',
                                     '状态', '视频时长', '音频时长']
                table.align['专栏ID'] = 'l'
                table.align['专栏名称'] = 'l'
                table.align['章节ID'] = 'l'
                table.align['章节名称'] = 'l'
                table.align['课程ID'] = 'l'
                table.align['课程名称'] = 'l'
                table.align['视频ID'] = 'l'
                table.align['音频ID'] = 'l'
                table.align['状态'] = 'l'
                table.align['视频时长'] = 'l'
                table.align['音频时长'] = 'l'

                pre_process_items = []

                for section in sections:
                    section_id = section['id']
                    section_name = section['sectionName']
                    course_id = section['courseId']
                    lessons = section['courseLessons']
                    for lesson in lessons:
                        lesson_id = lesson['id']
                        lesson_app_id = lesson['appId']
                        lesson_name = lesson['theme']
                        lesson_text_content = lesson['textContent']
                        lesson_status = lesson['status']
                        lesson_text_url = lesson['textUrl']
                        lesson_play_type_code = lesson['playTypeCode']

                        lesson_video_id = lesson['videoMediaDTO']['id']
                        lesson_video_channel = lesson['videoMediaDTO']['channel']
                        lesson_video_duration = lesson['videoMediaDTO']['duration']
                        lesson_video_duration_num = lesson['videoMediaDTO']['durationNum']
                        lesson_video_file_id = lesson['videoMediaDTO']['fileId']
                        lesson_video_file_url = lesson['videoMediaDTO']['fileUrl']
                        lesson_video_file_edk = lesson['videoMediaDTO']['fileEdk']
                        lesson_video_file_size = lesson['videoMediaDTO']['fileSize']
                        lesson_video_enc_file_id = lesson['videoMediaDTO']['encryptedFileId']
                        lesson_video_media_id = lesson['videoMediaDTO']['mediaId']
                        lesson_video_clarity = lesson['videoMediaDTO']['clarity']
                        lesson_video_tc_enc_file_id = lesson['videoMediaDTO']['tcEncryptedFileId']
                        lesson_video_tc_app_id = lesson['videoMediaDTO']['tcAppId']
                        lesson_video_tc_player_token = lesson['videoMediaDTO']['tcPlayerToken']
                        lesson_video_free = lesson['videoMediaDTO']['free']

                        lesson_audio_id = lesson['audioMediaDTO']['id']
                        lesson_audio_channel = lesson['audioMediaDTO']['channel']
                        lesson_audio_duration = lesson['audioMediaDTO']['duration']
                        lesson_audio_duration_num = lesson['audioMediaDTO']['durationNum']
                        lesson_audio_file_id = lesson['audioMediaDTO']['fileId']
                        lesson_audio_file_url = lesson['audioMediaDTO']['fileUrl']
                        lesson_audio_file_edk = lesson['audioMediaDTO']['fileEdk']
                        lesson_audio_file_size = lesson['audioMediaDTO']['fileSize']
                        lesson_audio_enc_file_id = lesson['audioMediaDTO']['encryptedFileId']
                        lesson_audio_media_id = lesson['audioMediaDTO']['mediaId']
                        lesson_audio_clarity = lesson['audioMediaDTO']['clarity']
                        lesson_audio_tc_enc_file_id = lesson['audioMediaDTO']['tcEncryptedFileId']
                        lesson_audio_tc_app_id = lesson['audioMediaDTO']['tcAppId']
                        lesson_audio_tc_player_token = lesson['audioMediaDTO']['tcPlayerToken']
                        lesson_audio_free = lesson['audioMediaDTO']['free']

                        pre_process_items.append(
                            {
                                'section_id': section_id,
                                'section_name': section_name,
                                'course_id': course_id,
                                'lesson_id': lesson_id,
                                'lesson_app_id': lesson_app_id,
                                'lesson_name': lesson_name,
                                'lesson_text_content': lesson_text_content,
                                'lesson_status': lesson_status,
                                'lesson_text_url': lesson_text_url,
                                'lesson_play_type_code': lesson_play_type_code,
                                'lesson_video_id': lesson_video_id,
                                'lesson_video_channel': lesson_video_channel,
                                'lesson_video_duration': lesson_video_duration,
                                'lesson_video_duration_num': lesson_video_duration_num,
                                'lesson_video_file_id': lesson_video_file_id,
                                'lesson_video_file_url': lesson_video_file_url,
                                'lesson_video_file_edk': lesson_video_file_edk,
                                'lesson_video_file_size': lesson_video_file_size,
                                'lesson_video_enc_file_id': lesson_video_enc_file_id,
                                'lesson_video_media_id': lesson_video_media_id,
                                'lesson_video_clarity': lesson_video_clarity,
                                'lesson_video_tc_enc_file_id': lesson_video_tc_enc_file_id,
                                'lesson_video_tc_app_id': lesson_video_tc_app_id,
                                'lesson_video_tc_player_token': lesson_video_tc_player_token,
                                'lesson_video_free': lesson_video_free,
                                'lesson_audio_id': lesson_audio_id,
                                'lesson_audio_channel': lesson_audio_channel,
                                'lesson_audio_duration': lesson_audio_duration,
                                'lesson_audio_duration_num': lesson_audio_duration_num,
                                'lesson_audio_file_id': lesson_audio_file_id,
                                'lesson_audio_file_url': lesson_audio_file_url,
                                'lesson_audio_file_edk': lesson_audio_file_edk,
                                'lesson_audio_file_size': lesson_audio_file_size,
                                'lesson_audio_enc_file_id': lesson_audio_enc_file_id,
                                'lesson_audio_media_id': lesson_audio_media_id,
                                'lesson_audio_clarity': lesson_audio_clarity,
                                'lesson_audio_tc_enc_file_id': lesson_audio_tc_enc_file_id,
                                'lesson_audio_tc_app_id': lesson_audio_tc_app_id,
                                'lesson_audio_tc_player_token': lesson_audio_tc_player_token,
                                'lesson_audio_free': lesson_audio_free,
                            }
                        )

                        table.add_row(
                            [course_id, course_name, section_id, section_name, lesson_id, lesson_name, lesson_video_id,
                             lesson_audio_id, lesson_status, lesson_video_duration, lesson_audio_duration])

                if op_type == 'SHOW':
                    print(table)
                elif op_type == 'PDF':
                    self.__create_pdf_file(items=pre_process_items)
                elif op_type == 'VIDEO':
                    self.__create_video_file(items=pre_process_items)
                elif op_type == 'AUDIO':
                    self.__create_audio_file(items=pre_process_items)
                elif op_type == 'ALL':
                    self.__create_all_file(items=pre_process_items)
                else:
                    pass
            else:
                print(content['message'])

        else:
            print("=>请求出错")

    def __create_pdf_file(self, items):
        print("=>开始创建PDF文件..")

    def __create_video_file(self, items):
        print("=>开始下载视频文件..")

    def __create_audio_file(self, items):
        print("=>开始下载音频文件..")

    def __create_all_file(self, items):
        self.__create_pdf_file(items=items)
        self.__create_video_file()
        self.__create_audio_file()

    def __save_tasks(self, items):
        print("=>任务持久化成   功")


if __name__ == '__main__':
    app = App()

    try:
        while True:
            command = input('=>请输入子命令: ')
            if command == 'help':
                app.show_usage_info()
            elif command == 'quit':
                print('Bye')
                break
            elif command == 'list':
                app.list_all_courses()
            elif command == 'pdf':
                app.get_course_detail(op_type='PDF')
            elif command == 'video':
                app.get_course_detail(op_type='VIDEO')
            elif command == 'audio':
                app.get_course_detail(op_type='AUDIO')
            elif command == 'all':
                app.get_course_detail(op_type='ALL')
            elif command == 'login':
                if app.login():
                    app.get_member_center_info()
            elif command == 'detail':
                app.get_course_detail(op_type='SHOW')
            else:
                app.show_usage_info()

    except KeyboardInterrupt:
        print("")
        print("Bye")
        exit(0)
