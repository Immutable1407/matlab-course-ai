# 第1题 二分法求非线性方程根

## 题目

用二分法求方程

\[
x^3-x-1=0
\]

在区间 \([1,2]\) 内的实根。要求输出每次迭代的区间端点、中点、函数值和误差，并给出最终近似根。

## 代码

```matlab
clc; clear; close all;
format long

f = @(x) x.^3 - x - 1;

a = 1;
b = 2;
tol = 1e-8;
maxIter = 100;

if f(a)*f(b) > 0
    error('区间端点函数值同号，不能直接使用二分法');
end

fprintf(' k             a             b             c          f(c)        error\n');
fprintf('----------------------------------------------------------------------------\n');

for k = 1:maxIter
    c = (a+b)/2;
    fc = f(c);
    err = (b-a)/2;

    fprintf('%2d  %13.8f %13.8f %13.8f %13.4e %13.4e\n', ...
        k, a, b, c, fc, err);

    if abs(fc) < tol || err < tol
        break;
    end

    if f(a)*fc < 0
        b = c;
    else
        a = c;
    end
end

root = (a+b)/2;
fprintf('\n近似根 root = %.12f\n', root);
fprintf('函数值 f(root) = %.4e\n', f(root));
```

# 第2题 牛顿法求方程根

## 题目

用牛顿迭代法求方程

\[
\cos x - x = 0
\]

的近似根。取初值 \(x_0=0.5\)，输出迭代过程，并画出函数图像和根的位置。

## 代码

```matlab
clc; clear; close all;
format long

f = @(x) cos(x) - x;
df = @(x) -sin(x) - 1;

x = 0.5;
tol = 1e-10;
maxIter = 50;

fprintf(' k              x_k            f(x_k)          error\n');
fprintf('---------------------------------------------------------\n');

for k = 1:maxIter
    x_new = x - f(x)/df(x);
    err = abs(x_new - x);

    fprintf('%2d   %16.10f   %13.4e   %13.4e\n', ...
        k, x_new, f(x_new), err);

    x = x_new;
    if err < tol || abs(f(x)) < tol
        break;
    end
end

fprintf('\n近似根 root = %.12f\n', x);

xx = linspace(0, 1, 300);
plot(xx, f(xx), 'b-', 'LineWidth', 1.5);
hold on;
yline(0, 'k--');
plot(x, f(x), 'ro', 'MarkerSize', 8, 'LineWidth', 1.5);
grid on;
xlabel('x');
ylabel('f(x)');
title('Newton法求 cos(x)-x=0 的根');
```

# 第3题 割线法求方程根

## 题目

用割线法求方程

\[
e^{-x}-x=0
\]

的近似根。取初始点 \(x_0=0\)、\(x_1=1\)，输出每一步迭代结果。

## 代码

```matlab
clc; clear; close all;
format long

f = @(x) exp(-x) - x;

x0 = 0;
x1 = 1;
tol = 1e-10;
maxIter = 50;

fprintf(' k             x_k            f(x_k)          error\n');
fprintf('--------------------------------------------------------\n');

for k = 1:maxIter
    fx0 = f(x0);
    fx1 = f(x1);

    if abs(fx1 - fx0) < eps
        error('割线法分母过小，迭代失败');
    end

    x2 = x1 - fx1*(x1-x0)/(fx1-fx0);
    err = abs(x2 - x1);

    fprintf('%2d   %16.10f   %13.4e   %13.4e\n', ...
        k, x2, f(x2), err);

    x0 = x1;
    x1 = x2;

    if err < tol || abs(f(x1)) < tol
        break;
    end
end

fprintf('\n近似根 root = %.12f\n', x1);
```

# 第4题 拉格朗日插值

## 题目

已知数据点

\[
x=[0,1,2,3],\quad y=[1,2,0,5]
\]

编写 MATLAB 程序构造拉格朗日插值多项式，并计算 \(x=1.5\) 处的插值结果，同时绘制插值曲线和原始数据点。

## 代码

```matlab
clc; clear; close all;

x = [0 1 2 3];
y = [1 2 0 5];
x0 = 1.5;

n = length(x);
L = 0;

for i = 1:n
    li = 1;
    for j = 1:n
        if j ~= i
            li = li * (x0 - x(j))/(x(i) - x(j));
        end
    end
    L = L + y(i)*li;
end

fprintf('x = %.4f 处的拉格朗日插值结果 y = %.8f\n', x0, L);

xx = linspace(min(x), max(x), 300);
yy = zeros(size(xx));

for k = 1:length(xx)
    temp = 0;
    for i = 1:n
        li = 1;
        for j = 1:n
            if j ~= i
                li = li * (xx(k) - x(j))/(x(i) - x(j));
            end
        end
        temp = temp + y(i)*li;
    end
    yy(k) = temp;
end

plot(xx, yy, 'b-', 'LineWidth', 1.5);
hold on;
plot(x, y, 'ro', 'MarkerSize', 8, 'LineWidth', 1.5);
plot(x0, L, 'ks', 'MarkerSize', 8, 'LineWidth', 1.5);
grid on;
xlabel('x');
ylabel('y');
title('拉格朗日插值');
legend('插值曲线', '数据点', '插值点', 'Location', 'best');
```

# 第5题 三次样条插值

## 题目

给定数据

\[
x=[0,1,2,3,4],\quad y=[1,3,2,4,3]
\]

用三次样条插值计算 \(x=2.5\) 处的函数值，并绘制样条曲线和数据点。

## 代码

```matlab
clc; clear; close all;

x = [0 1 2 3 4];
y = [1 3 2 4 3];
x0 = 2.5;

y0 = spline(x, y, x0);

fprintf('x = %.4f 处的三次样条插值结果 y = %.8f\n', x0, y0);

xx = linspace(min(x), max(x), 400);
yy = spline(x, y, xx);

plot(xx, yy, 'b-', 'LineWidth', 1.5);
hold on;
plot(x, y, 'ro', 'MarkerSize', 8, 'LineWidth', 1.5);
plot(x0, y0, 'ks', 'MarkerSize', 8, 'LineWidth', 1.5);
grid on;
xlabel('x');
ylabel('y');
title('三次样条插值');
legend('样条曲线', '数据点', '插值点', 'Location', 'best');
```

# 第6题 最小二乘直线拟合

## 题目

已知实验数据

\[
x=[1,2,3,4,5,6],\quad y=[2.1,2.9,3.7,4.2,5.1,5.9]
\]

用最小二乘法拟合直线 \(y=ax+b\)，输出拟合参数、残差平方和，并绘制散点图和拟合直线。

## 代码

```matlab
clc; clear; close all;

x = [1 2 3 4 5 6]';
y = [2.1 2.9 3.7 4.2 5.1 5.9]';

X = [x, ones(size(x))];
coef = X \ y;

a = coef(1);
b = coef(2);
y_fit = a*x + b;

SSE = sum((y - y_fit).^2);

fprintf('拟合直线：y = %.6f x + %.6f\n', a, b);
fprintf('残差平方和 SSE = %.8f\n', SSE);

plot(x, y, 'ro', 'MarkerSize', 8, 'LineWidth', 1.5);
hold on;
plot(x, y_fit, 'b-', 'LineWidth', 1.5);
grid on;
xlabel('x');
ylabel('y');
title('最小二乘直线拟合');
legend('实验数据', '拟合直线', 'Location', 'best');
```

# 第7题 多项式拟合与误差分析

## 题目

对数据

\[
x=0:0.5:3,\quad y=\sin x+0.05[0,-1,1,0,1,-1,0]
\]

分别进行二次和三次多项式拟合，计算残差平方和，并比较拟合效果。

## 代码

```matlab
clc; clear; close all;

x = 0:0.5:3;
y = sin(x) + 0.05*[0 -1 1 0 1 -1 0];

p2 = polyfit(x, y, 2);
p3 = polyfit(x, y, 3);

y2 = polyval(p2, x);
y3 = polyval(p3, x);

SSE2 = sum((y - y2).^2);
SSE3 = sum((y - y3).^2);

fprintf('二次多项式系数：\n');
disp(p2);
fprintf('三次多项式系数：\n');
disp(p3);
fprintf('二次拟合 SSE = %.8f\n', SSE2);
fprintf('三次拟合 SSE = %.8f\n', SSE3);

xx = linspace(min(x), max(x), 400);
plot(x, y, 'ko', 'MarkerSize', 8, 'LineWidth', 1.5);
hold on;
plot(xx, polyval(p2, xx), 'b-', 'LineWidth', 1.5);
plot(xx, polyval(p3, xx), 'r--', 'LineWidth', 1.5);
grid on;
xlabel('x');
ylabel('y');
title('多项式拟合比较');
legend('数据点', '二次拟合', '三次拟合', 'Location', 'best');
```

# 第8题 数值微分误差比较

## 题目

对函数

\[
f(x)=e^x\sin x
\]

在 \(x=1\) 处分别用前向差分、后向差分和中心差分近似一阶导数。取不同步长 \(h=10^{-1},10^{-2},\ldots,10^{-6}\)，比较三种方法误差。

## 代码

```matlab
clc; clear; close all;
format long

f = @(x) exp(x).*sin(x);
df = @(x) exp(x).*(sin(x) + cos(x));

x0 = 1;
hList = 10.^(-(1:6));
exact = df(x0);

fprintf(' h          前向误差        后向误差        中心误差\n');
fprintf('--------------------------------------------------------\n');

errForward = zeros(size(hList));
errBackward = zeros(size(hList));
errCentral = zeros(size(hList));

for k = 1:length(hList)
    h = hList(k);

    dForward = (f(x0+h) - f(x0))/h;
    dBackward = (f(x0) - f(x0-h))/h;
    dCentral = (f(x0+h) - f(x0-h))/(2*h);

    errForward(k) = abs(dForward - exact);
    errBackward(k) = abs(dBackward - exact);
    errCentral(k) = abs(dCentral - exact);

    fprintf('%8.1e   %12.4e   %12.4e   %12.4e\n', ...
        h, errForward(k), errBackward(k), errCentral(k));
end

loglog(hList, errForward, 'o-', 'LineWidth', 1.5);
hold on;
loglog(hList, errBackward, 's-', 'LineWidth', 1.5);
loglog(hList, errCentral, '^-', 'LineWidth', 1.5);
grid on;
xlabel('h');
ylabel('绝对误差');
title('数值微分误差比较');
legend('前向差分', '后向差分', '中心差分', 'Location', 'best');
```

# 第9题 Jacobi迭代法解线性方程组

## 题目

用 Jacobi 迭代法求解线性方程组

\[
\begin{cases}
10x_1- x_2+2x_3=6,\\
-x_1+11x_2-x_3+3x_4=25,\\
2x_1-x_2+10x_3-x_4=-11,\\
3x_2-x_3+8x_4=15.
\end{cases}
\]

输出每次迭代的近似解和误差。

## 代码

```matlab
clc; clear; close all;
format long

A = [10 -1 2 0;
     -1 11 -1 3;
      2 -1 10 -1;
      0 3 -1 8];
b = [6; 25; -11; 15];

x = zeros(size(b));
tol = 1e-8;
maxIter = 100;

D = diag(diag(A));
R = A - D;

fprintf(' k              x1              x2              x3              x4          error\n');
fprintf('-----------------------------------------------------------------------------------\n');

for k = 1:maxIter
    x_new = D \ (b - R*x);
    err = norm(x_new - x, inf);

    fprintf('%2d   %14.8f  %14.8f  %14.8f  %14.8f  %12.4e\n', ...
        k, x_new(1), x_new(2), x_new(3), x_new(4), err);

    x = x_new;
    if err < tol
        break;
    end
end

fprintf('\nJacobi迭代解：\n');
disp(x);
fprintf('直接法解：\n');
disp(A\b);
```

# 第10题 四阶Runge-Kutta法求解微分方程

## 题目

用四阶 Runge-Kutta 方法求解初值问题

\[
y'=x+y,\qquad y(0)=1
\]

在区间 \([0,1]\) 上的数值解，步长 \(h=0.1\)，输出数值结果并绘制解曲线。

## 代码

```matlab
clc; clear; close all;

f = @(x,y) x + y;

a = 0;
b = 1;
h = 0.1;
x = a:h:b;
y = zeros(size(x));
y(1) = 1;

for i = 1:length(x)-1
    k1 = f(x(i), y(i));
    k2 = f(x(i)+h/2, y(i)+h*k1/2);
    k3 = f(x(i)+h/2, y(i)+h*k2/2);
    k4 = f(x(i)+h, y(i)+h*k3);

    y(i+1) = y(i) + h*(k1 + 2*k2 + 2*k3 + k4)/6;
end

fprintf('    x           y_RK4\n');
fprintf('------------------------\n');
for i = 1:length(x)
    fprintf('%8.4f   %12.8f\n', x(i), y(i));
end

plot(x, y, 'bo-', 'LineWidth', 1.5);
grid on;
xlabel('x');
ylabel('y');
title('四阶Runge-Kutta法求解初值问题');
```
