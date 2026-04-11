# Flatlander

Flatlander 的灵感来自于 [primitive](https://github.com/fogleman/primitive/)，后者是一个知名项目，使用简单的几何图形近似复杂图像。

不过，primitive 使用 Go 语言实现，其文档中指出的编译方式似乎已经失效。考虑到我不熟悉 Go 语言，我决定使用 Python 实现类似的功能，加入更灵活的配置选项。

## 简介

Flatlander 使用随机生成的简单几何图形（shapes）逐步逼近输入图像，并可导出为 SVG 或常见光栅格式。项目以可扩展的 shapes 插件化设计为目标，方便添加自定义形状。

## 安装/执行

- 使用 Poetry:

```bash
poetry install
poetry run flatlander INPUT.png OUTPUT.svg -a 0.75 -n 256 -t 24
```

- 使用 pip:

```bash
python -m pip install -e .
flatlander INPUT.png OUTPUT.svg -a 0.75 -n 256 -t 24
```

## 快速使用

- `INPUT`：输入图像（将自动转换为 RGBA）。
- `OUTPUT`：输出文件，扩展名为 `.svg` 时生成矢量输出，否则为光栅格式（由 PIL 处理）。
- 常用参数：
  - `-a/--alpha`：形状的透明度（0.0-1.0）。
  - `-t/--trials`：每次尝试多少随机形状（越大通常结果越好但更慢）。
  - `-n/--num-shapes`：要添加的形状总数。
  - `-b/--background-color`：背景色，可为 `average`、`mode` 或颜色字符串（如 `#RRGGBBAA`）。
  - `--seed`：随机种子（可复现结果）。

可以使用 `--help` 查看完整参数列表。

## 作为库使用（API）

请自行阅读源码解决问题。

## Shapes 插件约定

Shapes 模块放在 `shapes/` 目录下，项目通过内部的 registry 加载这些模块。每个 shape 模块应该导出以 `random_` 为前缀的工厂函数，例如 `random_circle(width, height)`。

工厂函数应返回 `(shape_drawer, cmds)`：
- `shape_drawer(draw, color=None)`：一个可调用对象，接收 `PIL.ImageDraw` 实例并在其上绘制（用于 mask 计算与合成）。
- `cmds`：用于导出 SVG 的命令列表（可以是字典序列，`svg_export.py` 会根据这些描述生成相应图形）。

具体示例可以参考项目文件。

## 许可

本项目使用 MIT 许可，详见 `LICENSE` 文件。

## 其他

本 README 由 GPT-5 mini 辅助生成。
