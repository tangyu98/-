import hashlib
import random
from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from tiantianshengxian.decorators import auto_session
from . import db
from django.http.response import JsonResponse


def index(request):
    # 获取表数据
    sql = 'select * from goods'
    goods = db.query_list(sql)
    user = request.session.get("LOGIN_LOCAL_FLAG")
    if user is None:
        return render(request, "index.html", {"goods": goods})
    user_id = user.get("id")
    sql1 = "select num from shop_car where user_id=%s"
    list1 = db.query_list(sql1, params=(user_id,))
    num = 0
    for i in range(len(list1)):
        num = list1[i]["num"] + num
    return render(request, "index.html", {"goods": goods, "num": num})


# 注册
@require_http_methods(["POST"])
def register(request):
    name = request.POST.get("name")
    password = request.POST.get("password")
    email = request.POST.get("email")
    pwd = hashlib.md5(password.encode())
    password = pwd.hexdigest()

    sql = "select * from users where name = %s"
    user = db.query(sql, params=(name,))
    if user:
        return render(request, "register.html", {"msg": "账号已存在"})
    sql = "insert into users(name,password,email) values(%s,%s,%s)"
    # 主键
    pk = db.update(sql, params=(name, password, email))

    return render(request, "next_reg.html", {"pk": pk})


# 完善信息
def reg_v(request):
    params = request.POST.dict()
    id = params["id"]
    addr = params["addr"]
    tel = params["tel"]
    # 找到对应用户，完善信息
    sql = "update users set addr=%s, tel=%s where id = %s"
    db.update(sql, params=(addr, tel, id,))
    # render(request, "login.html")
    return redirect(to="/login")


# 匹配所有的跳转
def path(request, path):
    return render(request, f"{path}.html")


# 登陆
def login(request):
    params = request.POST.dict()
    password = request.POST.get("password")
    name = request.POST.get("name")
    # 加密
    from hashlib import md5
    m = md5(password.encode())
    password = m.hexdigest()
    sql = "select * from users where name = %(name)s and password = %(password)s"
    params["password"] = password
    user = db.query(sql, params=params)
    if user is None:
        return render(request, "login.html", {"msg": "账号或者密码不正确", "user": params})
    user_id = user.get("id")
    sql1 = "select num from shop_car where user_id=%s"
    list1 = db.query_list(sql1, params=(user_id,))
    num = 0
    for i in range(len(list1)):
        num = list1[i]["num"] + num
    user["num"] = num

    request.session.setdefault("LOGIN_LOCAL_FLAG", user)

    # users = request.session.get("LOGIN_LOCAL_FLAG")
    # user_id = user.get("id")
    # sql1 = "select num from shop_car where user_id=%s"
    # list1 = db.query_list(sql1, params=(user_id,))
    # num = 0
    # for i in range(len(list1)):
    #     num = list1[i]["num"] + num
    # return render(request, "index.html", {"users": params})
    # return render(request, "index.html", {"num": num})

    return redirect(to="/")


# 退出登陆
def logout(request):
    # 删除过期的session
    request.session.clear_expired()
    # 强制消亡
    request.session.flush()
    return redirect(to="/index")


# 收获地址表的完善
@auto_session
def site(request):
    name = request.POST.get("name")
    addr = request.POST.get("addr")
    post_num = request.POST.get("post_num")
    tel = request.POST.get("tel")
    tel = tel[:3] + "****" + tel[7:]
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")
    if len(tel) == 11:
        sql = "insert into u_addr (name,addr,post_num,tel,user_id) values(%s,%s,%s,%s,%s)"
        pk = db.update(sql, params=(name, addr, post_num, tel, user_id))
        sql1 = "select * from u_addr where name = %s"
        u_addr_new = db.query(sql1, (name,))
        return render(request, "user_center_site.html", {"pk": pk, "u_addr_new": u_addr_new})
    return render(request, "user_center_site.html", {"msg": "请输入正确的电话号码"})


# 去购物车
@auto_session
def cars(request):
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")

    sql = "SELECT c.*,g.* FROM shop_car c LEFT JOIN goods g ON c.goods_id =g.id WHERE c.user_id = %s"

    goods = db.query_list(sql, params=(user_id,))
    prices1 = 0
    nums = len(goods)
    for i in range(len(goods)):
        price = goods[i].get("price")
        num = goods[i].get("num")
        prices = price * num
        prices1 = prices + prices1
    return render(request, "cart.html", {"goods": goods, "prices1": prices1, "nums": nums})


# 浏览数据的显示
@auto_session
def user_center_info(request):
    user = request.session.get("LOGIN_LOCAL_FLAG")
    id = user["id"]
    sql = "select * from looked where user_id=%s order by id desc"
    lookedlist = db.query_list(sql, params=(id,))
    # good_id = lookedlist["good_id"]
    goodlist = []
    for i in range(len(lookedlist)):
        p = lookedlist[i]
        goods_id = lookedlist[i]["goods_id"]
        sql = "select * from goods where id=%s"
        goodsdict = db.query(sql, params=(goods_id,))
        goodlist.append(goodsdict)
    return render(request, "user_center_info.html", {"lookedlist": lookedlist, "goodlist": goodlist})


# 订单
@auto_session
def orders(request, page):
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")
    # sql = "select * from orders where user_id=%s"
    # orders = db.query_list(sql, params=(user_id,))
    # for i in orders:
    sql = "select o.* , g.name , g.photo from orders o left join goods g on o.goods_id = g.id " \
          "where o.user_id=%s order by status,time desc"
    goods = db.query_list(sql, params=(user_id,))
    querset = goods
    paginator = Paginator(querset, 4)
    page = paginator.get_page(int(page))
    ran = range(1, page.paginator.num_pages + 1)
    return render(request, "user_center_order.html", {"goods": page, "ran": ran})


# 详情
# @auto_session/
def detail(request, pk):
    # 添加浏览表
    # 用户id
    user = request.session.get("LOGIN_LOCAL_FLAG")
    counts = 0
    if user is not None:
        user_id = user.get("id")
        sql1 = "select * from looked where goods_id = %s"
        user1 = db.query(sql1, params=(pk,))
        sql3 = "select num from shop_car where user_id=%s"
        user_id = user.get("id")
        countlist = db.query_list(sql3, params=(user_id,))
        # counts = 0
        for i in range(len(countlist)):
            counts = counts + countlist[i].get("num")
        if user1 is None:
            sql2 = "insert into looked (goods_id, user_id) value(%s,%s)"
            db.update(sql2, params=(pk, user_id))
        sql3 = "delete from looked where goods_id = %s"
        db.update(sql3, params=(pk,))
        sql4 = "insert into looked (goods_id, user_id) value(%s,%s)"
        db.update(sql4, params=(pk, user_id))

    # 新品推荐
    sql = "select * from goods where id = %s"
    good = db.query(sql, params=(pk,))
    list1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    list1.remove(pk)
    good_new_list2 = []
    for i in range(2):
        sql = "select * from goods where id = %s"
        good_new = db.query(sql, params=(list1[i],))
        good_new_list2.append(good_new)
    return render(request, "detail.html", {"good": good, "good_new_list2": good_new_list2, "counts": counts})


# 详情页商品加入购物车
@auto_session
def add_cart(request, pk, num):
    # 查询商品信息
    sql3 = "select * from goods where id=%s"
    gooddict = db.query(sql3, params=(pk,))
    name = gooddict["name"]
    id = gooddict["id"]

    # 查询购物车是否有改商品
    sql = "select * from shop_car where goods_id = %s"
    good = db.query(sql, params=(pk,))
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")

    if good is None:
        sql1 = "insert into shop_car (name, num, goods_id, user_id, status) values(%s,%s,%s,%s,%s)"
        db.update(sql1, params=(name, num, id, user_id, 1))
        luyou = "/detail" + "/" + str(pk)
        return redirect(to=luyou)
    num1 = good["num"] + num
    sql2 = "update shop_car set num=%s where goods_id=%s"
    db.update(sql2, params=(num1, pk,))
    luyou = "/detail" + "/" + str(pk)
    return redirect(to=luyou)


# 保存地址数据
@auto_session
def to_site(request, pk):
    sql = "select * from u_addr where user_id = %s"
    u_addr = db.query(sql, params=(pk,))
    if u_addr is None:
        return redirect(to="/user_center_site")
    return render(request, "user_center_site.html", {"u_addr": u_addr})


# 立即购买
@auto_session
def to_place(request, gid, num):
    # 商品详情
    sql = "select * from goods where id = %s"
    good = db.query(sql, params=(gid,))
    price = good["price"]
    sum = price * num
    # 用户id
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")
    # 地址详情
    sql1 = "select * from u_addr where user_id = %s"
    u_addr = db.query(sql1, params=(user_id,))
    # 随机订单号
    str1 = ""
    for i in range(10):
        num1 = random.randint(0, 9)
        str1 = str1 + str(num1)
    import datetime
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 添加到订单表
    sql2 = "insert into orders (order_id, goods_id, user_id, status, time, money, num) value(%s,%s,%s,%s,%s,%s,%s)"
    db.update(sql2, params=(str1, gid, user_id, 1, now_time, sum, num))
    sums = sum + 10
    return render(request, "place_order.html",
                  {"good": good, "sum": sum, "u_addr": u_addr, "num": num, "sums": sums, "str1": str1})


def find_goods(request):
    name = request.POST.get("name")
    sql = "select * from goods where name=%s"
    goods = db.query(sql, params=(name,))
    if goods:
        return JsonResponse(data={"status": True, "goods": goods})
    return JsonResponse(data={"status": False, "message": "没有该商品！"})


# 提交订单,传入的是支付方式
@auto_session
def to_order(request, way, good_id, order_id):
    # 用户id
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")
    # 查取用户信息
    sql = "select * from users where id=%s"
    user = db.query(sql, params=(user_id,))
    pay_account = user["name"]
    import datetime
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 支付订单的数据
    sql1 = "insert into pay_for (pay_way, pay_account, user_id, time) value(%s, %s, %s, %s)"
    db.update(sql1, params=(way, pay_account, user_id, time))

    sql2 = "update orders set status=%s where order_id=%s"
    db.update(sql2, params=(2, order_id))
    # sql2 = "update shop_car set num=%s where id=%s"

    return redirect(to="/orders/1")


#删除购物车的物品
def delete(request, pk):
    sql = "DELETE FROM shop_car WHERE goods_id=%s"
    db.update(sql, params=(pk,))
    return redirect(to="/cars")


# def choose(request):
#     sql = "select * from goods"
#     good = db.query_list(sql)
#     return render(request,"list.html",{"good":good})


def chooseone(request, status, page):
    sql = "select * from goods where status=%s"
    one = db.query_list(sql, params=(status,))
    querset = one
    paginator = Paginator(querset, 2)
    page = paginator.get_page(int(page))
    ran = range(1, page.paginator.num_pages + 1)

    user = request.session.get("LOGIN_LOCAL_FLAG")
    counts = 0
    if user is not None:
        user_id = user.get("id")
        sql3 = "select num from shop_car where user_id=%s"
        countlist = db.query_list(sql3, params=(user_id,))
        for i in range(len(countlist)):
            counts = counts + countlist[i].get("num")
    return render(request, "list.html", {"one": page, "ran": ran, "status": status,"counts":counts})


#添加购物车
@auto_session
def cars_add(request):
    pk = request.POST.get("pk")
    sql3 = "select * from goods where id=%s"
    gooddict = db.query(sql3, params=(pk,))
    name = gooddict["name"]
    id = gooddict["id"]
    sql = "select * from shop_car where goods_id = %s"
    good = db.query(sql, params=(id,))
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")
    if good is None:
        sql1 = "insert into shop_car (name, num, goods_id, user_id, status) values(%s,%s,%s,%s,%s)"
        db.update(sql1, params=(name, 1, id, user_id, 1))
        return redirect(to="/cars")
    num = good["num"] + 1
    sql2 = "update shop_car set num=%s where goods_id=%s"
    db.update(sql2, params=(num, id))

    sql1 = "select num from shop_car where user_id=%s"
    list1 = db.query_list(sql1, params=(user_id,))
    num = 0
    for i in range(len(list1)):
        num = list1[i]["num"] + num
    return JsonResponse(data={"status": False, "message": "已加入购物车。", "num": num})


@auto_session
def order(request):
    user = request.session.get("LOGIN_LOCAL_FLAG")
    user_id = user.get("id")
    status = 1
    sql = "select * from shop_car where user_id=%s and status=%s"
    goods = db.query_list(sql, params=(user_id, status))
    import datetime
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for items in goods:
        goods_id = items["goods_id"]
        sql = "select * from goods where id=%s"
        good = db.query(sql, params=(goods_id,))
        price = good.get("price")
        num = items.get("num")
        str1 = ""
        for i in range(10):
            num1 = random.randint(0, 9)
            str1 = str1 + str(num1)
        sql = "insert into orders(order_id,goods_id,user_id,status,time,money,num) " \
              "values(%s,%s,%s,%s,%s,%s,%s)"
        db.update(sql, params=(str1, goods_id, user_id, 1, now_time, price, num))
    sql = "select o.*,g.photo,g.name,g.price from shop_car o left join goods g " \
          "on o.goods_id = g.id where user_id=%s and o.status=%s"
    order = db.query_list(sql, params=(user_id, status))
    sql = "delete from shop_car where user_id = %s and status=%s"
    db.update(sql, params=(user_id, status))
    sql = "select * from u_addr where user_id=%s"
    u_addr = db.query(sql, params=(user_id,))
    return render(request, "order.html", {"order": order, "u_addr": u_addr})


# 改变购物车表里的数据
def changenum(request):
    nums = request.POST.get("nums")
    good_id = request.POST.get("id")
    sql = "update shop_car set num=%s where goods_id=%s"
    db.update(sql, params=(nums, good_id))
    return JsonResponse(data={"msg": "111"})


# 改变购物车物品状态
def changestatus(request):
    status = request.POST.get("status")
    # good_id = request.POST.get("id")
    sql = "update shop_car set status=%s"
    db.update(sql, params=(status,))
    return JsonResponse(data={"msg": "111"})


# 改变一个状态
def changestatusone(request):
    status = request.POST.get("status")
    good_id = request.POST.get("id")
    sql = "update shop_car set status=%s where goods_id=%s"
    db.update(sql, params=(status, good_id))
    return JsonResponse(data={"msg": "111"})

# 同步session的数据

# def session_num(request):
#     num = request.POST.get("num")
#     user = request.session.get("LOGIN_LOCAL_FLAG")
#     user["num"] = num
#     request.session.setdefault("LOGIN_LOCAL_FLAG", user)
#     user1 = request.session.get("LOGIN_LOCAL_FLAG")
#
#     return JsonResponse(data={"num": num})
