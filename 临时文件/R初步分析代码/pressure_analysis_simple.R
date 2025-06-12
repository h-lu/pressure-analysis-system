# ============================================================================
# 压力采集数据分析 - 简洁交互式版本
# 使用tidyverse，无函数封装，方便修改和运行
# ============================================================================

# 清理环境
rm(list = ls())

# 检查并安装必要的包
required_packages <- c("tidyverse", "readr", "ggplot2", "dplyr", "slider", "broom")
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) {
  install.packages(new_packages)
  cat("已安装新包:", paste(new_packages, collapse = ", "), "\n")
}

# 加载必要的包
library(tidyverse)
library(readr)
library(ggplot2)
library(dplyr)
library(slider)
library(broom)
library(GGally)

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


print("开始压力数据分析...")

# ============================================================================
# 1. 数据加载
# ============================================================================


# # 生成示例数据
# set.seed(123)
# n <- 100
# target_forces <- c(5, 25, 50)

# sample_data <- tibble(
# 序号 = 1:n,
# X = round(rnorm(n, 100, 5), 1),
# Y = round(rnorm(n, 100, 5), 1), 
# Z = round(rnorm(n, 100, 5), 1),
# 力值 = map_dbl(1:n, ~{
#     target <- sample(target_forces, 1)
#     noise <- rnorm(1, 0, target * 0.08)
#     trend <- .x * 0.001
#     round(target + noise + trend, 1)
# }) %>% paste0("N")
# )

# write_csv(sample_data, "sample_data.csv")


# 读取数据
data_file <- "demo_data.csv"
raw_data <- read_csv(data_file, locale = locale(encoding = "UTF-8"))

# 查看原始数据
print("原始数据预览:")
print(raw_data)
print(paste("数据维度:", nrow(raw_data), "行", ncol(raw_data), "列"))

# ============================================================================
# 2. 数据清理
# ============================================================================

print("\n开始数据清理...")

# 标准化列名
colnames(raw_data) <- c("sequence", "x", "y", "z", "force")

# 清理力值列（移除单位）
data <- raw_data %>%
  mutate(force = as.numeric(str_remove_all(force, "[^0-9.-]")))

print("清理后数据预览:")
print(head(data))
print(paste("清理后维度:", nrow(data), "行", ncol(data), "列"))

# ============================================================================
# 3. 数据质量检查
# ============================================================================

print("\n=== 数据质量检查 ===")

# 基本统计
data_summary <- data %>%
  summarise(
    总行数 = n(),
    缺失值 = sum(is.na(.)),
    重复行 = sum(duplicated(.)),
    力值最小值 = min(force, na.rm = TRUE),
    力值最大值 = max(force, na.rm = TRUE),
    力值均值 = mean(force, na.rm = TRUE),
    力值标准差 = sd(force, na.rm = TRUE),
    负值数量 = sum(force < 0, na.rm = TRUE),
    零值数量 = sum(force == 0, na.rm = TRUE)
  )

print(data_summary)

# 坐标范围检查
coord_summary <- data %>%
  select(x, y, z) %>%
  summarise_all(list(
    最小值 = ~min(., na.rm = TRUE),
    最大值 = ~max(., na.rm = TRUE),
    唯一值数量 = ~n_distinct(.)
  ))

print("坐标范围:")
print(coord_summary)

# ============================================================================
# 4. 基础统计分析
# ============================================================================

print("\n=== 基础统计分析 ===")

# 整体力值统计
overall_stats <- data %>%
  summarise(
    样本数 = n(),
    均值 = mean(force),
    中位数 = median(force),
    标准差 = sd(force),
    最小值 = min(force),
    最大值 = max(force),
    Q25 = quantile(force, 0.25),
    Q75 = quantile(force, 0.75),
    变异系数 = sd(force) / mean(force) * 100
  ) %>%
  mutate_if(is.numeric, round, 3)

print("力值整体统计:")
print(overall_stats)

# 目标力值分析
target_forces <- c(5, 25, 50)  # 目标力值
tolerance_abs <- 2             # 绝对容差 (N) - 例如: ±2N
tolerance_pct <- 5             # 百分比容差 (%) - 例如: ±5%
window_size <- 10              # 移动窗口大小

# 容差说明:
# - 绝对容差: 固定的数值范围，如 ±2N
# - 百分比容差: 相对于目标值的百分比，如 ±5%
# - 综合判断: 数据点必须同时满足两种容差才算合格
# 例如: 目标25N时，绝对容差±2N = [23,27]N，百分比容差±5% = [23.75,26.25]N
#       实际合格范围是两者的交集 = [23.75,27]N

# 为每个数据点匹配最近的目标力值并计算容差
data_with_target <- data %>%
  mutate(
    # 使用purrr风格匹配最近的目标力值
    target_force = map_dbl(force, ~ target_forces[which.min(abs(.x - target_forces))]),
    # 计算偏差和容差
    deviation_abs = force - target_force,
    deviation_pct = (force - target_force) / target_force * 100,
    tolerance_abs_limit = tolerance_abs,
    tolerance_pct_limit = target_force * tolerance_pct / 100,
    # 判断容差
    within_tolerance_abs = abs(deviation_abs) <= tolerance_abs_limit,
    within_tolerance_pct = abs(deviation_abs) <= tolerance_pct_limit,
    within_tolerance = within_tolerance_abs & within_tolerance_pct
  )

target_analysis <- data_with_target %>%
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

print("目标力值分析:")
print(target_analysis)

# ============================================================================
# 5. 趋势分析（按目标力值分组）
# ============================================================================

print("\n=== 趋势分析 ===")

# 整体趋势分析
overall_trend_model <- lm(force ~ sequence, data = data_with_target)
overall_trend_summary <- summary(overall_trend_model)

overall_trend_stats <- tibble(
  分组 = "整体",
  斜率 = overall_trend_model$coefficients[2],
  截距 = overall_trend_model$coefficients[1],
  R平方 = overall_trend_summary$r.squared,
  p值 = overall_trend_summary$coefficients[2, 4]
) %>%
  mutate_if(is.numeric, round, 6)

# 按目标力值分组的趋势分析
grouped_trend_stats <- data_with_target %>%
  group_nest(target_force) %>%
  mutate(
    # 使用map拟合模型
    model = map(data, ~ lm(force ~ sequence, data = .x)),
    # 使用broom提取模型统计信息
    glance_results = map(model, broom::glance),
    tidy_results = map(model, broom::tidy)
  ) %>%
  # 提取需要的统计量
  mutate(
    分组 = paste0("目标", target_force, "N"),
    R平方 = map_dbl(glance_results, ~ .x$r.squared),
    斜率 = map_dbl(tidy_results, ~ filter(.x, term == "sequence")$estimate),
    截距 = map_dbl(tidy_results, ~ filter(.x, term == "(Intercept)")$estimate),
    p值 = map_dbl(tidy_results, ~ filter(.x, term == "sequence")$p.value)
  ) %>%
  select(分组, 斜率, 截距, R平方, p值) %>%
  mutate_if(is.numeric, round, 6)

# 合并趋势分析结果
trend_stats <- bind_rows(overall_trend_stats, grouped_trend_stats)

print("趋势分析结果:")
print(trend_stats)

# 趋势解释
cat("\n趋势分析解释:")
for(i in 1:nrow(trend_stats)) {
  row <- trend_stats[i, ]
  if(row$p值 < 0.05) {
    trend_direction <- ifelse(row$斜率 > 0, "上升", "下降")
    cat("\n-", row$分组, ": 显著", trend_direction, "趋势 (斜率:", row$斜率, ", p值:", row$p值, ")")
  } else {
    cat("\n-", row$分组, ": 无显著趋势 (p值:", row$p值, ")")
  }
}

# 移动平均（按目标力值分组）
if(nrow(data_with_target) >= 20) {
  
  data_with_target <- data_with_target %>%
    group_by(target_force) %>%
    arrange(sequence) %>%
    mutate(
      移动平均 = slider::slide_dbl(force, mean, .before = window_size-1, .complete = TRUE),
      移动标准差 = slider::slide_dbl(force, sd, .before = window_size-1, .complete = TRUE)
    ) %>%
    ungroup()
  
  print(paste("\n已计算分组移动平均，窗口大小:", window_size))
}

# ============================================================================
# 5.5. 高级时间序列分析
# ============================================================================

print("\n=== 高级时间序列分析 ===")

# 1. 异常值检测（按组）
outlier_analysis <- data_with_target %>%
  group_by(target_force) %>%
  mutate(
    Q1 = quantile(force, 0.25),
    Q3 = quantile(force, 0.75),
    IQR = Q3 - Q1,
    is_outlier = force < Q1 - 1.5*IQR | force > Q3 + 1.5*IQR,
    # Z-score异常检测
    z_score = abs((force - mean(force)) / sd(force)),
    is_z_outlier = z_score > 3
  ) %>%
  ungroup()

outlier_summary <- outlier_analysis %>%
  group_by(target_force) %>%
  summarise(
    总数据点 = n(),
    IQR异常值 = sum(is_outlier),
    Z异常值 = sum(is_z_outlier),
    IQR异常率 = round(sum(is_outlier)/n()*100, 2),
    Z异常率 = round(sum(is_z_outlier)/n()*100, 2),
    .groups = 'drop'
  )

print("异常值检测结果:")
print(outlier_summary)

# 2. 稳定性分析（游程检验）- 现代化版本
stability_analysis <- data_with_target %>%
  group_nest(target_force) %>%
  mutate(
    # 使用map计算游程统计
    run_stats = map(data, ~ {
      force_data <- arrange(.x, sequence)
      median_val <- median(force_data$force)
      
      runs_data <- force_data %>%
        mutate(
          above_median = force > median_val,
          run_id = cumsum(above_median != lag(above_median, default = first(above_median)))
        ) %>%
        count(run_id, name = "run_length")
      
      tibble(
        总游程数 = nrow(runs_data),
        平均游程长度 = round(mean(runs_data$run_length), 2),
        最长游程 = max(runs_data$run_length),
        游程长度标准差 = round(sd(runs_data$run_length), 2)
      )
    })
  ) %>%
  select(target_force, run_stats) %>%
  unnest(run_stats)

print("\n稳定性分析（游程检验）:")
print(stability_analysis)

# 3. 变化点检测（现代化版本）
change_point_analysis <- data_with_target %>%
  group_nest(target_force) %>%
  mutate(
    # 使用map进行变化点检测
    change_results = map(data, ~ {
      force_data <- arrange(.x, sequence)
      n <- nrow(force_data)
      
      if(n < 20) {
        return(tibble(潜在变化点数量 = 0L, 最大均值变化 = 0))
      }
      
      window_size <- min(10, n %/% 4)
      
      # 计算滑动窗口均值差异
      change_data <- force_data %>%
        mutate(
          moving_mean_diff = slider::slide_dbl(force, 
            ~ if(length(.x) >= 2*window_size) {
              mid <- length(.x) %/% 2
              mean(.x[(mid-window_size+1):mid]) - mean(.x[(mid+1):(mid+window_size)])
            } else NA_real_,
            .before = window_size, .after = window_size, .complete = FALSE
          ),
          potential_change = abs(moving_mean_diff) > 2 * sd(force, na.rm = TRUE)
        ) %>%
        filter(potential_change, !is.na(moving_mean_diff))
      
      tibble(
        潜在变化点数量 = nrow(change_data),
        最大均值变化 = if(nrow(change_data) > 0) round(max(abs(change_data$moving_mean_diff)), 3) else 0,
        变化点位置 = if(nrow(change_data) > 0) list(change_data$sequence) else list(integer(0))
      )
    })
  ) %>%
  select(target_force, change_results) %>%
  unnest(change_results)

change_points <- change_point_analysis %>%
  filter(潜在变化点数量 > 0) %>%
  select(-变化点位置)

print("\n变化点检测:")
if(nrow(change_points) > 0) {
  print(change_points)
} else {
  print("未检测到明显的变化点")
}

# 4. 自相关分析（现代化版本）
autocorr_analysis <- data_with_target %>%
  group_nest(target_force) %>%
  mutate(
    # 使用map计算不同滞后期的自相关
    autocorr_results = map(data, ~ {
      force_data <- arrange(.x, sequence)$force
      n <- length(force_data)
      
      tibble(
        lag1_correlation = if(n > 1) cor(force_data[-n], force_data[-1], use = "complete.obs") else NA_real_,
        lag2_correlation = if(n > 2) cor(force_data[1:(n-2)], force_data[3:n], use = "complete.obs") else NA_real_,
        lag3_correlation = if(n > 3) cor(force_data[1:(n-3)], force_data[4:n], use = "complete.obs") else NA_real_
      )
    })
  ) %>%
  select(target_force, autocorr_results) %>%
  unnest(autocorr_results) %>%
  mutate_if(is.numeric, round, 4)

print("\n自相关分析:")
print(autocorr_analysis)

# 5. 综合质量评估（现代化版本）
quality_assessment <- data_with_target %>%
  group_nest(target_force) %>%
  mutate(
    quality_metrics = map(data, ~ {
      force_data <- .x$force
      
      # 基础统计量
      basic_stats <- tibble(
        样本数 = length(force_data),
        均值 = mean(force_data),
        标准差 = sd(force_data),
        变异系数 = sd(force_data) / mean(force_data) * 100
      )
      
      # 分布特征
      distribution_stats <- tibble(
        偏度 = ifelse(length(force_data) > 2, 
                    sum((force_data - mean(force_data))^3) / (length(force_data) * sd(force_data)^3), 
                    NA_real_),
        峰度 = ifelse(length(force_data) > 3,
                    sum((force_data - mean(force_data))^4) / (length(force_data) * sd(force_data)^4) - 3,
                    NA_real_)
      )
      
      bind_cols(basic_stats, distribution_stats)
    })
  ) %>%
  select(target_force, quality_metrics) %>%
  unnest(quality_metrics) %>%
  mutate_if(is.numeric, round, 3)

print("\n综合质量评估:")
print(quality_assessment)

# 6. 过程能力分析（简化版）
if(nrow(target_analysis) > 0) {
  process_capability <- target_analysis %>%
    mutate(
      # 过程能力指数 Cp（仅考虑变异）
      Cp = (绝对容差限制 * 2) / (6 * 标准差),
      # 过程能力指数 Cpk（考虑偏移）
      Cpk = pmin(
        (绝对容差限制 - abs(平均偏差_绝对)) / (3 * 标准差),
        (绝对容差限制 + abs(平均偏差_绝对)) / (3 * 标准差)
      ),
      # 能力等级
      能力等级 = case_when(
        Cpk >= 1.33 ~ "优秀",
        Cpk >= 1.0 ~ "合格", 
        Cpk >= 0.67 ~ "勉强",
        TRUE ~ "不合格"
      )
    ) %>%
    select(target_force, Cp, Cpk, 能力等级) %>%
    mutate_if(is.numeric, round, 3)
  
  print("\n过程能力分析:")
  print(process_capability)
}

# 更新数据以包含异常值信息
data_with_target <- outlier_analysis

# ============================================================================
# 6. 数据可视化
# ============================================================================

print("\n=== 生成图表 ===")

# 加载额外的可视化包
if(!require("plotly", quietly = TRUE)) install.packages("plotly")
if(!require("GGally", quietly = TRUE)) install.packages("GGally")
if(!require("patchwork", quietly = TRUE)) install.packages("patchwork")
if(!require("cluster", quietly = TRUE)) install.packages("cluster")

library(plotly)
library(GGally)
library(patchwork)
library(cluster)

# 1. 力值时间序列图（按目标力值着色，带容差指示）
p1 <- data_with_target %>%
  ggplot(aes(sequence, force, color = factor(target_force))) +
  geom_line(alpha = 0.7, linewidth = 0.5) +
  geom_point(aes(shape = within_tolerance), alpha = 0.6, size = 1.5) +
  geom_hline(aes(yintercept = target_force), color = "red", linetype = "dashed") +
  # 添加容差区间
  geom_ribbon(aes(ymin = target_force - tolerance_abs_limit, 
                  ymax = target_force + tolerance_abs_limit, 
                  fill = factor(target_force)), alpha = 0.1) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
  labs(
    title = "力值时间序列图（按目标力值分组）",
    subtitle = "实心点=在容差内，空心点=超出容差，阴影=容差区间",
    x = "序号", 
    y = "力值(N)", 
    color = "目标力值",
    fill = "目标力值"
  )

print("显示时间序列图...")
print(p1)

# 2. 力值分布直方图（按目标力值分面）
p2 <- data_with_target %>%
  ggplot(aes(x = force, fill = factor(target_force))) +
  geom_histogram(bins = 15, alpha = 0.7, color = "white") +
  geom_vline(aes(xintercept = target_force), color = "red", linetype = "dashed", linewidth = 1) +
  geom_vline(data = data_with_target %>% group_by(target_force) %>% summarise(mean_force = mean(force)), 
             aes(xintercept = mean_force), color = "blue", linetype = "solid", linewidth = 1) +
  facet_wrap(~target_force, scales = "free", labeller = label_both) +
  labs(
    title = "力值分布直方图（按目标力值分组）",
    subtitle = "红虚线=目标值，蓝实线=实际均值",
    x = "力值 (N)",
    y = "频次",
    fill = "目标力值"
  )

print("显示分布直方图...")
print(p2)

# 3. 箱线图（按目标力值分组）
p3 <- data_with_target %>%
  ggplot(aes(x = factor(target_force), y = force, fill = factor(target_force))) +
  geom_boxplot(alpha = 0.7, outlier.color = "red", outlier.size = 2) +
  geom_hline(aes(yintercept = target_force), color = "red", linetype = "dashed") +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3, fill = "white") +
  labs(
    title = "力值箱线图（按目标力值分组）",
    subtitle = "红点=异常值，白菱形=均值，红虚线=目标值",
    x = "目标力值 (N)",
    y = "力值 (N)",
    fill = "目标力值"
  )

print("显示箱线图...")
print(p3)

# 4. 绝对偏差箱线图（按目标力值分组）
p4 <- data_with_target %>%
  ggplot(aes(factor(target_force), deviation_abs, fill = factor(target_force))) +
  geom_boxplot(alpha = 0.7, outlier.color = "red") +
  geom_hline(yintercept = 0, color = "green", linetype = "solid", linewidth = 1) +
  geom_hline(yintercept = c(-tolerance_abs, tolerance_abs), 
             color = "orange", linetype = "dashed", linewidth = 1) +
  labs(
    title = "绝对偏差分布（按目标力值分组）",
    subtitle = "绿线=零偏差，橙色虚线=绝对容差限制",
    x = "目标力值(N)", 
    y = "绝对偏差(N)", 
    fill = "目标力值"
  )

print("显示绝对偏差箱线图...")
print(p4)

# 5. 百分比偏差箱线图（按目标力值分组）
p5 <- data_with_target %>%
  ggplot(aes(factor(target_force), deviation_pct, fill = factor(target_force))) +
  geom_boxplot(alpha = 0.7, outlier.color = "red") +
  geom_hline(yintercept = 0, color = "green", linetype = "solid", linewidth = 1) +
  geom_hline(yintercept = c(-tolerance_pct, tolerance_pct), 
             color = "orange", linetype = "dashed", linewidth = 1) +
  labs(
    title = "百分比偏差分布（按目标力值分组）",
    subtitle = "绿线=零偏差，橙色虚线=百分比容差限制",
    x = "目标力值(N)", 
    y = "百分比偏差(%)", 
    fill = "目标力值"
  )

print("显示百分比偏差箱线图...")
print(p5)

# 6. 控制图（Shewhart控制图，按目标力值分组）
if(exists("data_with_target") && "移动平均" %in% colnames(data_with_target)) {
  # 计算控制限
  control_limits <- data_with_target %>%
    group_by(target_force) %>%
    summarise(
      center = mean(force),
      ucl = mean(force) + 3*sd(force),
      lcl = mean(force) - 3*sd(force),
      ucl_2sigma = mean(force) + 2*sd(force),
      lcl_2sigma = mean(force) - 2*sd(force),
      .groups = 'drop'
    )
  
  p6_control <- data_with_target %>%
    ggplot(aes(x = sequence, y = force)) +
    # 控制区域填充
    geom_ribbon(aes(ymin = target_force - 3*sd(force), ymax = target_force + 3*sd(force)), 
                alpha = 0.1, fill = "blue") +
    geom_ribbon(aes(ymin = target_force - 2*sd(force), ymax = target_force + 2*sd(force)), 
                alpha = 0.1, fill = "yellow") +
    # 数据点和连线
    geom_line(aes(color = factor(target_force)), alpha = 0.7, linewidth = 0.5) +
    geom_point(aes(color = factor(target_force), shape = is_outlier), alpha = 0.8, size = 1.5) +
    # 控制线
    geom_hline(data = control_limits, aes(yintercept = center), 
               color = "green", linewidth = 1) +
    geom_hline(data = control_limits, aes(yintercept = ucl), 
               color = "red", linetype = "dashed", linewidth = 0.8) +
    geom_hline(data = control_limits, aes(yintercept = lcl), 
               color = "red", linetype = "dashed", linewidth = 0.8) +
    geom_hline(data = control_limits, aes(yintercept = ucl_2sigma), 
               color = "orange", linetype = "dotted", linewidth = 0.6) +
    geom_hline(data = control_limits, aes(yintercept = lcl_2sigma), 
               color = "orange", linetype = "dotted", linewidth = 0.6) +
    scale_shape_manual(values = c(16, 4), name = "异常值") +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(
      title = "Shewhart控制图（按目标力值分组）",
      subtitle = "绿线=中心线，红虚线=3σ控制限，橙点线=2σ警戒线，X=异常值",
      x = "序号",
      y = "力值(N)",
      color = "目标力值"
    )
  
  print("显示Shewhart控制图...")
  print(p6_control)
}

# 7. 移动平均图（按目标力值分组）
if(exists("data_with_target") && "移动平均" %in% colnames(data_with_target)) {
  p7_moving <- data_with_target %>%
    filter(!is.na(移动平均)) %>%
    ggplot(aes(sequence)) +
    # 置信区间
    geom_ribbon(aes(ymin = 移动平均 - 移动标准差, ymax = 移动平均 + 移动标准差, 
                    fill = factor(target_force)), alpha = 0.2) +
    # 数据线
    geom_line(aes(y = force, color = factor(target_force)), alpha = 0.4, linewidth = 0.5) +
    geom_line(aes(y = 移动平均, color = factor(target_force)), linewidth = 1.2) +
    # 目标线
    geom_hline(aes(yintercept = target_force), color = "red", linetype = "dashed") +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(
      title = "移动平均分析（按目标力值分组）",
      subtitle = paste0("窗口大小=", window_size, "，彩色带=移动标准差范围"),
      x = "序号",
      y = "力值(N)",
      color = "目标力值",
      fill = "目标力值"
    )
  
  print("显示移动平均图...")
  print(p7_moving)
}

# 8. 多维空间可视化：3D交互式散点图
print("生成3D交互式散点图...")
p8_3d <- plot_ly(data_with_target, x = ~x, y = ~y, z = ~z, 
                color = ~factor(target_force), 
                symbol = ~within_tolerance,
                symbols = c('circle-open', 'circle'),
                size = ~abs(deviation_abs),
                text = ~paste("序号:", sequence, "<br>力值:", force, "N<br>目标:", target_force, "N<br>偏差:", round(deviation_abs, 2), "N")) %>%
  add_markers() %>%
  layout(
    title = list(text = "3D交互式散点图 - 空间分布与异常检测"),
    scene = list(
      xaxis = list(title = "X坐标"),
      yaxis = list(title = "Y坐标"),
      zaxis = list(title = "Z坐标")
    )
  )
print(p8_3d)

# 9. 分面2D散点图矩阵（按目标力值分组）
print("生成分面散点图矩阵...")
data_matrix <- data_with_target %>%
  select(x, y, z, target_force, within_tolerance) %>%
  mutate(target_force = factor(target_force))

p9_matrix <- ggpairs(data_matrix, 
                    columns = 1:3,
                    aes(color = target_force, shape = within_tolerance),
                    upper = list(continuous = "points"),
                    lower = list(continuous = "points"),
                    diag = list(continuous = "densityDiag")) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  labs(title = "XYZ坐标对比矩阵（按目标力值分组）")

print(p9_matrix)

# 10. XY平面热力图（按target_force分面）
p10_heatmap <- data_with_target %>%
  ggplot(aes(x, y)) +
  stat_density_2d_filled(alpha = 0.7) +
  geom_point(aes(color = within_tolerance, shape = within_tolerance), size = 1.5) +
  scale_color_manual(values = c("red", "blue"), name = "在容差内") +
  scale_shape_manual(values = c(4, 16), name = "在容差内") +
  facet_wrap(~target_force, labeller = label_both) +
  labs(title = "XY平面密度热力图（按目标力值分组）", 
       x = "X坐标", y = "Y坐标")

print("显示XY平面热力图...")
print(p10_heatmap)

# 11. 并行坐标图（按目标力值分组）
data_parallel <- data_with_target %>%
  select(x, y, z, force, target_force, within_tolerance) %>%
  mutate(target_force = factor(target_force))

p11_parallel <- ggparcoord(data_parallel, 
                          columns = 1:4, 
                          groupColumn = "target_force",
                          alphaLines = 0.3,
                          showPoints = TRUE) +
  scale_color_viridis_d() +
  labs(title = "并行坐标图 - 多维异常模式（按目标力值分组）", color = "目标力值")

print("显示并行坐标图...")
print(p11_parallel)

# 12. 分层2D投影图组合
# XY投影
p12a_xy <- data_with_target %>%
  ggplot(aes(x, y, color = factor(target_force))) +
  geom_point(aes(shape = within_tolerance, size = abs(deviation_abs)), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 4), name = "绝对偏差") +
  labs(title = "XY投影", color = "目标力值")

# XZ投影  
p12b_xz <- data_with_target %>%
  ggplot(aes(x, z, color = factor(target_force))) +
  geom_point(aes(shape = within_tolerance, size = abs(deviation_abs)), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 4), name = "绝对偏差") +
  labs(title = "XZ投影", color = "目标力值")

# YZ投影
p12c_yz <- data_with_target %>%
  ggplot(aes(y, z, color = factor(target_force))) +
  geom_point(aes(shape = within_tolerance, size = abs(deviation_abs)), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 4), name = "绝对偏差") +
  labs(title = "YZ投影", color = "目标力值")

# 组合投影图
library(patchwork)

p12_combined <- (p12a_xy | p12b_xz) / p12c_yz +
  plot_annotation(title = "2D投影图组合（按目标力值分组）")

print("显示2D投影图组合...")
print(p12_combined)

# 13. 空间聚类异常检测图（按目标力值分组）
coords_data <- data_with_target %>% select(x, y, z)
distances <- dist(coords_data)
hc <- hclust(distances)
data_with_target$cluster <- cutree(hc, k = 5)

p13_cluster <- data_with_target %>%
  ggplot(aes(x, y)) +
  geom_point(aes(color = factor(cluster), 
                 shape = within_tolerance,
                 size = abs(deviation_abs)), alpha = 0.7) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  scale_size_continuous(range = c(1, 5), name = "绝对偏差") +
  facet_wrap(~target_force, labeller = label_both) +
  labs(title = "空间聚类 + 异常检测（按目标力值分组）", 
       color = "空间聚类")

print("显示空间聚类图...")
print(p13_cluster)

# 14. 成功率趋势分析（按目标力值分组）
success_trend_batch_size <- 10
success_trend <- data_with_target %>%
  mutate(batch = ceiling(sequence / success_trend_batch_size)) %>%
  group_by(batch, target_force) %>%
  summarise(
    success_rate = mean(within_tolerance) * 100,
    batch_center = mean(sequence),
    .groups = 'drop'
  )

p14_success <- success_trend %>%
  ggplot(aes(batch, success_rate, color = factor(target_force))) +
  geom_line(linewidth = 1) +
  geom_point(size = 2) +
  geom_hline(yintercept = 90, color = "green", linetype = "dashed", alpha = 0.7) +
  geom_hline(yintercept = 95, color = "blue", linetype = "dashed", alpha = 0.7) +
  facet_wrap(~target_force, labeller = label_both) +
  ylim(0, 100) +
  labs(title = "成功率趋势分析（按目标力值分组）", 
       subtitle = paste0("批次大小=", success_trend_batch_size, "，绿线=90%，蓝线=95%"),
       x = "批次", y = "成功率(%)", color = "目标力值")

print("显示成功率趋势图...")
print(p14_success)

# 15. 过程能力图表（Cp, Cpk可视化）
if(exists("process_capability")) {
  p15_capability <- process_capability %>%
    pivot_longer(cols = c(Cp, Cpk), names_to = "指标", values_to = "值") %>%
    ggplot(aes(factor(target_force), 值, fill = 指标)) +
    geom_col(position = "dodge", alpha = 0.7) +
    geom_hline(yintercept = 1.0, color = "orange", linetype = "dashed") +
    geom_hline(yintercept = 1.33, color = "green", linetype = "dashed") +
    geom_text(aes(label = round(值, 2)), position = position_dodge(width = 0.9), vjust = -0.5) +
    labs(title = "过程能力指数（按目标力值分组）",
         subtitle = "橙线=合格线(1.0)，绿线=优秀线(1.33)",
         x = "目标力值(N)", y = "能力指数", fill = "指标类型")
  
  print("显示过程能力图...")
  print(p15_capability)
}

# 16. 综合质量仪表盘
if(nrow(target_analysis) > 0) {
  # 成功率表盘
  p16a_gauge <- target_analysis %>%
    ggplot(aes(factor(target_force), 成功率_综合, fill = factor(target_force))) +
    geom_col(alpha = 0.7) +
    geom_hline(yintercept = 90, color = "orange", linetype = "dashed") +
    geom_hline(yintercept = 95, color = "green", linetype = "dashed") +
    geom_text(aes(label = paste0(成功率_综合, "%")), vjust = -0.5, color = "black", fontface = "bold") +
    ylim(0, 100) +
    labs(title = "综合成功率", x = "目标力值(N)", y = "成功率(%)", fill = "目标力值")
  
  # 变异系数表盘
  cv_data <- data_with_target %>%
    group_by(target_force) %>%
    summarise(cv = sd(force)/mean(force)*100, .groups = 'drop')
  
  p16b_cv <- cv_data %>%
    ggplot(aes(factor(target_force), cv, fill = factor(target_force))) +
    geom_col(alpha = 0.7) +
    geom_hline(yintercept = 5, color = "green", linetype = "dashed") +
    geom_hline(yintercept = 10, color = "orange", linetype = "dashed") +
    geom_text(aes(label = paste0(round(cv, 1), "%")), vjust = -0.5, color = "black", fontface = "bold") +
    labs(title = "变异系数", x = "目标力值(N)", y = "变异系数(%)", fill = "目标力值")
  
  # 组合仪表盘
  p16_dashboard <- p16a_gauge / p16b_cv +
    plot_annotation(title = "质量控制仪表盘（按目标力值分组）")
  
  print("显示质量仪表盘...")
  print(p16_dashboard)
}

# 17. 相关性分析（保持不变，因为这是整体分析）
if(all(c("x", "y", "z", "force") %in% colnames(data))) {
  cor_data <- data %>%
    select(x, y, z, force) %>%
    cor(use = "complete.obs") %>%
    as_tibble(rownames = "var1") %>%
    pivot_longer(-var1, names_to = "var2", values_to = "correlation")
  
  p17 <- cor_data %>%
    ggplot(aes(var1, var2, fill = correlation)) +
    geom_tile() +
    geom_text(aes(label = round(correlation, 2)), color = "black") +
    scale_fill_gradient2(low = "blue", high = "red", mid = "white", midpoint = 0) +
    labs(
      title = "变量相关性矩阵",
      x = "", y = "",
      fill = "相关系数"
    ) +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1)
    )
  
  print("显示相关性矩阵...")
  print(p17)
}

# 18. 帕雷托图 - 异常原因分析（按目标力值分组）
pareto_data <- data_with_target %>%
  mutate(
    异常类型 = case_when(
      !within_tolerance_abs & !within_tolerance_pct ~ "双重超差",
      !within_tolerance_abs & within_tolerance_pct ~ "绝对超差",
      within_tolerance_abs & !within_tolerance_pct ~ "百分比超差",
      TRUE ~ "正常"
    )
  ) %>%
  group_by(target_force, 异常类型) %>%
  summarise(数量 = n(), .groups = 'drop') %>%
  filter(异常类型 != "正常") %>%
  group_by(target_force) %>%
  arrange(desc(数量)) %>%
  mutate(
    累计数量 = cumsum(数量),
    累计百分比 = cumsum(数量) / sum(数量) * 100
  ) %>%
  ungroup()

if(nrow(pareto_data) > 0) {
  p18_pareto <- pareto_data %>%
    ggplot(aes(reorder(异常类型, -数量))) +
    geom_col(aes(y = 数量, fill = factor(target_force)), alpha = 0.7) +
    geom_line(aes(y = 累计百分比 * max(数量) / 100, group = target_force, color = factor(target_force)), 
              linewidth = 1) +
    geom_point(aes(y = 累计百分比 * max(数量) / 100, color = factor(target_force)), size = 2) +
    scale_y_continuous(
      sec.axis = sec_axis(~. * 100 / max(pareto_data$数量), name = "累计百分比 (%)")
    ) +
    facet_wrap(~target_force, labeller = label_both, scales = "free") +
    labs(title = "帕雷托图 - 异常原因分析（按目标力值分组）",
         subtitle = "识别主要异常类型",
         x = "异常类型", y = "异常数量", 
         fill = "目标力值", color = "目标力值")
  
  print("显示帕雷托图...")
  print(p18_pareto)
}

# 19. 残差分析图（按目标力值分组）
residual_data <- data_with_target %>%
  group_by(target_force) %>%
  mutate(
    fitted_value = mean(force),
    residual = force - fitted_value,
    standardized_residual = residual / sd(residual)
  ) %>%
  ungroup()

p19_residual <- residual_data %>%
  ggplot(aes(fitted_value, residual, color = factor(target_force))) +
  geom_point(aes(shape = within_tolerance), alpha = 0.7) +
  geom_hline(yintercept = 0, color = "red", linetype = "dashed") +
  geom_smooth(method = "loess", se = TRUE, alpha = 0.3) +
  scale_shape_manual(values = c(1, 16), name = "在容差内") +
  facet_wrap(~target_force, scales = "free", labeller = label_both) +
  labs(title = "残差分析图（按目标力值分组）",
       subtitle = "检查模型适合度和异常模式",
       x = "拟合值", y = "残差", color = "目标力值")

print("显示残差分析图...")
print(p19_residual)

# 20. QQ图 - 正态性检验（按目标力值分组）
p20_qq <- data_with_target %>%
  ggplot(aes(sample = force, color = factor(target_force))) +
  stat_qq() +
  stat_qq_line() +
  facet_wrap(~target_force, scales = "free", labeller = label_both) +
  labs(title = "QQ图 - 正态性检验（按目标力值分组）",
       subtitle = "检验数据分布的正态性",
       x = "理论分位数", y = "样本分位数", color = "目标力值")

print("显示QQ图...")
print(p20_qq)

# 21. 运行图（Run Chart）- 按目标力值分组
run_chart_data <- data_with_target %>%
  group_by(target_force) %>%
  mutate(
    center_line = median(force),
    above_center = force > center_line,
    run_id = cumsum(above_center != lag(above_center, default = first(above_center)))
  ) %>%
  ungroup()

p21_run <- run_chart_data %>%
  ggplot(aes(sequence, force, color = factor(target_force))) +
  geom_line(alpha = 0.7, linewidth = 0.5) +
  geom_point(aes(shape = above_center), alpha = 0.7) +
  geom_hline(aes(yintercept = center_line), color = "blue", linetype = "dashed") +
  scale_shape_manual(values = c(25, 24), name = "相对中位数") +
  facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
  labs(title = "运行图（按目标力值分组）",
       subtitle = "蓝虚线=中位数，检测非随机模式",
       x = "序号", y = "力值(N)", color = "目标力值")

print("显示运行图...")
print(p21_run)

# 22. 雷达图 - 质量指标综合评估（按目标力值分组）
if(exists("target_analysis") && exists("process_capability")) {
  # 准备雷达图数据
  radar_data <- target_analysis %>%
    left_join(process_capability, by = "target_force") %>%
    select(target_force, 成功率_综合, Cp, Cpk) %>%
    mutate(
      # 标准化到0-100分
      成功率得分 = 成功率_综合,
      Cp得分 = pmin(Cp * 75, 100),  # Cp=1.33时得100分
      Cpk得分 = pmin(Cpk * 75, 100) # Cpk=1.33时得100分
    ) %>%
    select(target_force, 成功率得分, Cp得分, Cpk得分) %>%
    pivot_longer(-target_force, names_to = "指标", values_to = "得分")
  
  p22_radar <- radar_data %>%
    ggplot(aes(指标, 得分, group = factor(target_force), color = factor(target_force))) +
    geom_line(linewidth = 1) +
    geom_point(size = 3) +
    coord_polar() +
    ylim(0, 100) +
    labs(title = "质量指标雷达图（按目标力值分组）",
         subtitle = "综合质量评估（满分100分）",
         color = "目标力值")
  
  print("显示雷达图...")
  print(p22_radar)
}

# 23. CUSUM累计和控制图 - 检测小幅偏移
print("生成CUSUM控制图...")

cusum_data <- data_with_target %>%
  group_by(target_force) %>%
  arrange(sequence) %>%
  mutate(
    cusum_plus = cumsum(pmax(0, force - target_force - 1)),
    cusum_minus = cumsum(pmax(0, target_force - force - 1))
  ) %>%
  ungroup()

if(nrow(cusum_data) > 0) {
  p23_cusum <- cusum_data %>%
    select(sequence, target_force, cusum_plus, cusum_minus) %>%
    pivot_longer(cols = c(cusum_plus, cusum_minus), 
                 names_to = "cusum_type", values_to = "cusum_value") %>%
    ggplot(aes(x = sequence, y = cusum_value, color = cusum_type)) +
    geom_line(linewidth = 1) +
    geom_hline(yintercept = c(4, -4), linetype = "dashed", color = "red") +
    facet_wrap(~target_force, scales = "free", 
               labeller = labeller(target_force = function(x) paste("目标力值:", x, "N"))) +
    scale_color_manual(values = c("cusum_plus" = "red", "cusum_minus" = "blue"),
                       labels = c("累计正偏", "累计负偏")) +
    labs(title = "CUSUM控制图 - 小幅偏移检测",
         subtitle = "检测过程均值的微小持续性偏移",
         x = "序号", y = "累计和", color = "类型")

  print("显示CUSUM控制图...")
  print(p23_cusum)
}

# 24. 热力图 - 位置vs力值异常分析
position_heatmap_data <- data_with_target %>%
  mutate(
    x_bin = round(x/2)*2,  # 分箱处理
    y_bin = round(y/2)*2
  ) %>%
  group_by(x_bin, y_bin, target_force) %>%
  summarise(
    异常率 = (1 - mean(within_tolerance)) * 100,
    数据点数 = n(),
    .groups = 'drop'
  ) %>%
  filter(数据点数 >= 2)  # 过滤数据点太少的组

if(nrow(position_heatmap_data) > 0) {
  p24_position_heatmap <- position_heatmap_data %>%
    ggplot(aes(x_bin, y_bin, fill = 异常率)) +
    geom_tile() +
    scale_fill_gradient2(low = "green", mid = "yellow", high = "red", 
                        midpoint = 50, name = "异常率(%)") +
    facet_wrap(~target_force, labeller = label_both) +
    labs(title = "位置-异常率热力图（按目标力值分组）",
         subtitle = "识别空间异常分布模式",
         x = "X坐标", y = "Y坐标")
  
  print("显示位置异常率热力图...")
  print(p24_position_heatmap)
}

# 25. 瀑布图 - 质量损失分析
if(nrow(target_analysis) > 0) {
  waterfall_data <- target_analysis %>%
    mutate(
      损失率 = 100 - 成功率_综合,
      target_label = paste0("目标", target_force, "N")
    ) %>%
    arrange(target_force) %>%
    mutate(
      cumsum_loss = cumsum(损失率),
      cumsum_lag = lag(cumsum_loss, default = 0)
    )
  
  p25_waterfall <- waterfall_data %>%
    ggplot() +
    geom_col(aes(target_label, 损失率, fill = factor(target_force)), alpha = 0.7) +
    geom_step(aes(target_label, cumsum_loss, group = 1), 
              color = "red", linewidth = 1, direction = "mid") +
    geom_point(aes(target_label, cumsum_loss), color = "red", size = 3) +
    geom_text(aes(target_label, 损失率/2, label = paste0(round(损失率, 1), "%")), 
              fontface = "bold") +
    labs(title = "质量损失瀑布图（按目标力值分组）",
         subtitle = "累积质量损失分析",
         x = "目标力值", y = "损失率(%)", fill = "目标力值")
  
  print("显示瀑布图...")
  print(p25_waterfall)
}

# 26. 控制图组合面板
if(exists("data_with_target") && "移动平均" %in% colnames(data_with_target)) {
  # X-bar图（均值图）
  xbar_data <- data_with_target %>%
    group_by(target_force) %>%
    mutate(
      xbar = mean(force),
      ucl_xbar = xbar + 3*sd(force)/sqrt(n()),
      lcl_xbar = xbar - 3*sd(force)/sqrt(n())
    ) %>%
    ungroup()
  
  p26a_xbar <- xbar_data %>%
    ggplot(aes(sequence, force, color = factor(target_force))) +
    geom_line(alpha = 0.7) +
    geom_point(alpha = 0.7) +
    geom_hline(aes(yintercept = xbar), color = "green") +
    geom_hline(aes(yintercept = ucl_xbar), color = "red", linetype = "dashed") +
    geom_hline(aes(yintercept = lcl_xbar), color = "red", linetype = "dashed") +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(title = "X-bar控制图", y = "力值(N)", color = "目标力值")
  
  # R图（极差图）
  r_data <- data_with_target %>%
    group_by(target_force) %>%
    arrange(sequence) %>%
    mutate(
      range_val = abs(force - lag(force, default = first(force))),
      r_bar = mean(range_val, na.rm = TRUE),
      ucl_r = r_bar * 3.267,  # D4 for n=2
      lcl_r = max(0, r_bar * 0)  # D3 for n=2
    ) %>%
    ungroup()
  
  p26b_r <- r_data %>%
    ggplot(aes(sequence, range_val, color = factor(target_force))) +
    geom_line(alpha = 0.7) +
    geom_point(alpha = 0.7) +
    geom_hline(aes(yintercept = r_bar), color = "green") +
    geom_hline(aes(yintercept = ucl_r), color = "red", linetype = "dashed") +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(title = "R控制图", x = "序号", y = "移动极差", color = "目标力值")
  
  # 组合控制图
  p26_combined_control <- p26a_xbar / p26b_r +
    plot_annotation(title = "X-bar & R 控制图组合（按目标力值分组）")
  
  print("显示控制图组合...")
  print(p26_combined_control)
}

# 27. EWMA指数加权移动平均控制图
print("生成EWMA控制图...")

ewma_data <- data_with_target %>%
  group_by(target_force) %>%
  arrange(sequence) %>%
  mutate(
    lambda = 0.2,  # 平滑常数
    ewma_mean = target_force,
    ewma_sigma = sd(force) * sqrt(lambda / (2 - lambda)),
    ucl_ewma = ewma_mean + 3 * ewma_sigma,
    lcl_ewma = ewma_mean - 3 * ewma_sigma
  ) %>%
  group_modify(~ {
    .x$ewma <- rep(0, nrow(.x))
    .x$ewma[1] <- .x$force[1]
    for(i in 2:nrow(.x)) {
      .x$ewma[i] <- 0.2 * .x$force[i] + 0.8 * .x$ewma[i-1]
    }
    return(.x)
  }) %>%
  ungroup()

if(nrow(ewma_data) > 0) {
  p27_ewma <- ewma_data %>%
    ggplot(aes(x = sequence)) +
    # 控制限区域
    geom_ribbon(aes(ymin = lcl_ewma, ymax = ucl_ewma), 
                alpha = 0.2, fill = "lightblue") +
    # 中心线
    geom_line(aes(y = ewma_mean), color = "green", linewidth = 1, linetype = "solid") +
    # 控制限
    geom_line(aes(y = ucl_ewma), color = "red", linewidth = 1, linetype = "dashed") +
    geom_line(aes(y = lcl_ewma), color = "red", linewidth = 1, linetype = "dashed") +
    # EWMA曲线
    geom_line(aes(y = ewma, color = factor(target_force)), linewidth = 1.2) +
    geom_point(aes(y = ewma, color = factor(target_force)), size = 2) +
    # 异常点标识
    geom_point(data = ewma_data %>% filter(ewma > ucl_ewma | ewma < lcl_ewma),
               aes(y = ewma), shape = 4, size = 3, color = "red") +
    facet_wrap(~target_force, scales = "free_y", 
               labeller = labeller(target_force = function(x) paste("目标力值:", x, "N"))) +
    labs(title = "EWMA指数加权移动平均控制图",
         subtitle = "对小幅偏移敏感的控制图，平滑参数λ=0.2",
         x = "序号", y = "EWMA值", color = "目标力值")
  
  print("显示EWMA控制图...")
  print(p27_ewma)
}

# 28. 个值-移动极差图 (I-MR Chart)
print("生成I-MR控制图...")

imr_data <- data_with_target %>%
  group_by(target_force) %>%
  arrange(sequence) %>%
  mutate(
    # 个值图数据
    x_mean = mean(force),
    mr = abs(force - lag(force, default = first(force))),
    mr_mean = mean(mr, na.rm = TRUE),
    # 控制限
    ucl_x = x_mean + 2.66 * mr_mean,
    lcl_x = x_mean - 2.66 * mr_mean,
    ucl_mr = 3.27 * mr_mean,
    lcl_mr = 0
  ) %>%
  ungroup()

if(nrow(imr_data) > 0) {
  # I图（个值图）
  p28a_i <- imr_data %>%
    ggplot(aes(x = sequence)) +
    geom_line(aes(y = force, color = factor(target_force)), alpha = 0.7) +
    geom_point(aes(y = force, color = factor(target_force))) +
    geom_hline(aes(yintercept = x_mean), color = "green", linewidth = 1) +
    geom_hline(aes(yintercept = ucl_x), color = "red", linetype = "dashed") +
    geom_hline(aes(yintercept = lcl_x), color = "red", linetype = "dashed") +
    geom_point(data = imr_data %>% filter(force > ucl_x | force < lcl_x),
               aes(y = force), shape = 4, size = 3, color = "red") +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(title = "个值控制图 (I Chart)", y = "个值", color = "目标力值")
  
  # MR图（移动极差图）
  p28b_mr <- imr_data %>%
    ggplot(aes(x = sequence)) +
    geom_line(aes(y = mr, color = factor(target_force)), alpha = 0.7) +
    geom_point(aes(y = mr, color = factor(target_force))) +
    geom_hline(aes(yintercept = mr_mean), color = "green", linewidth = 1) +
    geom_hline(aes(yintercept = ucl_mr), color = "red", linetype = "dashed") +
    geom_hline(aes(yintercept = lcl_mr), color = "red", linetype = "dashed") +
    geom_point(data = imr_data %>% filter(mr > ucl_mr),
               aes(y = mr), shape = 4, size = 3, color = "red") +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(title = "移动极差控制图 (MR Chart)", 
         x = "序号", y = "移动极差", color = "目标力值")
  
  # 组合I-MR图
  p28_imr_combined <- p28a_i / p28b_mr +
    plot_annotation(title = "I-MR控制图组合（按目标力值分组）",
                    subtitle = "适用于个别测量值的统计控制")
  
  print("显示I-MR控制图...")
  print(p28_imr_combined)
}

# 29. 过程能力直方图（规格限制图）
print("生成过程能力直方图...")

capability_data <- data_with_target %>%
  group_by(target_force) %>%
  mutate(
    # 规格限制
    usl = target_force + tolerance_abs,  # 上规格限
    lsl = target_force - tolerance_abs,  # 下规格限
    # 过程统计
    process_mean = mean(force),
    process_sigma = sd(force),
    # 能力指数
    cp = (usl - lsl) / (6 * process_sigma),
    cpk = min((usl - process_mean) / (3 * process_sigma),
              (process_mean - lsl) / (3 * process_sigma))
  ) %>%
  ungroup()

if(nrow(capability_data) > 0) {
  p29_capability <- capability_data %>%
    ggplot(aes(x = force)) +
    # 直方图
    geom_histogram(aes(y = after_stat(density), fill = factor(target_force)), 
                   bins = 12, alpha = 0.7, color = "white") +
    # 正态密度曲线
    geom_density(aes(color = factor(target_force)), linewidth = 1.2, alpha = 0.8) +
    # 规格限制线
    geom_vline(aes(xintercept = usl), color = "red", linewidth = 1.5, linetype = "dashed") +
    geom_vline(aes(xintercept = lsl), color = "red", linewidth = 1.5, linetype = "dashed") +
    geom_vline(aes(xintercept = target_force), color = "green", linewidth = 1.5) +
    # 过程均值线
    geom_vline(aes(xintercept = process_mean), color = "blue", linewidth = 1, linetype = "dotted") +
    # 添加能力指数标签
    geom_text(aes(x = Inf, y = Inf, 
                  label = paste0("Cp=", round(cp, 2), "\nCpk=", round(cpk, 2))),
              hjust = 1.1, vjust = 1.1, size = 3.5, fontface = "bold") +
    facet_wrap(~target_force, scales = "free", 
               labeller = labeller(target_force = function(x) paste("目标力值:", x, "N"))) +
    labs(title = "过程能力分析直方图",
         subtitle = "红线=规格限制，绿线=目标值，蓝线=过程均值",
         x = "力值 (N)", y = "密度", 
         fill = "目标力值", color = "目标力值")
  
  print("显示过程能力直方图...")
  print(p29_capability)
}

# ============================================================================
# 7. 生成总结报告
# ============================================================================

print("\n=== 分析报告 ===")

cat("\n压力采集数据分析报告")
cat("\n==================")
cat("\n分析时间:", as.character(Sys.time()))
cat("\n数据文件:", data_file)
cat("\n数据点数量:", nrow(data))

cat("\n\n数据概览:")
cat("\n- 力值范围:", round(min(data$force), 2), "-", round(max(data$force), 2), "N")
cat("\n- 平均力值:", round(mean(data$force), 2), "N")
cat("\n- 标准差:", round(sd(data$force), 2), "N")
cat("\n- 变异系数:", round(sd(data$force)/mean(data$force)*100, 2), "%")

cat("\n\n趋势分析:")
for(i in 1:nrow(trend_stats)) {
  row <- trend_stats[i, ]
  trend_direction <- ifelse(row$斜率 > 0, "上升", "下降")
  trend_significance <- ifelse(row$p值 < 0.05, "显著", "不显著")
  cat("\n-", row$分组, ":", trend_direction, "(", trend_significance, "), 斜率:", round(row$斜率, 6))
}

# 添加高级分析结果
if(exists("outlier_summary")) {
  cat("\n\n异常值分析:")
  for(i in 1:nrow(outlier_summary)) {
    row <- outlier_summary[i, ]
    cat("\n- 目标", row$target_force, "N: IQR异常率", row$IQR异常率, "%, Z异常率", row$Z异常率, "%")
  }
}

if(exists("stability_analysis")) {
  cat("\n\n稳定性分析:")
  for(i in 1:nrow(stability_analysis)) {
    row <- stability_analysis[i, ]
    cat("\n- 目标", row$target_force, "N: 平均游程长度", row$平均游程长度, ", 最长游程", row$最长游程)
  }
}

if(nrow(target_analysis) > 0) {
  cat("\n\n目标力值分析:")
  for(i in 1:nrow(target_analysis)) {
    row <- target_analysis[i, ]
    cat("\n- 目标", row$target_force, "N:")
    cat(" 数据点", row$数据点数, "个")
    cat("\n  综合成功率:", row$成功率_综合, "% (绝对:", row$成功率_绝对, "%, 百分比:", row$成功率_百分比, "%)")
    cat("\n  平均偏差: 绝对", row$平均偏差_绝对, "N, 百分比", row$平均偏差_百分比, "%")
    cat("\n  容差限制: 绝对±", row$绝对容差限制, "N, 百分比±", row$百分比容差限制, "N")
  }
}

# 建议
recommendations <- c()
cv <- sd(data$force) / mean(data$force) * 100
if(cv > 10) {
  recommendations <- c(recommendations, "数据变异性较大，建议检查测量系统稳定性")
}
if(any(trend_stats$p值 < 0.05)) {
  recommendations <- c(recommendations, "检测到显著趋势，建议监控系统漂移")
}
if(length(recommendations) == 0) {
  recommendations <- "数据质量良好，系统运行稳定"
}

cat("\n\n建议:")
for(rec in recommendations) {
  cat("\n-", rec)
}

# ============================================================================
# 8. 保存结果
# ============================================================================

# 保存清理后的数据
write_csv(data_with_target, "cleaned_pressure_data.csv")

# 保存分析结果
analysis_results <- list(
  data_summary = data_summary,
  overall_stats = overall_stats,
  target_analysis = target_analysis,
  trend_stats = trend_stats
)

save(analysis_results, file = "analysis_results.RData")

print("\n=== 分析完成 ===")
print("文件已保存:")
print("- cleaned_pressure_data.csv (清理后的数据)")
print("- analysis_results.RData (分析结果)")

print("\n主要发现:")
print(paste("- 总数据点:", nrow(data)))
print(paste("- 力值范围:", round(min(data$force), 2), "-", round(max(data$force), 2), "N"))
print(paste("- 变异系数:", round(cv, 2), "%"))
print(paste("- 趋势:", trend_direction, "(", trend_significance, ")"))

cat("\n\n=== 使用说明 ===")
cat("\n🔧 参数配置:")
cat("\n   - target_forces: 目标力值列表")
cat("\n   - tolerance_abs: 绝对容差 (N)")
cat("\n   - tolerance_pct: 百分比容差 (%)")
cat("\n")
cat("\n📊 现代化特性:")
cat("\n   - 使用 group_nest + map + broom 的现代 tidyverse 工作流")
cat("\n   - 函数式编程风格，避免过时的 do() 函数")
cat("\n   - 嵌套数据框架构，便于复杂分析")
cat("\n   - broom 包提供统一的模型结果接口")
cat("\n")
cat("\n🔍 分析功能:")
cat("\n   - 分组趋势分析（线性回归 + broom）")
cat("\n   - 高级异常值检测（IQR + Z-score）")
cat("\n   - 稳定性分析（游程检验）")
cat("\n   - 变化点检测（滑动窗口）")
cat("\n   - 自相关分析（多滞后期）")
cat("\n   - 综合质量评估（偏度、峰度）")
cat("\n   - 过程能力分析（Cp、Cpk）")
cat("\n")
cat("\n💡 扩展提示:")
cat("\n   - 所有分析结果都采用嵌套tibble结构")
cat("\n   - 可以轻松添加新的map分析函数")
cat("\n   - 支持管道操作和函数式编程")
cat("\n   - 便于与其他tidyverse包集成")

# ============================================================================
# 9. 图形分析指南
# ============================================================================

cat("\n\n", paste(rep("=", 80), collapse = ""))
cat("\n📊 图形分析指南 - 如何解读压力数据分析图表")
cat("\n", paste(rep("=", 80), collapse = ""))

cat("\n\n🎯 【基础分析图形】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n1️⃣ 力值时间序列图（按目标力值分组）")
cat("\n📋 图形用途: 观察力值随时间的变化趋势和波动模式")
cat("\n🔍 如何解读:")
cat("\n   • 实心点 = 在容差内的合格数据点")
cat("\n   • 空心点 = 超出容差的异常数据点") 
cat("\n   • 红虚线 = 目标力值水平线")
cat("\n   • 阴影区域 = 绝对容差范围")
cat("\n   • 按目标力值分面显示，便于对比不同力值的表现")
cat("\n💡 关注要点:")
cat("\n   - 数据点是否主要集中在容差区域内")
cat("\n   - 是否存在明显的上升或下降趋势")
cat("\n   - 异常点是否存在聚集现象或周期性模式")
cat("\n   - 不同目标力值组的稳定性对比")

cat("\n\n2️⃣ 力值分布直方图（按目标力值分组）")
cat("\n📋 图形用途: 分析每个目标力值组的数据分布特征")
cat("\n🔍 如何解读:")
cat("\n   • 直方图 = 力值的频次分布")
cat("\n   • 红虚线 = 目标力值位置")
cat("\n   • 蓝实线 = 实际测量的平均值")
cat("\n   • 分面显示 = 不同目标力值的独立分布")
cat("\n💡 关注要点:")
cat("\n   - 分布是否接近正态分布（钟形曲线）")
cat("\n   - 实际均值与目标值的偏离程度")
cat("\n   - 分布的宽度（反映数据稳定性）")
cat("\n   - 是否存在双峰或多峰分布（可能表示系统不稳定）")

cat("\n\n3️⃣ 力值箱线图（按目标力值分组）")
cat("\n📋 图形用途: 快速识别数据的分位数特征和异常值")
cat("\n🔍 如何解读:")
cat("\n   • 箱体 = 25%-75%分位数范围（IQR）")
cat("\n   • 中线 = 中位数")
cat("\n   • 白菱形 = 平均值")
cat("\n   • 红点 = 统计异常值")
cat("\n   • 红虚线 = 目标力值")
cat("\n   • 须线 = 1.5倍IQR范围内的数据边界")
cat("\n💡 关注要点:")
cat("\n   - 箱体的高度（数据离散程度）")
cat("\n   - 中位数与目标值的对齐程度")
cat("\n   - 异常值的数量和分布")
cat("\n   - 不同目标力值组的离散程度对比")

cat("\n\n🎯 【偏差分析图形】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n4️⃣ 绝对偏差箱线图（按目标力值分组）")
cat("\n📋 图形用途: 分析实际测量值与目标值的绝对偏差分布")
cat("\n🔍 如何解读:")
cat("\n   • Y轴 = 实际力值 - 目标力值")
cat("\n   • 绿线 = 零偏差（理想状态）")
cat("\n   • 橙虚线 = 绝对容差限制(±2N)")
cat("\n   • 正值 = 测量值高于目标")
cat("\n   • 负值 = 测量值低于目标")
cat("\n💡 关注要点:")
cat("\n   - 偏差分布是否以零为中心")
cat("\n   - 是否存在系统性偏移（整体偏高或偏低）")
cat("\n   - 超出容差限制的数据点比例")
cat("\n   - 不同目标力值的偏差稳定性")

cat("\n\n5️⃣ 百分比偏差箱线图（按目标力值分组）")
cat("\n📋 图形用途: 分析相对于目标值的百分比偏差")
cat("\n🔍 如何解读:")
cat("\n   • Y轴 = (实际力值-目标力值)/目标力值 × 100%")
cat("\n   • 绿线 = 零偏差")
cat("\n   • 橙虚线 = 百分比容差限制(±5%)")
cat("\n   • 消除了目标值大小的影响，便于对比")
cat("\n💡 关注要点:")
cat("\n   - 不同目标力值组的相对精度是否一致")
cat("\n   - 小力值和大力值的相对稳定性对比")
cat("\n   - 百分比容差的实际达成情况")

cat("\n\n🎯 【控制图系列】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n6️⃣ Shewhart控制图（按目标力值分组）")
cat("\n📋 图形用途: 统计过程控制(SPC)的核心工具，监测过程稳定性")
cat("\n🔍 如何解读:")
cat("\n   • 绿线 = 过程中心线（均值）")
cat("\n   • 红虚线 = 3σ控制限（99.7%数据应在此范围内）")
cat("\n   • 橙点线 = 2σ警戒线（95%数据应在此范围内）")
cat("\n   • 蓝色区域 = 3σ控制区间")
cat("\n   • 黄色区域 = 2σ警戒区间")
cat("\n   • X标记 = 检测到的异常值")
cat("\n💡 关注要点:")
cat("\n   - 超出3σ控制限的点（过程失控）")
cat("\n   - 连续7点在中心线同一侧（过程偏移）")
cat("\n   - 连续趋势或周期性模式")
cat("\n   - 数据点在2σ和3σ之间的分布")

cat("\n\n7️⃣ 移动平均图（按目标力值分组）")
cat("\n📋 图形用途: 平滑短期波动，突出长期趋势")
cat("\n🔍 如何解读:")
cat("\n   • 细线 = 原始数据")
cat("\n   • 粗线 = 移动平均线")
cat("\n   • 彩色带 = 移动标准差范围")
cat("\n   • 红虚线 = 目标力值")
cat("\n💡 关注要点:")
cat("\n   - 移动平均线是否稳定在目标值附近")
cat("\n   - 标准差带的宽度变化（稳定性变化）")
cat("\n   - 长期趋势的方向和幅度")

cat("\n\n8️⃣ X-bar & R控制图组合")
cat("\n📋 图形用途: 同时监控过程均值和变异性")
cat("\n🔍 如何解读:")
cat("\n   • X-bar图 = 监控过程平均水平")
cat("\n   • R图 = 监控过程变异性（极差）")
cat("\n   • 绿线 = 中心线")
cat("\n   • 红虚线 = 控制限")
cat("\n💡 关注要点:")
cat("\n   - X-bar图超限表示均值偏移")
cat("\n   - R图超限表示变异增大")
cat("\n   - 两图需结合分析，识别不同类型的过程变化")

cat("\n\n🎯 【多维空间分析】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n9️⃣ 3D交互式散点图")
cat("\n📋 图形用途: 在三维空间中可视化数据点分布和异常模式")
cat("\n🔍 如何解读:")
cat("\n   • X、Y、Z轴 = 空间坐标")
cat("\n   • 颜色 = 目标力值分组")
cat("\n   • 形状 = 实心圆（合格）vs 空心圆（异常）")
cat("\n   • 大小 = 绝对偏差的大小")
cat("\n   • 鼠标悬停 = 详细信息")
cat("\n💡 关注要点:")
cat("\n   - 异常点在空间中的聚集模式")
cat("\n   - 不同区域的质量表现差异")
cat("\n   - 可通过旋转发现隐藏的空间关系")

cat("\n\n🔟 散点图矩阵（按目标力值分组）")
cat("\n📋 图形用途: 分析多变量间的两两关系")
cat("\n🔍 如何解读:")
cat("\n   • 对角线 = 各变量的密度分布")
cat("\n   • 下三角 = 散点图")
cat("\n   • 上三角 = 相关系数")
cat("\n   • 颜色 = 目标力值分组")
cat("\n   • 形状 = 合格性标识")
cat("\n💡 关注要点:")
cat("\n   - 变量间的线性相关关系")
cat("\n   - 异常点在多维空间的表现")
cat("\n   - 相关系数的强度和方向")

cat("\n\n🎯 【专业质量控制图】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n1️⃣1️⃣ 帕雷托图（按目标力值分组）")
cat("\n📋 图形用途: 识别主要的异常原因（80/20原则）")
cat("\n🔍 如何解读:")
cat("\n   • 柱状图 = 各类异常的数量")
cat("\n   • 折线图 = 累积百分比")
cat("\n   • 异常类型: 双重超差 > 绝对超差 > 百分比超差")
cat("\n💡 关注要点:")
cat("\n   - 哪种异常类型最常见")
cat("\n   - 前80%的问题由哪几种原因造成")
cat("\n   - 不同目标力值的异常模式差异")

cat("\n\n2️⃣3️⃣ CUSUM累计和控制图（按目标力值分组）")
cat("\n📋 图形用途: 检测过程均值的小幅持续性偏移")
cat("\n🔍 如何解读:")
cat("\n   • 红线 = 累计正偏差（高于目标的累积）")
cat("\n   • 蓝线 = 累计负偏差（低于目标的累积）") 
cat("\n   • 水平虚线 = ±4的决策界限")
cat("\n   • 斜率变化 = 过程偏移的开始或结束")
cat("\n💡 关注要点:")
cat("\n   - 超出±4界限表示过程失控")
cat("\n   - 持续上升/下降趋势表示系统偏移")
cat("\n   - 比Shewhart图对小偏移更敏感")

cat("\n\n2️⃣7️⃣ EWMA指数加权移动平均控制图")
cat("\n📋 图形用途: 对小幅偏移敏感的统计控制")
cat("\n🔍 如何解读:")
cat("\n   • 粗线 = EWMA曲线（平滑的指数加权移动平均）")
cat("\n   • 绿线 = 目标中心线")
cat("\n   • 红虚线 = 3σ控制限")
cat("\n   • 蓝色阴影 = 控制区间")
cat("\n   • X标记 = 超出控制限的异常点")
cat("\n💡 关注要点:")
cat("\n   - 平滑参数λ=0.2，对历史数据有记忆")
cat("\n   - 比传统控制图更快检测小偏移")
cat("\n   - EWMA线的连续趋势比单点更重要")

cat("\n\n2️⃣8️⃣ I-MR个值移动极差控制图组合")
cat("\n📋 图形用途: 适用于个别测量值的统计过程控制")
cat("\n🔍 如何解读:")
cat("\n   • I图(上) = 个别测量值的控制")
cat("\n   • MR图(下) = 相邻测量值间变异的控制")
cat("\n   • 绿线 = 过程中心线")
cat("\n   • 红虚线 = 控制限")
cat("\n   • X标记 = 失控点")
cat("\n💡 关注要点:")
cat("\n   - I图失控表示过程位置偏移")
cat("\n   - MR图失控表示过程变异增大")
cat("\n   - 适用于单个测量值的连续监控")

cat("\n\n2️⃣9️⃣ 过程能力分析直方图")
cat("\n📋 图形用途: 直观显示过程分布与规格限制的关系")
cat("\n🔍 如何解读:")
cat("\n   • 直方图 = 实际数据分布")
cat("\n   • 曲线 = 正态密度拟合")
cat("\n   • 红虚线 = 上下规格限制(USL/LSL)")
cat("\n   • 绿实线 = 目标值")
cat("\n   • 蓝点线 = 过程均值")
cat("\n   • 右上角数值 = Cp和Cpk指数")
cat("\n💡 关注要点:")
cat("\n   - 分布是否完全在规格限制内")
cat("\n   - 过程均值与目标值的偏离")
cat("\n   - Cp≥1.33且Cpk≥1.33为优秀过程")

cat("\n\n1️⃣2️⃣ 残差分析图（按目标力值分组）")
cat("\n📋 图形用途: 检验模型假设和识别系统性误差")
cat("\n🔍 如何解读:")
cat("\n   • X轴 = 模型拟合值（均值）")
cat("\n   • Y轴 = 残差（实际值-拟合值）")
cat("\n   • 红虚线 = 零残差线")
cat("\n   • 平滑曲线 = 残差趋势")
cat("\n💡 关注要点:")
cat("\n   - 残差是否随机分布在零线两侧")
cat("\n   - 是否存在残差的系统性模式")
cat("\n   - 方差是否均匀（等方差性）")

cat("\n\n1️⃣3️⃣ QQ图（正态性检验）")
cat("\n📋 图形用途: 检验数据是否符合正态分布")
cat("\n🔍 如何解读:")
cat("\n   • X轴 = 理论正态分位数")
cat("\n   • Y轴 = 样本分位数")
cat("\n   • 直线 = 完美正态分布的参考线")
cat("\n   • 点的偏离程度 = 偏离正态性的程度")
cat("\n💡 关注要点:")
cat("\n   - 数据点是否紧贴参考直线")
cat("\n   - 尾部的偏离情况（重尾或轻尾）")
cat("\n   - 整体分布的偏斜程度")

cat("\n\n1️⃣4️⃣ 运行图（Run Chart）")
cat("\n📋 图形用途: 检测数据中的非随机模式")
cat("\n🔍 如何解读:")
cat("\n   • 蓝虚线 = 中位数")
cat("\n   • 三角形 = 高于/低于中位数的点")
cat("\n   • 连续游程 = 连续的同向偏离")
cat("\n💡 关注要点:")
cat("\n   - 连续8点在中位数同一侧（非随机模式）")
cat("\n   - 游程长度的分布")
cat("\n   - 明显的趋势或周期性")

cat("\n\n1️⃣5️⃣ 雷达图（质量指标综合评估）")
cat("\n📋 图形用途: 多指标综合评估的直观展示")
cat("\n🔍 如何解读:")
cat("\n   • 各轴 = 不同的质量指标（成功率、Cp、Cpk）")
cat("\n   • 距离中心的远近 = 指标得分高低")
cat("\n   • 封闭图形的面积 = 综合质量水平")
cat("\n💡 关注要点:")
cat("\n   - 各指标的均衡发展情况")
cat("\n   - 短板指标的识别")
cat("\n   - 不同目标力值组的综合对比")

cat("\n\n🎯 【热力图和地理分析】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n1️⃣6️⃣ 位置异常率热力图")
cat("\n📋 图形用途: 识别空间位置与质量表现的关系")
cat("\n🔍 如何解读:")
cat("\n   • 颜色深浅 = 异常率高低")
cat("\n   • 绿色 = 质量良好区域")
cat("\n   • 黄色 = 质量一般区域")
cat("\n   • 红色 = 质量问题区域")
cat("\n💡 关注要点:")
cat("\n   - 是否存在质量热点区域")
cat("\n   - 空间异常模式的规律性")
cat("\n   - 不同目标力值在相同位置的表现")

cat("\n\n1️⃣7️⃣ XY平面密度热力图")
cat("\n📋 图形用途: 显示数据点在平面上的密度分布")
cat("\n🔍 如何解读:")
cat("\n   • 等高线 = 数据密度等级")
cat("\n   • 点的颜色和形状 = 合格性状态")
cat("\n   • 密度高的区域 = 数据集中区")
cat("\n💡 关注要点:")
cat("\n   - 数据采集的空间代表性")
cat("\n   - 高密度区域的质量表现")
cat("\n   - 异常点的空间分布特征")

cat("\n\n🎯 【趋势和能力分析】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n1️⃣8️⃣ 成功率趋势分析")
cat("\n📋 图形用途: 监控质量表现的时间趋势")
cat("\n🔍 如何解读:")
cat("\n   • X轴 = 时间批次")
cat("\n   • Y轴 = 成功率百分比")
cat("\n   • 绿虚线 = 90%质量基准")
cat("\n   • 蓝虚线 = 95%优秀基准")
cat("\n💡 关注要点:")
cat("\n   - 成功率的趋势方向")
cat("\n   - 是否达到质量基准")
cat("\n   - 批次间的稳定性")
cat("\n   - 异常批次的识别")

cat("\n\n1️⃣9️⃣ 过程能力指数图")
cat("\n📋 图形用途: 评估过程满足规格要求的能力")
cat("\n🔍 如何解读:")
cat("\n   • Cp = 过程潜在能力（仅考虑变异）")
cat("\n   • Cpk = 过程实际能力（考虑偏移）")
cat("\n   • 橙线 = 1.0（合格线）")
cat("\n   • 绿线 = 1.33（优秀线）")
cat("\n💡 关注要点:")
cat("\n   - Cp ≥ 1.33: 过程能力优秀")
cat("\n   - 1.0 ≤ Cp < 1.33: 过程能力合格")
cat("\n   - Cp < 1.0: 过程能力不足")
cat("\n   - Cpk显著小于Cp: 存在系统偏移")

cat("\n\n2️⃣0️⃣ 质量仪表盘")
cat("\n📋 图形用途: 关键质量指标的快速监控")
cat("\n🔍 如何解读:")
cat("\n   • 成功率表盘 = 直观显示合格率")
cat("\n   • 变异系数表盘 = 显示过程稳定性")
cat("\n   • 数值标签 = 精确的指标值")
cat("\n💡 关注要点:")
cat("\n   - 成功率是否达到预期目标")
cat("\n   - 变异系数是否在可接受范围")
cat("\n   - 不同目标力值的表现对比")

cat("\n\n🎯 【综合分析建议】")
cat("\n", paste(rep("-", 50), collapse = ""))

cat("\n\n💡 图形分析优先级:")
cat("\n1. 首先查看控制图和趋势图 → 识别过程稳定性")
cat("\n2. 然后分析分布图和箱线图 → 了解数据特征")
cat("\n3. 接着观察偏差图和能力图 → 评估质量水平")
cat("\n4. 最后使用多维图和特殊图 → 深入问题根因")

cat("\n\n🔍 异常识别指导:")
cat("\n• 单点异常: 查看箱线图和散点图")
cat("\n• 趋势异常: 查看时间序列图和移动平均图")
cat("\n• 分布异常: 查看直方图和QQ图")
cat("\n• 空间异常: 查看3D图和热力图")
cat("\n• 过程异常: 查看控制图和运行图")

cat("\n\n📊 决策支持指南:")
cat("\n• 过程调整: 基于控制图的失控模式")
cat("\n• 设备维护: 基于空间异常分布")
cat("\n• 工艺优化: 基于过程能力分析")
cat("\n• 质量改进: 基于帕雷托图的主要问题")

cat("\n\n⚠️  注意事项:")
cat("\n• 所有图形都按目标力值分组，便于对比分析")
cat("\n• 异常值检测使用多种方法，结果需综合判断")
cat("\n• 统计控制图基于正态分布假设，需验证数据分布")
cat("\n• 空间分析图适用于有位置信息的数据")

cat("\n\n", paste(rep("=", 80), collapse = ""))
cat("\n✅ 图形分析指南完成")
cat("\n", paste(rep("=", 80), collapse = "")) 