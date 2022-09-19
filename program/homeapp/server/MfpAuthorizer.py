# -*- coding: UTF8 -*-
import re
import os
import requests
import json
import time
import hashlib

from pyramid.view import view_config
from hmserver.apps.common.logger import logger_obj


class MfpAuthorizer(object):

    __headers = None
    __key = "a97dk4_m_"

    __licenseFilePath = "LicenseCode.json"

    def __init__(self, headers):
        self.__headers = headers

    # licenseCategory: 1 短码，2 长码
    def __saveLicenseCode(self, licenseCategory, licenseCode):
        licenseJson = {
            "licenseCategory": licenseCategory,
            "licenseCode": licenseCode,
            "verifyTimeStamp": int(time.time())
        }
        if os.path.isfile(self.__licenseFilePath):
            os.remove(self.__licenseFilePath)
        if not os.path.isfile(self.__licenseFilePath):
            newFile = open(self.__licenseFilePath, 'w+')
            newFile.write(json.dumps(licenseJson))
            newFile.close()
        logger_obj.log("[MfpAuthorizer]LicenseCode Saved: " +
                       json.dumps(licenseJson))
        return licenseJson

    def __loadLicenseCode(self):
        licenseJson = None
        if os.path.isfile(self.__licenseFilePath):
            fileObj = open(self.__licenseFilePath, 'r')
            text = fileObj.read()
            fileObj.close()
            if text:
                licenseJson = json.loads(text)
        logger_obj.log("[MfpAuthorizer]LicenseCode Loaded: " +
                       json.dumps(licenseJson))
        return licenseJson

    def __buildMachineCodePlain(self):
        miGetter = MfpInfoGetter(self.__headers)
        mfpInfo = miGetter.GetMfpdeviceCapability()
        sn = mfpInfo["serial_no"]
        modelName = mfpInfo["model_name"]
        # macAddress = mfpInfo["mac_address"]
        # hostName = mfpInfo["host_name"]
        appInfo = miGetter.GetAppContextSelf()
        appId = appInfo["app_id"]
        # appName = appInfo["app_name"]
        # appType = appInfo["app_type"]
        appVersion = appInfo["app_version"]
        plain = sn+","+modelName+","+appId+","+appVersion
        return plain

    def __buildLicensePlain(self, licenseType):
        miGetter = MfpInfoGetter(self.__headers)
        mfpInfo = miGetter.GetMfpdeviceCapability()
        sn = mfpInfo["serial_no"]
        modelName = mfpInfo["model_name"]
        appInfo = miGetter.GetAppContextSelf()
        appId = appInfo["app_id"]
        appVersion = appInfo["app_version"]
        plain = str(licenseType)+","+sn+","+modelName + \
            ","+appId+","+appVersion+",4102415999"
        return plain

    def __buildShortLicensePlain(self, licenseType):
        miGetter = MfpInfoGetter(self.__headers)
        mfpInfo = miGetter.GetMfpdeviceCapability()
        sn = mfpInfo["serial_no"]
        modelName = mfpInfo["model_name"]
        appInfo = miGetter.GetAppContextSelf()
        appId = appInfo["app_id"]
        appVersion = appInfo["app_version"]

        # license type in (1,2,3)
        plain = str(licenseType)+","+sn+","+modelName + \
            ","+appId+",1.0.0,4102415999"
        # license type is 9
        if licenseType == 9:
            plain = str(licenseType)+","+sn+","+modelName + \
                ","+appId+","+appVersion+",4102415999"
        return plain

    # maichine code format: sn,modelName,appId,appVersion
    def GetMachineCode(self):
        plain = self.__buildMachineCodePlain()
        logger_obj.log("[MfpAuthorizer]GetMachineCode Plain: " + plain)
        tse = TSEncrypter(self.__key)
        encrypted16 = tse.Encrypt(plain)
        logger_obj.log(
            "[MfpAuthorizer]GetMachineCode Encrypted16: " + encrypted16)
        return encrypted16

    # license code format: licenseType,sn,modelName,appId,appVersion,expiredTimeStamp
    # license type: 1 free, 2 professional, 3 enterprise, 9 require same version
    def __verifyLicenseCode(self, licenseCode):
        logger_obj.log("[MfpAuthorizer]VerifyLicenseCode: "+licenseCode)
        miGetter = MfpInfoGetter(self.__headers)
        mfpInfo = miGetter.GetMfpdeviceCapability()
        sn = mfpInfo["serial_no"]
        modelName = mfpInfo["model_name"]
        appInfo = miGetter.GetAppContextSelf()
        appId = appInfo["app_id"]
        appVersion = appInfo["app_version"]
        tse = TSEncrypter(self.__key)
        plain = tse.Decrypt(licenseCode)
        plainParts = plain.split(',')
        licenseType = int(plainParts[0])
        snFromLicense = plainParts[1]
        modelNameFromLicense = plainParts[2]
        appIdFromLicense = plainParts[3]
        appVersionFromLicense = plainParts[4]
        expiredTimeStamp = int(plainParts[5])
        err_msg = ""
        # 基本信息是否合法
        isBaseInfoValid = snFromLicense == sn and modelNameFromLicense == modelName and appIdFromLicense == appId
        if not isBaseInfoValid:
            err_msg += "License信息有误;"
        # 根据license类型进行判断
        isLicenseTypeValid = True
        if licenseType == 9:
            isLicenseTypeValid = appVersion == appVersionFromLicense
        if not isLicenseTypeValid:
            err_msg += "非License授权软件版本;"
        # 是否在有效期内
        isNotExpired = int(time.time()) < expiredTimeStamp
        if not isNotExpired:
            err_msg += "License已过期;"
        isValid = isBaseInfoValid and isNotExpired
        if isValid:
            err_msg = "License验证通过!"
        return {
            "is_valid": isValid,
            "license_type": licenseType,
            "license_app_version": appVersionFromLicense,
            "expired_timestamp": expiredTimeStamp,
            "err_msg": err_msg
        }

    def VerifyLicenseCode(self, licenseCode):
        saveResult = None
        licenseResult = self.__verifyLicenseCode(licenseCode)
        if licenseResult["is_valid"]:
            saveResult = self.__saveLicenseCode(2, licenseCode)
            licenseResult["verify_timestamp"] = saveResult["verifyTimeStamp"]
        logger_obj.log(
            "[MfpAuthorizer]VerifyShortLicenseCode Result: "+json.dumps(licenseResult))
        return licenseResult

    # 验证7位License短码，第一位表示license类型，后6位为license明文信息的定制hash值
    def __verifyShortLicenseCode(self, shortLicenseCode):
        result = {
            "is_valid": False,
            "license_type": 1,
            "license_app_version": None,
            "expired_timestamp": 4102415999,
            "err_msg": "license验证未通过！"
        }
        logger_obj.log(
            "[MfpAuthorizer]VerifyShortLicenseCode: "+shortLicenseCode)
        if shortLicenseCode and len(shortLicenseCode) == 7:
            licenseType = shortLicenseCode[0]
            hashCode = shortLicenseCode[1:7]
            plain = self.__buildShortLicensePlain(licenseType)
            tse = TSEncrypter(self.__key)
            hashCodeLocal = tse.Hash(plain)
            result["is_valid"] = hashCodeLocal == hashCode
            if result["is_valid"]:
                result["err_msg"] = "License验证通过！"
        return result

    def VerifyShortLicenseCode(self, shortLicenseCode):
        saveResult = None
        licenseResult = self.__verifyShortLicenseCode(shortLicenseCode)
        if licenseResult["is_valid"]:
            saveResult = self.__saveLicenseCode(1, shortLicenseCode)
            licenseResult["verify_timestamp"] = saveResult["verifyTimeStamp"]
        logger_obj.log(
            "[MfpAuthorizer]VerifyShortLicenseCode Result: "+json.dumps(licenseResult))
        return licenseResult

    def IsLicenseValid(self):
        result = {
            "is_valid": False,
            "license_type": 0,
            "license_app_version": None,
            "expired_timestamp": 4102415999,
            "err_msg": "未设置License",
            "verify_timestamp": 0
        }
        licenseJson = self.__loadLicenseCode()
        if licenseJson:
            if licenseJson["licenseCategory"] == 1:
                result = self.__verifyShortLicenseCode(
                    licenseJson["licenseCode"])
            elif licenseJson["licenseCategory"] == 2:
                result = self.__verifyLicenseCode(licenseJson["licenseCode"])
            result["verify_timestamp"] = licenseJson["verifyTimeStamp"]
        logger_obj.log(
            "[MfpAuthorizer]IsLicenseValid Result: " + json.dumps(result))
        return result

    def RemoveLicense(self):
        if os.path.isfile(self.__licenseFilePath):
            os.remove(self.__licenseFilePath)


class MfpInfoGetter(object):

    __headers = None
    __baseUrl = "http://embapp-local.toshibatec.co.jp:50187/v1.0"

    def __init__(self, headers):
        self.__headers = headers

    def __del__(self):
        pass

    def __get(self, url):
        try:
            logger_obj.log("get:" + url)
            resp = requests.get(self.__baseUrl + url, headers=self.__headers)
            logger_obj.log("resp:" + json.dumps(resp.json()))
            return resp.json()
        except Exception as err:
            logger_obj.log("exception:" + str(err))
            return None

    def GetMfpdeviceCapability(self):
        return self.__get("/mfpdevice/capability")

    def GetAppContextSelf(self):
        return self.__get("/app/context/self")


class TSEncrypter(object):

    # 矩阵列数
    __cols = 4
    # 加密密钥
    __key = ""
    # 加密密钥ASCII码数组
    __keyIntArray = []
    # 加密密钥长度
    __keyLength = 0
    # 非16进制字母
    __randoms = "ghijklmnopqrstuvwxyz"
    # HASH时用的映射表
    __hashChars = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    __hashCharsLength = 0
    # __randoms的长度
    __randomsLength = 0

    def __init__(self, key):
        self.__key = key
        # 获取密钥ASCII码数组
        self.__keyIntArray = [ord(c) for c in key]
        self.__keyLength = len(key)
        self.__randomsLength = len(self.__randoms)
        self.__hashCharsLength = len(self.__hashChars)

    def __del__(self):
        pass

    def __stringtomd5(self, originstr):
        """将string转化为MD5"""
        signaturemd5 = hashlib.md5()
        signaturemd5.update(originstr.encode("utf8"))
        return signaturemd5.hexdigest()

    def Hash(self, plain):
        # md5为32位16进制字符串
        md5 = self.__stringtomd5(plain+self.__key)
        # 映射成6位字符串，规则为6+5+5+5+5+6
        char1 = self.__hashChars[int("0x" + md5[0:6], 16) %
                                 self.__hashCharsLength]
        char2 = self.__hashChars[int("0x" + md5[6:11], 16) %
                                 self.__hashCharsLength]
        char3 = self.__hashChars[int(
            "0x" + md5[11:16], 16) % self.__hashCharsLength]
        char4 = self.__hashChars[int(
            "0x" + md5[16:21], 16) % self.__hashCharsLength]
        char5 = self.__hashChars[int(
            "0x" + md5[21:26], 16) % self.__hashCharsLength]
        char6 = self.__hashChars[int(
            "0x" + md5[26:32], 16) % self.__hashCharsLength]
        hashcode = char1+char2+char3+char4+char5+char6
        return hashcode.lower()

    def Encrypt(self, plain):
        plainLength = len(plain)
        # 明文ASCII码数组
        plainIntArray = [ord(c) for c in plain]
        # 矩阵行数
        rows = plainLength // self.__cols
        # 尾部剩余项，如：明文长度为5，列数为4，则最后一项不放入矩阵，lefts为1，
        lefts = plainLength % self.__cols
        # 构造明文ASCII码二维数组矩阵
        plainIntArray2 = [([0] * self.__cols) for i in range(rows)]
        for r in range(rows):
            for c in range(self.__cols):
                plainIntArray2[r][c] = plainIntArray[r*self.__cols + c]
        # 正向行位移
        plainIntArray2C = [([0] * self.__cols) for i in range(rows)]
        for r in range(rows):
            for c in range(self.__cols):
                plainIntArray2C[r][c] = plainIntArray2[(r+c) % rows][c]
        # 转回一维数组
        plainIntArrayC = sum(plainIntArray2C, [])
        # 尾部剩余项倒序拼在尾部
        for i in range(lefts):
            plainIntArrayC.append(plainIntArray[-1*(i+1)])
        # 和key做异或运算进行加密
        encryptedIntArray = [(plainIntArrayC[i] ^ self.__keyIntArray[i %
                                                                     self.__keyLength]) for i in range(plainLength)]
        # 10进制转16进制，并替换0x为非16进制字母，以便解密时进行分割
        encryptedInt16Array = [(hex(encryptedIntArray[i]).replace(
            '0x', self.__randoms[encryptedIntArray[i] % self.__randomsLength])) for i in range(plainLength)]
        # join，形成密文
        encrypted16 = "".join(encryptedInt16Array)
        return encrypted16

    def Decrypt(self, encrypted16):
        pattern = re.compile(r'[ghijklmnopqrstuvwxyz]')
        encrypted16re = re.sub(pattern, ',', encrypted16)[1:]
        encryptedIntArray = [int('0x'+n, 16)
                             for n in encrypted16re.split(',')]
        plainLength = len(encryptedIntArray)
        # 异或运算解密
        plainIntArrayC = [(encryptedIntArray[i] ^ self.__keyIntArray[i %
                                                                     self.__keyLength]) for i in range(plainLength)]
        rows = plainLength // self.__cols
        lefts = plainLength % self.__cols
        # 构造矩阵
        plainIntArray2C = [([0] * self.__cols) for i in range(rows)]
        for r in range(rows):
            for c in range(self.__cols):
                plainIntArray2C[r][c] = plainIntArrayC[r*self.__cols + c]
        # 正向行位移逆过程
        plainIntArray2 = [([0] * self.__cols) for i in range(rows)]
        for r in range(rows):
            for c in range(self.__cols):
                plainIntArray2[(r+c) % rows][c] = plainIntArray2C[r][c]
        # 尾部剩余项倒序拼在尾部
        plainIntArray = sum(plainIntArray2, [])
        for i in range(lefts):
            plainIntArray.append(plainIntArrayC[-1*(i+1)])
        plain = "".join([chr(n) for n in plainIntArray])
        return plain


@view_config(route_name='license_verify', xhr=True, renderer='jsonp', request_method='POST')
def LicenseVerify(request):
    result = None
    try:
        logger_obj.log("POST /app/license/verify")
        token = request.session["X-WebAPI-AccessToken"] if "X-WebAPI-AccessToken" in request.session else request.headers['X-WebAPI-AccessToken']
        headers = {"X-WebAPI-AccessToken": token}
        licenseCategory = request.json_body["license_category"]
        licenseCode = request.json_body["license_code"]
        logger_obj.log(licenseCategory)
        logger_obj.log(licenseCode)
        mfpAuthorizer = MfpAuthorizer(headers)
        if licenseCategory == 1:
            result = mfpAuthorizer.VerifyShortLicenseCode(licenseCode)
        elif licenseCategory == 2:
            result = mfpAuthorizer.VerifyLicenseCode(licenseCode)
    except Exception as err:
        logger_obj.log("exception: " + str(err), log_level='exception')
        result = {
            "is_valid": False,
            "err_msg": "未知错误！"
        }
    return result


@view_config(route_name='license_remove', xhr=True, renderer='jsonp', request_method='DELETE')
def LicenseRemove(request):
    result = {"status": 200}
    try:
        logger_obj.log("POST /app/license/remove")
        token = request.session["X-WebAPI-AccessToken"] if "X-WebAPI-AccessToken" in request.session else request.headers['X-WebAPI-AccessToken']
        headers = {"X-WebAPI-AccessToken": token}
        mfpAuthorizer = MfpAuthorizer(headers)
        mfpAuthorizer.RemoveLicense()
    except Exception as err:
        logger_obj.log("exception: " + str(err), log_level='exception')
    return result


@view_config(route_name='license_status', xhr=True, renderer='jsonp', request_method='GET')
def LicenseStatus(request):
    result = None
    try:
        logger_obj.log("GET /app/license/status")
        token = request.session["X-WebAPI-AccessToken"] if "X-WebAPI-AccessToken" in request.session else request.headers['X-WebAPI-AccessToken']
        headers = {"X-WebAPI-AccessToken": token}
        mfpAuthorizer = MfpAuthorizer(headers)
        result = mfpAuthorizer.IsLicenseValid()
    except Exception as err:
        logger_obj.log("exception: " + str(err), log_level='exception')
        result = {
            "is_valid": False,
            "err_msg": "未知错误！"
        }
    return result


@view_config(route_name='mfpdevice_capability', xhr=True, renderer='jsonp', request_method='GET')
def MfpdeviceCapability(request):
    result = {"status": 500}
    try:
        logger_obj.log("GET /mfpdevice/capability")
        token = request.session["X-WebAPI-AccessToken"] if "X-WebAPI-AccessToken" in request.session else request.headers['X-WebAPI-AccessToken']
        headers = {"X-WebAPI-AccessToken": token}
        getter = MfpInfoGetter(headers)
        result = getter.GetMfpdeviceCapability()
    except Exception as err:
        logger_obj.log("exception: " + str(err), log_level='exception')
    return result


@view_config(route_name='app_context', xhr=True, renderer='jsonp', request_method='GET')
def AppContext(request):
    result = {"status": 500}
    try:
        logger_obj.log("GET /app/context/self")
        token = request.session["X-WebAPI-AccessToken"] if "X-WebAPI-AccessToken" in request.session else request.headers['X-WebAPI-AccessToken']
        headers = {"X-WebAPI-AccessToken": token}
        getter = MfpInfoGetter(headers)
        result = getter.GetAppContextSelf()
    except Exception as err:
        logger_obj.log("exception: " + str(err), log_level='exception')
    return result


# 使用说明：该文件放在server目录
# 只需在pyramid路由表中增加以下路由信息即可
# config.add_route('license_verify', 'app/license/verify', xhr=True)
# config.add_route('license_remove', 'app/license/remove', xhr=True)
# config.add_route('license_status', 'app/license/status', xhr=True)
# config.add_route('mfpdevice_capability', 'mfpdevice/capability', xhr=True)
# config.add_route('app_context', 'app/context/self', xhr=True)
