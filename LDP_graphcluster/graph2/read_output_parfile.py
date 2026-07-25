import re
import pandas as pd

# comparison_musae_PTBR_edges_sample_mean 'musae_PTBR_edges_sample', 'facebook_combined_sample', 'musae_ES_edges_sample'
filename = 'parameter_musae_PTBR_edges_sample_mean'
# 读取文本文件内容
file_path = r'../output/' + filename + '.txt'  # 替换为实际文件路径
with open(file_path, 'r') as file:
    file_content = file.read()

# 使用正则表达式提取多个内容块
content_blocks = re.split(r'\n\n', file_content)  # 使用两个换行符分隔内容块

# 初始化存储数据的列表
data_list = []

# 解析每个内容块并提取数据
for block in content_blocks:
    # print('block:',block)
    parameter_match = re.search(r'threshold_d,\s*threshold_beta:\s*(\S+)\s*(\S+)', block)
    if parameter_match:
        threshold_d = parameter_match.group(1).strip()
        threshold_beta = parameter_match.group(2).strip()

        modularity_match = re.search(r'Modularity: (.*?)\n', block)
        modularity = modularity_match.group(1).strip()

        nmi_match = re.search(r'Normalized Mutual Information: (.*?)\n', block)
        nmi = nmi_match.group(1).strip()

        f1_score_match = re.search(r'F1 Score: (.*?)\n', block)
        f1_score = f1_score_match.group(1).strip()

        ari_match = re.search(r'Adjusted Rand Index: (.*?)\n', block)
        ari = ari_match.group(1).strip() if ari_match else ''

        ami_match = re.search(r'Adjusted Mutual Information: (.*?)\n', block)
        ami = ami_match.group(1).strip() if ami_match else ''
        # print('ami_match:', ami_match)

        entropy_match = re.search(r'Relative Entropy: (.*?)(?:\n|$)', block)
        print('entropy_match:', entropy_match)
        entropy = entropy_match.group(1).strip()

        data_list.append([threshold_d, threshold_beta, modularity, nmi, f1_score, ari, ami, entropy])

# 创建DataFrame
df = pd.DataFrame(data_list,
                  columns=['threshold_d', 'threshold_beta', 'Modularity', 'Normalized Mutual Information', 'F1 Score',
                           'Adjusted Rand Index', 'Adjusted Mutual Information', 'Relative Entropy'])

# 根据隐私预算和算法排序DataFrame
df = df.sort_values(by=['threshold_d', 'threshold_beta'])

# 重新排列DataFrame，以Algorithm为行索引，privacy_budget为列索引
result_df = df.pivot(index='threshold_d', columns='threshold_beta')

# 将结果保存到CSV文件
result_df.to_csv(r'../output/out/' + filename + '.csv')

print("结果已保存到 output.csv 文件中。")
