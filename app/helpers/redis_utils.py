from app.extensions import redis_store
import json
from time import time
from app.settings import Operations
import datetime


def email_task(user, cate):
    assert cate in [
        Operations.CHANGE_EMAIL,
        Operations.CONFIRM,
        Operations.RESET_PASSWORD,
    ]
    return {"to": user.email, "cate": cate, "username": user.username, "time": time()}


def download_task(subjects_id, cate, priority=0):
    """@param cate: movie or celebrity,image
    @param subjects_id: 需要爬去的唯一标示
    @param priority: 0>low 1>middle 2>high...
    """
    assert cate in ["movie:showing", "movie:coming", "movie", "celebrity", "image"]
    return {"subjects_id": subjects_id, "cate": cate, "priority": priority}


def import_info_from_douban_task(user, douban_id):
    return {"user": user.username, "douban_id": douban_id}


def add_download_task_to_redis(task):
    """以 ``zset`` 存储方便优先级高的在前面
    """
    redis_store.zadd("task:" + task["cate"], {task["subjects_id"]: task["priority"]})


def add_email_task_to_redis(task):
    """@param task : ``email_task`` instance
    return::``None``
    """
    redis_store.rpush("task:email", json.dumps(task))


def add_import_info_from_douban_task_to_redis(task):
    """将用户从豆瓣导入到本网站的任务写入redis
    """
    redis_store.sadd("task:douban", json.dumps(task))


def add_movie_to_rank_redis(movie, dec=False):
    """@param rating: Rating instance
    @param dec: score 自减1
    在用户评分时,添加所评价电影到redis zset中 ,并设置过期时间
    """
    key = "rating:" + datetime.date.today().strftime("%y%m%d")
    # 设置过期时间为三十天
    if dec:
        redis_store.zincrby(key, -1, str(movie.id))
    else:
        redis_store.zincrby(key, 1, str(movie.id))
    redis_store.expire(key, time=60 * 60 * 24 * 31)


def rank_redis_zset_paginate(
    keys, time_range="week", page=1, per_page=20, desc=True, withscores=False
):
    """@param keys :redis``key``list
    @param page :需要取出第几页,从1开始计数
    @param per_page :每页返回的数量
    @param desc :``True`` 降序排序, ``False`` 升序排序
    @param with_score: ``True`` 带分数返回,``False`` 不带分数返回
    """
    today_rank_key = (
        "rating:rank:" + time_range + ":" + datetime.date.today().strftime("%y%m%d")
    )
    if not redis_store.exists(today_rank_key):
        redis_store.zunionstore(today_rank_key, keys=keys)
        redis_store.expire(today_rank_key, time=60 * 5)  # 排行榜临时键过期时间为五分钟

    start = per_page * (page - 1)
    end = start + per_page - 1
    total_count = redis_store.zcard(today_rank_key)

    return (
        [
            value.decode()
            for value in redis_store.zrange(
                today_rank_key, start=start, end=end, desc=desc, withscores=withscores
            )
            if redis_store.zrange(
                today_rank_key, start=start, end=end, desc=desc, withscores=withscores
            )
        ],
        total_count,
    )


def send_email_limit(user, cate):
    """
    @param user : Object of `User`
    @param cate : Operations
    发送邮件前检测用户是否发送频繁
    @return :-2  发送成功 ,>0 限制 多少秒后才可发送 , 默认限制5分钟发送一次
    """
    if cate == Operations.CONFIRM:
        key = "confirmEmail:limit:" + user.email
    elif cate == Operations.RESET_PASSWORD:
        key = "resetPasswordEmail:limit:" + user.email
    elif cate == Operations.CHANGE_EMAIL:
        key = "changeEmail:limit:" + user.email

    ttl_time = redis_store.ttl(key)
    if ttl_time > 0:
        return ttl_time
    task = email_task(user, cate=cate)
    add_email_task_to_redis(task)
    redis_store.set(key, 1, 5 * 60)  # 限制300's 发送一次

    return -2


def had_downloaded(id, cate):
    """将已经下载过的资料存储到redis中, 避免重复下载
    @param id:下载过的资源id
    @param cate:下载过的资源类别
    """
    assert cate in ["movie", "celebrity", "image"]
    redis_store.sadd("downloaded:" + cate, str(id))
