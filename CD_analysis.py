import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
plt.style.use('ggplot') #设定绘图风格

## 1. 数据读取
# 由于数据没有含表头，先create表头，在读取数据时赋予表内。字符串是空格分割，用\s+表示匹配任意空白符。
columns = ['order_id', 'order_date', 'order_product', 'order_amount']
df = pd.read_csv('CDNOW_master.txt', names=columns, sep='\s+')


## 2. 数据描述
df.head()
# 观察数据，order_id表示:订单号； order_date:购买时间； order_product:购买产品数量； order_amunt:购买金额；
# 1.在order_date数据中，时间格式不对；2.购买金额较小；3.同一天可多次购买，例如用户id2出现两次；


df.describe()
# 订单接近7万个；从order_product来看，用户平均每笔订单购买2.4个商品，标准差在2.3，稍稍具有波动性。中位数为2，75%用户为3个产品。
# 说明大部分订单购买数量不多，且购买金额较小；最大购买数量为99个；
# 一般而言，消费类的数据分布，都是长尾形态。大部分用户都是小额，然而小部分用户贡献了收入的大头，俗称二八。

df.info()
# 没有空值，数据干净


## 3. 数据预处理
# 时间的数据类型转换；
df['order_date'] = pd.to_datetime(df.order_date,format="%Y%m%d")
# pd.to_datetime可以将特定的字符串或者数字转换成时间格式，其中的format参数用于匹配。
# 例如19970101，%Y匹配前四位数字1997，如果y小写只匹配两位数字97，%m匹配01，%d匹配01。
# 另外，小时是%h，分钟是%M，注意和月的大小写不一致，秒是%s。若是1997-01-01这形式，则是%Y-%m-%d，以此类推。

df['month']=df.order_date.values.astype('datetime64[M]') #将时间转化成月精度，以决定用来作为时间窗口来分析消费用户行为
# datetime64[D] 日精度；datetime64[M] 月精度；
df.head()


## 4. 数据分析和可视化
# 1）按用户的纬度分析；每个用户的CD总消费数量和总消费金额；可以用df.groupby
customer_group = df.groupby('order_id').sum()
customer_group.head()
customer_group.describe()
# 从用户角度看，每位用户平均购买7张CD，最多的用户购买了1033张，属于狂热用户了。用户的平均消费金额（客单价）100元，标准差是240;
# 结合分位数和最大值看，平均值才和75分位接近，肯定存在小部分的高额消费用户。




# 2）按月的维度分析；每个月的CD总消费数量和总消费金额；
# 每个月的CD总数量；
month_product = df.groupby('month').order_product.sum()
month_product.head()
month_product.plot()
plt.title('total number of CD per month')

# 每个月的CD总消费金额；
month_amount = df.groupby('month').order_amount.sum()
month_amount.head()
month_amount.plot()
plt.title('total amount of CD per month')
# 前3个月销量非常高，比较异常，但4月份之后销售量开始平稳；
# 假设是用户身上出了问题，早期时间段的用户中有异常值，第二假设是各类促销营销，但这里只有消费数据，所以无法判断。

#### scatter plot
# 每笔订单散点图; 使用函数：df.plot.scatter(x=,y=)
df.plot.scatter(x='order_amount', y='order_product')
plt.title('scatter plot by order')
# 从图中观察，订单消费金额和订单商品量呈规律性，每个商品十元左右(200/20)。订单的极值较少，超出1000的就几个。显然不是异常波动的罪魁祸首。

# 每个用户散点图；
customer_group.plot.scatter(x='order_amount', y='order_product')
plt.title('scatter plot by customer')
# 用户也比较健康，而且规律性比订单更强。因为这是CD网站的销售数据，商品比较单一，金额和商品量的关系也因此呈线性，没几个离群点。

#### histogram - subplot; 观察用户消费的金额和购买量
plt.figure(figsize=(12,4)) #figsize(宽，高)
plt.subplot(121) #121：表示分成1*2个图片区域，占用第1个，即第一行第一列
df.groupby('order_id').order_amount.sum().hist(bins=50) #每个用户的总金额柱状子图
plt.xlabel('total order amount')
plt.ylabel('number of customers')
plt.xlim(0,2000) #x轴的区间
plt.title('total order amount by customer')

plt.subplot(122)
df.groupby('order_id').order_product.sum().hist(bins=50) #每个用户的总购买量柱状子图
plt.xlabel('total order product')
plt.ylabel('number of customers')
plt.xlim(0,150)
plt.title('total order product by customer')
# 从直方图看，大部分用户的消费能力确实不高，高消费用户在图上几乎看不到。这也确实符合消费行为的行业规律




# 3）按消费时间节点
df.groupby('order_id').month.min().value_counts()
# month.min(): 用户消费行为的第一次消费时间（月份）
# value_counts(): 相同时间的相加
# 因此，用户第一次消费时间集中在前三个月

df.groupby('order_id').month.max().value_counts()
# month.max(): 用户消费行为的最后一次消费时间
# 绝大部分数据依然集中在前三个月。后续的时间段内，依然有用户在消费，但是缓慢减少。




# 4) 分析消费中的复购率和回购率
# 1. 先将用户消费数据进行数据透视；用pivot_table()，fillna()
pivoted_counts = df.pivot_table(index='order_id', columns='month', values='order_date', aggfunc='count').fillna(0)
# index: table的行；columns：table的列；values：用哪个数值计算；aggfunc：用什么计算方法
# fillna(0)：用0去填充缺少值
columns_month = df.month.sort_values().astype('str').unique()
pivoted_counts.columns = columns_month
print(pivoted_counts.head())
# sort_values(): 将数值从小到大排序；astype('str'): 将数据格式从datetime64改成字符串str；unique(): 去除重复数值

# 2. 将数据转换一下，消费两次及以上记为1，消费一次记为0，没有消费记为NaN。用applymap()，lambda x:函数
pivoted_counts_transf = pivoted_counts.applymap(lambda x: 1 if x > 1 else np.NaN if x == 0 else 0)
print(pivoted_counts_transf.head())
# applymap(): 针对DataFrame里的所有数据。用lambda进行判断，因为这里涉及了多个结果，所以要两个if else，记住，lambda没有elif的用法。

# 3. 计算复购率；复购率：单位时间内，消费两次以及以上的用户数/购买总用户数
repurchase_rate = pivoted_counts_transf.sum()/pivoted_counts_transf.count()
repurchase_rate.plot(figsize=(10,4))
plt.xlabel('month')
plt.ylabel('percentage')
plt.title('repurchase rate per month')
# 用sum和cou单看新客和老客，复购率有三倍左右的差距nt相除即可计算出复购率。因为这两个函数都会忽略NaN，而NaN是没有消费的用户，count不论0还是1都会统计，所以是总的消费用户数，
# 而sum求和计算了两次以上的消费用户。这里用了比较巧妙的替代法计算复购率，SQL中也可以用。
# 图上可以看出复购率在早期，因为大量新用户加入的关系，新客的复购率并不高，譬如1月新客们的复购率只有6%左右。
# 而在后期，这时的用户都是大浪淘沙剩下的老客，复购率比较稳定，在20%左右。单看新客和老客，复购率有三倍左右的差距

# 4. 计算回购类率；回购率：上一个时间窗口内的消费用户，在下一个时间窗口仍消费的用户数/购买总用户数; 类似步骤1，2，3；
# 将消费金额进行数据透视，这里作为练习，使用了平均值。
pivoted_amount = df.pivot_table(index='order_id', columns='month', values='order_amount', aggfunc='mean').fillna(0)
pivoted_amount.columns = columns_month
print(pivoted_amount.head())

pivoted_amount_transf = pivoted_amount.applymap(lambda x: 1 if x > 0 else 0)
print(pivoted_amount_transf.head())
# 再次用applymap+lambda转换数据，只要有过购买，记为1，反之为0。

# 由于回购率涉及了横向跨时间窗口的对比，需要新建一个判断函数。data是输入的数据，即用户在18个月内是否消费的记录，status是空列表，后续用来保存用户是否回购的字段。
def purchase_return(data):
    temp = []
    for i in range (17):
        #若本月消费了
        if data[i] == 1:
            if data[i+1] == 1:
                temp.append(1)
            if data[i+1] == 0:
                temp.append(0)
        #若本月没有消费
        else:
            temp.append(np.NaN)
    temp.append(np.NaN)
    return pd.Series(temp, index=columns_month)

pivoted_purchase_return = pivoted_amount_transf.apply(purchase_return, axis=1) #用apply函数应用在所有行上，获得想要的结果
print(pivoted_purchase_return.head())
# 因为有18个月，所以每个月都要进行一次判断，需要用到循环。
# if的主要逻辑是，如果用户本月进行过消费，且下月消费过，记为1，没有消费过是0。本月若没有进行过消费，为NaN，后续的统计中进行排除。

purchase_return_rate = pivoted_purchase_return.sum()/pivoted_purchase_return.count()
purchase_return_rate.plot(figsize=(10,4))
plt.xlabel('month')
plt.ylabel('percentage')
plt.title('purchase return rate per month')
# 从图中可以看出，用户的回购率高于复购，约在30%左右，波动性也较强。新用户的回购率在15%左右，和老客差异不大。
# 将回购率和复购率综合分析，可以得出，新客的整体质量低于老客，老客的忠诚度（回购率）表现较好，消费频次稍次，这是CDNow网站的用户消费特征。




# 5) 用户消费行为分层分析; 计算回流用户比，活跃用户比
# 按照用户的消费行为，简单划分成几个维度：新用户、活跃用户、不活跃用户、回流用户
# 新用户的定义是第一次消费。活跃用户即老客，在某一个时间窗口内有过消费。不活跃用户则是时间窗口内没有消费过的老客。
# 回流用户是在上一个窗口中没有消费，而在当前时间窗口内有过消费。以上的时间窗口都是按月统计。
# 比如某用户在1月第一次消费，那么他在1月的分层就是新用户；他在2月消费国，则是活跃用户；3月没有消费，此时是不活跃用户；4月再次消费，此时是回流用户，5月还是消费，是活跃用户。

# 1.新建用户分层判断函数
def active_status(data):
    status=[]
    for i in range(18):
        #若本月没有消费
        if data[i]==0:
            #若本月不是第一个月
            if len(status)>0:
                #若上个月是为未注册用户，则为未注册用户
                if status[i-1]=='unreg':
                    status.append('unreg')
                #否则为不活跃用户
                else:
                    status.append('inactive')
            #若本月是第一个月，则为未注册用户
            else:
                status.append('unreg')

        #若本月消费了
        else:
            #若本月是第一个月，则为新用户
            if len(status)==0:
                status.append('new')
            #若本月不是第一个月，则为老用户
            else:
                #若上个月为不活跃用户，则为回流用户
                if status[i-1]=='inactive':
                    status.append('return')
                #若上个月为未注册用户，则为新客户
                elif status[i-1]=='unreg':
                    status.append('new')
                #否则为活跃用户
                else:
                    status.append('active')
    return pd.Series(status, index=columns_month)
# 主要分为两部分的判断，以本月是否消费为界。本月没有消费，还要额外判断他是不是新客，
# 因为部分用户是3月份才消费成为新客，那么在1、2月份他应该连新客都不是，用unreg表示。如果是老客，则为inactive。

# 2.使用用户分层函数来判断是否有消费的pivot table，并计算4个分层用户的数量

pivoted_purchase_status = pivoted_amount_transf.apply(active_status, axis=1)
print(pivoted_purchase_status.head())

purchase_status_counts = pivoted_purchase_status.replace('unreg', np.NaN).apply(lambda x:pd.value_counts(x))
print(purchase_status_counts)
# unreg状态排除掉，它是「未来」才作为新客，不能算在内。换算成不同分层每月的统计量。

purchase_status_counts.fillna(0).T.plot.area(figsize=(12,6))
# T.plot.are()面积图函数；因为它只是某时间段消费过的用户的后续行为，蓝色和灰色区域都可以不看。
# 只看紫色回流和红色活跃这两个分层，用户数比较稳定。这两个分层相加，就是消费用户占比（后期没新客）。

# 3. 计算回流占比 = 回流用户数 / 总用户数；活跃比率 = 活跃用户数 / 总用户数
# 回流占比；另外一种指标叫回流率，指【上个月】多少不活跃消费用户在本月活跃 / 消费。因为不活跃的用户总量近似不变，所以这里的回流率也近似回流占比。
plt.plot()

plt.subplot(121)
return_rate = purchase_status_counts.apply(lambda x: x/x.sum(), axis=1) #axis=1表示作用于行，axis=0，或者不写作用于列
return_rate.loc['return'].plot(figsize=(22,6))
plt.xlabel('month')
plt.ylabel('return rate')
plt.title('return rate per month')

plt.subplot(122)
return_rate = purchase_status_counts.apply(lambda x: x/x.sum(), axis=1)
return_rate.loc['active'].plot(figsize=(22,6))
plt.xlabel('month')
plt.ylabel('active rate')
plt.title('active rate per month')
# 用户回流占比在5%～8%，有下降趋势。
# 活跃用户的下降趋势更明显，占比在3%～5%间。这里用户活跃可以看作连续消费用户，质量在一定程度上高于回流用户。
# 结合回流用户和活跃用户看，在后期的消费用户中，60%是回流用户，40%是活跃用户/连续消费用户，整体质量还好，但是针对这两个分层依旧有改进的空间，可以继续细化数据。



# 6) 分析用户质量
# 1.消费金额累加
# 因为消费行为有明显的二八倾向，我们需要知道高质量用户为消费贡献了多少份额。使用cumsum（）累加函数。逐行计算累计的金额
user_amount = df.groupby('order_id').order_amount.sum().sort_values().reset_index()
user_amount['amount_cumsum'] = user_amount.order_amount.cumsum()
print(user_amount.tail())

# 转化成百分比
total_amount = user_amount.amount_cumsum.max()
user_amount['prop'] = user_amount.apply(lambda x: x.amount_cumsum/total_amount, axis=1)
print(user_amount.tail())

user_amount.prop.plot()
plt.xlabel('order_amount')
plt.ylabel('amount_cumsum')
plt.title('amount cumsum proprtion')
# 横坐标是按贡献金额大小排序而成，纵坐标则是用户累计贡献。可以很清楚的看到，前20000个用户贡献了40%的消费。后面4000位用户贡献了60%，确实呈现28倾向。
# 可以很清楚的看到，前20000个用户贡献了40%的消费。后面4000位用户贡献了60%，确实呈现28倾向。



# 2.用户生命周期；这里定义第一次消费至最后一次消费为整个用户生命
order_date_min = df.groupby('order_id').order_date.min()
order_date_max = df.groupby('order_id').order_date.max()

print((order_date_max - order_date_min).head(10))
print((order_date_max - order_date_min).mean())
# 所有用户的平均生命周期是134天，比预想的高，但是平均数不靠谱，还是看一下分布.

((order_date_max - order_date_min)/np.timedelta64(1, 'D')).hist(bins=15)
plt.xlabel('Days')
plt.ylabel('no. of users')
plt.title('life time cycle')

# 因为这里的数据类型是timedelta时间，它无法直接作出直方图，所以先换算成数值。
# 换算的方式直接除timedelta函数即可，这里的np.timedelta64(1, 'D')，D表示天，1表示1天，作为单位使用的。因为max-min已经表示为天了，两者相除就是周期的天数。

# 可以看到大部分用户只消费了一次，所有生命周期的大头都集中在了0天。但这不是我们想要的答案，不妨将只消费了一次的新客排除，来计算所有消费过两次以上的老客的生命周期。
lifetime = (order_date_max - order_date_min).reset_index() #通过reset_index()转化成dataframe
print(lifetime.head())

lifetime['life_time'] = lifetime.order_date/np.timedelta64(1, 'D')
lifetime[lifetime.life_time>0].life_time.hist(bins=100, figsize=(12, 6))
plt.xlabel('Days')
plt.ylabel('no. of users')
plt.title('regular customer life time cycle')
# 这个图比上面的靠谱多了，虽然仍旧有不少用户生命周期靠拢在0天。这是双峰趋势图。部分质量差的用户，虽然消费了两次，但是仍旧无法持续，
# 在用户首次消费30天内应该尽量引导。少部分用户集中在50天～300天，属于普通型的生命周期，高质量用户的生命周期，集中在400天以后，这已经属于忠诚用户了

print(lifetime[lifetime.life_time>0].life_time.mean())
# 消费两次以上的用户生命周期是276天，远高于总体。从策略看，用户首次消费后应该花费更多的引导其进行多次消费，提供生命周期，这会带来2.5倍的增量



# 3.留存率
# 留存率指用户在第一次消费后，有多少比率进行第二次消费。和回流率的区别是留存倾向于计算第一次消费，并且有多个时间窗口。
user_purchase = df[['order_id', 'order_product', 'order_amount', 'order_date']]
user_purchase_retention = pd.merge(left=user_purchase, right=order_date_min.reset_index(),
                                   how='inner', on='order_id', suffixes=('', '_min'))
print(user_purchase_retention.head())
# merge函数，它和SQL中的join差不多，用来将两个DataFrame进行合并。我们选择了inner 的方式，对标inner join。即只合并能对应得上的数据。
# 这里以on=user_id为对应标准。这里merge的目的是将用户消费行为和第一次消费时间对应上，形成一个新的DataFrame。suffxes参数是如果合并的内容中有重名column，加上后缀。


# 将order_date和order_date_min相减。获得一个新的列，为用户每一次消费距第一次消费的时间差值
user_purchase_retention['order_date_diff'] = user_purchase_retention.order_date - user_purchase_retention.order_date_min
print(user_purchase_retention.head())

date_transf = lambda x: x/np.timedelta64(1, 'D')
user_purchase_retention['date_diff'] = user_purchase_retention.order_date_diff.apply(date_transf)
print(user_purchase_retention.head())
# 将日期转化成时间数值

bin = [0, 3, 7, 15, 30, 60, 90, 180, 365]
user_purchase_retention['date_diff_bin'] = pd.cut(user_purchase_retention.date_diff,bins=bin)
print(user_purchase_retention.head(20))
# 下面将时间差值分桶。我这里分成0～3天内，3～7天内，7～15天等，代表用户当前消费时间距第一次消费属于哪个时间段呢
# 这里date_diff=0并没有被划分入0～3天，因为计算的是留存率，如果用户仅消费了一次，留存率应该是0。
# 另外一方面，如果用户第一天内消费了多次，但是往后没有消费，也算作留存率0。

pivoted_retention = user_purchase_retention.pivot_table(index='order_id', columns='date_diff_bin',
                                                        values='order_amount', aggfunc=sum, dropna= False)
print(pivoted_retention.head(10))
#用pivot_table数据透视，获得的结果是用户在第一次消费之后，在后续各时间段内的消费总额。

pivoted_retention.mean()
# 计算一下用户在后续各时间段的平均消费额，这里只统计有消费的平均值。虽然后面时间段的金额高，但是它的时间范围也宽广。
# 从平均效果看，用户第一次消费后的0～3天内，更可能消费更多。

# 用lambda和applymap将NaN转化成0，其余为1代表二次消费
pivoted_retention_transf = pivoted_retention.fillna(0).applymap(lambda x: 1 if x > 0 else 0)
print(pivoted_retention_transf.head())
# 计算留存率指用户在第一次消费后，有多少比率进行第二次消费
retention_rate = pivoted_retention_transf.sum()/pivoted_retention_transf.count()
retention_rate.plot.bar()
plt.xlabel('date_diff_bin')
plt.ylabel('percentage')
plt.title('retention rate')
# 只有2.5%的用户在第一次消费的次日至3天内有过消费，3%的用户在3～7天内有过消费。
# 数字并不好看，CD购买确实不是高频消费行为。时间范围放宽后数字好看了不少，有20%的用户在第一次消费后的三个月到半年之间有过购买，27%的用户在半年后至1年内有过购买。
# 从运营角度看，CD机营销在教育新用户的同时，应该注重用户忠诚度的培养，放长线掉大鱼，在一定时间内召回用户购买。




# 4.平均购买周期：用户的两次消费行为的时间间隔
# shift() - x.shift()是往上偏移一个位置，x.shift(-1)是往下偏移一个位置，加参数axis=1则是左右偏移
def diff(group):
    d = group.date_diff - group.date_diff.shift(-1)
    return d

last_diff = user_purchase_retention.groupby('order_id').apply(diff)
print(last_diff.head(10))

last_diff.mean()
# 用mean函数即可求出用户的平均消费间隔时间是68天。想要召回用户，在60天左右的消费间隔是比较好的。

last_diff.hist(bins=20)
plt.xlabel('days')
plt.ylabel('no. of customers')
plt.title('average purchase cycle')
# 如图所示，典型的长尾分布，大部分用户的消费间隔确实比较短。
# 不妨将时间召回点设为消费后立即赠送优惠券，消费后10天询问用户CD怎么样，消费后30天提醒优惠券到期，消费后60天短信推送。