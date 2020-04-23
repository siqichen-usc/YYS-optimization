# YYS-optimization

阴阳师是我自己很喜欢的手机游戏，最近出了一个新活动————阴阳师万事屋，为了收益最大化，就基于python用gurobi写了一个优化。

## 具体功能
- 生成长期计划 (短至几小时，多达几天，仅考虑自然恢复)
- 生成短期计划（适合未来几小时只想收一次或者几次菜，不想调整纸人设置的小伙伴）
- 计算精英调查（**注意**输入合适的长期计划时间，比如**24H!**）

## 使用步骤
### Step 1: 安装 Gurobi
1. 前往https://www.gurobi.com/downloads/gurobi-software/ ，选择合适版本的 Gurobi Optimizer 并安装
2. 前往http://www.gurobi.com/downloads/user/licenses/free-academic ，注册后申请免费学术许可证（free academic license）
- **注意：只有在获得并使用了许可证后，才可以使用gurobi！！！**
3. 下载许可证文件，并在电脑终端内运行以下指令，**请把示例中的许可证换成你个人的许可证**
```grbgetkey ae36ac20-16e6-acd2-f242-4da6e765fa0a```
