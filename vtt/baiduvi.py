import base64
import json
import os
import time
import shutil
import requests

class BaiduVoiceToTxt():
    # 初始化函数
    def __init__(self):
        # 定义要进行切割的pcm文件的位置。speech-vad-demo固定好的，没的选
        self.pcm_path = ".\\speech-vad-demo\\pcm\\16k_1.pcm"
        # 定义pcm文件被切割后，分割成的文件输出到的目录。speech-vad-demo固定好的，没的选
        self.output_pcm_path = ".\\speech-vad-demo\\output_pcm\\"

    # 百度AI接口只接受pcm格式，所以需要转换格式
    # 此函数用于将要识别的mp3文件转换成pcm格式，并输出为.\speech-vad-demo\pcm\16k_1.pcm
    def change_file_format(self,filepath):
        file_name = filepath
        # 如果.\speech-vad-demo\pcm\16k_1.pcm文件已存在，则先将其删除
        if os.path.isfile(f"{self.pcm_path}"):
            os.remove(f"{self.pcm_path}")
        # 调用系统命令，将文件转换成pcm格式，并输出为.\speech-vad-demo\pcm\16k_1.pcm
        change_file_format_command = f".\\ffmpeg\\bin\\ffmpeg.exe -y  -i {file_name}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {self.pcm_path}"
        os.system(change_file_format_command)

    # 百度AI接口最长只接受60秒的音视，所以需要切割
    # 此函数用于将.\speech-vad-demo\pcm\16k_1.pcm切割
    def devide_video(self):
        # 如果切割输出目录.\speech-vad-demo\output_pcm\已存在，那其中很可能已有文件，先将其清空
        # 清空目录的文件是先删除，再创建
        if os.path.isdir(f"{self.output_pcm_path}"):
            shutil.rmtree(f"{self.output_pcm_path}")
        time.sleep(1)
        os.mkdir(f"{self.output_pcm_path}")
        # vad-demo.exe使用相对路径.\pcm和.\output_pcm，所以先要将当前工作目录切换到.\speech-vad-demo下不然vad-demo.exe找不到文件
        os.chdir(".\\speech-vad-demo\\")
        # 直接执行.\vad-demo.exe，其默认会将.\pcm\16k_1.pcm文件切割并输出到.\output_pcm目录下
        devide_video_command = ".\\vad-demo.exe"
        os.system(devide_video_command)
        # 切换回工作目录
        os.chdir("..\\")

    # 此函数用于将.\speech-vad-demo\output_pcm\下的文件的文件名的时间格式化成0:00:00,000形式
    def format_time(self, msecs):
        # 一个小时毫秒数
        hour_msecs = 60 * 60 * 1000
        # 一分钟对应毫秒数
        minute_msecs = 60 * 1000
        # 一秒钟对应毫秒数
        second_msecs = 1000
        # 文件名的时间是毫秒需要先转成秒。+500是为了四舍五入，//是整除
        # msecs = (msecs + 500) // 1000
        # 小时
        hour = msecs // hour_msecs
        if hour < 10:
            hour = f"0{hour}"
        # 扣除小时后剩余毫秒数
        hour_left_msecs = msecs % hour_msecs
        # 分钟
        minute = hour_left_msecs // minute_msecs
        # 如果不足10分钟那在其前补0凑成两位数格式
        if minute < 10:
            minute = f"0{minute}"
        # 扣除分钟后剩余毫秒数
        minute_left_msecs = hour_left_msecs % minute_msecs
        # 秒
        second = minute_left_msecs // second_msecs
        # 如果秒数不足10秒，一样在其前补0凑足两位数格式
        if second < 10:
            second = f"0{second}"
        # 扣除秒后剩余毫秒数
        second_left_msecs = minute_left_msecs % second_msecs
        # 如果不足10毫秒或100毫秒，在其前补0凑足三位数格式
        if second_left_msecs < 10:
            second_left_msecs = f"00{second_left_msecs}"
        elif second_left_msecs < 100:
            second_left_msecs = f"0{second_left_msecs}"
        # 格式化成00:00:00,000形式，并返回
        time_format = f"{hour}:{minute}:{second},{second_left_msecs}"
        return time_format

    # 此函数用于申请访问ai接口的access_token
    def get_access_token(self):
        # 此变量赋值成自己API Key的值
        client_id = 'f3wT23Otc8jXlDZ4HGtS4jfT'
        # 此变量赋值成自己Secret Key的值
        client_secret = 'YPPjW3E0VGPUOfZwhjNGVn7LTu3hwssj'
        auth_url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret

        response_at = requests.get(auth_url)
        # 以json格式读取响应结果
        json_result = json.loads(response_at.text)
        # 获取access_token
        access_token = json_result['access_token']
        return access_token

    # 此函数用于将.\speech-vad-demo\output_pcm\下的单个文件由语音转成文件
    def transfer_voice_to_srt(self,access_token,filepath):
        # 百度语音识别接口
        url_voice_ident = "http://vop.baidu.com/server_api"
        # 接口规范，以json格式post数据
        headers = {
            'Content-Type': 'application/json'
        }
        # 打开pcm文件并读取文件内容
        pcm_obj = open(filepath,'rb')
        pcm_content_base64 = base64.b64encode(pcm_obj.read())
        pcm_obj.close()
        # 获取pcm文件大小
        pcm_content_len = os.path.getsize(filepath)

        # 接口规范，则体函义见官方文件，值得注意的是cuid和speech两个参数的写法
        post_data = {
            "format": "pcm",
            "rate": 16000,
            "dev_pid": 1737,
            "channel": 1,
            "token": access_token,
            "cuid": "1111111111",
            "len": pcm_content_len,
            "speech": pcm_content_base64.decode(),
        }
        proxies = {
            'http':"127.0.0.1:8080"
        }
        # 调用接口，进行音文转换
        response = requests.post(url_voice_ident, headers=headers, data=json.dumps(post_data))
        # response = requests.post(url_voice_ident,headers=headers,data=json.dumps(post_data),proxies=proxies)
        return response.text

if __name__ == "__main__":
    # 实例化
    baidu_voice_to_srt_obj = BaiduVoiceToTxt()
    # 自己要进行音文转换的音视存放的文件夹
    video_dir = ".\\video\\"
    all_video_file =[]
    all_file = os.listdir(video_dir)
    subtitle_format = "{\\fscx75\\fscy75}"
    # 只接受.mp3格式文件。因为其他格式没研究怎么转成pcm才是符合接口要求的
    for filename in all_file:
        if ".mp3" in filename:
            all_video_file.append(filename)
    all_video_file.sort()
    i = 0
    video_file_num = len(all_video_file)
    print(f"当前共有{video_file_num}个音频文件需要转换，即将进行处理请稍等...")
    # 此层for循环是逐个mp3文件进行处理
    for video_file_name in all_video_file:
        i += 1
        print(f"当前转换{video_file_name}({i}/{video_file_num})")
        # 将音视翻译成的内容输出到同目录下同名.txt文件中
        video_file_srt_path = f".\\video\\{video_file_name[:-4]}.srt"
        # 以覆盖形式打开.txt文件
        video_file_srt_obj = open(video_file_srt_path,'w+')

        filepath = os.path.join(video_dir, video_file_name)
        # 调用change_file_format将mp3转成pcm格式
        baidu_voice_to_srt_obj.change_file_format(filepath)
        # 将转换成的pcm文件切割成多个小于60秒的pcm文件
        baidu_voice_to_srt_obj.devide_video()
        # 获取token
        access_token = baidu_voice_to_srt_obj.get_access_token()
        # 获取.\speech-vad-demo\output_pcm\目录下的文件列表
        file_dir = baidu_voice_to_srt_obj.output_pcm_path
        all_pcm_file = os.listdir(file_dir)
        all_pcm_file.sort()
        j = 0
        pcm_file_num = len(all_pcm_file)
        print(f"当前所转文件{video_file_name}({i}/{video_file_num})被切分成{pcm_file_num}块，即将逐块进行音文转换请稍等...")
        # 此层for是将.\speech-vad-demo\output_pcm\目录下的所有文件逐个进行音文转换
        for filename in all_pcm_file:
            j += 1
            filepath = os.path.join(file_dir, filename)
            if (os.path.isfile(filepath)):
                # 获取文件名上的时间
                time_str = filename[10:-6]
                time_str_dict = time_str.split("-")
                time_start_str = baidu_voice_to_srt_obj.format_time(int(time_str_dict[0]))
                time_end_str = baidu_voice_to_srt_obj.format_time(int(time_str_dict[1]))
                print(f"当前转换{video_file_name}({i}/{video_file_num})-{time_start_str}-{time_end_str}({j}/{pcm_file_num})")
                response_text = baidu_voice_to_srt_obj.transfer_voice_to_srt(access_token, filepath)
                # 以json形式读取返回结果
                json_result = json.loads(response_text)
                # 将音文转换结果写入.srt文件
                video_file_srt_obj.writelines(f"{j}\r\n")
                video_file_srt_obj.writelines(f"{time_start_str} --> {time_end_str}\r\n")
                if json_result['err_no'] == 0:
                    print(f"{time_start_str}-{time_end_str}({j}/{pcm_file_num})转换成功：{json_result['result'][0]}")
                    video_file_srt_obj.writelines(f"{subtitle_format}{json_result['result'][0]}\r\n")
                elif json_result['err_no'] == 3301:
                    print(f"{time_start_str}-{time_end_str}({j}/{pcm_file_num})音频质量过差无法识别")
                    video_file_srt_obj.writelines(f"{subtitle_format}音频质量过差无法识别\r\n")
                else:
                    print(f"{time_start_str}-{time_end_str}({j}/{pcm_file_num})转换过程遇到其他错误")
                    video_file_srt_obj.writelines(f"{subtitle_format}转换过程遇到其他错误\r\n")
                video_file_srt_obj.writelines(f"\r\n")
        video_file_srt_obj.close()
