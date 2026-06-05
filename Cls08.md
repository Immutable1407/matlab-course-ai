# 第1题 单个受试者建图与基本指标

## 题目

已知 BrainData.mat 中 AdjMatrices(:,:,1) 表示第1名受试者的脑功能连接矩阵，NodeNames 给出了90个脑区名称，推荐阈值为0.23。

完成：

1. 将该受试者的加权连接矩阵按阈值0.23二值化，建立无向脑网络模型，并写出相应MATLAB建图代码。
2. 计算各节点的度，并求该网络的平均度。
3. 分别计算 Frontal_Sup_L、Precuneus_L、Hippocampus_L 的局部聚类系数，并比较哪个节点更可能是局部团簇中的关键节点。
4. 绘制该受试者的脑网络图。 :contentReference[oaicite:0]{index=0}

## 代码

### 主程序

```matlab
clc; clear; close all;

load('BrainData.mat');

thr = RecommendedThreshold(1);
W = AdjMatrices(:,:,1);
nNodes = size(W,1);

B = double(W >= thr);
B(1:nNodes+1:end) = 0;
B = double((B+B') > 0);

G = graph(B, NodeNames);

deg = degree(G);
meanDegree = mean(deg);

fprintf('第1名受试者网络边数 = %d\n', nnz(triu(B,1)));
fprintf('平均度 = %.4f\n', meanDegree);

C = localClusteringCoeff(B);

targets = ["Frontal_Sup_L";
           "Precuneus_L";
           "Hippocampus_L"];

for i = 1:length(targets)
    idx = find(string(NodeNames) == targets(i));
    fprintf('%s: 编号=%d, 度=%d, 局部聚类系数=%.4f\n', ...
        targets(i), idx, deg(idx), C(idx));
end

figure;
p = plot(G,'Layout','force','NodeLabel',{});
title('Subject 1 Binary Brain Network');

targetIdx = zeros(length(targets),1);
for i = 1:length(targets)
    targetIdx(i) = find(string(NodeNames) == targets(i));
end

highlight(p,targetIdx,'NodeColor','r','MarkerSize',8);
```

### 函数 localClusteringCoeff.m

```matlab
function C = localClusteringCoeff(B)

n = size(B,1);
C = zeros(n,1);

for i = 1:n

    neigh = find(B(i,:) > 0);
    k = length(neigh);

    if k >= 2
        subB = B(neigh,neigh);
        actualEdges = nnz(triu(subB,1));

        C(i) = 2*actualEdges/(k*(k-1));
    else
        C(i) = 0;
    end

end

end
```

---

# 第2题 100名受试者网络指标统计

## 题目

现对全部100名受试者进行分析。每名受试者都按照阈值0.23将连接矩阵二值化，得到对应脑网络。

完成：

1. 对每名受试者计算平均度、平均聚类系数、全局效率。
2. 将结果整理成数据表，包含 SubjectID、Labels 以及各项网络指标。
3. 给出 HC、MCI、AD 三组上述指标的均值和标准差。
4. 简要说明这些指标分别反映脑网络的什么特征。 :contentReference[oaicite:1]{index=1}

## 代码

```matlab
clc; clear; close all;

load('BrainData.mat');

thr = RecommendedThreshold(1);
nSub = size(AdjMatrices,3);
nNodes = size(AdjMatrices,1);

Labels = string(Labels);
SubjectID = string(SubjectID);

MeanDegree = zeros(nSub,1);
MeanClustering = zeros(nSub,1);
GlobalEfficiency = zeros(nSub,1);

for s = 1:nSub

    W = AdjMatrices(:,:,s);

    B = double(W >= thr);
    B(1:nNodes+1:end) = 0;
    B = double((B+B') > 0);

    G = graph(B);

    MeanDegree(s) = mean(degree(G));
    MeanClustering(s) = mean(localClusteringCoeff(B));
    GlobalEfficiency(s) = globalEfficiency(B);

end

SubjectMetrics = table(SubjectID, Labels, ...
    MeanDegree, MeanClustering, GlobalEfficiency);

disp(SubjectMetrics);

groupOrder = ["HC","MCI","AD"];

for i = 1:length(groupOrder)

    g = groupOrder(i);
    idx = Labels == g;

    fprintf('\n%s组：\n', g);

    fprintf('平均度 = %.4f ± %.4f\n', ...
        mean(MeanDegree(idx)), std(MeanDegree(idx)));

    fprintf('平均聚类系数 = %.4f ± %.4f\n', ...
        mean(MeanClustering(idx)), std(MeanClustering(idx)));

    fprintf('全局效率 = %.4f ± %.4f\n', ...
        mean(GlobalEfficiency(idx)), std(GlobalEfficiency(idx)));

end
```

### 函数 globalEfficiency.m

```matlab
function E = globalEfficiency(B)

G = graph(B);
D = distances(G);

n = size(B,1);

invD = 1 ./ D;

invD(eye(n)==1) = 0;
invD(isinf(invD)) = 0;

E = sum(invD(:)) / (n*(n-1));

end
```

---

# 第3题 组间比较与统计检验

## 题目

利用第2题中得到的网络指标，比较 HC、MCI、AD 三组受试者脑网络结构的差异。

完成：

1. 对平均度、平均聚类系数和全局效率分别绘制按组分类的箱线图。
2. 采用单因素方差分析（ANOVA）检验三组在上述指标上是否存在显著差异。
3. 若检验结果显著，进一步说明如何进行事后两两比较。
4. 从脑网络退化角度进行简要解释。 :contentReference[oaicite:2]{index=2}

## 代码

```matlab
clc; clear; close all;

load('BrainData.mat');

thr = RecommendedThreshold(1);
nSub = size(AdjMatrices,3);
nNodes = size(AdjMatrices,1);

Labels = string(Labels);

MeanDegree = zeros(nSub,1);
MeanClustering = zeros(nSub,1);
GlobalEfficiency = zeros(nSub,1);

for s = 1:nSub

    W = AdjMatrices(:,:,s);

    B = double(W >= thr);
    B(1:nNodes+1:end) = 0;
    B = double((B+B') > 0);

    G = graph(B);

    MeanDegree(s) = mean(degree(G));
    MeanClustering(s) = mean(localClusteringCoeff(B));
    GlobalEfficiency(s) = globalEfficiency(B);

end

figure;

subplot(1,3,1);
boxplot(MeanDegree, Labels);
title('MeanDegree');
ylabel('平均度');

subplot(1,3,2);
boxplot(MeanClustering, Labels);
title('MeanClustering');
ylabel('平均聚类系数');

subplot(1,3,3);
boxplot(GlobalEfficiency, Labels);
title('GlobalEfficiency');
ylabel('全局效率');

[p1,tbl1,stats1] = anova1(MeanDegree, Labels);
[p2,tbl2,stats2] = anova1(MeanClustering, Labels);
[p3,tbl3,stats3] = anova1(GlobalEfficiency, Labels);

c1 = multcompare(stats1);
c2 = multcompare(stats2);
c3 = multcompare(stats3);
```

---

# 第4题 自拟研究问题

## 题目

基于 BrainData.mat 提供的数据，自拟一个与脑网络结构差异有关的研究问题，并完成分析。

要求：

1. 研究问题与脑网络拓扑特征、组间差异、关键节点或功能模块有关。
2. 可采用更换阈值、提取新指标、模块分析等方法。
3. 至少给出1张图和1个统计结果表。
4. 给出主要结论并说明局限性。 :contentReference[oaicite:3]{index=3}

## 代码

```matlab
clc; clear; close all;

load('BrainData.mat');

thr = RecommendedThreshold(1);

nSub = size(AdjMatrices,3);
nNodes = size(AdjMatrices,1);

Labels = string(Labels);
ModuleNames = string(ModuleNames);

dmnMask = ModuleNames == "DMN";
nDMN = sum(dmnMask);

DMNDensity = zeros(nSub,1);

for s = 1:nSub

    W = AdjMatrices(:,:,s);

    B = double(W >= thr);
    B(1:nNodes+1:end) = 0;
    B = double((B+B') > 0);

    Bdmn = B(dmnMask, dmnMask);

    DMNDensity(s) = sum(Bdmn(:)) / (nDMN*(nDMN-1));

end

figure;
boxplot(DMNDensity, Labels);

title('DMN模块内部连接密度');
ylabel('DMN density');

groupOrder = ["HC","MCI","AD"];

for i = 1:length(groupOrder)

    g = groupOrder(i);
    idx = Labels == g;

    fprintf('%s组 DMN密度 = %.4f ± %.4f\n', ...
        g, mean(DMNDensity(idx)), std(DMNDensity(idx)));

end

[p,tbl,stats] = anova1(DMNDensity, Labels);

c = multcompare(stats);
```

---

# 第5题 K-means聚类实验

## 题目

数据文件 BrainFeatures_100.mat 已给出100名受试者的三个指标：平均度、聚类系数、全局效率。

完成：

1. 加载数据，选择平均聚类系数与全局效率两个指标，对数据进行标准化。
2. 使用 K-means 将受试者分为3类，并绘制聚类结果及聚类中心。
3. 讨论仅利用这三个网络指标是否能够完全区分健康人与病人。 :contentReference[oaicite:4]{index=4}

## 代码

### 数据标准化

```matlab
clc; clear; close all;

load('BrainFeatures_100.mat');

X = [MeanClustering(:), GlobalEfficiency(:)];

Xz = zscore(X);

disp(mean(Xz));
disp(std(Xz));
```

### K-means聚类

```matlab
clc; clear; close all;

load('BrainFeatures_100.mat');

X = [MeanClustering(:), GlobalEfficiency(:)];

Xz = zscore(X);

K = 3;

[idx,C] = kmeans(Xz, K, 'Replicates',10);

figure;

gscatter(Xz(:,1), Xz(:,2), idx, 'rgb', 'osd', 8);

hold on;

plot(C(:,1), C(:,2), ...
    'kx', ...
    'MarkerSize',14, ...
    'LineWidth',3);

xlabel('平均聚类系数（标准化）');
ylabel('全局效率（标准化）');

title('K-means 聚类结果（K=3)');
grid on;
```

---

# 第6题 KNN分类预测

## 题目

利用已知受试者指标以及对应诊断标签（GroupCode：1-健康，2-MCI，3-AD）。

完成：

1. 随机划分训练集（70人）和测试集（30人）。
2. 建立 K=3 的 KNN 分类器。
3. 计算分类准确率。
4. 讨论 K 值选择对分类效果的影响。 :contentReference[oaicite:5]{index=5}

## 代码

### 建立分类器

```matlab
clc; clear; close all;

load('BrainFeatures_100.mat');

X = [MeanDegree(:), MeanClustering(:), GlobalEfficiency(:)];
Y = GroupCode(:);

rng(1);

n = length(Y);

randIndex = randperm(n);

trainIndex = randIndex(1:70);
testIndex  = randIndex(71:100);

trainX = X(trainIndex,:);
trainY = Y(trainIndex);

testX = X(testIndex,:);
testY = Y(testIndex);

mu = mean(trainX);
sigma = std(trainX);

trainXz = (trainX - repmat(mu,size(trainX,1),1)) ...
        ./ repmat(sigma,size(trainX,1),1);

testXz = (testX - repmat(mu,size(testX,1),1)) ...
       ./ repmat(sigma,size(testX,1),1);

K = 3;

mdl = fitcknn(trainXz, trainY, ...
    'NumNeighbors',K);
```

### 分类预测与准确率计算

```matlab
predY = predict(mdl, testXz);

acc = mean(predY == testY);

fprintf('KNN 分类准确率：%.2f%%\n', acc*100);

C = confusionmat(testY, predY);

disp(C);

figure;

gscatter(testXz(:,2), testXz(:,3), ...
    testY, 'bgr', 'osd', 8);

hold on;

gscatter(testXz(:,2), testXz(:,3), ...
    predY, 'bgr', 'xxx', 10);

xlabel('平均聚类系数（标准化）');
ylabel('全局效率（标准化）');

title('KNN 测试集分类结果');

grid on;
```