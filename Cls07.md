# 第1题

## 题目

课本 P321 第1题：建立刀具厚度对于切削时间的回归模型，对模型和回归系数进行检验，并预测 7.5h 和 15h 后的刀具厚度。

## 代码

```matlab
clear;clc;close all
format long

x=0:10;
y=[30.6 29.1 28.4 28.1 28.0 27.7 27.5 27.2 27.0 26.8 26.5];

n=length(x);
X=[ones(n,1),x'];

[b,bi,r,ri,s]=regress(y',X,0.05)

figure
plot(x,y,'+'),grid on,hold on
xx=0:0.1:15;
yy=b(1)+b(2)*xx;
plot(xx,yy)
xlabel('切削时间/h')
ylabel('刀具厚度/cm')
title('刀具厚度对切削时间的一元线性回归')

figure
rcoplot(r,ri)
title('残差分析')

x0=[7.5;15];
X0=[ones(2,1),x0];
y0=X0*b

[p,S]=polyfit(x,y,1);
[yfit,delta]=polyconf(p,x0,S,'alpha',0.05,'predopt','observation');
pre_interval=[yfit-delta,yfit+delta]

mdl=fitlm(x,y)
predict(mdl,x0,'Prediction','observation')
```

# 第2题

## 题目

课本 P322 第4题：13 名少年儿童参加睡眠时间与年龄关系的调查，画出散点图，建立回归模型并检验模型有效性，解释结果；给出 10 岁孩子的平均睡眠时间及预测区间。

## 代码

```matlab
clear;clc;close all
format long

y=[586 462 491 565 462 532 478 515 493 528 576 533 531];
x=[4.4 14.0 10.1 6.7 11.5 9.6 12.4 8.9 11.1 7.8 5.5 8.6 7.2];

n=length(x);
X=[ones(n,1),x'];

[b,bi,r,ri,s]=regress(y',X,0.05)

figure
plot(x,y,'+'),grid on,hold on
xx=min(x):0.1:max(x);
yy=b(1)+b(2)*xx;
plot(xx,yy)
xlabel('年龄/岁')
ylabel('睡眠时间/min')
title('睡眠时间与年龄的一元线性回归')

figure
rcoplot(r,ri)
title('残差分析')

x0=10;
X0=[1,x0];
y0=X0*b

[p,S]=polyfit(x,y,1);
[yfit,delta]=polyconf(p,x0,S,'alpha',0.05,'predopt','observation');
pre_interval=[yfit-delta,yfit+delta]

mdl=fitlm(x,y)
predict(mdl,x0,'Prediction','observation')
```

# 第3题

## 题目

课本 P326 第10题：根据某城市 18 位 35–44 岁经理的年平均收入、风险偏好度和人寿保险额数据，建立合适的回归模型，分析人寿保险额与年平均收入、风险偏好度之间的关系，并学习使用 `fitlm()` 函数进行回归分析。

## 代码

```matlab
clear;clc;close all
format long

y =[196 63 252 84 126 14 49 49 266 49 105 98 77 14 56 245 133 133];
x1=[66.290 40.964 72.996 45.010 57.204 26.852 38.122 35.840 75.796 ...
    37.408 54.376 46.186 46.130 30.366 39.060 79.380 52.766 55.916];
x2=[7 5 10 6 4 5 4 6 9 5 2 7 4 3 5 1 8 6];

n=length(y);

X=[ones(n,1),x1',x2'];
[b,bi,r,ri,s]=regress(y',X,0.05)

figure
rcoplot(r,ri)
title('线性模型残差分析')

X2=[ones(n,1),x1',x1'.^2,x2'];
[b2,bi2,r2,ri2,s2]=regress(y',X2,0.05)

figure
rcoplot(r2,ri2)
title('含x1二次项模型残差分析')

X3=[ones(n,1),x1',x2',x1'.^2,x1'.*x2',x2'.^2];
[b3,bi3,r3,ri3,s3]=regress(y',X3,0.05)

figure
rcoplot(r3,ri3)
title('完全二次模型残差分析')

x=[x1;x2]';
rstool(x,y','quadratic')

T=table(y',x1',x2','VariableNames',{'y','x1','x2'});

mdl1=fitlm(T,'y ~ x1 + x2')
mdl2=fitlm(T,'y ~ x1 + x1^2 + x2')
mdl3=fitlm(T,'y ~ x1 + x2 + x1^2 + x1:x2 + x2^2')

anova(mdl1)
anova(mdl2)
anova(mdl3)
```