# 第1题

## 题目

求解如下线性规划问题：

\[
\begin{cases}
\min f(x)=6x_1+12x_2,\\
x_1+3x_2\ge 7,\\
3x_1-x_2\le 4,\\
x_1,x_2\ge 0.
\end{cases}
\]

## 代码

```matlab
clc; clear;

c = [6; 12];

A = [-1 -3;
      3 -1];
b = [-7; 4];

Aeq = [];
beq = [];

lb = [0; 0];
ub = [];

[x, fval] = linprog(c, A, b, Aeq, beq, lb, ub);

disp('最优解 x = ');
disp(x);
disp('最优值 fval = ');
disp(fval);
```

# 第2题

## 题目

求函数

\[
f(x)=x^2\sin x
\]

在区间 \([-10,10]\) 内的极大值点和极小值点，并通过函数图像体会局部极小值的含义。

## 代码

```matlab
clc; clear; close all;

f = @(x) x.^2 .* sin(x);

fplot(f, [-10, 10], 'LineWidth', 1.5);
grid on;
xlabel('x');
ylabel('f(x)');
title('f(x) = x^2 sin(x) 在 [-10,10] 上的图像');
hold on;

[xmin, fmin] = fminbnd(f, -10, 10);

[xmax, yval] = fminbnd(@(x) -f(x), -10, 10);
fmax = -yval;

plot(xmin, fmin, 'ro', 'MarkerSize', 8, 'LineWidth', 1.5);
plot(xmax, fmax, 'bo', 'MarkerSize', 8, 'LineWidth', 1.5);

legend('f(x)', '极小值点', '极大值点');

disp('全局极小值点 xmin = ');
disp(xmin);
disp('对应函数值 fmin = ');
disp(fmin);

disp('全局极大值点 xmax = ');
disp(xmax);
disp('对应函数值 fmax = ');
disp(fmax);
```

# 第3题

## 题目

求解无约束优化问题：

\[
\min f(x)=
(4x_1^2+2x_2^2+4x_1x_2+2x_2+1)e^{x_1}.
\]

## 代码

```matlab
clc; clear;

fun = @(x) (4*x(1)^2 + 2*x(2)^2 + 4*x(1)*x(2) + 2*x(2) + 1) * exp(x(1));

x0 = [-1; 1];

[x, fval] = fminunc(fun, x0);

disp('最优解 x = ');
disp(x);
disp('最优值 fval = ');
disp(fval);
```

# 第4题

## 题目

求解如下约束优化问题：

\[
\begin{cases}
\min f(x)=-x_1x_2x_3,\\
0\le x_1+2x_2+3x_3\le 72,
\end{cases}
\]

初始点为

\[
[10,10,10].
\]

## 代码

```matlab
clc; clear;

fun = @(x) -x(1)*x(2)*x(3);

x0 = [10; 10; 10];

A = [1 2 3];
b = 72;

Aeq = [];
beq = [];

lb = [0; 0; 0];
ub = [];

[x, fval] = fmincon(fun, x0, A, b, Aeq, beq, lb, ub);

disp('最优解 x = ');
disp(x);
disp('最优值 fval = ');
disp(fval);
```

# 第5题

## 题目

求解指派问题例题。

## 代码

```matlab
clc; clear;

C = [3  8  2 10  3;
     8  7  2  9  7;
     6  4  2  7  5;
     8  4  2  3  5;
     9 10  6  9 10];

c = C(:);

intcon = 1:25;

Aeq1 = zeros(5,25);
for i = 1:5
    Aeq1(i, (i-1)*5+1 : i*5) = 1;
end

Aeq2 = zeros(5,25);
for j = 1:5
    for i = 1:5
        Aeq2(j, (i-1)*5+j) = 1;
    end
end

Aeq = [Aeq1; Aeq2];
beq = ones(10,1);

A = [];
b = [];

lb = zeros(25,1);
ub = ones(25,1);

[x, fval] = intlinprog(c, intcon, A, b, Aeq, beq, lb, ub);

X = reshape(round(x), 5, 5);

disp('指派矩阵 X = ');
disp(X);
disp('最小总时间 = ');
disp(fval);

disp('具体安排如下：');
for i = 1:5
    j = find(X(i,:) == 1);
    fprintf('人员%d -> 任务%d\n', i, j);
end
```

# 第6题

## 题目

写出供应与选址问题最后一个模型的 MATLAB 文件 `xuanzhif3.m` 和调用程序。

## 代码

```matlab
clc; clear;

x0 = [1;1;1;1;1;1; 2;2; 6;6];

A = [ 1 1 1 1 1 1 0 0 0 0;
     -1 -1 -1 -1 -1 -1 0 0 0 0];
b = [20; -16];

Aeq = [];
beq = [];

lb = [0;0;0;0;0;0; 0;0;0;0];

ub = [3;5;4;7;6;11; inf;inf;inf;inf];

[x, fval] = fmincon(@xuanzhif3, x0, A, b, Aeq, beq, lb, ub);

disp('最优解 x = ');
disp(x);

disp('最小吨公里数 = ');
disp(fval);

disp('1号料场位置 (s1,t1) = ');
disp([x(7), x(8)]);

disp('2号料场位置 (s2,t2) = ');
disp([x(9), x(10)]);

d = [3 5 4 7 6 11];

disp('1号料场供给量 = ');
disp(x(1:6)');

disp('2号料场供给量 = ');
disp((d - x(1:6)') );

function f = xuanzhif3(x)

a = [1.25, 8.75, 0.50, 5.75, 3.00, 7.25];
b = [1.25, 0.75, 4.75, 5.00, 6.50, 7.75];

d = [3, 5, 4, 7, 6, 11];

f = 0;

for i = 1:6
    dist1 = sqrt((x(7) - a(i))^2 + (x(8) - b(i))^2);
    dist2 = sqrt((x(9) - a(i))^2 + (x(10) - b(i))^2);

    f = f + x(i)*dist1 + (d(i)-x(i))*dist2;
end

end
```

# 第7题

## 题目

黄金分割法也称 0.618 法。根据给定算法步骤写出算法程序，并任选一个一元函数利用该程序求极值。

## 代码

```matlab
clc; clear; close all;

fun = @(x) x.^2 - 4*x + 5;

a = 0;
b = 5;
tol = 1e-6;
maxit = 200;

[xopt, fopt, k] = gold618(fun, a, b, tol, maxit);

fprintf('最优点 x = %.8f\n', xopt);
fprintf('最优值 f(x) = %.8f\n', fopt);
fprintf('迭代次数 k = %d\n', k);

fplot(fun, [a,b], 'LineWidth', 1.5);
grid on; hold on;
plot(xopt, fopt, 'ro', 'MarkerSize', 8, 'LineWidth', 1.5);
title('黄金分割法求极小值');
xlabel('x');
ylabel('f(x)');

function [xopt, fopt, k] = gold618(fun, a, b, tol, maxit)

r = (sqrt(5) - 1) / 2;

x1 = b - r*(b-a);
x2 = a + r*(b-a);
f1 = fun(x1);
f2 = fun(x2);

k = 0;
while (b-a > tol) && (k < maxit)
    if f1 > f2
        a = x1;
        x1 = x2;
        f1 = f2;
        x2 = a + r*(b-a);
        f2 = fun(x2);
    else
        b = x2;
        x2 = x1;
        f2 = f1;
        x1 = b - r*(b-a);
        f1 = fun(x1);
    end
    k = k + 1;
end

xopt = (a+b)/2;
fopt = fun(xopt);

end
```