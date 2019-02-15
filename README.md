# keystone

* [API 说明](#api-说明)
     * [基础访问](#基础访问)
        * [登录](#登录)
        * [登出](#登出)
        * [刷新 Token](#刷新-token)
     * [域管理](#域管理)
        * [查询域](#查询域)
        * [添加域](#添加域)
        * [修改域](#修改域)
        * [删除域](#删除域)
     * [项目管理](#项目管理)
        * [查询项目](#查询项目)
        * [添加项目](#添加项目)
        * [修改项目](#修改项目)
        * [删除项目](#删除项目)
     * [用户管理](#用户管理)
        * [查询用户](#查询用户)
        * [添加用户](#添加用户)
        * [修改用户](#修改用户)
        * [删除用户](#删除用户)
        * [查询用户的所属组关联](#查询用户的所属组关联)
        * [新增用户的所属组关联](#新增用户的所属组关联)
        * [设置用户的所属组关联](#设置用户的所属组关联)
        * [删除用户的所属组关联](#删除用户的所属组关联)
        * [查询用户的引用角色关联](#查询用户的引用角色关联)
        * [添加用户的引用角色关联](#添加用户的引用角色关联)
        * [设置用户的引用角色关联](#设置用户的引用角色关联)
        * [删除用户的引用角色关联](#删除用户的引用角色关联)
     * [用户组管理](#用户组管理)
        * [查询用户组](#查询用户组)
        * [添加用户组](#添加用户组)
        * [修改用户组](#修改用户组)
        * [删除用户组](#删除用户组)
        * [查询组的所含用户关联](#查询组的所含用户关联)
        * [添加组的所含用户关联](#添加组的所含用户关联)
        * [设置组的所含用户关联](#设置组的所含用户关联)
        * [删除组的所含用户关联](#删除组的所含用户关联)
     * [角色管理](#角色管理)
        * [查询角色](#查询角色)
        * [添加角色](#添加角色)
        * [修改角色](#修改角色)
        * [删除角色](#删除角色)
     * [策略管理](#策略管理)
        * [查询策略](#查询策略)
        * [添加策略](#添加策略)
        * [修改策略](#修改策略)
        * [删除策略](#删除策略)
     * [服务管理](#服务管理)
        * [查询服务](#查询服务)
        * [添加服务](#添加服务)
        * [修改服务](#修改服务)
        * [删除服务](#删除服务)
     * [端点管理](#端点管理)
        * [查询端点](#查询端点)
        * [添加端点](#添加端点)
        * [修改端点](#修改端点)
        * [删除端点](#删除端点)

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

[返回目录](#keystone)
    
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
    
[返回目录](#keystone)

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
    
[返回目录](#keystone)

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

[返回目录](#keystone)

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
    
[返回目录](#keystone)
    
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
    
[返回目录](#keystone)

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
    
[返回目录](#keystone)

### 项目管理
#### 查询项目
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/partition/projects/|否|是|
    
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
                    "name": "运维中心",
                    "domain": "0bfd60f8154d11e981cdfa163ef8d597",
                    "description": "啥事都得干",
                    "enable": true,
                    "comment": null,
                    "uuid": "ce9acf96156c11e9bf4cfa163ef8d597",
                    "created_by": "0de251e00fc511e99f9cfa163ef8d597",
                    "created_time": "2019-01-11 14:47:47",
                    "updated_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                    "updated_time": "2019-01-28 14:21:51"
                }
            ]
        },
        "message": null
    }
    ```

[返回目录](#keystone)
    
#### 添加项目
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/partition/projects/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |name|str|是|项目名|
    |description|str|是|描述|
    |domain|str|否|只有云管理用户有此参数权限|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)

#### 修改项目
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/partition/projects/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|项目 uuid|
    |name|str|否|项目名|
    |description|str|否|描述|
    |domain|str|否|只有云管理用户有此参数权限|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)
    
#### 删除项目
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/partition/projects/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|项目 uuid|

[返回目录](#keystone)
    
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

[返回目录](#keystone)
    
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

[返回目录](#keystone)

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

[返回目录](#keystone)

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

[返回目录](#keystone)
    
#### 查询用户的所属组关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/identity/users/<font color=red>user_uuid</font>/groups/|否|是|
    
- 响应
    ``` json
    {
        "code": 200,
        "data":{
            "total": 1,
            "data": [
                {
                    "name": "运维开发",
                    "domain": "0bfd60f8154d11e981cdfa163ef8d597",
                    "enable": true,
                    "comment": "吹牛2小时，编程5分钟",
                    "uuid": "8957e5a0158911e9b68ffa163ef8d597",
                    "created_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                    "created_time": "2019-01-11 18:13:27",
                    "updated_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                    "updated_time": "2019-01-11 18:22:19",
                    "users_count": 1,
                    "roles_count": 0
                }
            ]
        },
        "message": null
    }
    ```

[返回目录](#keystone)
    
#### 新增用户的所属组关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/identity/users/<font color=red>user_uuid</font>/groups/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户组 uuid 的列表|

- 响应

    和查询用户的所属组响应一致
 
[返回目录](#keystone)
   
#### 设置用户的所属组关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/identity/users/<font color=red>user_uuid</font>/groups/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户组 uuid 的列表|

- 响应

    和查询用户的所属组响应一致

[返回目录](#keystone)

#### 删除用户的所属组关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/identity/users/<font color=red>user_uuid</font>/groups/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户组 uuid 的列表|

- 响应

    和查询用户的所属组响应一致

[返回目录](#keystone)
    
#### 查询用户的引用角色关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/identity/users/<font color=red>user_uuid</font>/roles/|否|是|
    
- 响应
    ``` json
    {
        "code": 200,
        "data":[
            {
                "name": "DoaminAdminstrator",
                "domain": "0bfd60f8154d11e981cdfa163ef8d597",
                "builtin": false,
                "enable": true,
                "comment": null,
                "uuid": "fa11c96c22c911e9b881fa163ef8d597",
                "created_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                "created_time": "2019-01-28 14:57:29",
                "updated_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                "updated_time": "2019-01-28 14:58:54"
            }
        ],
        "message": null
    }
    ```

[返回目录](#keystone)

#### 添加用户的引用角色关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/identity/users/<font color=red>user_uuid</font>/roles/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户组 uuid 的列表|

- 响应

    和查询用户的所属组响应一致

[返回目录](#keystone)
    
#### 设置用户的引用角色关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/identity/users/<font color=red>user_uuid</font>/roles/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户组 uuid 的列表|

- 响应

    和查询用户的所属组响应一致

[返回目录](#keystone)
    
#### 删除用户的引用角色关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/identity/users/<font color=red>user_uuid</font>/roles/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户组 uuid 的列表|

- 响应

    和查询用户的所属组响应一致

[返回目录](#keystone)

### 用户组管理
#### 查询用户组
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/identity/groups/|否|是|
        
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
                "name": "运维开发",
                "domain": "0bfd60f8154d11e981cdfa163ef8d597",
                "enable": true,
                "comment": "吹牛2小时，编程5分钟",
                "uuid": "8957e5a0158911e9b68ffa163ef8d597",
                "created_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                "created_time": "2019-01-11 18:13:27",
                "updated_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                "updated_time": "2019-01-11 18:22:19",
                "users_count": 0,
                "roles_count": 0
            }
        ]
    },
    "message": null
    }
    ```
    
    查询单个组响应
    ``` json
     {
        "code": 200,
        "data": {
            "name": "运维开发",
            "domain": "0bfd60f8154d11e981cdfa163ef8d597",
            ...
        }

        "message": null
    }
    ```

[返回目录](#keystone)
    
#### 添加用户组
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/identity/groups/|否|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |name|str|是|组名|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|
    |domain|str|否|只有云管理用户有此参数权限|
    
- 响应
    
    和查询单个组响应一致

[返回目录](#keystone)
    
#### 修改用户组
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/identity/groups/|否|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|组 uuid|
    |name|str|否|组名|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|
    |domain|str|否|只有云管理用户有此参数权限|
    
- 响应
    
    和查询单个组响应一致

[返回目录](#keystone)
    
#### 删除用户组
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/identity/groups/|否|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|组 uuid|

- 响应
    ``` json
     {
            "code": 200,
            "data": "success to delete group 运维开发"
            "message": null
    }
    ```

[返回目录](#keystone)
    
#### 查询组的所含用户关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/identity/groups/<font color=red>group_uuid</font>/users/|否|是|
    
- 响应
    ``` json
        {
        "code": 200,
        "data":{
            "total": 2,
            "data": [
                {
                    "email": "zhanghuaming@ijunhai.com",
                    "phone": "15622330312",
                    "username": "zhanghuaming",
                    ...
                },
                {
                    "email": "yunwei@ijunhai.com",
                    "phone": "15622330312",
                    "username": "admin",
                    ...
                }
            ]
        },
        "message": null
    }
    ```

[返回目录](#keystone)
    
#### 添加组的所含用户关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/identity/groups/<font color=red>group_uuid</font>/users/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户 uuid 的列表|

- 响应

    和查询组的所含用户关联响应一致

[返回目录](#keystone)

#### 设置组的所含用户关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/identity/groups/<font color=red>group_uuid</font>/users/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户 uuid 的列表|

- 响应

    和查询组的所含用户关联响应一致

[返回目录](#keystone)

#### 删除组的所含用户关联
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/identity/groups/<font color=red>group_uuid</font>/users/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid_list|list|是|包含用户 uuid 的列表|

- 响应

    和查询组的所含用户关联响应一致

[返回目录](#keystone)
    
### 角色管理
#### 查询角色
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/assignment/roles/|否|是|
        
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
            "total": 4,
            "data":[
                {
                    "name": "Administrator",
                    "domain": "ccb09c100f4011e99a87fa163ef8d597",
                    "builtin": true,
                    "enable": true,
                    "comment": null,
                    "uuid": "ea9138d62dc511e9a5abfa163ef8d597",
                    "created_by": "0de251e00fc511e99f9cfa163ef8d597",
                    "created_time": "2019-02-11 14:26:07",
                    "updated_by": null,
                    "updated_time": "2019-02-11 14:26:07"
                }
            ]
        },
        "message": null
    }
    ```

[返回目录](#keystone)

#### 添加角色
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/assignment/roles/|是|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |name|str|是|角色名|
    |domain|str|否|只有云管理用户有此参数权限|
    |builtin|bool|否|是否为内置，只有云管理用户有此参数权限|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)
    
#### 修改角色
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/assignment/roles/|是|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|角色 uuid|
    |name|str|否|角色名|
    |domain|str|否|只有云管理用户有此参数权限|
    |builtin|bool|否|是否为系统内置，只有云管理用户有此参数权限|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)
    
#### 删除角色
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DETELE|/assignment/roles/|是|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|角色 uuid|

[返回目录](#keystone)
    
### 策略管理
#### 查询策略
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/assignment/policies/|否|是|
        
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|否|策略 uuid|
    |page|int|否|目标页|
    |pagesize|int|否|页大小|
    
- 响应
    ``` json
    {
        "code": 200,
        "data":{
            "total": 3,
            "data":[
                {
                    "name": "ManageUser",
                    "domain": "ccb09c100f4011e99a87fa163ef8d597",
                    "service": "3ac33b5a250711e98c76fa163ef8d597",
                    "view": "identity.views.user.UsersView",
                    "method": "*",
                    "request_params":[
                        {"page": "1", "pagesize": "1"}
                    ],
                    "view_params":[
                        {}
                    ],
                    "effect": "allow",
                    "builtin": true,
                    "enable": true,
                    "comment": null,
                    "uuid": "0bb16dd823b211e9b639fa163ef8d597",
                    "created_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                    "created_time": "2019-01-29 18:38:41",
                    "updated_by": "0de251e00fc511e99f9cfa163ef8d597",
                    "updated_time": "2019-01-31 11:24:09"
                }
            ]
        },
        "message": null
    }
    ```

[返回目录](#keystone)

#### 添加策略
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/assignment/policies/|是|是|

    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |name|str|是|策略名|
    |service|str|是|策略 uuid|
    |view|str|是|视图类|
    |method|str|是|方法|
    |request_params|list|是|包含请求参数字典的列表|
    |view_params|list|是|包含视图参数字典的列表|
    |effect|str|是|效力|
    |domain|str|否|只有云管理用户有此参数权限|
    |builtin|bool|否|是否为内置，只有云管理用户有此参数权限|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)

#### 修改策略
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/assignment/policies/|是|是|

    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|策略 uuid|
    |name|str|否|策略名|
    |service|str|否|服务 uuid|
    |view|str|否|视图类|
    |method|str|否|方法|
    |request_params|list|否|包含请求参数字典的列表|
    |view_params|list|否|包含视图参数字典的列表|
    |effect|str|否|效力|
    |domain|str|否|只有云管理用户有此参数权限|
    |builtin|bool|否|是否为内置，只有云管理用户有此参数权限|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)

#### 删除策略
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/assignment/policies/|是|是|

    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|策略 uuid|

[返回目录](#keystone)
    
### 服务管理
#### 查询服务
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/catalog/services/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|否|服务 uuid|
    |page|int|否|目标页|
    |pagesize|int|否|页大小|
    
- 响应
    ``` json
    {
        "code": 200,
        "data":{
            "total": 3,
            "data":[
                {
                    "name": "cmdb",
                    "function": "提供资产管理",
                    "enable": true,
                    "comment": null,
                    "uuid": "0b4d4440197911e99b13fa163ef8d597",
                    "created_by": "9c7e8ae8157b11e99fb9fa163ef8d597",
                    "created_time": "2019-01-16 18:25:28",
                    "updated_by": "0de251e00fc511e99f9cfa163ef8d597",
                    "updated_time": "2019-02-11 19:05:26",
                    "endpoint_count": 0
                }
            ]
        },
        "message": null
    }
    ```

[返回目录](#keystone)
    
#### 添加服务
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/catalog/services/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |name|str|是|服务名|
    |function|str|是|功能|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)
    
#### 修改服务
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/catalog/services/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|服务 uuid|
    |name|str|否|服务名|
    |function|str|否|功能|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)
    
#### 删除服务
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/catalog/services/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|服务 uuid|

[返回目录](#keystone)

### 端点管理
#### 查询端点
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |GET|/catalog/endpoints/|否|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|否|端点 uuid|
    |page|int|否|目标页|
    |pagesize|int|否|页大小|

[返回目录](#keystone)
    
#### 添加端点
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |POST|/catalog/endpoints/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |service|str|是|服务 uuid|
    |ip|str|是|ip 地址|
    |port|str|是|端口|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)
    
#### 修改端点
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |PUT|/catalog/endpoints/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|端点 uuid|
    |service|str|否|服务 uuid|
    |ip|str|否|ip 地址|
    |port|str|否|端口|
    |comment|str|否|备注|
    |enable|bool|否|是否启用|

[返回目录](#keystone)
    
#### 删除端点
- 请求

    |方法|路由|必须参数|必须凭证|
    | --- | --- | --- | --- |
    |DELETE|/catalog/endpoints/|是|是|
    
    |参数名|类型|是否必须|说明|
    | --- | --- | --- | --- |
    |uuid|str|是|端点 uuid|

[返回目录](#keystone)

    









    





    
    

    




        




