import base64
import json
import logging
import urllib

import requests


class BaiduContentAudit():
    def get_access_token(self):
        client_id = '4mvNz3iC1C65Hf5AudbsMyF2'                #此变量赋值成自己API Key的值
        client_secret = 'THPwnPzG8h0UtLO53L88P9Bjqk837YzL'    #此变量赋值成自己Secret Key的值
        auth_url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret

        response_at = requests.get(auth_url)
        json_result = json.loads(response_at.text)
        access_token = json_result['access_token']
        return access_token

    def audit_conetnt(self,img_url,access_token):
        url_audit_content = f"https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/user_defined?access_token={access_token}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # 因为提交URL让baidu去读取图片，总是返回图片下载错误
        # 所以我们这里将读取URL指向的图片，将图片转成BASE64编码，改用提交BASE64编码而不是提交URL
        # img_obj = urllib.request.urlopen(img_url)
        # img_obj = open('pic/87.67576599-20180627-7732316426fb579fba666eb5de0fde29.jpg','rb')
        img_obj = requests.get(img_url)
        img_base64 = base64.b64encode(img_obj.content)
        post_data = {
            # 'image': url_pic,
            # 'image_type' : 'URL',
            'image': img_base64,
        }
        response = requests.post(url_audit_content,headers=headers,data=post_data)
        logging.warning(response.text)
        json_result = json.loads(response.text)
        if "不合规" in json_result['conclusion']:
            for people in json_result['data']:
                logging.warning(f"{people['msg']}--{people['stars'][0]['name']}:{people['stars'][0]['probability']}")



if __name__ == '__main__':
    img_url = "https://b-ssl.duitang.com/uploads/item/201601/12/20160112140519_hRWZe.jpeg"
    baidu_content_audit = BaiduContentAudit()
    access_token = baidu_content_audit.get_access_token()
    baidu_content_audit.audit_conetnt(img_url,access_token)