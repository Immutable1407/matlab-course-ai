# 第1题

## 题目

利用 Euler 折线法编程求解如下初值问题

\[
y'=1+y,\qquad y(0)=1
\]

其中

\[
x_0=0,\quad h=0.5,\quad 0\le x\le 2
\]

并画出该解与精确解的对比图像。

## 代码

```matlab
clear;
syms x y

f = 1 + y;
a = 0;
b = 2;
h = 0.5;
n = (b-a)/h;

x = 0;
y = 1;
szj = [x,y];

for i = 1:n
    y = y + h*double(subs(f, {'x','y'}, {x,y}));
    x = x + h;
    szj = [szj; x,y];
end

xx = a:0.01:b;
yy = 2*exp(xx) - 1;

plot(szj(:,1), szj(:,2), 'or-','LineWidth',1.2);
hold on;
plot(xx, yy, 'b-','LineWidth',1.5);
grid on;
legend('Euler数值解','精确解');
title('题1：Euler法与精确解比较');
xlabel('x');
ylabel('y');
```

# 第2题

## 题目

将第1题中的步长缩短，取

\[
h=0.1
\]

观察步长变化对数值解精度的影响。

## 代码

```matlab
clear;
syms x y

f = 1 + y;
a = 0;
b = 2;
h = 0.1;
n = (b-a)/h;

x = 0;
y = 1;
szj = [x,y];

for i = 1:n
    y = y + h*double(subs(f, {'x','y'}, {x,y}));
    x = x + h;
    szj = [szj; x,y];
end

xx = a:0.01:b;
yy = 2*exp(xx) - 1;

plot(szj(:,1), szj(:,2), 'or-','LineWidth',1.1);
hold on;
plot(xx, yy, 'b-','LineWidth',1.5);
grid on;
legend('Euler数值解(h=0.1)','精确解');
title('题2：步长缩短后 Euler 法与精确解比较');
xlabel('x');
ylabel('y');

y_exact_2 = 2*exp(2) - 1;
err = abs(szj(end,2) - y_exact_2);

disp('x=2 处的绝对误差为：');
disp(err);
```

# 第3题

## 题目

分别利用 Euler 折线法和 Runge-Kutta（龙格-库塔）方法求解初值问题

\[
\begin{cases}
y'=y+2x,\\
y(0)=1,
\end{cases}
\qquad 0\le x\le 1
\]

并与精确解进行比较，观察 Euler 法和 Runge-Kutta 法的精度差异。

## 代码

```matlab
clear;
syms x y

f = y + 2*x;
a = 0;
b = 1;
n = 10;
h = (b-a)/n;

x1 = 0;
y1 = 1;
szj1 = [x1,y1];

for i = 1:n
    y1 = y1 + h*double(subs(f, {'x','y'}, {x1,y1}));
    x1 = x1 + h;
    szj1 = [szj1; x1,y1];
end

x2 = 0;
y2 = 1;
szj2 = [x2,y2];

for i = 1:n
    l1 = subs(f, {'x','y'}, {x2,y2});
    l2 = subs(f, {'x','y'}, {x2+h/2, y2+double(l1)*h/2});
    l3 = subs(f, {'x','y'}, {x2+h/2, y2+double(l2)*h/2});
    l4 = subs(f, {'x','y'}, {x2+h, y2+double(l3)*h});

    y2 = y2 + h*double(l1 + 2*l2 + 2*l3 + l4)/6;
    x2 = x2 + h;
    szj2 = [szj2; x2,y2];
end

xx = a:0.01:b;
yy = 3*exp(xx) - 2*xx - 2;

plot(szj1(:,1), szj1(:,2), 'or-','LineWidth',1.1);
hold on;
plot(szj2(:,1), szj2(:,2), 'dg-','LineWidth',1.1);
plot(xx, yy, 'b-','LineWidth',1.5);
grid on;
legend('Euler法','Runge-Kutta法','精确解');
title('题3：Euler法、Runge-Kutta法与精确解比较');
xlabel('x');
ylabel('y');

y_exact_1 = 3*exp(1) - 4;
err1 = abs(szj1(end,2) - y_exact_1);
err2 = abs(szj2(end,2) - y_exact_1);

disp('Euler法在 x=1 处的绝对误差：');
disp(err1);
disp('Runge-Kutta法在 x=1 处的绝对误差：');
disp(err2);
```

# 第4题

## 题目

利用 MATLAB 函数求以下问题的解析解与数值近似解：

### (1)

\[
y''-2y'+5y=e^x\cos 2x
\]

### (2)

\[
\begin{cases}
\dfrac{dx}{dt}+x+2y=e^t\\
\dfrac{dy}{dt}-x-y=0
\end{cases}
\]

初值条件：

\[
x(0)=1,\qquad y(0)=0
\]

### (3)

\[
y'=1+5y,\qquad y(0)=1
\]

在区间 \([0,1]\) 上求数值近似解。

### (4)

\[
y''-(1-y^2)y'+y=0
\]

初值条件：

\[
y(0)=0,\qquad y'(0)=-0.5
\]

在区间 \([0,20]\) 上求数值近似解。

## 代码

### (1)

```matlab
clear;
syms y(x)

Dy = diff(y,x);
D2y = diff(y,x,2);

eq = D2y - 2*Dy + 5*y == exp(x)*cos(2*x);
y_general = dsolve(eq);

disp('方程(1)的通解为：');
disp(simplify(y_general));
```

### (2)

```matlab
clear;
syms x(t) y(t)

eq1 = diff(x,t) + x + 2*y == exp(t);
eq2 = diff(y,t) - x - y == 0;

cond1 = x(0) == 1;
cond2 = y(0) == 0;

[xs, ys] = dsolve(eq1, eq2, cond1, cond2);

disp('方程组(2)的解 x(t) 为：');
disp(simplify(xs));

disp('方程组(2)的解 y(t) 为：');
disp(simplify(ys));
```

### (3)

```matlab
clear;

fun = @(t,y) 1 + 5*y;
[t,y] = ode45(fun,[0,1],1);

plot(t,y,'r.-','LineWidth',1.2,'MarkerSize',12);
grid on;
title('题4(3)：ode45求数值近似解');
xlabel('t');
ylabel('y');
```

### (4)

```matlab
clear;

f = @(t,y)[y(2);
           (1-y(1)^2)*y(2)-y(1)];

[t,y] = ode45(f,[0,20],[0,-0.5]);

plot(t,y(:,1),'r-','LineWidth',1.2);
grid on;
title('题4(4)：y(x) 的数值近似解');
xlabel('x');
ylabel('y');

figure;
plot(y(:,1),y(:,2),'b-','LineWidth',1.2);
grid on;
title('题4(4)：相轨线');
xlabel('y');
ylabel('y''');
```

# 第5题

## 题目

一个慢跑者在平面上沿椭圆跑步，其轨迹为

\[
x=10+20\cos t,\qquad y=20+15\sin t
\]

一只狗从原点出发，以恒定速度

\[
w=20
\]

追赶慢跑者，并且狗的运动方向始终指向慢跑者。

利用参数方程给出狗的运动轨迹。

## 代码

```matlab
clear;

w = 20;

f = @(t,z)[ ...
    w*((10+20*cos(t))-z(1)) / ...
    sqrt(((10+20*cos(t))-z(1))^2 + ((20+15*sin(t))-z(2))^2);

    w*((20+15*sin(t))-z(2)) / ...
    sqrt(((10+20*cos(t))-z(1))^2 + ((20+15*sin(t))-z(2))^2) ];

[t,z] = ode45(f,[0,10],[0,0]);

tt = 0:0.01:10;
xr = 10 + 20*cos(tt);
yr = 20 + 15*sin(tt);

plot(xr,yr,'b-','LineWidth',1.2);
hold on;
plot(z(:,1),z(:,2),'r-','LineWidth',1.2);
plot(0,0,'ko','MarkerFaceColor','k');

grid on;
axis equal;
legend('慢跑者轨迹','狗的轨迹','狗的出发点');
title('题5：w=20时狗的运动轨迹');
xlabel('x');
ylabel('y');
```
