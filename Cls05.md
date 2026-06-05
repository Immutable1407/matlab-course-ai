# 第1题

## 题目

用蒙特卡洛方法计算下列函数在给定区间上的积分，并改变随机点数目观察对结果的影响。

### (1)

\[
y=e^{3x}\sin 2x,\qquad 0\le x\le 2
\]

### (2)

\[
y=\frac{1}{\sqrt{2\pi}}e^{-x^2/2},\qquad -2\le x\le 2
\]

## 代码

### (1)

```matlab
clear; clc;

f = @(x) sin(x.^2);
a = 0;
b = 2;

Nlist = [100, 500, 1000, 5000, 10000, 50000];
I_mc = zeros(size(Nlist));

for k = 1:length(Nlist)
    n = Nlist(k);
    x = a + (b-a) * rand(1, n);
    I_mc(k) = (b-a) * mean(f(x));
end

I_true = integral(f, a, b);

fprintf('理论参考值 = %.8f\n\n', I_true);

for k = 1:length(Nlist)
    fprintf('n = %-6d  Monte Carlo估计 = %.8f  误差 = %.8e\n', ...
        Nlist(k), I_mc(k), abs(I_mc(k) - I_true));
end

figure;
plot(Nlist, I_mc, 'o-', 'LineWidth', 1.5);
hold on;
yline(I_true, 'r--', 'LineWidth', 1.5);
xlabel('随机点数 n');
ylabel('积分估计值');
title('\int_0^2 sin(x^2) dx 的蒙特卡洛估计');
legend('Monte Carlo估计', '参考值');
grid on;
```

### (2)

```matlab
clear; clc;

f = @(x) exp(-x.^2 / 2);
a = -2;
b = 2;

Nlist = [100, 500, 1000, 5000, 10000, 50000];
I_mc = zeros(size(Nlist));

for k = 1:length(Nlist)
    n = Nlist(k);
    x = a + (b-a) * rand(1, n);
    I_mc(k) = (b-a) * mean(f(x));
end

I_true = integral(f, a, b);

fprintf('理论参考值 = %.8f\n\n', I_true);

for k = 1:length(Nlist)
    fprintf('n = %-6d  Monte Carlo估计 = %.8f  误差 = %.8e\n', ...
        Nlist(k), I_mc(k), abs(I_mc(k) - I_true));
end

figure;
plot(Nlist, I_mc, 'o-', 'LineWidth', 1.5);
hold on;
yline(I_true, 'r--', 'LineWidth', 1.5);
xlabel('随机点数 n');
ylabel('积分估计值');
title('\int_{-2}^2 e^{-x^2/2} dx 的蒙特卡洛估计');
legend('Monte Carlo估计', '参考值');
grid on;
```

# 第2题

## 题目

冰淇淋的下部为锥体，上部为半球。设它由锥面

\[
z=\sqrt{x^2+y^2}
\]

和半球面

\[
x^2+y^2+(z-1)^2=1
\]

组成，用蒙特卡洛方法计算它的体积。

## 代码

```matlab
clear; clc;

n = 2e5;

xmin = -1; xmax = 1;
ymin = -1; ymax = 1;
zmin = 0;  zmax = sqrt(2);

x = xmin + (xmax - xmin) * rand(1, n);
y = ymin + (ymax - ymin) * rand(1, n);
z = zmin + (zmax - zmin) * rand(1, n);

r = sqrt(x.^2 + y.^2);

in_cone = (z >= 0) & (z <= 1) & (r <= z);
in_hemi = (z >= 1) & (z <= sqrt(2)) & (x.^2 + y.^2 + z.^2 <= 2);

inside = in_cone | in_hemi;

V_box = (xmax-xmin) * (ymax-ymin) * (zmax-zmin);
V_mc = V_box * mean(inside);

V_true = pi/3 + integral(@(z) pi*(2-z.^2), 1, sqrt(2));

fprintf('Monte Carlo估计体积 = %.8f\n', V_mc);
fprintf('理论参考体积       = %.8f\n', V_true);
fprintf('绝对误差           = %.8e\n', abs(V_mc - V_true));
```

# 第3题

## 题目

设炮弹射击的目标为半径为 \(100m\) 的圆形区域，弹着点以圆心为中心服从二维正态分布。两个分量的标准差分别为 \(80m\) 和 \(50m\)，相关系数为 \(0.4\)。用蒙特卡洛方法求炮弹命中圆形区域的概率。

## 代码

```matlab
clear; clc;

n = 2e5;

mu = [0, 0];
sigma_x = 80;
sigma_y = 50;
rho = 0.4;

Sigma = [sigma_x^2, rho*sigma_x*sigma_y;
         rho*sigma_x*sigma_y, sigma_y^2];

XY = mvnrnd(mu, Sigma, n);
x = XY(:,1);
y = XY(:,2);

R = 100;
hit = (x.^2 + y.^2 <= R^2);

P_mc = mean(hit);

fprintf('Monte Carlo估计命中概率 = %.8f\n', P_mc);
```

# 第4题

## 题目

在一场舞会开始时，舞池中有 20 个女孩和 22 个男孩，舞池外还有无穷多等待入场的女孩和男孩。规则如下：

- 每一轮中，若选出的是女孩，则邀请一位女孩和一位男孩入场跳三人舞，舞曲结束后三人均留在舞池内；
- 若选出的是男孩，则邀请一位舞池中的女孩跳双人舞，曲子结束后双双离场；
- 当舞池中只剩两个男孩时舞会结束。

求舞会平均会进行多少轮才会终止，并用蒙特卡洛模拟法估计该均值。

## 代码

```matlab
clear; clc;

Nsim = 50000;
rounds = zeros(Nsim, 1);

for s = 1:Nsim
    girls = 20;
    boys  = 22;
    cnt = 0;

    while ~(girls == 0 && boys == 2)
        total = girls + boys;
        u = rand;

        if u < girls / total
            girls = girls + 1;
            boys  = boys + 1;
        else
            girls = girls - 1;
            boys  = boys - 1;
        end

        cnt = cnt + 1;
    end

    rounds(s) = cnt;
end

avg_rounds = mean(rounds);

fprintf('Monte Carlo估计均值 = %.8f\n', avg_rounds);
fprintf('样本标准差         = %.8f\n', std(rounds));
```

# 第5题

## 题目

一列火车大约在下午 1 点离开 \(A\) 站，其离站时间分布为：

| 离站时间 | 13:00 | 13:05 | 13:10 |
|---|---|---|---|
| 概率 | 0.7 | 0.2 | 0.1 |

火车从 \(A\) 到 \(B\) 途中所需时间服从均值为 30 分、标准差为 2 分钟的正态分布。若要赶的是这趟火车的下一站 \(B\)，到达 \(B\) 站的时间分布为：

| 时间 | 13:28 | 13:30 | 13:32 | 13:34 |
|---|---|---|---|---|
| 概率 | 0.3 | 0.4 | 0.2 | 0.1 |

求能赶上这列火车的概率，并用随机模拟方法设计实验计算结果。

## 代码

```matlab
clear; clc;

n = 2e5;
success = 0;

for i = 1:n
    u1 = rand;

    if u1 < 0.7
        t1 = 0;
    elseif u1 < 0.9
        t1 = 5;
    else
        t1 = 10;
    end

    t2 = normrnd(30, 2);

    u3 = rand;

    if u3 < 0.3
        t3 = 28;
    elseif u3 < 0.7
        t3 = 30;
    elseif u3 < 0.9
        t3 = 32;
    else
        t3 = 34;
    end

    if t3 < t1 + t2
        success = success + 1;
    end
end

P_mc = success / n;

fprintf('Monte Carlo估计概率 = %.8f\n', P_mc);
```