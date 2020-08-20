from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from urllib import parse

import requests
from bs4 import BeautifulSoup
import json
import time
import os
import random
import sys
requests.packages.urllib3.disable_warnings()#去除SSL认证的警告

PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAxbzZk3gEsbSe7A95iCIk
59Kvhs1fHKE6zRUfOUyTaKd6Rzgh9TB/jAK2ZN7rHzZExMM9kw6lVwmlV0VabSmO
YL9OOHDCiEjOlsfinlZpMZ4VHg8gkFoOeO4GvaBs7+YjG51Am6DKuJWMG9l1pAge
96Uhx8xWuDQweIkjWFADcGLpDJJtjTcrh4fy8toE0/0zJMmg8S4RM/ub0q59+VhM
zBYAfPmCr6YnEZf0QervDcjItr5pTNlkLK9E09HdKI4ynHy7D9lgLTeVmrITdq++
mCbgsF/z5Rgzpa/tCgIQTFD+EPPB4oXlaOg6yFceu0XUQEaU0DvAlJ7Zn+VwPkkq
JEoGudklNePHcK+eLRLHcjd9MPgU6NP31dEi/QSCA7lbcU91F3gyoBpSsp5m7bf5
//OBadjWJDvl2KML7NMQZUr7YXqUQW9AvoNFrH4edn8d5jY5WAxWsCPQlOqNdybM
vKF2jhjIE1fTWOzK+AvvFyNhxer5bWGU4S5LTr7QNXnvbngXCdkQfrcSn/ydQXP0
vXfjf3NhpluFXqWe5qUFKXvjY6+PdrE/lvTmX4DdvUIu9NDa2JU9mhwAPPR1yjjp
4IhgYOTQL69ZQcvy0Ssa6S25Xi3xx2XXbdx8svYcQfHDBF1daK9vca+YRX/DzXxl
1S4uGt+FUWSwuFdZ122ZCZ0CAwEAAQ==
-----END PUBLIC KEY-----
'''


#加密密码
def encrypt_passwd(passwd):
    cipher = PKCS1_v1_5.new(RSA.importKey(PUBLIC_KEY))
    cipher_text = base64.b64encode(cipher.encrypt(bytes(passwd, encoding="utf8")))
    return parse.quote(cipher_text.decode("utf-8"))

#随机古诗接口 content-内容 author-作者 origin-标题
def poem():
    poem = requests.get('https://v1.jinrishici.com/all.json',verify =False)
    poem_dict = json.loads(poem.text)
    #print (poem_dict['content'], poem_dict['author'], poem_dict['origin'])
    return poem_dict

#判断是否成功
def isDone(response):
    response_dict = json.loads(response.text)
    if response_dict['message'] in ['操作成功', '请求成功']:
        return '√'
    else:
        return ('× -> 错误信息：'+ response_dict['message']+'\n')

#登录
def login(account, passwd):
    encrypt_password = encrypt_passwd(passwd)
    form_data = {
        'account': account,
        'passwd': encrypt_password,
        'ct': '2',
        'app': '1',
        'v': '4.7.11',
        'identify':'0'
       }
    
    login_josn = requests.get('https://mobile.yiban.cn/api/v2/passport/login', params=form_data, verify=False)

    try:
        login_info_dict = json.loads(login_josn.text)
        
        print('嘿,',login_info_dict['data']['user']['name'])
        print('欢迎交流学习爬虫')
        global access_token
        global user_id
        global headers
        global token
        token = login_info_dict['data']['token']
        access_token = login_info_dict['data']['access_token']
        user_id = login_info_dict['data']['user']['user_id']
        headers = {
            'Authorization': 'Bearer '+access_token,
            'Host': 'mobile.yiban.cn',
            'User-Agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/530.17(KHTML,like Gecko)Version/4.0 Mobile Safari/530.17',
            'AppVersion': '4.7.11',
            'loginToken': access_token
        }
        return True
    except:
        print('登录中....'+isDone(login_josn))
        print('登录出错，请重试')
        
        return False
        #exit(-1)
#签到
def checkin():
    checkin = requests.post('https://mobile.yiban.cn/api/v3/checkin/answer',verify=False, data={'access_token':access_token, 'optionId':'18030'}, headers=headers)
    print('\n签到开始(网薪不固定，一般+2)')
    print('正在进行签到....'+isDone(checkin))
    return

#易瞄瞄 发帖 评论 *3
def ymm():
    print('\n获取易瞄瞄相关网薪....')
    print('将在易瞄瞄进行 (发帖+评论)*3，预计网薪+8')
    print('易瞄瞄比较鸡贼，因此发帖时间间隔设置为1分钟，耐心等等(2分钟)...')
    ymm_headders = {
        'Authorization': 'Bearer' + access_token,
       'User-Agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/530.17(KHTML,like Gecko)Version/4.0 Mobile Safari/530.17',
       'host':'ymm.yiban.cn', 
       'loginToken': access_token
       }
    
    
    for i in range(3):
        ymmform ={
            'id': access_token,
            'content': poem()['content'],
        }
        #发布
        ymm_post = requests.post('https://ymm.yiban.cn/article/index/add', data=ymmform, verify=False, headers=ymm_headders)
        print('进行第{}次发帖{}'.format(i+1,isDone(ymm_post)),end='')
        if isDone(ymm_post) != '√':
            print('\n易瞄瞄搞事情,跳过吧')
            continue

        try:
            ymmlist = requests.get('https://ymm.yiban.cn/news/list/news?page=1&size=1' + '&uid=' + user_id + '', headers=ymm_headders, verify=False)
            ymminfo = json.loads(ymmlist.text)
            Article_id = ymminfo['data']['list'][0]['Article_id']
            comment_json = {
                "id": Article_id,
                "comment": poem()['content'],
            }
            
            #评论
            ymm_comment = requests.post('https://ymm.yiban.cn/news/comment/add?&id='+ Article_id,cookies= {'loginToken': access_token,'client':'android'}, json=comment_json, verify=False)
            print('\t评论'+isDone(ymm_comment), end='')
           
            #删除
            ymm_del = requests.post('https://ymm.yiban.cn/article/index/del?'+'&id=' + Article_id,headers=ymm_headders, verify=False)
            print('\t删除'+isDone(ymm_del), end='\r')
            if i != 2:
                time.sleep(60)
        except:
            print('\n你的易瞄瞄可能出了点问题，将跳过易瞄瞄相关部分')
            break
    print('')
    return

#动态 发布 同情 点赞 x3
def feeds():
    print('\n获取动态相关网薪.....')
    print('将进行 (发布+点赞+同情)*3，动态仅自己可见！预计网薪+16')
   
    for i in range(3):
        try:
            feedsform = {
                'access_token':access_token,
                'content':poem()['content'],
                'visibleScope':'3',
                'toUserIds':user_id
            }

            time.sleep(1)
            #发布
            pfeeds = requests.post('https://mobile.yiban.cn/api/v3/feeds', data=feedsform, verify=False, headers=headers )
            print('进行第 {} 次\t发布{}'.format(i+1,isDone(pfeeds)),end='')

            feeds_dict = json.loads(pfeeds.text)
            feedsId = str(feeds_dict['data']['feedId']) #居然是整形

            time.sleep(1)
            #点赞
            downs = requests.post('https://mobile.yiban.cn/api/v3/feeds/'+feedsId+'/downs', data={'access_token':access_token}, verify=False, headers=headers)
            print('\t点赞'+isDone(downs), end='')
            
            time.sleep(1)
            #同情
            ups = requests.post('https://mobile.yiban.cn/api/v3/feeds/'+feedsId+'/ups', data={'access_token':access_token}, verify=False, headers=headers)
            print('\t同情'+isDone(ups), end='\r')
        except:
            print('\n好像出了点问题，没事没事继续......')
    print('')
    return

#获取机构&群信息
def getID():
    #获取机构列表

    org = requests.get('https://mobile.yiban.cn/api/v2/user/follows',headers= headers, verify=False, params= {'access_token':access_token, 'kind':'2'})

    print('正在获取机构账号列表...'+isDone(org))
    try:
        orgdict = json.loads(org.text)
        orglist = []
        for i in  orgdict['data']['users']:
            orglist.append({'name': i['name'], 'org_id': i['user_id']})
    except:
        print('哦豁？获取出错...算了算了~~')

    #获取公共群列表
    groups = requests.get('https://mobile.yiban.cn/api/v2/groups/mygroups',headers= headers, verify=False, params= {'access_token':access_token, 'is_org_group':'0'})
    print('正在获取公共群列表.....'+isDone(groups))
    try:
        groupsdict = json.loads(groups.text)
        groundlist = []
        for i in  groupsdict['data']['myJoinGroups']['list']:
            groundlist.append({'name': i['name'], 'group_id': i['group_id']})
            
    except:
         print('哦豁？获取出错...算了算了~~')
    
    return {'grouplist':groundlist, 'orglist':orglist}
#公共群&机构
def topages():
    print('\n获取公共群&机构相关网薪，预计网薪+62')
    try:
        id_dict = getID()
        randomgr = random.choice(range(len(id_dict['grouplist'])))
        randomorg = random.choice(range(len(id_dict['orglist'])))
        global grid
        global grname
        grid = id_dict['grouplist'][randomgr]['group_id']
        grname =  id_dict['grouplist'][randomgr]['name']

        orgaid = id_dict['orglist'][randomorg]['org_id']
        orgname = id_dict['orglist'][randomorg]['name']

    except:
        print('因为信息获取出错，此部分跳过！')
        return
        
    print('\n即将访问机构和公共群群主页*100 (事实上只需要5次，但老是出现玄学情况所以直接怼100)')
    for i in range(100):
        #time.sleep(2)
        orgapage = requests.get('https://mobile.yiban.cn/api/v1/organizations/'+orgaid, params={'access_token':access_token}, verify=False, headers=headers)
        isDone(orgapage)

        grpages = requests.get('https://mobile.yiban.cn/api/v2/groups/'+grid, params={'access_token':access_token}, verify=False, headers=headers)
        print('访问机构账号主页',orgname,'第{}次 '.format(i+1)+isDone(grpages)+'\t公共群账号主页',grname,'第{}次 '.format(i+1)+isDone(grpages),end='\r') 
    print('')
    return
def grapp():
    global grapps_headers
    global grapps
    global puid
    global channel_id
    grapps_headers={
        'Host': 'www.yiban.cn',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Pro Build/QKQ1.190915.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36 yiban_android',
        'logintoken': access_token,
    }
    
    print('\n后续操作将在公共群 {} 进行，正在获取各种xxx'.format(grname))
    try:
        #请求cookies, 获取id
        grapps = requests.Session()
        grapps.get('https://www.yiban.cn/blog/Index/index/userid/'+user_id,verify=False, cookies={'loginToken':access_token},headers=grapps_headers)
        print('请求cookies.......√')

        rpuid = grapps.get('https://mobile.yiban.cn/api/v2/groups/'+grid+'?access_token='+access_token, verify=False)
        puid = json.loads(rpuid.text)['data']['group']['user']['user_id']
        print('请求puid..........'+ isDone(rpuid))
        
        rchannel = grapps.post('https://www.yiban.cn/forum/api/getListAjax',data={'puid':puid,'group_id':grid,}, headers=grapps_headers,verify=False)
        channel_id = json.loads(rchannel.text)['data']['channel_id']
        print('请求channel_id....'+ isDone(rchannel))
    except:
        print('获取信息失败，跳过后续轻社区发帖&投票')
        return

    #轻社区发布话题
    poem_dict = poem()
    article_form = {
        'channel_id': channel_id,
        'puid': puid,
        'title': poem_dict['content'],
        'content': poem_dict['author'] +'《'+poem_dict['origin']+'》' + '<br/>&emsp;&emsp;&emsp;&emsp;——'+time.ctime(),
    }
    posting = grapps.post('https://www.yiban.cn/forum/article/addAjax',headers=grapps_headers, data=article_form, verify=False)
    print('在 {} 轻社区发布话题*1 {}'.format(grname, isDone(posting)))

    #投票相关
    print('即将在 {} 轻投票进行发布、点赞、评论、删除 *5'.format(grname))
    try:
        for i in range(5):
            vote_form = {
                'puid':puid,
                'uid':user_id,
                'group_id':grid,
                'title':time.ctime(),
                'subjectTxt_1':poem()['content'],
                'subjectTxt_2':poem()['content'],
                'scopeMin':'1',
                'scopeMax':'1',
                'isAnonymous':'1',
                'voteValue': time.strftime("%Y-%m-%d %H:%M",time.localtime(time.time()+60*60)),
                'public_type':'4',
                'voteKey':'2',
                'voteIsCaptcha': '0',
                'minimum':'1',
                'options_num':'2'
            }
            
            #发布
            vote = grapps.post('https://www.yiban.cn/vote/vote/add',verify=False, headers=grapps_headers, data=vote_form)
            print('第 {} 次\t发布{}'.format(i+1, isDone(vote)), end='')
            vote_id = json.loads(vote.text)['data']['lastInsetId']

           
            #获取投票选项信息
            vote_info = grapps.post('https://www.yiban.cn/vote/vote/getVoteDetail', verify=False, data={'vote_id':vote_id, 'actor_id':user_id, 'group_id':grid, 'puid':puid}, headers=grapps_headers)
            voptions_id = json.loads(vote_info.text)['data']['option_list'][0]['id']
            mount_id = json.loads(vote_info.text)['data']['vote_list']['mount_id']

            
            #投票
            voptions_form = {
                'vote_id':vote_id,
                'voptions_id':voptions_id,
                'group_id':grid,
                'puid':puid,
                'scopeMax':'1',
                'minimum':'1'
            }
            option = grapps.post('https://www.yiban.cn/vote/vote/act', verify=False, headers=grapps_headers, data=voptions_form)
            print('\t投票{}'.format(isDone(option)), end='')

            
            #点赞
            love = grapps.post('https://www.yiban.cn/vote/vote/editLove', verify=False, headers=grapps_headers, data={
                'vote_id':vote_id,
                'group_id':grid,
                'puid':puid,
                'flag':'1',
            })
            print('\t点赞{}'.format(isDone(love)), end='')

            
            #评论
            comment = grapps.post('https://www.yiban.cn/vote/vote/addComment', verify=False, headers=grapps_headers, data={
                'msg':'[开心]',
                'vote_id':vote_id,
                'group_id':grid,
                'puid':puid,
                'author_id':user_id,
                'mountid':mount_id,
            })
            print('\t评论{}'.format(isDone(comment)), end='')

            #删除投票
            delvote = grapps.post('https://www.yiban.cn/vote/Expand/delVote', data={'group_id':grid, 'puid':puid,'vote_id':vote_id}, verify=False,headers=grapps_headers)
            print('\t删除{}'.format(isDone(delvote)), end='\r')
        print('')
    except:
        print('')
        print('好像出现验证码了，散了散了...')
    return

#博客 发布 点赞 x3
def blog():
    print('\n获取博客相关网薪....')
    print('将在轻博客进行 (发布+点赞)*3，博客仅自己可见！预计网薪+16')
    global blog_headers
    blog_headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Pro Build/QKQ1.190915.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36 yiban_android',
        'appversion': '4.7.11',
        'logintoken': access_token,
    }
    global blog_session 
    blog_session = requests.Session()
    #请求cookies
    blog_session.get('https://www.yiban.cn/blog/Index/index/userid/'+user_id,verify=False, cookies={'loginToken':access_token},headers=blog_headers)
    
    #请求token
    blog_html = blog_session.get('https://www.yiban.cn/blog/index/addblog', verify=False, headers=blog_headers).text
    blog_soup = BeautifulSoup(blog_html, features="html.parser")
    token = blog_soup.find(attrs={"id": "up_token",'type':'hidden'})['value']

    for i in range(3):
        #发布
        poem_dict = poem()
        blog_form ={
            'title': poem_dict['content'],
            'content':  poem_dict['author'] +'《'+poem_dict['origin']+'》' + '<br/>&emsp;&emsp;&emsp;&emsp;——'+time.ctime(),
            'ranges':'2',
            'type':'2',
            'token':token,
        }
        pblog = blog_session.post('https://www.yiban.cn/blog/blog/addblog', data=blog_form, verify=False, headers=blog_headers)
        print('进行第{}次发布{}'.format(i+1,isDone(pblog)),end='\r')
    print('')
    
    #获取博客列表
    blogs = blog_session.get('https://www.yiban.cn/blog/Index/index/userid/'+user_id, headers=blog_headers, verify=False).text
    blogls_soup = BeautifulSoup(blogs, features="html.parser")
    blogs_list = blogls_soup.find_all('div',attrs={"class": "blog_item",'data-uid':user_id,})
    global blogs_id
    blogs_id = []
    for i in blogs_list:
        blogs_id.append(i['data-blogid'])
    
    #点赞
    for i in range(3):
        time.sleep(1)
        try:
            blogid = blogs_id[i]
            addlike = blog_session.get('https://www.yiban.cn/blog/blog/addlike/uid/'+ user_id + '/blogid/'+ blogid, headers=blog_headers, verify=False)
            print('进行第{}次点赞{}'.format(i+1,isDone(addlike)),end='\r')
            
        except:
            print('\n哦豁...点赞出错了，那就跳过吧~',end='')
            break
    print('')
    return

#博客 删除
def delblog():
    print('\n即将对博客擦屁股')
    print('将删除博客*3(回滚刚刚操作)')
    for i in range(3):
        try:
            blogid = blogs_id[i]
            delblog = blog_session.get('https://www.yiban.cn/blog/blog/delblog/uid/13241/blogid/'+ blogid, headers=blog_headers, verify=False)
            print('进行第{}次删除{}'.format(i+1,isDone(delblog)),end='\r')

        except:
            print('\n哦豁...删除出错了，可能你的博客已经空了\n跳过跳过~',end='')
            break

    print('')
    return

#轻社区话题 删除
def deltopics():
    #获取列表
    try:
        print('\n即将回滚轻社区话题*1')
        articles = grapps.post('https://www.yiban.cn/forum/article/listAjax',verify=False, headers=grapps_headers, data={
            'my':'1', 
            'group_id':grid, 
            'puid':puid,
            
        })
        article_dict = json.loads(articles.text)
        article_id = []
        for i in article_dict['data']['list']:
            article_id.append(i['id'])
        print('获取个人话题列表....'+isDone(articles))
    except:
        print('获取信息炸毛了，算了自己手动删吧....')
        return

        #删！
    try:
        for i in range(1):
            #time.sleep(3)
            del_topics = grapps.post('https://www.yiban.cn/forum/article/setDelAjax',verify=False, headers=grapps_headers,data={
                'article_id_list':article_id[i],
                'puid':puid,
                'channel_id':channel_id,
            })
            print('正在删除话题....{}'.format(isDone(del_topics)),end='\r')
        print('')
    except:
        print('删除时发生异常，可能你发布的话题已经清空了')
    return

#动态删除
def delfeeds():
    print('\n即将删除动态*3')
    try:
        feeds_list = requests.get('https://mobile.yiban.cn/api/v3/feeds/user',verify=False, headers=headers, params={
            'access_token':access_token,
            'userId':user_id,
            'limit':'100',
        })
        

        feeds_ls = json.loads(feeds_list.text)['data']['list']
        feeds_id = []
        for i in feeds_ls:
            feeds_id.append(i['id'])
        print('获取个人动态列表....'+isDone(feeds_list))
    except:
        print('获取信息炸毛了，跳过跳过~~')
        return

    #删除
    try:

        for i in range(3):
            feeds_del = requests.delete('https://mobile.yiban.cn/api/v3/feeds/'+str(feeds_id[i])+'?access_token='+access_token, verify=False, headers=headers)
            print('删除动态*{}....{}'.format(i+1, isDone(feeds_del)),end='\r')
        print('')
    except:
        print('删除过程出现bug，进行下一部分↓')
    return

def clear():
    print('\n能扒的网薪已经尽力扒了，下面根据你的需要擦擦屁股(删除)')
    choose = input('\n是否删除刚刚发布的动态和博客\n数量：各3条\n权限：仅自己可见\n内容：随机古诗词，注意：删除会扣一定的网薪，留着别人也看不见..\n\n确认删除输入 del 并回车，跳过直接回车>')
    if choose == 'del':
        delfeeds()
        delblog()
    choose = input('\n是否删除刚刚发布轻社区话题\n数量：1条\n权限：公开\n内容：随机古诗词\n注意：扣一定的网薪，保留可以为公共群水一下EGPA\n\n确认删除输入 del 并回车，跳过直接回车>')
    if choose == 'del':
        deltopics()
    return
def main():
    os.system("mode con cols=120 lines=40")
    print('NOTICE：\n\n\t1.密码加密轮子取自 LooyeaGee 链接：https://looyeagee.cn/software/yiban/ ')
    print('\t2.古诗词接口采用 一言·古诗词 API 链接：https://github.com/xenv/gushici/')
    print('\t3.此软件可模拟易班app进行一系列日常获取网薪的任务(签到、动态、博客等等。。)')
    print('\t4.模拟环境：Redmi Note 7 Pro Android 10; app版本：4.7.11')
    print('\t5.成功登录后将会退出你手机上的易班账号，但可以有效跳过PC端网页的验证码')
    print('\t6.运行过程勿在手机app上登录！')
    print('\t7.软件纯玩具代码打包，仅供学习交流使用')
    print('\t8.有问题可反馈到邮箱：hmcx527@gmail.com 或 GitHub：https://github.com/ChanEKan/YibanSpider')
    while(True):
        account =  input('\n\n账号：\t')
        passwd = input('密码：\t')
        os.system('cls')
        if login(account, passwd):
            break
    checkin()
    topages()
    grapp()
    ymm()
    feeds()
    
    blog()
    clear()
    
    print('All Done!')
    input('\n<现在你可以登录app检查一下网薪明细，回车退出>')
    return
main()
