# 第1题

## 题目

对两个月的汽油价格数据进行统计推断，包括均值假设检验、均值和标准差估计、均值差的区间估计。

## 代码

```matlab
clc; clear;

jan = [119 117 115 116 112 121 115 122 116 118 109 112 119 ...
       112 117 113 114 109 109 118];

feb = [118 119 115 122 118 121 120 122 128 116 120 123 121 ...
       119 117 119 128 126 118 125];

alpha = 0.05;

[h_jan,p_jan,ci_jan_test,stats_jan] = ttest(jan,115,alpha,0);
[h_feb,p_feb,ci_feb_test,stats_feb] = ttest(feb,115,alpha,0);

disp(' (1) 均值假设检验');
fprintf('1月: h = %d, p = %.6f, t统计量 = %.4f\n', h_jan, p_jan, stats_jan.tstat);
fprintf('2月: h = %d, p = %.6f, t统计量 = %.4f\n', h_feb, p_feb, stats_feb.tstat);

[mu_jan,sigma_jan,muci_jan,sigmaci_jan] = normfit(jan,alpha);
[mu_feb,sigma_feb,muci_feb,sigmaci_feb] = normfit(feb,alpha);

disp(' ');
disp(' (2) 均值与标准差估计、均值置信区间');
fprintf('1月均值点估计 = %.4f\n', mu_jan);
fprintf('1月均值95%%置信区间 = [%.4f, %.4f]\n', muci_jan(1), muci_jan(2));
fprintf('1月标准差点估计 = %.4f\n', sigma_jan);

fprintf('2月均值点估计 = %.4f\n', mu_feb);
fprintf('2月均值95%%置信区间 = [%.4f, %.4f]\n', muci_feb(1), muci_feb(2));
fprintf('2月标准差点估计 = %.4f\n', sigma_feb);

[h_diff,p_diff,ci_diff,stats_diff] = ttest2(jan,feb,alpha,0,'unequal');

disp(' ');
disp(' (3) 1月与2月均值差的区间估计');
fprintf('均值差（1月-2月）的95%%置信区间 = [%.4f, %.4f]\n', ci_diff(1), ci_diff(2));
fprintf('对应检验: h = %d, p = %.6f, t统计量 = %.4f\n', h_diff, p_diff, stats_diff.tstat);
```

# 第2题

## 题目

设计实验验证：在正态总体假设下，对于给定的显著性水平 \(\alpha\)，样本量 \(n\) 越大，均值 \(\mu\) 的置信区间长度越小，估计精度越高。并对 \(\sigma^2\) 的估计区间作类似验证。

## 代码

```matlab
clc; clear;

alpha = 0.05;
mu0 = 10;
sigma0 = 2;

nlist = 10:10:200;
L_mu = zeros(size(nlist));
L_sigma2 = zeros(size(nlist));

rng(1);

for k = 1:length(nlist)
    n = nlist(k);
    x = normrnd(mu0,sigma0,n,1);

    xb = mean(x);
    s = std(x);

    tval = tinv(1-alpha/2, n-1);
    ci_mu = [xb - tval*s/sqrt(n), xb + tval*s/sqrt(n)];
    L_mu(k) = ci_mu(2) - ci_mu(1);

    s2 = var(x);
    chi1 = chi2inv(alpha/2, n-1);
    chi2 = chi2inv(1-alpha/2, n-1);
    ci_sigma2 = [(n-1)*s2/chi2, (n-1)*s2/chi1];
    L_sigma2(k) = ci_sigma2(2) - ci_sigma2(1);
end

disp('   n       L_mu         L_sigma2');
disp([nlist(:), L_mu(:), L_sigma2(:)]);

figure;
plot(nlist, L_mu, 'o-','LineWidth',1.5);
grid on;
xlabel('样本容量 n');
ylabel('\mu 的置信区间长度');
title('\mu 的置信区间长度随样本量变化');

figure;
plot(nlist, L_sigma2, 's-','LineWidth',1.5);
grid on;
xlabel('样本容量 n');
ylabel('\sigma^2 的置信区间长度');
title('\sigma^2 的置信区间长度随样本量变化');
```

# 第3题

## 题目

学校随机抽取 100 名学生，测量他们的身高和体重。

要求：

1. 对这些数据给出直观图形描述，检验分布的正态性；
2. 根据这些数据对全校学生的平均身高和体重做出估计，并给出估计误差范围；
3. 已知学校 10 年前学生平均身高为 \(167.5\text{cm}\)，平均体重为 \(60.2\text{kg}\)，根据本次调查数据判断学生平均身高和体重有无显著变化。

## 代码

```matlab
clc; clear; close all;

height = [...
172 171 166 160 155 173 166 170 167 173 178 173 163 165 170 163 172 182 171 177 ...
169 168 168 175 176 168 161 169 171 178 177 170 173 172 170 172 177 176 175 184 ...
169 165 164 173 172 169 173 173 166 163 170 160 165 177 169 176 177 172 165 166 ...
171 169 170 172 169 167 175 164 166 169 167 179 176 182 186 166 169 173 169 171 ...
167 168 165 168 176 170 158 165 172 169 169 172 162 175 174 167 166 174 168 170];

weight = [...
75 62 62 55 57 58 55 63 53 60 60 73 47 66 60 50 57 63 59 64 ...
55 67 65 67 64 50 49 63 61 64 66 58 67 59 62 59 58 68 68 70 ...
64 52 59 74 69 52 57 61 70 57 56 65 58 66 63 60 67 56 56 49 ...
65 62 58 64 58 72 76 59 63 54 54 62 63 69 77 76 72 59 65 71 ...
47 65 64 57 57 57 51 62 53 66 58 50 52 75 66 63 50 64 62 59];

alpha = 0.05;

figure;
histogram(height);
grid on;
title('身高直方图');
xlabel('身高/cm');
ylabel('频数');

figure;
qqplot(height);
grid on;
title('身高QQ图');

figure;
histogram(weight);
grid on;
title('体重直方图');
xlabel('体重/kg');
ylabel('频数');

figure;
qqplot(weight);
grid on;
title('体重QQ图');

[h_h,p_h] = lillietest(height,alpha);
[h_w,p_w] = lillietest(weight,alpha);

disp(' (1) 正态性检验');
fprintf('身高: h = %d, p = %.6f\n', h_h, p_h);
fprintf('体重: h = %d, p = %.6f\n', h_w, p_w);

[mu_h,sigma_h,muci_h,sigmaci_h] = normfit(height,alpha);
[mu_w,sigma_w,muci_w,sigmaci_w] = normfit(weight,alpha);

disp(' ');
disp(' (2) 参数估计');
fprintf('身高均值点估计 = %.4f cm\n', mu_h);
fprintf('身高均值95%%置信区间 = [%.4f, %.4f] cm\n', muci_h(1), muci_h(2));
fprintf('身高标准差点估计 = %.4f\n', sigma_h);

fprintf('体重均值点估计 = %.4f kg\n', mu_w);
fprintf('体重均值95%%置信区间 = [%.4f, %.4f] kg\n', muci_w(1), muci_w(2));
fprintf('体重标准差点估计 = %.4f\n', sigma_w);

err_h = (muci_h(2) - muci_h(1))/2;
err_w = (muci_w(2) - muci_w(1))/2;

fprintf('身高估计误差范围 = ±%.4f cm\n', err_h);
fprintf('体重估计误差范围 = ±%.4f kg\n', err_w);

mu0_h = 167.5;
mu0_w = 60.2;

[hh,ph,cih,statsh] = ttest(height,mu0_h,alpha,0);
[hw,pw,ciw,statsw] = ttest(weight,mu0_w,alpha,0);

disp(' ');
disp(' (3) 与10年前比较的假设检验');

fprintf('身高检验: h = %d, p = %.6f, t统计量 = %.4f\n', hh, ph, statsh.tstat);
fprintf('身高均值差异对应95%%置信区间参考 = [%.4f, %.4f]\n', cih(1), cih(2));

fprintf('体重检验: h = %d, p = %.6f, t统计量 = %.4f\n', hw, pw, statsw.tstat);
fprintf('体重均值差异对应95%%置信区间参考 = [%.4f, %.4f]\n', ciw(1), ciw(2));
```

# 第4题

## 题目

20 名学生参加某课程同样知识的两次测验。根据两次测验成绩判断两次测验的难度是否相同。

## 代码

```matlab
clc; clear; close all;

x1 = [93 85 79 90 78 76 81 85 88 68 92 73 88 84 90 70 69 83 83 85];
x2 = [88 89 86 85 87 88 75 93 88 78 86 86 80 89 85 79 78 88 88 90];

alpha = 0.05;

d = x1 - x2;

disp('成对差值');
disp(d);

figure;
histogram(d);
grid on;
title('两次成绩差值直方图');
xlabel('第一次-第二次');
ylabel('频数');

figure;
qqplot(d);
grid on;
title('两次成绩差值QQ图');

[h_d,p_d] = lillietest(d,alpha);

disp(' ');
disp('差值正态性检验');
fprintf('h = %d, p = %.6f\n', h_d, p_d);

[h,p,ci,stats] = ttest(x1,x2,alpha,0);

disp(' ');
disp('成对t检验结果');
fprintf('h = %d\n', h);
fprintf('p = %.6f\n', p);
fprintf('t统计量 = %.4f\n', stats.tstat);
fprintf('均值差的95%%置信区间 = [%.4f, %.4f]\n', ci(1), ci(2));

m1 = mean(x1);
s1 = std(x1);
m2 = mean(x2);
s2 = std(x2);

disp(' ');
disp('描述统计');
fprintf('第一次测试：均值 = %.4f, 标准差 = %.4f\n', m1, s1);
fprintf('第二次测试：均值 = %.4f, 标准差 = %.4f\n', m2, s2);
fprintf('平均差值(第一次-第二次) = %.4f\n', mean(d));
```

# 第5题

## 题目

参考吸血压例子中的自编函数 `pttest2()`，编写一个函数实现两个正态总体方差比检验。输入参数为样本均值和样本方差、显著性水平以及双侧单侧等信息，输出类似 `vartest2()` 函数的所有结果，命名为 `Ftest2`。

## 代码

```matlab
function [h,sig,ci,stats] = Ftest2(s1sq,s2sq,n1,n2,alpha,tail)

F = s1sq / s2sq;
v1 = n1 - 1;
v2 = n2 - 1;

stats.fstat = F;
stats.df1 = v1;
stats.df2 = v2;

if tail == 0
    Fl = finv(alpha/2, v1, v2);
    Fu = finv(1-alpha/2, v1, v2);

    if F >= Fl && F <= Fu
        h = 0;
    else
        h = 1;
    end

    sig = 2 * min(fcdf(F,v1,v2), 1-fcdf(F,v1,v2));
    ci = [F / finv(1-alpha/2,v1,v2), F / finv(alpha/2,v1,v2)];
end

if tail == 1
    Fu = finv(1-alpha, v1, v2);

    if F <= Fu
        h = 0;
    else
        h = 1;
    end

    sig = 1 - fcdf(F,v1,v2);
    ci = [F / finv(1-alpha,v1,v2), inf];
end

if tail == -1
    Fl = finv(alpha, v1, v2);

    if F >= Fl
        h = 0;
    else
        h = 1;
    end

    sig = fcdf(F,v1,v2);
    ci = [0, F / finv(alpha,v1,v2)];
end

end
```

```matlab
clc; clear;

x = [12.1 11.8 12.5 11.9 12.3 12.0 11.7 12.4];
y = [11.2 11.6 11.4 11.5 11.8 11.3 11.7 11.1];

n1 = length(x);
n2 = length(y);
s1sq = var(x);
s2sq = var(y);

alpha = 0.05;
tail = 0;

[h,sig,ci,stats] = Ftest2(s1sq,s2sq,n1,n2,alpha,tail);

disp(' Ftest2 检验结果');
fprintf('h = %d\n', h);
fprintf('p值 = %.6f\n', sig);
fprintf('F统计量 = %.6f\n', stats.fstat);
fprintf('置信区间 = [%.6f, %.6f]\n', ci(1), ci(2));
```

# 第6题

## 题目

在“加油站合同制定问题”中，根据所给理论分析和公式，编程计算第 5 问中显著性水平和第二类错误表格中的值。

## 代码

```matlab
clc; clear;

x = [0.0864 0.0744 0.0864 0.0752 0.0760 ...
     0.0954 0.0936 0.1016 0.0800 0.0880];

n = length(x);
xbar = mean(x);
s = std(x);

mu0 = 0.08;
mu1 = 0.086;

alpha_list = [0.01 0.05 0.10 0.20 0.30];
beta_list = zeros(size(alpha_list));

for k = 1:length(alpha_list)
    alpha = alpha_list(k);

    t_alpha = tinv(1-alpha, n-1);

    delta = (mu1 - mu0) / (s/sqrt(n));
    beta_list(k) = nctcdf(t_alpha, n-1, delta);
end

disp('alpha 与 beta 对照表');
disp('   alpha         beta');
disp([alpha_list(:), beta_list(:)]);
```