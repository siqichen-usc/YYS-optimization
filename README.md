# YYS-optimization

阴阳师是我自己很喜欢的手机游戏，最近出了一个新活动————**阴阳师万事屋**，为了收益最大化，就基于Python用gurobi写了一个优化。

## 具体功能
- 生成长期经营计划 (短至几小时，多达几天，仅考虑自然恢复)
- 生成短期经营计划（适合未来几小时只想收一次或者几次菜，不想调整纸人设置的小伙伴）
- 计算最优精英调查选择（**注意**输入合适的长期计划时间，比如**24H!**）

## 使用步骤
- **使用前提：安装 Python** 
- 如果没有安装 Python 的小伙伴就不建议用了，因为步骤可能过于繁琐

### Step 1: 安装 Gurobi
1. 前往https://www.gurobi.com/downloads/gurobi-software/ ，选择合适版本的 Gurobi Optimizer 并安装
2. 前往http://www.gurobi.com/downloads/user/licenses/free-academic ，注册后申请免费学术许可证（free academic license）
> **注意：只有在获得并使用了许可证后，才可以使用gurobi！！！**
3. 下载许可证文件，并在终端内运行以下指令，**请把示例中的许可证换成你个人的许可证**

```grbgetkey ae36ac20-16e6-acd2-f242-4da6e765fa0a```

### Step 2: 下载并填写 Input.xlsx
- **注意：不要直接移动单元格！不要直接移动单元格！不要直接移动单元格！**
<img src="Input使用说明.png"
  alt="Markdown Monster icon"
  style="float: middle; margin-right: 10px;" />

### Step 3: 计算优化方案/最优精英调查选择
- **生成长期 & 短期经营计划**
1. 下载 YYS.py,并与Input.xlsx放在同一个文件夹中
2. 打开终端，并进入文件所在文件夹
```cd Downloads\YYS_Optimization ```
3. 运行优化程序,如果input.xlsx被改名了，记得相应调整指令哦
```python YYS.py Input.xlsx```

- **生成精英调查最优解**
1. 下载 choice.py,并与Input.xlsx放在同一个文件夹中
2. 打开终端，并进入文件所在文件夹
```cd Downloads\YYS_Optimization ```
3. 运行优化程序,如果input.xlsx被改名了，记得相应调整指令哦
```python choice.py Input.xlsx```

### Step 4: 理解优化内容
1. 
