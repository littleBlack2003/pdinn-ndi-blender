# PDINN / NDI 模型：4K 无文字透明成图

## 当前交付

- `renders/PDINN_Jelly_Final_4K_Transparent.png`：3840 × 2304，原生 Blender Cycles，16-bit RGBA PNG
- `pdinn_jelly.blend`：可编辑工程，默认采用本次 4K 透明成图设置
- `renders/PDINN_Jelly_Clear_Draft.png`：保留先前 1200 × 720、48 采样的透明草稿，方便对照
- `checkpoints/pdinn_jelly_before_final4k.blend`：完整保留此前快速预览的工程设置

最终图没有标题、配比文字、图例或页脚。只有模型与真实 Alpha 通道，没有烘焙白色背景或棋盘格。凝胶保留半透明像素。不同应用可能用黑色、白色或棋盘格显示透明区域，这些不是文件背景。

## 本次最终渲染

- 实际像素：3840 × 2304，未放大草稿
- Cycles CPU，8 线程
- 自适应采样上限：512；最低采样：64；噪声阈值：0.01
- 总反弹 16，透射反弹 12，透明反弹 16
- PNG RGBA，每通道 16 bit
- 实际渲染用时：1891.28 秒（约 31.5 分钟）
- 当前 Blender 构建未包含 OpenImageDenoise，因此采用高采样原始出图；未进行降噪、锐化或 AI 图像替换

自适应采样会让已收敛像素提前结束，因此 512 是采样上限，不表示每个像素都恰好进行了 512 次采样。透明与高光处仍可能在 100% 放大时看到细微采样颗粒。

## 保留的模型

- PDINN：135 个，sRGB #F0B47C
- 聚合物核：141 个，sRGB #BE7A9A
- 8 条弯曲链，4 个分子深度层
- 镜头高度角 42°，侧向角 24°
- 凝胶尺寸、分子大小、分子几何、上下端连接、相机和灯光保持不变
- 颜色经过 sRGB 到线性转换；像素颜色正常受到高光、阴影和透射影响

RGBA 保留当前摄影棚灯光下的反光与透明效果；叠放到另一张背景图上，不会重新计算新背景的真实折射。

## 再次渲染

打开 `.blend` 后直接渲染即可采用当前 4K 配置。或从项目目录运行：

```sh
blender -b -t 8 --python scripts/render_final_4k.py
```

输出到 `renders/PDINN_Jelly_Final_4K_Transparent.png`。脚本在支持 OpenImageDenoise 的其他 Blender 构建中可自动使用该降噪器；本次交付明确未使用降噪。

如只需快速检查构图，可运行 `scripts/render_quality.py`，默认 1200 × 720、48 采样；这不会覆盖保存的 4K 工程配置。

`final4k_validation.json` 记录渲染配置、实际耗时、像素/Alpha 检查和场景内容不变性校验。其他 JSON 保留此前建模的验证记录。旧带文字项目在 `checkpoints/pdinn_jelly_before_textfree.blend`，旧排版源码归档在 `archive/labeled_layout_sources/`，不参与当前默认出图。

## 概念说明

PDINN 保留已确认的七个稠合六元环，NDI 保留四个稠合六元环。NDI 链按用户指定的上下 N–R 方向概念连接。图形省略完整原子标签、键级、羰基及共聚单元，是概念模型，不是完整化学结构或实测形貌。图标数量不表示化学计量配比。
