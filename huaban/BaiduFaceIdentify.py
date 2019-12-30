import base64
import urllib
import json
import logging
import requests


class BaiduFaceIdentify():
    #此函数用于获取access_token，返回access_token的值
    #此函数被parse_face_pic调用
    def get_access_token(self):
        client_id = 'KuLRFhTzX3zBFBSrbQBsl6Q4'                #此变量赋值成自己API Key的值
        client_secret = '8ahbIb2hEOePzXhehw9ZDL9kGvbzIHTU'    #此变量赋值成自己Secret Key的值
        auth_url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret

        response_at = requests.get(auth_url)
        json_result = json.loads(response_at.text)
        access_token = json_result['access_token']
        return access_token

    #此函数进行人脸识别，返回识别到的人脸列表
    #此函数被parse_face_pic调用
    def identify_faces(self,url_pic,url_fi):
        headers = {
            'Content-Type' : 'application/json; charset=UTF-8'
        }
        # 因为提交URL让baidu去读取图片，总是返回图片下载错误
        # 所以我们这里将读取URL指向的图片，将图片转成BASE64编码，改用提交BASE64编码而不是提交URL
        pic_obj = urllib.request.urlopen(url_pic)
        pic_base64 = base64.b64encode(pic_obj.read())
        post_data = {
            # 'image': url_pic,
            # 'image_type' : 'URL',
            'image': pic_base64,
            'image_type': 'BASE64',
            'face_field' : 'facetype,gender,age,beauty', #expression,faceshape,landmark,race,quality,glasses
            'max_face_num': 1
        }

        response_fi = requests.post(url_fi,headers=headers,data=post_data)
        json_fi_result = json.loads(response_fi.text)
        # 有些图片是没有人脸的，或者识别有问题，这个我们不细管直接捕获异常就返回空列表
        try:
            # if json_fi_result['result'] is None:
            #     return []
            # else:
                return json_fi_result['result']['face_list']
        except:
            return []
        #下边的print也许是最直观，你最想要的
        #print(json_fi_result['result']['face_list'][0]['age'])
        #print(json_fi_result['result']['face_list'][0]['beauty'])

    #此函数用于解析进行人脸图片，返回图片中人物颜值
    #此函数调用get_access_token、identify_faces
    def parse_face_pic(self,url_pic):
        #调用get_access_token获取access_token
        access_token = self.get_access_token()
        url_fi = 'https://aip.baidubce.com/rest/2.0/face/v3/detect?access_token=' + access_token
        #调用identify_faces，获取人脸列表
        json_faces = self.identify_faces(url_pic,url_fi)
        # 如果没有人脸，那么就以0.0为颜值评分返回
        if len(json_faces) == 0:
            logging.warning('未识别到人脸')
            return 0.0
        else:
            for json_face in json_faces:
                logging.debug('种类：'+json_face['face_type']['type'])
                logging.debug('性别：'+json_face['gender']['type'])
                logging.debug('年龄：'+str(json_face['age']))
                logging.debug('颜值：'+str(json_face['beauty']))
                # 如果识别到的不是妹子，也以1.0为颜值评分返回
                # 如果识别到的是妹子，直接以值颜值返回
                if json_face['gender']['type'] != 'female':
                    logging.info('图片不是妹子')
                    return 1.0
                else:
                    return json_face['beauty']

if __name__ == '__main__':
    #uil_pic赋值成自己要测试的图片的url地址
    url_pic = 'https://ss1.bdstatic.com/70cFuXSh_Q1YnxGkpoWK1HF6hhy/it/u=1357154930,886228461&fm=27&gp=0.jpg'
    bfi = BaiduFaceIdentify()
    bfi.parse_face_pic(url_pic)