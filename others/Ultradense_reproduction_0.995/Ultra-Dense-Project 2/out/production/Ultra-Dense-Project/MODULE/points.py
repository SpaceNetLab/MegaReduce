from global_land_mask import globe
import random


# 输入经纬度，判断是否在陆地上
# latitude>0为北纬,<0为南纬,=0在赤道上
# longitude>0为东经,<0为西经,=0在本初子午线
def is_land(latitude,longitude):
    return globe.is_land(latitude,longitude)


points=[]
while len(points) < 1000:
    longitude = random.uniform(-180, 180)
    latitude = random.uniform(-90, 90)
    if is_land(latitude , longitude):
        points.append([longitude, latitude])

# 指定输出文件名
output_file = "points.txt"

# 将二维列表内容写入文件
with open(output_file, 'w') as file:
    for row in points:
        # 将维度中的每个元素转换为字符串，并用空格拼接
        row_str = '\t'.join(str(item) for item in row)
        # 将每个维度写入文件，并在末尾加上换行符
        file.write(row_str + '\n')