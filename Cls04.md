# 第1题

## 题目

### (1)

在同一图形窗口中画出

\[
N(0,1),\quad N(0,4)
\]

的分布函数图。

### (2)

在同一图形上画出

\[
\chi^2(5),\quad \chi^2(8)
\]

的密度函数图像。

## 代码

### (1)

```matlab
clear; clc; close all;

x = -6:0.01:6;

F1 = normcdf(x, 0, 1);
F2 = normcdf(x, 0, 2);

plot(x, F1, 'b', 'LineWidth', 1.5);
hold on;
plot(x, F2, 'r', 'LineWidth', 1.5);
grid on;

legend('N(0,1)', 'N(0,4)', 'Location', 'best');
title('N(0,1)与N(0,4)的分布函数图');
xlabel('x');
ylabel('F(x)');
hold off;
```

### (2)

```matlab
clear; clc; close all;

x = 0:0.01:25;

y1 = chi2pdf(x, 5);
y2 = chi2pdf(x, 8);

plot(x, y1, 'b', 'LineWidth', 1.5);
hold on;
plot(x, y2, 'r', 'LineWidth', 1.5);
grid on;

legend('\chi^2(5)', '\chi^2(8)', 'Location', 'best');
title('\chi^2(5)与\chi^2(8)的密度函数图');
xlabel('x');
ylabel('p(x)');
hold off;
```

# 第2题

## 题目

某班概率统计课程的考试成绩如下：

\[
\begin{aligned}
&93,75,83,93,91,85,84,82,77,76,77,95,94,89,91,88,86,83,96,81,79,97,\\
&78,75,67,69,68,84,83,81,75,66,85,70,94,84,83,82,80,78,74,73,76,70,\\
&86,76,90,89,71,66,86,73,80,94,79,78,77,63,53,55.
\end{aligned}
\]

作直方图并附加其核密度估计曲线，计算均值、标准差、极差、偏度、峰度。

## 代码

```matlab
clear; clc; close all;

X = [93 75 83 93 91 85 84 82 77 76 77 95 94 89 91 88 86 83 96 81 79 97 ...
     78 75 67 69 68 84 83 81 75 66 85 70 94 84 83 82 80 78 74 73 76 70 ...
     86 76 90 89 71 66 86 73 80 94 79 78 77 63 53 55];

histogram(X, 'Normalization', 'pdf', 'NumBins', 8);
hold on;

[f, xi] = ksdensity(X);
plot(xi, f, 'r', 'LineWidth', 1.5);

grid on;
title('考试成绩直方图及核密度估计曲线');
xlabel('成绩');
ylabel('概率密度');
legend('直方图', '核密度估计', 'Location', 'best');
hold off;

x_mean = mean(X)
x_std  = std(X)
x_range = range(X)
x_skew = skewness(X)
x_kurt = kurtosis(X)
```

# 第3题

## 题目

编写一个函数寻找二项分布的概率最大项。函数输入参数为二项分布参数 \(n\) 和 \(p\)，输出结果显示为：

“二项分布 \(B(n,p)\) 的概率最大项为第？项，概率值为？。”

## 代码

```matlab
clear; clc;

binom_max_item(10, 0.3)

function binom_max_item(n, p)

k = 0:n;
prob = binopdf(k, n, p);

[maxProb, idx] = max(prob);
maxItem = k(idx);

fprintf('二项分布 B(%d, %.4f) 的概率最大项为第 %d 项，概率值为 %.6f。\n', ...
        n, p, maxItem, maxProb);
end
```

# 第4题

## 题目

设随机变量 \(X\) 的分布函数为

\[
F(x)=
\begin{cases}
0, & x<0,\\
\dfrac{x^2}{4}, & 0\le x<2,\\
1, & x\ge 2.
\end{cases}
\]

试用 MATLAB 编写函数，分别计算该随机变量在 \(x\) 点处的分布函数值和密度函数值。函数的输入参数为 \(x\)，输出参数为 \(f\)，函数名分别为 `Xcdf` 和 `Xpdf`，其中 \(x\) 可以是向量。

## 代码

```matlab
clear; clc;

x = [-1 0 0.5 1 1.5 2 3];

F = Xcdf(x)
P = Xpdf(x)

function f = Xcdf(x)

f = zeros(size(x));

f(x < 0) = 0;
f(x >= 0 & x < 2) = x(x >= 0 & x < 2).^2 / 4;
f(x >= 2) = 1;

end

function f = Xpdf(x)

f = zeros(size(x));

f(x >= 0 & x < 2) = x(x >= 0 & x < 2) / 2;
f(x < 0 | x >= 2) = 0;

end
```

# 第5题

## 题目

设二维随机变量 \((X,Y)\) 服从二维正态分布，均值向量为

\[
\mu=[0,0]
\]

协方差矩阵为

\[
\Sigma=
\begin{pmatrix}
1 & 1\\
1 & 3
\end{pmatrix}.
\]

分别画出 \((X,Y)\) 的联合分布函数及联合概率密度图形。

## 代码

```matlab
clear; clc; close all;

mu = [0 0];
Sigma = [1 1; 1 3];

[X, Y] = meshgrid(-4:0.1:4, -6:0.1:6);
xy = [X(:), Y(:)];

pdf_val = mvnpdf(xy, mu, Sigma);
PDF = reshape(pdf_val, size(X));

figure;
surf(X, Y, PDF);
shading interp;
grid on;
title('二维正态分布的联合概率密度图');
xlabel('x');
ylabel('y');
zlabel('f(x,y)');

cdf_val = mvncdf(xy, mu, Sigma);
CDF = reshape(cdf_val, size(X));

figure;
surf(X, Y, CDF);
shading interp;
grid on;
title('二维正态分布的联合分布函数图');
xlabel('x');
ylabel('y');
zlabel('F(x,y)');
```

# 第6题

## 题目

在路灯更换问题中，考虑没坏的灯泡还有回收价值，建立相应的数学模型并求出更换周期的表达式。

灯泡寿命服从正态分布

\[
N(4000,100^2),
\]

其中

\[
\mu=4000,\qquad \sigma=100.
\]

每个灯泡的安装价格是 70 元，管理部门对不亮灯泡的惩罚费用为 \(0.02\) 元/h，每个未坏灯泡的回收价为 5 元，计算最佳更换周期。

## 代码

```matlab
clear; clc; close all;

mu = 4000;
sigma = 100;
a = 70;
b = 0.02;
c = 5;

costfun = @(T) ( a - c*(1 - normcdf(T, mu, sigma)) + ...
    b * integral(@(x) (T - x).*normpdf(x, mu, sigma), -Inf, T) ) ./ T;

[T_opt, minCost] = fminbnd(costfun, 3500, 4500);

fprintf('最佳更换周期 T = %.4f 小时\n', T_opt);
fprintf('对应的最小单位时间平均成本 = %.6f 元/小时\n', minCost);

T = 3500:1:4500;
G = arrayfun(costfun, T);

figure;
plot(T, G, 'LineWidth', 1.5);
grid on;
hold on;
plot(T_opt, minCost, 'ro', 'MarkerSize', 8, 'LineWidth', 1.5);
title('考虑回收价值时的单位时间平均成本函数');
xlabel('更换周期 T（小时）');
ylabel('单位时间平均成本');
legend('G(T)', '最优点', 'Location', 'best');
hold off;
```