# keystone

[TOC]

## API 说明
### 基础访问
#### 登录
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- | 
    |POST|/identity/login/|是|否|

    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |type|str|是|登录类型：username、phone、email|
    |password|str|是|密码|
    |domain|str|否|域名，当 type 为 username 时必须|
    |username|str|否|用户名，当 type 为 username 时必须|
    |phone|str|否|手机，当 type 为 phone 时必须|
    |email|str|否|邮箱，当 type 为 email 时必须|

- 响应

    |参数名|类型|说明|
    | --- | --- | --- |
    |uuid|str|用户 uuid|
    |token|str|用户 token，需要存入 HEADER 作为凭证|
    |name|str|用户昵称|
    |expire_date|int|token 过期时间戳

    ``` json
    {
        "code": 200,
        "data": {
            "access_token": "f7ba9afdabd83e1fbd23bc582f5276a4",
            "access_expire_date": 1550047811,
            "refresh_token": "f736ec5b6cfc3461b3827747285dc561",
            "refresh_expire_date": 1550055011,
            "uuid": "9c7e8ae8157b11e99fb9fa163ef8d597",
            "domain": "0bfd60f8154d11e981cdfa163ef8d597",
            "name": "xiao帅哥"
        },
        "message": null
    }
    ```
    
#### 登出
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/identity/logout/|否|是|
    
- 响应
    ``` json
    {
        "code": 200,
        "data": "user 全局管理员 succeed to logout",
        "message": null
    }
    ```

#### 刷新 Token
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/identity/refresh/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |refresh_token|str|是|刷新token|
    
    
- 响应
    ``` json
    {
        "code": 200,
        "data": {
            "access_expire_date": 1550048272,
            "refresh_expire_date": 1550055472
        },
        "message": null
    }
    ```

### 用户管理
#### 查询用户
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/identity/users/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|否|用户 uuid|
    |page|int|否|目标页|
    |pagesize|int|否|页大小|
    
- 响应

    ``` json
    {
        "code": 200,
        "data":{
            "total": 2,
            "data":[
                {
                    "email": "zhanghuaming@ijunhai.com",
                    "phone": "15622330312",
                    "username": "zhanghuaming",
                    "domain": "0bfd60f8154d11e981cdfa163ef8d597",
                    "name": "xiao帅哥",
                    "is_main": true,
                    "enable": true,
                    "qq": null,
                    "comment": null,
                    "uuid": "9c7e8ae8157b11e99fb9fa163ef8d597",
                    "created_by": "0de251e00fc511e99f9cfa163ef8d597",
                    "created_time": "2019-01-11 16:33:46",
                    "updated_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                    "updated_time": "2019-01-22 18:36:14",
                    "deleted_by": null,
                    "deleted_time": null,
                    "behavior":{
                        "last_time": "2019-02-12 12:02:16",
                        "last_ip": "125.88.171.112",
                        "last_location": "亚洲 中国 广东 东莞市"
                    }, 
                    "groups_count": 0,
                    "roles_count": 1
                }
            ]
        },
        "message": null
    }
    ```
        
    查询单个用户响应
    ``` json
    {
        "code": 200,
        "data":{
            "email": "zhanghuaming@ijunhai.com",
            "phone": "15622330312",
            ...
        },
        "message": null
    }
    ```
    
#### 添加用户
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/identity/users/|否|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |username|str|是|用户名|
    |password|str|是|密码|
    |name|str|是|昵称|
    |email|str|是|邮箱|
    |phone|str|是|手机|
    |domain|str|否|只有云管理用户有此参数权限|
    |is_main|bool|否|只有云管理用户有此参数权限|
    |qq|str|否|QQ|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

- 响应

   和查询单个用户响应一致

#### 修改用户
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/identity/users/|否|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|用户 uuid|
    |username|str|是|用户名|
    |name|str|是|昵称|
    |email|str|是|邮箱|
    |phone|str|是|手机|
    |domain|str|否|只有云管理用户有此参数权限|
    |is_main|bool|否|只有云管理用户有此参数权限|
    |qq|str|否|QQ|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|
    
- 响应

    和查询单个用户响应一致

#### 删除用户
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/identity/users/|否|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|用户 uuid|
    
- 响应
    ``` json
     {
            "code": 200,
            "data": "success to delete user xiao帅哥"
            "message": null
    }
    ```

### 域管理
#### 查询域
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/partition/domains/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|否|域 uuid|
    |page|int|否|目标页|
    |pagesize|int|否|页大小|
    
- 响应

    ``` json
    {
        "code": 200,
        "data":{
            "total": 2,
            "data":[
                {
                    "name": "junhaiyouxi",
                    "company": "君海游戏",
                    "is_main": false,
                    "enable": true,
                    "comment": "用于管理君海游戏的资源",
                    "uuid": "0bfd60f8154d11e981cdfa163ef8d597",
                    "created_by": "0de251e00fc511e99f9cfa163ef8d597",
                    "created_time": "2019-01-11 11:00:26",
                    "updated_by": "0de251e00fc511e99f9cfa163ef8d597",
                    "updated_time": "2019-01-11 11:07:59",
                    "project_count": 2,
                    "user_count": 2,
                    "group_count": 2,
                    "custom_role_count": 3,
                    "custom_policy_count": 0
                }
            ]
        },
        "message": null
    }
```
查询单个域响应
    ``` json
    {
        "code": 200,
        "data":{
            "name": "junhaiyouxi",
            "company": "君海游戏",
            "is_main": false,
            "enable": true,
            "comment": "用于管理君海游戏的资源",
            "uuid": "0bfd60f8154d11e981cdfa163ef8d597",
            "created_by": "0de251e00fc511e99f9cfa163ef8d597",
            "created_time": "2019-01-11 11:00:26",
            "updated_by": "0de251e00fc511e99f9cfa163ef8d597",
            "updated_time": "2019-01-11 11:07:59",
            "project_count": 2,
            "user_count": 2,
            "group_count": 2,
            "custom_role_count": 3,
            "custom_policy_count": 0
        },
        "message": null
    }
```

#### 添加域
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/partition/domains/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |name|str|是|域名|
    |company|str|是|公司信息|
    |enable|bool|否|是否启用|
    |comment|bool|否|备注|
    
- 响应

    和查询单个域响应一致
    
#### 修改域
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/partition/domains/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|域 uuid|
    |name|str|是|域名|
    |company|str|是|公司信息|
    |enable|bool|否|是否启用|
    |comment|bool|否|备注|
    
- 响应

    和查询单个域响应一致
    
#### 删除域
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/partition/domains/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|域 uuid|

- 响应
    ``` json
     {
            "code": 200,
            "data": "success to delete domain junhaiyouxi"
            "message": null
    }
    ```


        




