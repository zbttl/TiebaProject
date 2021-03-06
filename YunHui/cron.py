from . import utils
from .models import User,Sign,Data,Robot,Tieba
import requests
import logging
import time

# 定时任务 设置在setting.py
# flag = 0  默认（未update,未sign）
# flag = 1  新用户update
# flag = 2  新用户sign

def do():
    # 云回帖
    u = User.objects.all()
    data = Data.objects.get(pk=1)
    try:
        content = requests.get('https://api.gushi.ci/rensheng.txt').text
        for i in u:
            ltime = time.localtime()
            t = ltime.tm_hour*60 + ltime.tm_min
            for j in i.tieba_set.all():
                if t % j.time == 0:
                    if j.stop:
                        j.stop_times = j.stop_times + 1
                        j.save()
                        continue
                    else:
                        if j.isLou:
                            # 客户端楼中楼
                            try:
                                res = utils.client_LZL(i.bduss,j.name,j.fid,content,j.qid,j.tid)
                                if res['error_code'] == '0':
                                    j.success = j.success + 1
                                    data.success += 1
                                else:
                                    j.fail = j.fail + 1
                            except Exception as e:
                                logging.info(e)
                            finally:
                                j.save()
                        else:
                            if i.i_type:
                                # 客户端回帖模式
                                try:
                                    ser = utils.client_Post(i.bduss, j.name, j.tid, j.fid, content)
                                    if ser['error_code'] == '0':
                                        j.success = j.success + 1
                                        data.success += 1
                                    else:
                                        j.fail = j.fail + 1
                                except Exception as e:
                                    logging.info(e)
                                finally:
                                    j.save()
                            else:
                                # 网页端回帖模式
                                try:
                                    ser = utils.Post(i.bduss, content, j.tid, j.fid, j.name)
                                    if ser['err_code'] == 0:
                                        j.success = j.success + 1
                                        data.success += 1
                                    else:
                                        j.fail = j.fail + 1
                                except Exception as e:
                                    logging.info(e)
                                finally:
                                    j.save()
    except Exception as e:
        print(e)
    finally:
        data.save()



def update():
    #更新用户关注的贴吧列表
    u = User.objects.all()
    for i in u:
        print(i.username + '开始更新...')
        datalist = []
        try:
            data = utils.get_favorite(i.bduss)
            for j in data['forum_list']['non-gconforum']:
                if type(j) == list:
                    for t in j:
                        try:
                            Sign.objects.get(fid=t['id'], user=i)
                        except Exception:
                            datalist.append(Sign(name=t['name'], fid=t['id'], level_id=t['level_id'], cur_score=t['cur_score'],
                                     user_id=i.pk))
                else:
                    try:
                        Sign.objects.get(fid=j['id'], user=i)
                    except Exception:
                        datalist.append(Sign(name=j['name'], fid=j['id'], level_id=j['level_id'], cur_score=j['cur_score'],
                                             user_id=i.pk))
            for k in data['forum_list']['gconforum']:
                if type(k) == list:
                    for s in k:
                        try:
                            Sign.objects.get(fid=s['id'], user=i)
                        except Exception:
                            datalist.append(Sign(name=s['name'], fid=s['id'], level_id=s['level_id'], cur_score=s['cur_score'],
                                     user_id=i.pk))
                else:
                    try:
                        Sign.objects.get(fid=k['id'], user=i)
                    except Exception:
                        datalist.append(Sign(name=k['name'], fid=k['id'], level_id=k['level_id'], cur_score=k['cur_score'],
                                             user_id=i.pk))
        except Exception as e:
            print(e)
        finally:
            Sign.objects.bulk_create(datalist)

def sign():
    # 每日签到
    data = {
        '0': '签到成功',
        '160002': '已经签过到了',
        '340008': '在黑名单中',
        '340006': '贴吧目录出问题啦',
        '300003': '加载数据失败',
    }
    u = User.objects.all()
    for i in u:
        try:
            tbs = utils.get_tbs(i.bduss)
            for j in i.sign_set.all():
                if j.is_sign is False:
                    res = utils.client_Sign(i.bduss, j.name, j.fid, tbs)
                    if res['error_code'] in data:
                        j.is_sign = True
                        j.save()
                    elif res['error_code'] == '340011':
                        time.sleep(0.1)
                    else:
                        print('用户：' + i.username + ' 贴吧：' + j.name + ' ')
                        print(res)
        except Exception as e:
            print(e)

def reset():
    # 每日凌晨将签到状态复位
    Sign.objects.all().update(is_sign=False)


def new_update():
    # 轮循数据库查找新用户更新贴吧
    u = User.objects.filter(flag=0)
    for i in u:
        print(i.username + '开始更新...')
        datalist = []
        try:
            data = utils.get_favorite(i.bduss)
            for j in data['forum_list']['non-gconforum']:
                if type(j) == list:
                    for t in j:
                        try:
                            Sign.objects.get(fid=t['id'], user=i)
                        except Exception:
                            datalist.append(Sign(name=t['name'], fid=t['id'], level_id=t['level_id'], cur_score=t['cur_score'],
                                     user_id=i.pk))
                else:
                    try:
                        Sign.objects.get(fid=j['id'], user=i)
                    except Exception:
                        datalist.append(Sign(name=j['name'], fid=j['id'], level_id=j['level_id'], cur_score=j['cur_score'],
                                             user_id=i.pk))
            for k in data['forum_list']['gconforum']:
                if type(k) == list:
                    for s in k:
                        try:
                            Sign.objects.get(fid=s['id'], user=i)
                        except Exception:
                            datalist.append(Sign(name=s['name'], fid=s['id'], level_id=s['level_id'], cur_score=s['cur_score'],
                                     user_id=i.pk))
                else:
                    try:
                        Sign.objects.get(fid=k['id'], user=i)
                    except Exception:
                        datalist.append(Sign(name=k['name'], fid=k['id'], level_id=k['level_id'], cur_score=k['cur_score'],
                                             user_id=i.pk))
        except Exception as e:
            print(e)
        finally:
            Sign.objects.bulk_create(datalist)
            i.flag = 1
            i.save()



def new_sign():
    # 签到
    data = {
        '0':'签到成功',
        '160002':'已经签过到了',
        '340008':'在黑名单中',
        '340006':'贴吧目录出问题啦',
        '300003':'加载数据失败',
    }
    u = User.objects.filter(flag=1)
    for i in u:
        try:
            tbs = utils.get_tbs(i.bduss)
            for j in i.sign_set.all():
                if j.is_sign == False:
                    res = utils.client_Sign(i.bduss, j.name, j.fid, tbs)
                    if res['error_code'] in data:
                        j.is_sign = True
                        j.save()
                    elif res['error_code'] == '340011':
                        time.sleep(0.1)
                    else:
                        print('用户：'+i.username+' 贴吧：'+j.name+' ')
                        print(res)
            i.flag = 2
            i.save()
        except Exception as e:
            print(e)


def robot():
    u = User.objects.get(username='旬阳城管')
    res = utils.get_at(u.bduss)
    at_num = res['message']['atme']
    at_list = res['at_list']
    for i in range(int(at_num)):
        post_id = at_list[i]['post_id']
        title = at_list[i]['title']
        content = at_list[i]['content'].strip('@旬阳城管 ').split(',')
        fname = at_list[i]['fname']
        is_fans = at_list[i]['replyer']['is_fans']
        thread_id = at_list[i]['thread_id']
        name = at_list[i]['replyer']['name']
        time = at_list[i]['time']
        fid = utils.get_fid(fname)
        if is_fans != '1':
            reply_content = '只有我的粉丝才可以at我 -_- #(乖)'
            utils.client_LZL(u.bduss, fname, fid, reply_content, post_id, thread_id)
        else:
            try:
                user = User.objects.get(username=name)
                if content[0] == 'reply':
                    Tieba.objects.create(name=fname, fid=fid, tid=thread_id, isLou=False, time=content[1],
                                         user_id=user.pk)
                    reply_content = fname + '吧' + content[1] + "分钟/贴添加完毕"
                elif content[0] == 'info':
                    reply_content = '已签到：' + str(user.已签到()) + '未签到' + str(user.未签到()) + '已云回' + str(
                        user.tieba_set.all().count())
                else:
                    reply_content = '命令错误 -_- #(乖)'
            except Exception:
                try:
                    Robot.objects.get(thread_id=thread_id, post_id=post_id)
                except Exception:
                    if Robot.objects.filter(username=name).count() > 5:
                        reply_content = '今天不陪你玩儿了 -_- #(乖)'
                    else:
                        reply_content = '#(滑稽)'
                    Robot.objects.create(thread_id=thread_id,post_id=post_id,title=title,username=name,is_fans=is_fans,fname=fname,content=content,time=time)
            finally:
                utils.client_LZL(u.bduss, fname, fid, reply_content, post_id, thread_id)








