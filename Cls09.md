# 第1题

## 题目

分别用随机投点法和均值估计法估计积分

\[
\int_0^\pi \left(3\sin x^2-\sqrt{1+x^2}\right)\,dx
\]

并进行正态性检验和均值检验。

## 代码

```matlab
clc; clear; close all;

f = @(x) 3*sin(x.^2) - sqrt(1+x.^2);
a = 0;
b = pi;

N = 10000;
M = 10;

x = linspace(a,b,1000);
y = f(x);

figure;
plot(x,y,'LineWidth',1.5);
grid on;
xlabel('x');
ylabel('f(x)');
title('被积函数图像');

mu = integral(f,a,b);

I_mean = zeros(M,1);
I_hit = zeros(M,1);

fmin = min(y);
fmax = max(y);

for k = 1:M
    xr = a + (b-a)*rand(N,1);

    I_mean(k) = (b-a)*mean(f(xr));

    xp = a + (b-a)*rand(N,1);
    yp = fmin + (fmax-fmin)*rand(N,1);
    fxp = f(xp);

    area_box = (b-a)*(fmax-fmin);
    I_hit(k) = area_box*mean(yp <= fxp) + (b-a)*fmin;
end

disp('均值估计法10次结果：');
disp(I_mean);

disp('随机投点法10次结果：');
disp(I_hit);

[h1,p1] = lillietest(I_mean);
[h2,p2] = lillietest(I_hit);

fprintf('均值估计法正态性检验：h=%d, p=%.6f\n',h1,p1);
fprintf('随机投点法正态性检验：h=%d, p=%.6f\n',h2,p2);

[h3,p3,ci3,stats3] = ttest(I_mean,mu);
[h4,p4,ci4,stats4] = ttest(I_hit,mu);

fprintf('均值估计法均值检验：h=%d, p=%.6f\n',h3,p3);
fprintf('随机投点法均值检验：h=%d, p=%.6f\n',h4,p4);
```

# 第2题

## 题目

某食品公司推出集卡活动，卡片上有“恭”“喜”“发”“财”四种图案，集齐四种图案即为成功。分别模拟四类卡片等概率和不等概率时，集齐四类卡片需要购买食品包数的期望。

## 代码

```matlab
clc; clear; close all;

N = 100000;

p1 = [1/4 1/4 1/4 1/4];
E1 = couponSim(p1,N);

fprintf('四类卡片等概率时，期望购买包数约为 %.4f\n',E1);

p2 = [0.1 0.3 0.3 0.3];
E2 = couponSim(p2,N);

fprintf('四类卡片概率为[0.1,0.3,0.3,0.3]时，期望购买包数约为 %.4f\n',E2);

function E = couponSim(p,N)

cnt = zeros(N,1);

for i = 1:N
    have = zeros(1,4);
    k = 0;

    while sum(have) < 4
        u = rand;
        cp = cumsum(p);
        card = find(u <= cp,1);

        have(card) = 1;
        k = k + 1;
    end

    cnt(i) = k;
end

E = mean(cnt);

end
```

# 第3题

## 题目

对给定回归数据：

|序号|Y|x1|x2|
|---|---|---|---|
|1|9.08|-1.49|4.01|
|2|46.6|1.65|5.43|
|3|35.52|1.61|3.84|
|4|9.16|-0.06|2.31|
|5|47.55|2.27|3.82|
|6|75.43|2.83|5.47|
|7|4.31|0.43|0.11|
|8|121.12|5.04|2.89|
|9|196.03|6.71|3.36|

分别作散点图，建立二元线性回归模型和完全二次回归模型，并用逐步回归精简模型。

## 代码

```matlab
clc; clear; close all;

Y  = [9.08 46.6 35.52 9.16 47.55 75.43 4.31 121.12 196.03]';
x1 = [-1.49 1.65 1.61 -0.06 2.27 2.83 0.43 5.04 6.71]';
x2 = [4.01 5.43 3.84 2.31 3.82 5.47 0.11 2.89 3.36]';

figure;
scatter(x1,Y,'filled');
grid on;
xlabel('x1');
ylabel('Y');
title('Y关于x1的散点图');

figure;
scatter(x2,Y,'filled');
grid on;
xlabel('x2');
ylabel('Y');
title('Y关于x2的散点图');

n = length(Y);

X1 = [ones(n,1),x1,x2];
[b1,bint1,r1,rint1,stats1] = regress(Y,X1,0.05);

disp('二元线性回归参数：');
disp(b1);
disp('二元线性回归统计量：');
disp(stats1);

figure;
rcoplot(r1,rint1);
title('二元线性回归残差图');

X2 = [ones(n,1),x1,x2,x1.*x2,x1.^2,x2.^2];
[b2,bint2,r2,rint2,stats2] = regress(Y,X2,0.05);

disp('完全二次回归参数：');
disp(b2);
disp('完全二次回归统计量：');
disp(stats2);

figure;
rcoplot(r2,rint2);
title('完全二次回归残差图');

X = [x1,x2,x1.*x2,x1.^2,x2.^2];
stepwise(X,Y);
```

# 第4题

## 题目

某公司未来三年内有3000万元资金用于投资。每年年初可以投资，任意一年投资 \(x\) 万元会在第三年年底收回资金并获得 \(8\sqrt{x}\) 万元投资收益。未投资资金可存入银行，并在当年年底获得8%的利息，银行本息可用于下一年投资。求如何使用资金才能在第三年年底获得最大投资收益。

## 代码

```matlab
clc; clear;

money0 = 3000;
r = 0.08;

fun = @(x) -(8*sqrt(x(1)) + 8*sqrt(x(2)) + 8*sqrt(x(3)));

A = [1 0 0;
     -1 1/(1+r) 0;
     -1 0 1/(1+r)^2];

b = [money0;
     0;
     0];

lb = [0 0 0];
ub = [];

x0 = [1000 1000 1000];

[xopt,fval] = fmincon(fun,x0,A,b,[],[],lb,ub);

maxIncome = -fval;

fprintf('第一年投资 %.4f 万元\n',xopt(1));
fprintf('第二年投资 %.4f 万元\n',xopt(2));
fprintf('第三年投资 %.4f 万元\n',xopt(3));
fprintf('最大投资收益 %.4f 万元\n',maxIncome);
```

# 第5题

## 题目

舰艇甲向位于其正东方1km处的舰艇乙发射导弹。舰艇乙以最大速度 \(v=15m/s\) 向东北方向直线逃离，导弹头始终对准舰艇乙，速度为 \(w\)。

1. 当 \(w=180m/s\) 时，绘制导弹运行曲线并估计导弹击中舰艇乙的时间。
2. 若导弹在2.5秒后击中舰艇乙，绘制导弹飞行轨迹并估计飞行距离。

## 代码

```matlab
clc; clear; close all;

v = 15;
w = 180;

xB0 = 1000;
yB0 = 0;

dir = [1,1]/sqrt(2);

f = @(t,z)[
    w*(xB0 + v*dir(1)*t - z(1)) / sqrt((xB0 + v*dir(1)*t - z(1))^2 + (yB0 + v*dir(2)*t - z(2))^2);
    w*(yB0 + v*dir(2)*t - z(2)) / sqrt((xB0 + v*dir(1)*t - z(1))^2 + (yB0 + v*dir(2)*t - z(2))^2)
];

[t,z] = ode45(f,[0,20],[0,0]);

xB = xB0 + v*dir(1)*t;
yB = yB0 + v*dir(2)*t;

d = sqrt((xB-z(:,1)).^2 + (yB-z(:,2)).^2);
idx = find(d < 1,1);

if ~isempty(idx)
    hitTime = t(idx);
else
    hitTime = NaN;
end

figure;
plot(z(:,1),z(:,2),'r','LineWidth',1.5);
hold on;
plot(xB,yB,'b--','LineWidth',1.2);
grid on;
axis equal;
xlabel('x/m');
ylabel('y/m');
title('w=180m/s时导弹追踪轨迹');
legend('导弹轨迹','舰艇乙轨迹');

fprintf('w=180m/s时击中时间约为 %.4f 秒\n',hitTime);

T = 2.5;

targetFun = @(ww) missDistance(ww,T,v,xB0,yB0,dir);

w2 = fzero(targetFun,[100,1000]);

f2 = @(t,z)[
    w2*(xB0 + v*dir(1)*t - z(1)) / sqrt((xB0 + v*dir(1)*t - z(1))^2 + (yB0 + v*dir(2)*t - z(2))^2);
    w2*(yB0 + v*dir(2)*t - z(2)) / sqrt((xB0 + v*dir(1)*t - z(1))^2 + (yB0 + v*dir(2)*t - z(2))^2)
];

[t2,z2] = ode45(f2,[0,T],[0,0]);

dist = sum(sqrt(diff(z2(:,1)).^2 + diff(z2(:,2)).^2));

figure;
plot(z2(:,1),z2(:,2),'r','LineWidth',1.5);
grid on;
axis equal;
xlabel('x/m');
ylabel('y/m');
title('2.5秒击中时导弹飞行轨迹');

fprintf('2.5秒击中时导弹速度约为 %.4f m/s\n',w2);
fprintf('导弹飞行距离约为 %.4f m\n',dist);

function d = missDistance(w,T,v,xB0,yB0,dir)

f = @(t,z)[
    w*(xB0 + v*dir(1)*t - z(1)) / sqrt((xB0 + v*dir(1)*t - z(1))^2 + (yB0 + v*dir(2)*t - z(2))^2);
    w*(yB0 + v*dir(2)*t - z(2)) / sqrt((xB0 + v*dir(1)*t - z(1))^2 + (yB0 + v*dir(2)*t - z(2))^2)
];

[~,z] = ode45(f,[0,T],[0,0]);

xBT = xB0 + v*dir(1)*T;
yBT = yB0 + v*dir(2)*T;

d = sqrt((z(end,1)-xBT)^2 + (z(end,2)-yBT)^2);

end
```