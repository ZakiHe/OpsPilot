# IForest

## 算法简介

孤立森林(Isolation Forest, IForest)是一个基于Ensemble的无监督异常检测方法，具有线性时间复杂度和高精确度。IForest使用了比较高效的策略，密度较高的簇需要被切割很多次才能将每个数据点分到单独的子空间中，而密度很低的点很容易就被分割到一个子空间中了。

## 使用场景
适用于<font color='red'>连续数据</font>的异常检测，可以用于<font color='red'>数据规模较大</font>的数据集（可以增加树的数量以增加算法稳定性，每棵树相互独立，可不属于大规模分布式系统加速运算），<font color='red'>不适用于维度过高大数据</font>，会导致算法可靠性降低。

## 3. 算法原理
![Excalidraw Image](./img/IForest.png)

该算法采用两个阶段的过程进行异常检测。第一阶段是训练阶段，对训练集数据进行子采样，通过递归将训练集进行划分直到数据点被孤立或达到limited hegiht，从而构建一系列的孤立树(iTree)，构建每棵孤立树时分割的指标随机选取，分割的值产生于指标值最大与最小值之间。第二阶段是评估阶段，将每个数据点通过每棵iTree，计算每个数据点在所有iTree上的平均路径长度(Average Path Length, APL)，用以衡量异常得分，将APL归一化于0-1范围内得到异常得分，异常得分远小于1表示明确正常，越接近1越有可能为异常点（异常点远离密度高的簇，很容易被分到一个子空间，因此平均路径长度会较短，如iTree1中的a）。

**原文链接**：<https://www.researchgate.net/publication/224384174_Isolation_Forest>