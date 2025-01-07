import math
import random
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil


def ClearFuncDir(): # 用于初始化文件夹
    # 清除
    try:
       shutil.rmtree('functions')
    except:
        pass
    try:
        os.makedirs("functions")
    except:
        pass


# 初始变量
size = 7 # 大小（2**size）

Undulating = 250 # 起伏（0~255 最佳）

Benchmark = -50 # 基准坐标

SeaLevel = -2 # 海平面 （基于基准坐标）

# 文件路径

# 可直接导出至行为包内
'''
FuncPath =  (os.getenv("LOCALAPPDATA") + \
             r'\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\development_behavior_packs\YourPack')
'''
FuncPath = r'.'

# 树
TreePos = []  # 位置
CanSpawnTree = None # 临时变量(控制树的生成)
TreeSpawn = True # 是否生成树


# 花朵种类
flower = ['dandelion', 'poppy', 'azure_bluet', 'red_tulip', 'orange_tulip', 'pink_tulip', 'oxeye_daisy', 'cornflower']




# 随机函数
def rand(x): # 概率为 1/x
    return random.randint(1, x) == 1


def fade(x):# fade函数
    y = 6 * x ** 5 - 15 * x ** 4 + 10 * x ** 3
    return y



def random_gradient():
    x = 2 * math.pi * random.random()
    gradient_vector = np.array([math.cos(x), math.sin(x)])
    return gradient_vector



# 随机梯度向量
map = np.zeros((2 ** size, 2 ** size))


for i in range(size - 3):
    length = 2 ** (size - i)
    row = 2 ** i

    gradient = []
    for y_row in range(row + 1):
        gradient_row = []
        for x_row in range(row + 1):
            gradient_row.append(random_gradient())
        gradient.append(gradient_row)

    for chunk in range(row ** 2):
        for y in range(length):
            for x in range(length):
                x_position = x / (length - 1)
                y_position = y / (length - 1)
                dot_point_a = np.dot(gradient[chunk % row][chunk // row], np.array([x_position, y_position]))
                dot_point_b = np.dot(gradient[chunk % row + 1][chunk // row], np.array([1 - x_position, y_position]))
                dot_point_c = np.dot(gradient[chunk % row][chunk // row + 1], np.array([x_position, 1 - y_position]))
                dot_point_d = np.dot(gradient[chunk % row + 1][chunk // row + 1],
                                     np.array([1 - x_position, 1 - y_position]))
                height_a = dot_point_a * fade(1 - x_position)
                height_a = height_a + dot_point_b * fade(x_position)
                height_a = height_a * fade(1 - y_position)
                height_b = dot_point_c * fade(1 - x_position)
                height_b = height_b + dot_point_d * fade(x_position)
                height_b = height_b * fade(y_position)
                height = height_a + height_b
                map[length * (chunk % row) + x, length * (chunk // row) + y] += 2 * height / row


# 生成地形
map = map / 10 * Undulating # 起伏运算

for y in range(2 ** size):
    for x in range(2 ** size):
        if map[x][y] < -6:
            map[x][y] = map[x][y] / 2
        if map[x][y] < 0:
            map[x][y] = map[x][y] / 2
map = map.astype(int)
map.reshape(2 ** size, 2 ** size) # 高度处理

# 图像展示
plt.imshow(map, cmap='gray')
plt.show()

# 修改路径
os.chdir(FuncPath)

# 初始化
ClearFuncDir()

# func 打开文件
func = open('functions/func1.mcfunction', 'a')

cmd = 0
for y in range(2 ** size):
    for x in range(2 ** size):
        if map[x][y] > SeaLevel:
            print('setblock', x, map[x][y] + Benchmark, y, 'grass', sep=' ', end='\n', file=func)
            print('fill', x, map[x][y] - 1 + Benchmark, y,  x, map[x][y] - 3 + Benchmark, y,'dirt', sep=' ', end='\n', file=func)
            cmd += 2

            # 花草树木
            if rand(4):
                if rand(12):

                    CanSpawnTree = True # 默认可生成
                    for i in TreePos:  # 判断是否能生成树
                        if abs(i[0] - x) + abs(i[1] - y) < 5:  # 如果距离不合理
                            CanSpawnTree = False # 取消生成

                    if rand(8) and CanSpawnTree and TreeSpawn:
                        # 树
                        print('structure load tree' + str(random.randint(1, 5)), x - 2, map[x][y] + 1 + Benchmark,
                              y - 2, \
                              str(random.choice([0, 90, 180, 270])) + '_degrees', sep=' ', end='\n', file=func)
                        TreePos.append([x, y])
                        cmd += 1
                    else:
                        # 花
                        print('setblock', x, map[x][y] + 1 + Benchmark, y, random.choice(flower), 'keep', sep=' ',
                              end='\n', file=func)
                        cmd += 1
                else:
                    # 草
                    print('setblock', x, map[x][y] + 1 + Benchmark, y, 'short_grass keep', sep=' ', end='\n', file=func)
                    cmd += 1

        elif map[x][y] == SeaLevel:
            print('setblock', x, map[x][y] - 1 + Benchmark, y, 'stone', sep=' ', end='\n', file=func)
            print('setblock', x, map[x][y] + Benchmark, y, 'sand', sep=' ', end='\n', file=func)
            cmd += 2

        else:
            print('setblock', x, map[x][y] - 1 + Benchmark, y, 'stone', sep=' ', end='\n', file=func)
            print('setblock', x, map[x][y] + Benchmark, y, 'sand', sep=' ', end='\n', file=func)
            print('setblock', x, SeaLevel + Benchmark, y, 'water', sep=' ', end='\n', file=func)
            cmd += 3

            # 海草
            if map[x][y] < -1 and rand(5):
                print('setblock', x, map[x][y] + 1 + Benchmark, y, 'seagrass', sep=' ', end='\n', file=func)
                cmd += 1
            elif map[x][y] < 0 and rand(8):
                print('setblock', x, map[x][y] + 1 + Benchmark, y, 'seagrass', sep=' ', end='\n', file=func)
                cmd += 1

        #############

        # 打开文件
        if cmd > 9997:
            func.close()
            func = open('functions/func2.mcfunction', 'a')
        if cmd > 19997:
            func.close()
            func = open('functions/func3.mcfunction', 'a')
        if cmd > 29997:
            func.close()
            func = open('functions/func4.mcfunction', 'a')
        if cmd > 39997:
            func.close()
            func = open('functions/func5.mcfunction', 'a')
        if cmd > 49997:
            func.close()
            func = open('functions/func6.mcfunction', 'a')
        if cmd > 59997:
            func.close()
            func = open('functions/func7.mcfunction', 'a')
        if cmd > 69997:
            func.close()
            func = open('functions/func8.mcfunction', 'a')
        if cmd > 79997:
            func.close()
            func = open('functions/func9.mcfunction', 'a')
        if cmd > 89997:
            func.close()
            func = open('functions/func10.mcfunction', 'a')
        if cmd > 99997:
            func.close()
            func = open('functions/func11.mcfunction', 'a')
        if cmd > 109997:
            func.close()
            func = open('functions/func12.mcfunction', 'a')
        if cmd > 119997:
            func.close()
            func = open('functions/func13.mcfunction', 'a')
        if cmd > 129997:
            func.close()
            func = open('functions/func14.mcfunction', 'a')
        if cmd > 139997:
            func.close()
            func = open('functions/func15.mcfunction', 'a')
        if cmd > 149997:
            func.close()
            func = open('functions/func16.mcfunction', 'a')
        if cmd > 159997:
            func.close()
            func = open('functions/func17.mcfunction', 'a')
        if cmd > 169997:
            func.close()
            func = open('functions/func18.mcfunction', 'a')
        if cmd > 179997:
            func.close()
            func = open('functions/func19.mcfunction', 'a')
        if cmd > 189997:
            func.close()
            func = open('functions/func20.mcfunction', 'a')

func.close()
print(cmd)
# 生成 .mcfunction文件
