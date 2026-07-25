# 导入必要的库
import scipy.io as spio

# 读取.mtx文件
matrix = spio.mmread(r'C:\Users\HP\Desktop\数据集\原数据集\CA-CondMat.mtx')

# 将矩阵写入.txt文件
with open(r'C:\Users\HP\Desktop\数据集\原数据集\CA-CondMat.txt', 'w') as file:
    for row in matrix:
        file.write(' '.join(str(val) for val in row) + '\n')
