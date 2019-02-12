# keystone
## API 说明
### 登录
- 请求

    |方法|路由|参数|
| --- | --- | --- | 
|POST|/identity/login/|有|

    |参数名|类型|是否必须|说明|
| --- | --- | --- | --- |
|type|str|是|登录类型：username、phone、email|
|password|str|是|密码|
|domain|str|否|域名，当 type 为 username 时必须|
|username|str|否|用户名，当 type 为 username 时必须|
|phone|str|否|手机，当 type 为 phone 时必须|
|email|str|否|邮箱，当 type 为 email 时必须|

- 响应数据

    |参数名|类型|说明|
| --- | --- | --- |
|uuid|str|用户 uuid，需要存入 COOKIE|
|token|str|用户 token，需要存入 COOKIE|
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

### 用户管理




