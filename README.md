# keystone
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
            "uuid": "0de251e00fc511e99f9cfa163ef8d597",
            "token": "15d64236a1f43934abad68bbc2d69ddd",
            "name": "全局管理员",
            "expire_date": 1549978471
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

#### 修改用户

#### 删除用户
        




