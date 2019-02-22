# TexasHoldem
## 游戏流程bug
1. [service] startGame 和 每轮次的用户存活检测，active_player更新的有问题
2. [service,frontend] 操作校验。
    - raise 限制：bet 必须高于当前最大值
    - check 条件：当前 bet 必须与上个人相等
    - 继续斟酌

## 需求池
1. [service] 用户标志结构，有条件加数据库
2. [frontend] ui优化，加扑克牌图
3. [service] 加 allin 边池，结算算法优化
4. [service,frontend] 登陆信息用 cookie 保存，v0.1登陆信息暂存页面中，关闭页面用户状态会丢失，不科学
5. [service] 加离线重连
6. [model] 加最高押注上限
6. [model] 返回json隐藏其他玩家的手牌
