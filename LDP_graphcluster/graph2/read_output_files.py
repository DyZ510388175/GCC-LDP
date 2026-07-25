import os
import re
import pandas as pd

# 定义输入文件夹路径
input_folder = r'../output'  # 替换为实际文件夹路径
output_folder = r'../output/out'  # 替换为实际文件夹路径
# 创建文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 获取文件夹中的所有文件
file_list = os.listdir(input_folder)

# 遍历文件列表
for file_name in file_list:
    # 提取文件名中的前缀、后缀和名字
    if file_name.startswith('comparison_') and file_name.endswith('_mean.txt'):
        prefix = 'comparison_'
        suffix = '_mean'
        name = file_name[len(prefix):-len(suffix)]  # 去掉前缀和后缀后的部分

        file_path = os.path.join(input_folder, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

            # 使用正则表达式提取多个内容块
            content_blocks = re.split(r'\n\n', file_content)  # 使用两个换行符分隔内容块

            # 初始化存储数据的列表
            data_list = []

            # 解析每个内容块并提取数据
            for block in content_blocks:
                # print('block:',block)
                algorithm_match = re.search(r'#--- (.*?) ---- (\d+)----#', block)
                if algorithm_match:
                    algorithm = algorithm_match.group(1).strip()
                    privacy_budget = int(algorithm_match.group(2).strip())  # 将隐私预算转换为整数

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
                    # print('entropy_match:', entropy_match)
                    entropy = entropy_match.group(1).strip()

                    data_list.append([algorithm, privacy_budget, modularity, nmi, f1_score, ari, ami, entropy])

            # 创建DataFrame
            df = pd.DataFrame(data_list,
                              columns=['Algorithm', 'privacy_budget', 'Modularity', 'Normalized Mutual Information',
                                       'F1 Score',
                                       'Adjusted Rand Index', 'Adjusted Mutual Information', 'Relative Entropy'])

            # 根据隐私预算和算法排序DataFrame
            df = df.sort_values(by=['privacy_budget', 'Algorithm'])

            # 重新排列DataFrame，以Algorithm为行索引，privacy_budget为列索引
            result_df = df.pivot(index='Algorithm', columns='privacy_budget')

            # 生成输出文件名
            output_file_name = f"{prefix}_{name}.csv"

            # 保存结果到CSV文件
            output_path = os.path.join(output_folder, output_file_name)
            result_df.to_csv(output_path)

            print(f"处理完成：{output_path}")

    elif file_name.startswith('parameter_') and file_name.endswith('_mean.txt'):
            prefix = 'parameter_'
            suffix = '_mean'
            name = file_name[len(prefix) + 1:-len(suffix) - 1]  # 去掉前缀和后缀后的部分
            # 读取文本文件内容
            file_path = os.path.join(input_folder, file_name)
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
                                  columns=['threshold_d', 'threshold_beta', 'Modularity', 'Normalized Mutual Information',
                                           'F1 Score',
                                           'Adjusted Rand Index', 'Adjusted Mutual Information', 'Relative Entropy'])

                # 根据隐私预算和算法排序DataFrame
                df = df.sort_values(by=['threshold_d', 'threshold_beta'])

                # 重新排列DataFrame，以Algorithm为行索引，privacy_budget为列索引
                result_df = df.pivot(index='threshold_d', columns='threshold_beta')

                # 生成输出文件名
                output_file_name = f"{prefix}_{name}.csv"

                # 保存结果到CSV文件
                output_path = os.path.join(output_folder, output_file_name)
                result_df.to_csv(output_path)

                print(f"处理完成：{output_path}")
