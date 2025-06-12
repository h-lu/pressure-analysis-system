# ============================================================================
# 压力数据快速分析 - 极简版
# 使用tidyverse，交互式，易修改
# ============================================================================

# 清理环境并加载包
rm(list = ls())

# 检查并安装必要的包
required_packages <- c("tidyverse", "ggthemr", "showtext", "plotly", "GGally", "patchwork", "cluster")
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) {
  install.packages(new_packages)
  cat("已安装新包:", paste(new_packages, collapse = ", "), "\n")
}

library(tidyverse)


# ============================================================================
# 主题和字体设置
# ============================================================================
library(ggthemr)
library(showtext)
# 添加中文字体支持
font_add("PingFang", "/System/Library/Fonts/PingFang.ttc")
font_add("Hiragino", "/System/Library/Fonts/Hiragino Sans GB.ttc")
showtext_auto()

# 设置ggthemr主题 - 选择干净的主题
ggthemr('fresh', layout = 'clean', spacing = 2, type = 'outer')

# 自定义主题设置
custom_theme <- theme_minimal() +
  theme(
    # 字体设置
    text = element_text(family = "PingFang", size = 12),
    plot.title = element_text(family = "PingFang", size = 16, face = "bold", hjust = 0.5, margin = margin(b = 20)),
    plot.subtitle = element_text(family = "PingFang", size = 12, hjust = 0.5, margin = margin(b = 15)),
    axis.title = element_text(family = "PingFang", size = 11),
    axis.text = element_text(family = "PingFang", size = 10),
    legend.title = element_text(family = "PingFang", size = 11),
    legend.text = element_text(family = "PingFang", size = 10),
    strip.text = element_text(family = "PingFang", size = 11, face = "bold"),
    
    # 背景和网格
    panel.background = element_rect(fill = "white", color = NA),
    plot.background = element_rect(fill = "white", color = NA),
    panel.grid.major = element_line(color = "grey90", linewidth = 0.5),
    panel.grid.minor = element_line(color = "grey95", linewidth = 0.25),
    
    # 图例设置
    legend.position = "bottom",
    legend.box = "horizontal",
    legend.margin = margin(t = 10),
    
    # 坐标轴
    axis.line = element_line(color = "grey30", linewidth = 0.5),
    axis.ticks = element_line(color = "grey30", linewidth = 0.5),
    
    # 分面设置
    strip.background = element_rect(fill = "grey95", color = "grey80"),
    panel.spacing = unit(1, "lines")
  )

# 设置为默认主题
theme_set(custom_theme)

# 自定义颜色调色板
custom_colors <- c("#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E", "#7209B7")
scale_colour_discrete <- function(...) scale_colour_manual(values = custom_colors)
scale_fill_discrete <- function(...) scale_fill_manual(values = custom_colors)



# ============================================================================
# 参数设置（可自由修改）
# ============================================================================
target_forces <- c(5, 25, 50)  # 目标力值
tolerance_abs <- 2             # 绝对容差 (N) - 例如: ±2N
tolerance_pct <- 5             # 百分比容差 (%) - 例如: ±5%
window_size <- 10              # 移动平均窗口
success_trend_batch_size <- 10

# 容差说明:
# - 绝对容差: 固定的数值范围，如 ±2N
# - 百分比容差: 相对于目标值的百分比，如 ±5%
# - 综合判断: 数据点必须同时满足两种容差才算合格
# 例如: 目标25N时，绝对容差±2N = [23,27]N，百分比容差±5% = [23.75,26.25]N
#       实际合格范围是两者的交集 = [23.75,27]N

# ============================================================================
# 数据加载
# ============================================================================


# # 生成示例数据
# set.seed(123)
# tibble(
#   序号 = 1:100,
#   X = round(rnorm(100, 100, 5), 1),
#   Y = round(rnorm(100, 100, 5), 1),
#   Z = round(rnorm(100, 100, 5), 1),
#   力值 = paste0(round(rep(target_forces, length.out = 100) + rnorm(100, 0, 2), 1), "N")
# ) %>% 
#   write_csv("demo_data.csv")

data_file <- "demo_data.csv"


# 读取并清理数据
data <- read_csv(data_file) %>%
  rename(sequence = 1, x = 2, y = 3, z = 4, force = 5) %>%
  mutate(force = as.numeric(str_extract(force, "\\d+"))) %>%
  # filter(!is.na(force)) %>%
  # 创建目标力值匹配变量
  mutate(
    target_force = map_dbl(force, ~{
      distances <- abs(.x - target_forces)
      target_forces[which.min(distances)]
    }),
    # 计算绝对偏差和百分比偏差
    deviation_abs = force - target_force,
    deviation_pct = (force - target_force) / target_force * 100,
    # 计算容差限制
    tolerance_abs_limit = tolerance_abs,
    tolerance_pct_limit = target_force * tolerance_pct / 100,
    # 判断是否在容差内（同时满足绝对容差和百分比容差）
    within_tolerance_abs = abs(deviation_abs) <= tolerance_abs_limit,
    within_tolerance_pct = abs(deviation_abs) <= tolerance_pct_limit,
    within_tolerance = within_tolerance_abs & within_tolerance_pct
  )

print(paste("数据维度:", nrow(data), "行", ncol(data), "列"))
print(paste("匹配到的目标力值:", paste(unique(data$target_force), collapse = ", ")))

# ============================================================================
# 快速统计
# ============================================================================

# 目标力值分析（使用匹配变量）
target_analysis <- data %>%
  group_by(target_force) %>%
  summarise(
    数据点数 = n(),
    成功率_综合 = round(sum(within_tolerance)/n()*100, 1),
    成功率_绝对 = round(sum(within_tolerance_abs)/n()*100, 1),
    成功率_百分比 = round(sum(within_tolerance_pct)/n()*100, 1),
    平均力值 = round(mean(force), 2),
    平均偏差_绝对 = round(mean(deviation_abs), 2),
    平均偏差_百分比 = round(mean(deviation_pct), 2),
    标准差 = round(sd(force), 2),
    最大偏差_绝对 = round(max(abs(deviation_abs)), 2),
    最大偏差_百分比 = round(max(abs(deviation_pct)), 2),
    绝对容差限制 = round(first(tolerance_abs_limit), 2),
    百分比容差限制 = round(first(tolerance_pct_limit), 2),
    .groups = 'drop'
  ) %>%
  arrange(target_force)

print("按目标力值分组的分析结果:")
print(target_analysis)

# ============================================================================
# 快速可视化
# ============================================================================

# 时间序列图（按目标力值着色）
data %>%
  ggplot(aes(sequence, force, color = factor(target_force))) +
  geom_line(alpha = 0.7) +
  geom_point(aes(shape = within_tolerance), alpha = 0.6) +
  geom_hline(aes(yintercept = target_force), color = "red", linetype = "dashed") +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  labs(title = "力值趋势（按目标力值分组）", 
       x = "序号", y = "力值(N)", color = "目标力值")

# 分布图（按目标力值分面）
data %>%
  ggplot(aes(force, fill = factor(target_force))) +
  geom_histogram(bins = 10, alpha = 0.7, position = "identity") +
  geom_vline(aes(xintercept = target_force), 
             color = "red", linetype = "dashed") +
  facet_wrap(~target_force, scales = "free", labeller = label_both) +
  labs(title = "力值分布（按目标力值分组）", 
       x = "力值(N)", y = "频次", fill = "目标力值")

# 绝对偏差箱线图
data %>%
  ggplot(aes(factor(target_force), deviation_abs, fill = factor(target_force))) +
  geom_boxplot(alpha = 0.7) +
  geom_hline(yintercept = 0, color = "red", linetype = "dashed") +
  geom_hline(yintercept = c(-tolerance_abs, tolerance_abs), 
             color = "orange", linetype = "dashed", size = 2) +
  labs(title = "绝对偏差分布（按目标力值分组）", 
       x = "目标力值(N)", y = "绝对偏差(N)", fill = "目标力值")

# 百分比偏差箱线图
data %>%
  ggplot(aes(factor(target_force), deviation_pct, fill = factor(target_force))) +
  geom_boxplot(alpha = 0.7) +
  geom_hline(yintercept = 0, color = "red", linetype = "dashed") +
  geom_hline(yintercept = c(-tolerance_pct, tolerance_pct), 
             color = "orange", linetype = "dashed", size = 2) +
  labs(title = "百分比偏差分布（按目标力值分组）", 
       x = "目标力值(N)", y = "百分比偏差(%)", fill = "目标力值")

# ============================================================================
# 多种空间可视化方法
# ============================================================================

# 方法1: 3维交互式散点图 (plotly)
library(plotly)

p_3d <- plot_ly(data, x = ~x, y = ~y, z = ~z, 
                color = ~factor(target_force), 
                symbol = ~within_tolerance,
                symbols = c('circle-open', 'circle'),
                text = ~paste("序号:", sequence, "<br>力值:", force, "N<br>目标:", target_force, "N")) %>%
  add_markers(size = 5) %>%
  layout(title = "3D交互式散点图 - 空间异常分布",
         scene = list(
           xaxis = list(title = "X坐标"),
           yaxis = list(title = "Y坐标"),
           zaxis = list(title = "Z坐标")
         ))
print(p_3d)

# 方法2: 分面2D散点图矩阵
library(GGally)

data %>%
  select(x, y, z, target_force, within_tolerance) %>%
  ggpairs(columns = 1:3,
          aes(color = factor(target_force), shape = within_tolerance),
          upper = list(continuous = "points"),
          lower = list(continuous = "points"),
          diag = list(continuous = "densityDiag")) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  labs(title = "XYZ坐标对比矩阵 - 异常点分布")

# 方法3: XY平面热力图（按target_force分面）
data %>%
  ggplot(aes(x, y)) +
  stat_density_2d_filled(alpha = 0.7) +
  geom_point(aes(color = within_tolerance, shape = within_tolerance), size = 2) +
  scale_color_manual(values = c("red", "blue"), name = "在容差内") +
  scale_shape_manual(values = c(4, 16), name = "在容差内") +
  facet_wrap(~target_force, labeller = label_both) +
  labs(title = "XY平面密度热力图 - 按目标力值分组", 
       x = "X坐标", y = "Y坐标")

# 方法4: 3D表面图（如果数据较规整）
# 创建网格化数据用于表面图
grid_data <- data %>%
  mutate(
    x_bin = round(x/5)*5,  # 网格化X
    y_bin = round(y/5)*5   # 网格化Y
  ) %>%
  group_by(x_bin, y_bin, target_force) %>%
  summarise(
    avg_z = mean(z),
    avg_force = mean(force),
    error_rate = 1 - mean(within_tolerance),
    .groups = 'drop'
  )

p_surface <- plot_ly() %>%
  add_trace(data = filter(grid_data, target_force == 5),
            x = ~x_bin, y = ~y_bin, z = ~error_rate,
            type = "scatter3d", mode = "markers",
            marker = list(size = ~avg_force*2, color = "red"),
            name = "目标5N") %>%
  add_trace(data = filter(grid_data, target_force == 25),
            x = ~x_bin, y = ~y_bin, z = ~error_rate,
            type = "scatter3d", mode = "markers",
            marker = list(size = ~avg_force*2, color = "green"),
            name = "目标25N") %>%
  add_trace(data = filter(grid_data, target_force == 50),
            x = ~x_bin, y = ~y_bin, z = ~error_rate,
            type = "scatter3d", mode = "markers",
            marker = list(size = ~avg_force*2, color = "blue"),
            name = "目标50N") %>%
  layout(title = "3D异常率分布图",
         scene = list(
           xaxis = list(title = "X坐标"),
           yaxis = list(title = "Y坐标"),
           zaxis = list(title = "异常率")
         ))
print(p_surface)

# 方法5: 并行坐标图 (使用GGally替代)
data_parallel <- data %>%
  select(x, y, z, force, target_force, within_tolerance) %>%
  mutate(target_force = factor(target_force))

ggparcoord(data_parallel, 
           columns = 1:4, 
           groupColumn = "target_force",
           alphaLines = 0.3,
           showPoints = TRUE) +
  scale_color_viridis_d() +
  labs(title = "并行坐标图 - 多维异常模式", color = "目标力值")

# 方法6: 分层2D投影图
# XY投影
p_xy <- data %>%
  ggplot(aes(x, y, color = factor(target_force))) +
  geom_point(aes(shape = within_tolerance, size = z), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 4), name = "Z坐标") +
  labs(title = "XY投影 (点大小=Z坐标)", color = "目标力值")

# XZ投影  
p_xz <- data %>%
  ggplot(aes(x, z, color = factor(target_force))) +
  geom_point(aes(shape = within_tolerance, size = y), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 4), name = "Y坐标") +
  labs(title = "XZ投影 (点大小=Y坐标)", color = "目标力值")

# YZ投影
p_yz <- data %>%
  ggplot(aes(y, z, color = factor(target_force))) +
  geom_point(aes(shape = within_tolerance, size = x), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 4), name = "X坐标") +
  labs(title = "YZ投影 (点大小=X坐标)", color = "目标力值")

# 组合投影图
library(patchwork)
(p_xy | p_xz) / p_yz

# 方法7: 空间聚类异常检测图
library(cluster)
coords_data <- data %>% select(x, y, z)
distances <- dist(coords_data)
hc <- hclust(distances)
data$cluster <- cutree(hc, k = 5)

data %>%
  ggplot(aes(x, y)) +
  geom_point(aes(color = factor(cluster), 
                 shape = within_tolerance,
                 size = abs(deviation_abs)), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 5), name = "绝对偏差") +
  facet_wrap(~target_force, labeller = label_both) +
  labs(title = "空间聚类 + 异常检测", 
       color = "空间聚类")

# ============================================================================
# 保存结果
# ============================================================================

# 保存清理后数据
write_csv(data, "clean_data.csv")

# 快速报告
cat("\n=== 快速分析报告 ===")
cat("\n数据点数:", nrow(data))
cat("\n力值范围:", round(min(data$force), 2), "-", round(max(data$force), 2), "N")
cat("\n平均力值:", round(mean(data$force), 2), "N")
cat("\n变异系数:", round(sd(data$force)/mean(data$force)*100, 1), "%")

# 按目标力值的详细报告
cat("\n\n按目标力值分组结果:")
for(i in 1:nrow(target_analysis)) {
  row <- target_analysis[i, ]
  cat("\n- 目标", row$target_force, "N:")
  cat(" 数据点", row$数据点数, "个")
  cat("\n  综合成功率:", row$成功率_综合, "% (绝对:", row$成功率_绝对, "%, 百分比:", row$成功率_百分比, "%)")
  cat("\n  平均偏差: 绝对", row$平均偏差_绝对, "N, 百分比", row$平均偏差_百分比, "%")
  cat("\n  容差限制: 绝对±", row$绝对容差限制, "N, 百分比±", row$百分比容差限制, "N")
}

print("\n✅ 分析完成！数据已保存到 clean_data.csv")

# ============================================================================
# 进阶分析（可选）
# ============================================================================

# 如果需要更详细分析，运行以下代码：

# 按目标力值分组的移动平均
library(slider)

data <- data %>%
  group_by(target_force) %>%
  arrange(sequence) %>%
  mutate(moving_avg = slide_dbl(force, mean, .before = window_size-1)) %>%
  ungroup()

# 按目标力值分组的异常值检测
outliers_by_target <- data %>%
  group_by(target_force) %>%
  mutate(
    Q1 = quantile(force, 0.25),
    Q3 = quantile(force, 0.75),
    IQR = Q3 - Q1,
    is_outlier = force < Q1 - 1.5*IQR | force > Q3 + 1.5*IQR
  ) %>%
  filter(is_outlier) %>%
  ungroup()

print(paste("异常值数量:", nrow(outliers_by_target)))

# 按目标力值分组的控制图
control_limits <- data %>%
  group_by(target_force) %>%
  summarise(
    center = mean(force),
    ucl = mean(force) + 3*sd(force),
    lcl = mean(force) - 3*sd(force),
    .groups = 'drop'
  )

data %>%
  ggplot(aes(sequence, force)) +
  geom_line(aes(color = factor(target_force))) +
  geom_hline(data = control_limits, aes(yintercept = center), color = "green") +
  geom_hline(data = control_limits, aes(yintercept = ucl), color = "red", linetype = "dashed") +
  geom_hline(data = control_limits, aes(yintercept = lcl), color = "red", linetype = "dashed") +
  facet_wrap(~target_force, scales = "free_y") +
  labs(title = "分组控制图", color = "目标力值")

# 成功率趋势分析
success_trend <- data %>%
  mutate(batch = ceiling(sequence / success_trend_batch_size)) %>%  # 每10个数据点为一批
  group_by(batch, target_force) %>%
  summarise(success_rate = mean(within_tolerance) * 100, .groups = 'drop')

success_trend %>%
  ggplot(aes(batch, success_rate, color = factor(target_force))) +
  geom_line() +
  geom_point() +
  labs(title = "成功率趋势", x = "批次", y = "成功率(%)", color = "目标力值")
