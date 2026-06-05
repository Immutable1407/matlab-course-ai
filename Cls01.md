# 第1题

## 题目

通过编程用左点法、梯形法、抛物线法计算

\[
\int_0^2 e^{3x}\sin(2x)\,dx
\]

并分析同一方法对不同步长的误差关系。

## 代码

```matlab
format long

syms x
fx = exp(3*x)*sin(2*x);

a = 0;
b = 2;

% 求精确值
I_exact = int(fx, x, a, b);
I_exact = double(I_exact);
fprintf('精确值 I = %.12f\n\n', I_exact);

N = [10 20 40 80 160 320];

fprintf('   n          左点法误差         梯形法误差        抛物线法误差\n');
fprintf('------------------------------------------------------------------\n');

for k = 1:length(N)
    n = N(k);
    h = (b-a)/n;

    I_left = 0;
    I_trap = 0;
    I_simp = 0;

    % 左点法
    for i = 1:n
        xj = a + (i-1)*h;
        fxj = subs(fx, x, xj);
        I_left = I_left + fxj*h;
    end
    I_left = double(I_left);

    % 梯形法
    for i = 1:n
        xj = a + (i-1)*h;
        xi = a + i*h;
        fxj = subs(fx, x, xj);
        fxi = subs(fx, x, xi);
        I_trap = I_trap + (fxj + fxi)*h/2;
    end
    I_trap = double(I_trap);

    % Simpson法
    if mod(n,2) ~= 0
        error('Simpson法要求分段数 n 为偶数');
    end

    for i = 1:2:n
        x0 = a + (i-1)*h;
        x1 = x0 + h;
        x2 = x0 + 2*h;

        fx0 = subs(fx, x, x0);
        fx1 = subs(fx, x, x1);
        fx2 = subs(fx, x, x2);

        I_simp = I_simp + (h/3)*(fx0 + 4*fx1 + fx2);
    end
    I_simp = double(I_simp);

    % 误差
    err_left = abs((I_left - I_exact)/I_exact);
    err_trap = abs((I_trap - I_exact)/I_exact);
    err_simp = abs((I_simp - I_exact)/I_exact);

    fprintf('%5d     %16.8e   %16.8e   %16.8e\n', ...
            n, err_left, err_trap, err_simp);
end
```

# 第2题

## 题目

分别用梯形法和抛物线法按照下表数据计算积分

\[
\int_{0.3}^{1.5} y(x)\,dx
\]

已知数据：

| x | 0.3 | 0.5 | 0.7 | 0.9 | 1.1 | 1.3 | 1.5 |
|---|---|---|---|---|---|---|---|
| y | 0.3985 | 0.6598 | 0.9147 | 1.1611 | 1.3971 | 1.6212 | 1.8325 |

## 代码

```matlab
x = [0.3 0.5 0.7 0.9 1.1 1.3 1.5];
y = [0.3985 0.6598 0.9147 1.1611 1.3971 1.6212 1.8325];

% 梯形法
I_trap = trapz(x, y);

% Simpson法
h = x(2) - x(1);
n = length(x) - 1;

I_simp = h/3 * ( y(1) + y(end) ...
    + 4*sum(y(2:2:end-1)) ...
    + 2*sum(y(3:2:end-2)) );

fprintf('梯形法结果 I_trap = %.8f\n', I_trap);
fprintf('Simpson法结果 I_simp = %.8f\n', I_simp);
```

# 第3题

## 题目

使用矩形法、梯形法、抛物线法计算积分

\[
\int_0^{10} e^{-0.8t|\sin t|}\,dt
\]

## 代码

```matlab
format long

syms t
ft = exp(-0.8*t*abs(sin(t)));

a = 0;
b = 10;
n = 200;
h = (b-a)/n;

I_rect = 0;
I_trap = 0;
I_simp = 0;

% 矩形法和梯形法
for i = 1:n
    tj = a + (i-1)*h;
    ti = a + i*h;

    ftj = subs(ft, t, tj);
    fti = subs(ft, t, ti);

    I_rect = I_rect + ftj*h;
    I_trap = I_trap + (ftj + fti)*h/2;
end

% Simpson法
for i = 1:2:n
    t0 = a + (i-1)*h;
    t1 = t0 + h;
    t2 = t0 + 2*h;

    ft0 = subs(ft, t, t0);
    ft1 = subs(ft, t, t1);
    ft2 = subs(ft, t, t2);

    I_simp = I_simp + h/3*(ft0 + 4*ft1 + ft2);
end

I_rect = double(I_rect);
I_trap = double(I_trap);
I_simp = double(I_simp);

fprintf('矩形法计算结果   = %.12f\n', I_rect);
fprintf('梯形法计算结果   = %.12f\n', I_trap);
fprintf('抛物线法计算结果 = %.12f\n', I_simp);
```

# 第4题

## 题目

使用两种不同的 MATLAB 函数计算积分

\[
\int_1^{1.5}\int_{1.4}^{2}(x^2+2y)\,dx\,dy
\]

## 代码

```matlab
format long

% dblquad
f1 = @(x,y) x.^2 + 2*y;
I1 = dblquad(f1, 1.4, 2, 1, 1.5);

fprintf('Use dblquad, the result is: %.12f\n\n', I1);

% 符号积分
syms x y
f2 = x^2 + 2*y;

I2 = int(int(f2, x, 1.4, 2), y, 1, 1.5);
I2 = double(I2);

fprintf('Use int, the result is: %.12f\n\n', I2);
```

# 第5题

## 题目

写出计算人造卫星轨道长度的脚本文件。

## 代码

```matlab
format long

r = 6371;
s1 = 439;
s2 = 2384;

rp = r + s1;
ra = r + s2;

a = (rp + ra)/2;
c = (ra - rp)/2;
b = sqrt(a^2 - c^2);

syms t
xt = a*cos(t);
yt = b*sin(t);

dx = diff(xt, t);
dy = diff(yt, t);

ft = sqrt(dx^2 + dy^2);

n = 1000;
t0 = 0;
t1 = 2*pi;
h = (t1 - t0)/n;

L = 0;

for i = 1:n
    tj = t0 + (i-1)*h;
    ti = t0 + i*h;

    ftj = subs(ft, t, tj);
    fti = subs(ft, t, ti);

    L = L + (ftj + fti)*h/2;
end

L = double(L);

fprintf('a = %.12f\n', a);
fprintf('b = %.12f\n', b);
fprintf('The orbit length is about: %.12f km\n', L);
```

# 第6题

## 题目

如下图所示地图边界测量数据如下（单位：mm）：

- x方向为东西方向
- y方向为南北方向
- 比例尺：18 mm 对应 40 km

根据给定边界点数据计算该国国土面积近似值，并与精确值

\[
41288\ \text{km}^2
\]

进行比较。

## 代码

```matlab
format long

x = [7.0 10.5 13.0 17.5 34.0 40.5 44.5 48.0 56.0 61.0 ...
     68.5 76.5 80.5 91.0 96.0 101.0 104.0 106.5 111.5 ...
     118.0 123.5 136.5 142.0 146.0 150.0 157.0 158.0];

y1 = [44 45 47 50 50 38 30 30 34 36 34 41 45 46 ...
      43 37 33 28 32 65 55 54 52 50 66 66 68];

y2 = [44 59 70 72 93 100 110 110 110 117 118 116 118 118 ...
      121 124 121 121 121 122 116 83 81 82 86 85 68];

y = y2 - y1;

Smap = 0;

for i = 1:length(x)-1
    hk = x(i+1) - x(i);
    Smap = Smap + (y(i) + y(i+1))*hk/2;
end

Smap = double(Smap);

scale = 40/18;
Sreal = Smap * scale^2;

Strue = 41288;

abserr = abs(Sreal - Strue);
relerr = abs((Sreal - Strue)/Strue);

fprintf('The area on the map is about: %.12f mm^2\n\n', Smap);
fprintf('The real area is about: %.12f km^2\n\n', Sreal);
fprintf('The exact area is: %.12f km^2\n\n', Strue);
fprintf('The absolute error is: %.12f km^2\n\n', abserr);
fprintf('The relative error is: %.12e\n\n', relerr);
```