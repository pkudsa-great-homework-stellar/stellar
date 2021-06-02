import mimetypes
import os
import zipfile
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import datetime
from secrets_local import MAIL, SMTP_SERVER


def zip_dir(dir_path, outFullName) -> bool:
    """
    压缩指定文件夹
    :param dir_path: 目标文件夹路径
    :param outFullName:  压缩文件保存路径+XXXX.zip
    :return:
    """
    testcase_zip = zipfile.ZipFile(outFullName, 'w', zipfile.ZIP_DEFLATED)
    for path, dir_names, file_names in os.walk(dir_path, topdown=False):
        for filename in file_names:
            testcase_zip.write(os.path.join(path, filename))
    testcase_zip.close()
    return True


def sendmail(tomail: str, name: str, results: str, attach_path: str) -> bool:
    server = smtplib.SMTP(SMTP_SERVER, 25)
    server.login(MAIL['user'], MAIL['password'])
    time = datetime.datetime.today().strftime("%m-%d %H:%M")
    msg = MIMEMultipart()
    msg.attach(MIMEText(f"{name}的计算完成！\n"+results +
                        "\n具体报告见附件\n"+f"完成时间：{time}", 'plain', 'utf-8'))
    msg['From'] = MAIL['user']
    msg['To'] = tomail
    msg['subject'] = f"{name}的计算报告"
    with open(attach_path, 'rb') as data:
        ctype, encoding = mimetypes.guess_type(attach_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        file_msg = MIMEBase(maintype, subtype)
        file_msg.set_payload(data.read())
    encoders.encode_base64(file_msg)
    file_msg.add_header('Content-Disposition',
                        'attachment', filename=f"{name}.zip")
    msg.attach(file_msg)
    server.sendmail(MAIL['user'], tomail, msg.as_string())
    server.quit()
    return True
