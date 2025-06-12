# ============================================================================
# 压力采集数据分析 - 完整版本（后端API专用）
# 基于pressure_analysis_simple.R，适配后端API使用
# ============================================================================

# 保存Python传入的参数（如果存在）
saved_data_file <- if(exists("data_file")) data_file else NULL
saved_target_forces <- if(exists("target_forces")) target_forces else NULL
saved_tolerance_abs <- if(exists("tolerance_abs")) tolerance_abs else NULL
saved_tolerance_pct <- if(exists("tolerance_pct")) tolerance_pct else NULL
saved_output_dir <- if(exists("output_dir")) output_dir else NULL

# 清理环境（但保留保存的参数）
rm(list = setdiff(ls(), c("saved_data_file", "saved_target_forces", "saved_tolerance_abs", "saved_tolerance_pct", "saved_output_dir")))

# 设置中文支持和图表参数
# 在Docker环境中，我们预装了"WenQuanYi Zen Hei"字体
font_family <- "WenQuanYi Zen Hei"
options(warn = -1)  # 抑制警告信息

# R包已在Docker构建时预安装，跳过运行时安装检查
# required_packages <- c("tidyverse", "readr", "ggplot2", "dplyr", "slider", "broom", "GGally", "plotly", "patchwork", "cluster", "jsonlite")
# new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
# if(length(new_packages)) {
#   install.packages(new_packages, repos = "https://cran.rstudio.com/", quiet = TRUE)
#   cat("已安装新包:", paste(new_packages, collapse = ", "), "\n")
# }

# 加载必要的包
suppressMessages({
  library(tidyverse)
  library(slider)
  library(broom)
  library(GGally)
  library(plotly)
  library(patchwork)
  library(cluster)
  library(jsonlite)
  library(argparse)
  library(tools)
})

# ============================================================================
# 参数设置（由Python通过命令行传入）
# ============================================================================
parser <- ArgumentParser(description="Pressure Analysis Script for Backend")

parser$add_argument("--input", type="character", required=TRUE, help="Path to the input CSV file.")
parser$add_argument("--output-dir", type="character", required=TRUE, help="Directory to save charts and results.")
parser$add_argument("--file-id", type="character", required=TRUE, help="Unique ID for this analysis run.")
parser$add_argument("--target-forces", type="character", required=TRUE, help="Comma-separated list of target forces (e.g., '10,20,30').")
parser$add_argument("--tolerance-abs", type="character", required=TRUE, help="Comma-separated list of absolute tolerances.")
parser$add_argument("--tolerance-pct", type="character", required=TRUE, help="Comma-separated list of percentage tolerances.")

# 解析参数
args <- parser$parse_args()

# 将解析出的参数赋值给脚本变量
data_file <- args$input
output_dir <- args$output_dir
file_id <- args$file_id # 虽然旧脚本可能没用，但保留它是好的实践
target_forces <- as.numeric(unlist(strsplit(args$target_forces, ",")))
tolerance_abs <- as.numeric(unlist(strsplit(args$tolerance_abs, ",")))
tolerance_pct <- as.numeric(unlist(strsplit(args$tolerance_pct, ",")))

# 确保输出目录存在
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

window_size <- 10  # 移动窗口大小

print("开始压力数据完整分析...")
print(paste("数据文件:", data_file))
print(paste("目标输出目录:", output_dir))
print(paste("实际输出目录:", normalizePath(output_dir, mustWork = FALSE)))

# ============================================================================
# 主题设置
# ============================================================================

# 自定义主题设置
custom_theme <- theme_minimal(base_family = font_family) +
  theme(
    # 字体设置
    text = element_text(size = 12, family = font_family),
    plot.title = element_text(size = 16, face = "bold", hjust = 0.5, margin = margin(b = 20), family = font_family),
    plot.subtitle = element_text(size = 12, hjust = 0.5, margin = margin(b = 15), family = font_family),
    axis.title = element_text(size = 11, family = font_family),
    axis.text = element_text(size = 10, family = font_family),
    legend.title = element_text(size = 11, family = font_family),
    legend.text = element_text(size = 10, family = font_family),
    strip.text = element_text(size = 11, face = "bold", family = font_family),
    
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

# ============================================================================
# 1. 数据加载和清理
# ============================================================================

tryCatch({
  # 读取数据
  raw_data <- read_csv(data_file, locale = locale(encoding = "UTF-8"), show_col_types = FALSE)
  
  print("原始数据预览:")
  print(head(raw_data))
  print(paste("数据维度:", nrow(raw_data), "行", ncol(raw_data), "列"))
  
  # 标准化列名
  if(ncol(raw_data) >= 5) {
    colnames(raw_data) <- c("sequence", "x", "y", "z", "force")
  } else {
    stop("数据文件列数不足，期望至少5列")
  }
  
  # 清理力值列（移除单位）
  data <- raw_data %>%
    mutate(force = as.numeric(str_remove_all(as.character(force), "[^0-9.-]")))
  
  # 移除无效数据
  data <- data %>% filter(!is.na(force) & force > 0)
  
  print("清理后数据预览:")
  print(head(data))
  print(paste("清理后维度:", nrow(data), "行", ncol(data), "列"))
  
}, error = function(e) {
  stop(paste("数据加载失败:", e$message))
})

# ============================================================================
# 2. 数据质量检查
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
# 3. 基础统计分析
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

# --- START OF FIX ---

# 创建一个容差的查找表 (data.frame)
# 确保所有向量长度一致
if(length(target_forces) != length(tolerance_abs) || length(target_forces) != length(tolerance_pct)) {
  stop("目标力值 (target_forces) 和容差 (tolerance_abs, tolerance_pct) 的列表长度必须相同。")
}

tolerance_df <- data.frame(
  target_force_map = target_forces,
  tolerance_abs_map = tolerance_abs,
  tolerance_pct_map = tolerance_pct
)

print("容差配置:")
print(tolerance_df)

# 为每个数据点匹配最近的目标力值
data_with_target <- data %>%
  mutate(
    # 使用purrr风格匹配最近的目标力值
    target_force = map_dbl(force, ~ target_forces[which.min(abs(.x - target_forces))])
  ) %>%
  # 将容差查找表连接进来
  left_join(tolerance_df, by = c("target_force" = "target_force_map")) %>%
  mutate(
    # 计算偏差和容差 (使用连接后的列)
    deviation_abs = force - target_force,
    deviation_pct = (force - target_force) / target_force * 100,
    tolerance_abs_limit = tolerance_abs_map, # 使用映射来的容差
    tolerance_pct_limit = target_force * tolerance_pct_map / 100, # 使用映射来的容差
    # 判断容差
    within_tolerance_abs = abs(deviation_abs) <= tolerance_abs_limit,
    within_tolerance_pct = abs(deviation_abs) <= tolerance_pct_limit,
    within_tolerance = within_tolerance_abs & within_tolerance_pct
  )

# --- END OF FIX ---

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
# 4. 趋势分析（按目标力值分组）
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
# 5. 高级时间序列分析
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

# 2. 稳定性分析（游程检验）
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

# 3. 变化点检测
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
      
      window_size_cp <- min(10, n %/% 4)
      
      # 计算滑动窗口均值差异
      change_data <- force_data %>%
        mutate(
          moving_mean_diff = slider::slide_dbl(force, 
            ~ if(length(.x) >= 2*window_size_cp) {
              mid <- length(.x) %/% 2
              mean(.x[(mid-window_size_cp+1):mid]) - mean(.x[(mid+1):(mid+window_size_cp)])
            } else NA_real_,
            .before = window_size_cp, .after = window_size_cp, .complete = FALSE
          ),
          potential_change = abs(moving_mean_diff) > 2 * sd(force, na.rm = TRUE)
        ) %>%
        filter(potential_change, !is.na(moving_mean_diff))
      
      tibble(
        潜在变化点数量 = nrow(change_data),
        最大均值变化 = if(nrow(change_data) > 0) round(max(abs(change_data$moving_mean_diff)), 3) else 0
      )
    })
  ) %>%
  select(target_force, change_results) %>%
  unnest(change_results)

change_points <- change_point_analysis %>%
  filter(潜在变化点数量 > 0)

print("\n变化点检测:")
if(nrow(change_points) > 0) {
  print(change_points)
} else {
  print("未检测到明显的变化点")
}

# 4. 自相关分析
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

# 5. 过程能力分析
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

print("高级分析完成")

# ============================================================================
# 6. 数据可视化
# ============================================================================

print("\n=== 生成图表 ===")

# 1. 力值时间序列图（按目标力值着色，带容差指示）
tryCatch({
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
    scale_color_manual(values = custom_colors) +
    scale_fill_manual(values = custom_colors) +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(
      title = "力值时间序列图（按目标力值分组）",
      subtitle = "实心点=在容差内，空心点=超出容差，阴影=容差区间",
      x = "序号", 
      y = "力值(N)", 
      color = "目标力值",
      fill = "目标力值"
    )
  
  ggsave(file.path(output_dir, "force_time_series.png"), p1, width = 14, height = 10, dpi = 300)
  print("✓ 生成时间序列图")
}, error = function(e) {
  print(paste("✗ 时间序列图生成失败:", e$message))
})

# 2. 力值分布直方图（按目标力值分面）
tryCatch({
  p2 <- data_with_target %>%
    ggplot(aes(x = force, fill = factor(target_force))) +
    geom_histogram(bins = 15, alpha = 0.7, color = "white") +
    geom_vline(aes(xintercept = target_force), color = "red", linetype = "dashed", linewidth = 1) +
    geom_vline(data = data_with_target %>% group_by(target_force) %>% summarise(mean_force = mean(force)), 
               aes(xintercept = mean_force), color = "blue", linetype = "solid", linewidth = 1) +
    scale_fill_manual(values = custom_colors) +
    facet_wrap(~target_force, scales = "free", labeller = label_both) +
    labs(
      title = "力值分布直方图（按目标力值分组）",
      subtitle = "红虚线=目标值，蓝实线=实际均值",
      x = "力值 (N)",
      y = "频次",
      fill = "目标力值"
    )
  
  ggsave(file.path(output_dir, "force_histogram.png"), p2, width = 12, height = 8, dpi = 300)
  print("✓ 生成分布直方图")
}, error = function(e) {
  print(paste("✗ 分布直方图生成失败:", e$message))
})

# 3. 箱线图（按目标力值分组）
tryCatch({
  p3 <- data_with_target %>%
    ggplot(aes(x = factor(target_force), y = force, fill = factor(target_force))) +
    geom_boxplot(alpha = 0.7, outlier.color = "red", outlier.size = 2) +
    geom_hline(aes(yintercept = target_force), color = "red", linetype = "dashed") +
    stat_summary(fun = mean, geom = "point", shape = 23, size = 3, fill = "white") +
    scale_fill_manual(values = custom_colors) +
    labs(
      title = "力值箱线图（按目标力值分组）",
      subtitle = "红点=异常值，白菱形=均值，红虚线=目标值",
      x = "目标力值 (N)",
      y = "力值 (N)",
      fill = "目标力值"
    )
  
  ggsave(file.path(output_dir, "force_boxplot.png"), p3, width = 10, height = 8, dpi = 300)
  print("✓ 生成箱线图")
}, error = function(e) {
  print(paste("✗ 箱线图生成失败:", e$message))
})

# 4. 绝对偏差箱线图
tryCatch({
  p4 <- data_with_target %>%
    ggplot(aes(factor(target_force), deviation_abs, fill = factor(target_force))) +
    geom_boxplot(alpha = 0.7, outlier.color = "red") +
    geom_hline(yintercept = 0, color = "green", linetype = "solid", linewidth = 1) +
    geom_hline(yintercept = c(-tolerance_abs, tolerance_abs), 
               color = "orange", linetype = "dashed", linewidth = 1) +
    scale_fill_manual(values = custom_colors) +
    labs(
      title = "绝对偏差分布（按目标力值分组）",
      subtitle = "绿线=零偏差，橙色虚线=绝对容差限制",
      x = "目标力值(N)", 
      y = "绝对偏差(N)", 
      fill = "目标力值"
    )
  
  ggsave(file.path(output_dir, "deviation_analysis.png"), p4, width = 10, height = 8, dpi = 300)
  print("✓ 生成绝对偏差箱线图")
}, error = function(e) {
  print(paste("✗ 绝对偏差箱线图生成失败:", e$message))
})

# 5. 百分比偏差箱线图
tryCatch({
  p5 <- data_with_target %>%
    ggplot(aes(factor(target_force), deviation_pct, fill = factor(target_force))) +
    geom_boxplot(alpha = 0.7, outlier.color = "red") +
    geom_hline(yintercept = 0, color = "green", linetype = "solid", linewidth = 1) +
    geom_hline(yintercept = c(-tolerance_pct, tolerance_pct), 
               color = "orange", linetype = "dashed", linewidth = 1) +
    scale_fill_manual(values = custom_colors) +
    labs(
      title = "百分比偏差分布（按目标力值分组）",
      subtitle = "绿线=零偏差，橙色虚线=百分比容差限制",
      x = "目标力值(N)", 
      y = "百分比偏差(%)", 
      fill = "目标力值"
    )
  
  ggsave(file.path(output_dir, "percentage_deviation.png"), p5, width = 10, height = 8, dpi = 300)
  print("✓ 生成百分比偏差箱线图")
}, error = function(e) {
  print(paste("✗ 百分比偏差箱线图生成失败:", e$message))
})

# 6. Shewhart控制图
if(exists("data_with_target")) {
  tryCatch({
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
      scale_color_manual(values = custom_colors) +
      facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
      labs(
        title = "Shewhart控制图（按目标力值分组）",
        subtitle = "绿线=中心线，红虚线=3σ控制限，橙点线=2σ警戒线，X=异常值",
        x = "序号",
        y = "力值(N)",
        color = "目标力值"
      )
    
    ggsave(file.path(output_dir, "shewhart_control.png"), p6_control, width = 14, height = 10, dpi = 300)
    print("✓ 生成Shewhart控制图")
  }, error = function(e) {
    print(paste("✗ Shewhart控制图生成失败:", e$message))
  })
}

# 7. 移动平均图
if(exists("data_with_target") && "移动平均" %in% colnames(data_with_target)) {
  tryCatch({
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
      scale_color_manual(values = custom_colors) +
      scale_fill_manual(values = custom_colors) +
      facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
      labs(
        title = "移动平均分析（按目标力值分组）",
        subtitle = paste0("窗口大小=", window_size, "，彩色带=移动标准差范围"),
        x = "序号",
        y = "力值(N)",
        color = "目标力值",
        fill = "目标力值"
      )
    
    ggsave(file.path(output_dir, "moving_average.png"), p7_moving, width = 14, height = 10, dpi = 300)
    print("✓ 生成移动平均图")
  }, error = function(e) {
    print(paste("✗ 移动平均图生成失败:", e$message))
  })
}

# 8. 成功率分析图
tryCatch({
  p8 <- target_analysis %>%
    ggplot(aes(factor(target_force), 成功率_综合, fill = factor(target_force))) +
    geom_col(alpha = 0.7) +
    geom_hline(yintercept = 90, color = "orange", linetype = "dashed") +
    geom_hline(yintercept = 95, color = "green", linetype = "dashed") +
    geom_text(aes(label = paste0(成功率_综合, "%")), vjust = -0.5, color = "black", fontface = "bold") +
    scale_fill_manual(values = custom_colors) +
    ylim(0, 100) +
    labs(
      title = "综合成功率",
      x = "目标力值(N)", 
      y = "成功率(%)", 
      fill = "目标力值"
    )
  
  ggsave(file.path(output_dir, "success_rate.png"), p8, width = 10, height = 8, dpi = 300)
  print("✓ 生成成功率分析图")
}, error = function(e) {
  print(paste("✗ 成功率分析图生成失败:", e$message))
})

# 9. 过程能力图表（Cp, Cpk可视化）
if(exists("process_capability")) {
  tryCatch({
    p9_capability <- process_capability %>%
      pivot_longer(cols = c(Cp, Cpk), names_to = "指标", values_to = "值") %>%
      ggplot(aes(factor(target_force), 值, fill = 指标)) +
      geom_col(position = "dodge", alpha = 0.7) +
      geom_hline(yintercept = 1.0, color = "orange", linetype = "dashed") +
      geom_hline(yintercept = 1.33, color = "green", linetype = "dashed") +
      geom_text(aes(label = round(值, 2)), position = position_dodge(width = 0.9), vjust = -0.5) +
      scale_fill_manual(values = c("Cp" = "#2E86AB", "Cpk" = "#A23B72")) +
      labs(title = "过程能力指数（按目标力值分组）",
           subtitle = "橙线=合格线(1.0)，绿线=优秀线(1.33)",
           x = "目标力值(N)", y = "能力指数", fill = "指标类型")
    
    ggsave(file.path(output_dir, "process_capability.png"), p9_capability, width = 10, height = 8, dpi = 300)
    print("✓ 生成过程能力图")
  }, error = function(e) {
    print(paste("✗ 过程能力图生成失败:", e$message))
  })
}

# 10. 3D散点图数据（为前端准备）
tryCatch({
  scatter_data <- data_with_target %>%
    select(x, y, z, force, target_force, within_tolerance, deviation_abs, is_outlier) %>%
    slice_head(n = 1000)  # 限制数据点数量以提高性能
  
  write_csv(scatter_data, file.path(output_dir, "scatter_3d_data.csv"))
  print("✓ 生成3D散点图数据")
}, error = function(e) {
  print(paste("✗ 3D散点图数据生成失败:", e$message))
})

# 11. XYZ坐标对比矩阵
tryCatch({
  data_matrix <- data_with_target %>%
    select(x, y, z, target_force, within_tolerance) %>%
    mutate(target_force = factor(target_force))
  
  p11_matrix <- ggpairs(data_matrix, 
                       columns = 1:3,
                       aes(color = target_force, shape = within_tolerance),
                       upper = list(continuous = "points"),
                       lower = list(continuous = "points"),
                       diag = list(continuous = "densityDiag")) +
    scale_shape_manual(values = c(1, 16), name = "在容差内") +
    scale_color_manual(values = custom_colors) +
    labs(title = "XYZ坐标对比矩阵（按目标力值分组）")
  
  ggsave(file.path(output_dir, "coordinate_matrix.png"), p11_matrix, width = 12, height = 10, dpi = 300)
  print("✓ 生成散点图矩阵")
}, error = function(e) {
  print(paste("✗ 散点图矩阵生成失败:", e$message))
})

# 12. XY平面热力图
tryCatch({
  p12_heatmap <- data_with_target %>%
    ggplot(aes(x, y)) +
    stat_density_2d_filled(alpha = 0.7) +
    geom_point(aes(color = within_tolerance, shape = within_tolerance), size = 1.5) +
    scale_color_manual(values = c("red", "blue"), name = "在容差内") +
    scale_shape_manual(values = c(4, 16), name = "在容差内") +
    facet_wrap(~target_force, labeller = label_both) +
    labs(title = "XY平面密度热力图（按目标力值分组）", 
         x = "X坐标", y = "Y坐标")
  
  ggsave(file.path(output_dir, "xy_heatmap.png"), p12_heatmap, width = 14, height = 10, dpi = 300)
  print("✓ 生成XY平面热力图")
}, error = function(e) {
  print(paste("✗ XY平面热力图生成失败:", e$message))
})

# 13. 并行坐标图
tryCatch({
  data_parallel <- data_with_target %>%
    select(x, y, z, force, target_force, within_tolerance) %>%
    mutate(target_force = factor(target_force)) %>%
    slice_head(n = 500)  # 限制数据点以提高可读性
  
  p13_parallel <- ggparcoord(data_parallel, 
                            columns = 1:4, 
                            groupColumn = "target_force",
                            alphaLines = 0.3,
                            showPoints = TRUE) +
    scale_color_manual(values = custom_colors) +
    labs(title = "并行坐标图 - 多维异常模式（按目标力值分组）", color = "目标力值")
  
  ggsave(file.path(output_dir, "parallel_coordinates.png"), p13_parallel, width = 12, height = 8, dpi = 300)
  print("✓ 生成并行坐标图")
}, error = function(e) {
  print(paste("✗ 并行坐标图生成失败:", e$message))
})

# 14. 2D投影图组合
tryCatch({
  # XY投影
  p14a_xy <- data_with_target %>%
    ggplot(aes(x, y, color = factor(target_force))) +
    geom_point(aes(shape = within_tolerance, size = abs(deviation_abs)), alpha = 0.7) +
    scale_shape_manual(values = c(1, 16), name = "在容差内") +
    scale_size_continuous(range = c(1, 4), name = "绝对偏差") +
    scale_color_manual(values = custom_colors) +
    labs(title = "XY投影", color = "目标力值")
  
  # XZ投影  
  p14b_xz <- data_with_target %>%
    ggplot(aes(x, z, color = factor(target_force))) +
    geom_point(aes(shape = within_tolerance, size = abs(deviation_abs)), alpha = 0.7) +
    scale_shape_manual(values = c(1, 16), name = "在容差内") +
    scale_size_continuous(range = c(1, 4), name = "绝对偏差") +
    scale_color_manual(values = custom_colors) +
    labs(title = "XZ投影", color = "目标力值")
  
  # YZ投影
  p14c_yz <- data_with_target %>%
    ggplot(aes(y, z, color = factor(target_force))) +
    geom_point(aes(shape = within_tolerance, size = abs(deviation_abs)), alpha = 0.7) +
    scale_shape_manual(values = c(1, 16), name = "在容差内") +
    scale_size_continuous(range = c(1, 4), name = "绝对偏差") +
    scale_color_manual(values = custom_colors) +
    labs(title = "YZ投影", color = "目标力值")
  
  # 组合投影图
  p14_combined <- (p14a_xy | p14b_xz) / p14c_yz +
    plot_annotation(title = "2D投影图组合（按目标力值分组）")
  
  ggsave(file.path(output_dir, "projection_combined.png"), p14_combined, width = 14, height = 10, dpi = 300)
  print("✓ 生成2D投影图组合")
}, error = function(e) {
  print(paste("✗ 2D投影图组合生成失败:", e$message))
})

# 15. 空间聚类异常检测图
tryCatch({
  coords_data <- data_with_target %>% select(x, y, z)
  distances <- dist(coords_data)
  hc <- hclust(distances)
  data_with_target$cluster <- cutree(hc, k = 5)
  
  p15_cluster <- data_with_target %>%
    ggplot(aes(x, y)) +
    geom_point(aes(color = factor(cluster), 
                   shape = within_tolerance,
                   size = abs(deviation_abs)), alpha = 0.7) +
    scale_shape_manual(values = c(1, 16), name = "在容差内") +
    scale_size_continuous(range = c(1, 5), name = "绝对偏差") +
    scale_color_manual(values = custom_colors) +
    facet_wrap(~target_force, labeller = label_both) +
    labs(title = "空间聚类 + 异常检测（按目标力值分组）", 
         color = "空间聚类")
  
  ggsave(file.path(output_dir, "spatial_clustering.png"), p15_cluster, width = 14, height = 10, dpi = 300)
  print("✓ 生成空间聚类图")
}, error = function(e) {
  print(paste("✗ 空间聚类图生成失败:", e$message))
})

# 16. 成功率趋势分析
tryCatch({
  success_trend_batch_size <- 10
  success_trend <- data_with_target %>%
    mutate(batch = ceiling(sequence / success_trend_batch_size)) %>%
    group_by(batch, target_force) %>%
    summarise(
      success_rate = mean(within_tolerance) * 100,
      batch_center = mean(sequence),
      .groups = 'drop'
    )
  
  p16_success <- success_trend %>%
    ggplot(aes(batch, success_rate, color = factor(target_force))) +
    geom_line(linewidth = 1) +
    geom_point(size = 2) +
    geom_hline(yintercept = 90, color = "green", linetype = "dashed", alpha = 0.7) +
    geom_hline(yintercept = 95, color = "blue", linetype = "dashed", alpha = 0.7) +
    scale_color_manual(values = custom_colors) +
    facet_wrap(~target_force, labeller = label_both) +
    ylim(0, 100) +
    labs(title = "成功率趋势分析（按目标力值分组）", 
         subtitle = paste0("批次大小=", success_trend_batch_size, "，绿线=90%，蓝线=95%"),
         x = "批次", y = "成功率(%)", color = "目标力值")
  
  ggsave(file.path(output_dir, "success_rate_trend.png"), p16_success, width = 14, height = 10, dpi = 300)
  print("✓ 生成成功率趋势图")
}, error = function(e) {
  print(paste("✗ 成功率趋势图生成失败:", e$message))
})

# 17. 质量控制仪表盘
if(nrow(target_analysis) > 0) {
  tryCatch({
    # 成功率表盘
    p17a_gauge <- target_analysis %>%
      ggplot(aes(factor(target_force), 成功率_综合, fill = factor(target_force))) +
      geom_col(alpha = 0.7) +
      geom_hline(yintercept = 90, color = "orange", linetype = "dashed") +
      geom_hline(yintercept = 95, color = "green", linetype = "dashed") +
      geom_text(aes(label = paste0(成功率_综合, "%")), vjust = -0.5, color = "black", fontface = "bold") +
      scale_fill_manual(values = custom_colors) +
      ylim(0, 100) +
      labs(title = "综合成功率", x = "目标力值(N)", y = "成功率(%)", fill = "目标力值")
    
    # 变异系数表盘
    cv_data <- data_with_target %>%
      group_by(target_force) %>%
      summarise(cv = sd(force)/mean(force)*100, .groups = 'drop')
    
    p17b_cv <- cv_data %>%
      ggplot(aes(factor(target_force), cv, fill = factor(target_force))) +
      geom_col(alpha = 0.7) +
      geom_hline(yintercept = 5, color = "green", linetype = "dashed") +
      geom_hline(yintercept = 10, color = "orange", linetype = "dashed") +
      geom_text(aes(label = paste0(round(cv, 1), "%")), vjust = -0.5, color = "black", fontface = "bold") +
      scale_fill_manual(values = custom_colors) +
      labs(title = "变异系数", x = "目标力值(N)", y = "变异系数(%)", fill = "目标力值")
    
    # 组合仪表盘
    p17_dashboard <- p17a_gauge / p17b_cv +
      plot_annotation(title = "质量控制仪表盘（按目标力值分组）")
    
    ggsave(file.path(output_dir, "quality_dashboard.png"), p17_dashboard, width = 12, height = 10, dpi = 300)
    print("✓ 生成质量仪表盘")
  }, error = function(e) {
    print(paste("✗ 质量仪表盘生成失败:", e$message))
  })
}

# 18. 相关性分析
if(all(c("x", "y", "z", "force") %in% colnames(data_with_target))) {
  tryCatch({
    cor_data <- data_with_target %>%
      select(x, y, z, force) %>%
      cor(use = "complete.obs") %>%
      as_tibble(rownames = "var1") %>%
      pivot_longer(-var1, names_to = "var2", values_to = "correlation")
    
    p18 <- cor_data %>%
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
    
    ggsave(file.path(output_dir, "correlation_matrix.png"), p18, width = 8, height = 6, dpi = 300)
    print("✓ 生成相关性矩阵")
  }, error = function(e) {
    print(paste("✗ 相关性矩阵生成失败:", e$message))
  })
}

# 19. 帕雷托图 - 异常原因分析
tryCatch({
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
    p19_pareto <- pareto_data %>%
      ggplot(aes(reorder(异常类型, -数量))) +
      geom_col(aes(y = 数量, fill = factor(target_force)), alpha = 0.7) +
      geom_line(aes(y = 累计百分比 * max(数量) / 100, group = target_force, color = factor(target_force)), 
                linewidth = 1) +
      geom_point(aes(y = 累计百分比 * max(数量) / 100, color = factor(target_force)), size = 2) +
      scale_y_continuous(
        sec.axis = sec_axis(~. * 100 / max(pareto_data$数量), name = "累计百分比 (%)")
      ) +
      scale_fill_manual(values = custom_colors) +
      scale_color_manual(values = custom_colors) +
      facet_wrap(~target_force, labeller = label_both, scales = "free") +
      labs(title = "帕雷托图 - 异常原因分析（按目标力值分组）",
           subtitle = "识别主要异常类型",
           x = "异常类型", y = "异常数量", 
           fill = "目标力值", color = "目标力值") +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
    
    ggsave(file.path(output_dir, "pareto_analysis.png"), p19_pareto, width = 14, height = 10, dpi = 300)
    print("✓ 生成帕雷托图")
  }
}, error = function(e) {
  print(paste("✗ 帕雷托图生成失败:", e$message))
})

# 20. 残差分析图
tryCatch({
  residual_data <- data_with_target %>%
    group_by(target_force) %>%
    mutate(
      fitted_value = mean(force),
      residual = force - fitted_value,
      standardized_residual = residual / sd(residual)
    ) %>%
    ungroup()
  
  p20_residual <- residual_data %>%
    ggplot(aes(fitted_value, residual, color = factor(target_force))) +
    geom_point(aes(shape = within_tolerance), alpha = 0.7) +
    geom_hline(yintercept = 0, color = "red", linetype = "dashed") +
    geom_smooth(method = "loess", se = TRUE, alpha = 0.3) +
    scale_shape_manual(values = c(1, 16), name = "在容差内") +
    scale_color_manual(values = custom_colors) +
    facet_wrap(~target_force, scales = "free", labeller = label_both) +
    labs(title = "残差分析图（按目标力值分组）",
         subtitle = "检查模型适合度和异常模式",
         x = "拟合值", y = "残差", color = "目标力值")
  
  ggsave(file.path(output_dir, "residual_analysis.png"), p20_residual, width = 14, height = 10, dpi = 300)
  print("✓ 生成残差分析图")
}, error = function(e) {
  print(paste("✗ 残差分析图生成失败:", e$message))
})

# 21. QQ图 - 正态性检验
tryCatch({
  p21_qq <- data_with_target %>%
    ggplot(aes(sample = force, color = factor(target_force))) +
    stat_qq() +
    stat_qq_line() +
    scale_color_manual(values = custom_colors) +
    facet_wrap(~target_force, scales = "free", labeller = label_both) +
    labs(title = "QQ图 - 正态性检验（按目标力值分组）",
         subtitle = "检验数据分布的正态性",
         x = "理论分位数", y = "样本分位数", color = "目标力值")
  
  ggsave(file.path(output_dir, "qq_plot.png"), p21_qq, width = 12, height = 8, dpi = 300)
  print("✓ 生成QQ图")
}, error = function(e) {
  print(paste("✗ QQ图生成失败:", e$message))
})

# 22. 运行图（Run Chart）
tryCatch({
  run_chart_data <- data_with_target %>%
    group_by(target_force) %>%
    mutate(
      center_line = median(force),
      above_center = force > center_line,
      run_id = cumsum(above_center != lag(above_center, default = first(above_center)))
    ) %>%
    ungroup()
  
  p22_run <- run_chart_data %>%
    ggplot(aes(sequence, force, color = factor(target_force))) +
    geom_line(alpha = 0.7, linewidth = 0.5) +
    geom_point(aes(shape = above_center), alpha = 0.7) +
    geom_hline(aes(yintercept = center_line), color = "blue", linetype = "dashed") +
    scale_shape_manual(values = c(25, 24), name = "相对中位数") +
    scale_color_manual(values = custom_colors) +
    facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
    labs(title = "运行图（按目标力值分组）",
         subtitle = "蓝虚线=中位数，检测非随机模式",
         x = "序号", y = "力值(N)", color = "目标力值")
  
  ggsave(file.path(output_dir, "run_chart.png"), p22_run, width = 14, height = 10, dpi = 300)
  print("✓ 生成运行图")
}, error = function(e) {
  print(paste("✗ 运行图生成失败:", e$message))
})

# 23. 雷达图 - 质量指标综合评估
if(exists("target_analysis") && exists("process_capability")) {
  tryCatch({
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
    
    p23_radar <- radar_data %>%
      ggplot(aes(指标, 得分, group = factor(target_force), color = factor(target_force))) +
      geom_line(linewidth = 1) +
      geom_point(size = 3) +
      coord_polar() +
      ylim(0, 100) +
      scale_color_manual(values = custom_colors) +
      labs(title = "质量指标雷达图（按目标力值分组）",
           subtitle = "综合质量评估（满分100分）",
           color = "目标力值")
    
    ggsave(file.path(output_dir, "radar_chart.png"), p23_radar, width = 10, height = 8, dpi = 300)
    print("✓ 生成雷达图")
  }, error = function(e) {
    print(paste("✗ 雷达图生成失败:", e$message))
  })
}

# 24. CUSUM累计和控制图
tryCatch({
  cusum_data <- data_with_target %>%
    group_by(target_force) %>%
    arrange(sequence) %>%
    mutate(
      cusum_plus = cumsum(pmax(0, force - target_force - 1)),
      cusum_minus = cumsum(pmax(0, target_force - force - 1))
    ) %>%
    ungroup()
  
  if(nrow(cusum_data) > 0) {
    p24_cusum <- cusum_data %>%
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
    
    ggsave(file.path(output_dir, "cusum_chart.png"), p24_cusum, width = 14, height = 10, dpi = 300)
    print("✓ 生成CUSUM控制图")
  }
}, error = function(e) {
  print(paste("✗ CUSUM控制图生成失败:", e$message))
})

# 25. EWMA指数加权移动平均控制图
tryCatch({
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
    p25_ewma <- ewma_data %>%
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
      scale_color_manual(values = custom_colors) +
      facet_wrap(~target_force, scales = "free_y", 
                 labeller = labeller(target_force = function(x) paste("目标力值:", x, "N"))) +
      labs(title = "EWMA指数加权移动平均控制图",
           subtitle = "对小幅偏移敏感的控制图，平滑参数λ=0.2",
           x = "序号", y = "EWMA值", color = "目标力值")
    
    ggsave(file.path(output_dir, "ewma_chart.png"), p25_ewma, width = 14, height = 10, dpi = 300)
    print("✓ 生成EWMA控制图")
  }
}, error = function(e) {
  print(paste("✗ EWMA控制图生成失败:", e$message))
})

# 26. I-MR个值移动极差控制图
tryCatch({
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
    p26a_i <- imr_data %>%
      ggplot(aes(x = sequence)) +
      geom_line(aes(y = force, color = factor(target_force)), alpha = 0.7) +
      geom_point(aes(y = force, color = factor(target_force))) +
      geom_hline(aes(yintercept = x_mean), color = "green", linewidth = 1) +
      geom_hline(aes(yintercept = ucl_x), color = "red", linetype = "dashed") +
      geom_hline(aes(yintercept = lcl_x), color = "red", linetype = "dashed") +
      geom_point(data = imr_data %>% filter(force > ucl_x | force < lcl_x),
                 aes(y = force), shape = 4, size = 3, color = "red") +
      scale_color_manual(values = custom_colors) +
      facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
      labs(title = "个值控制图 (I Chart)", y = "个值", color = "目标力值")
    
    # MR图（移动极差图）
    p26b_mr <- imr_data %>%
      ggplot(aes(x = sequence)) +
      geom_line(aes(y = mr, color = factor(target_force)), alpha = 0.7) +
      geom_point(aes(y = mr, color = factor(target_force))) +
      geom_hline(aes(yintercept = mr_mean), color = "green", linewidth = 1) +
      geom_hline(aes(yintercept = ucl_mr), color = "red", linetype = "dashed") +
      scale_color_manual(values = custom_colors) +
      facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
      labs(title = "移动极差控制图 (MR Chart)", 
           x = "序号", y = "移动极差", color = "目标力值")
    
    # 组合I-MR图
    p26_imr_combined <- p26a_i / p26b_mr +
      plot_annotation(title = "I-MR控制图组合（按目标力值分组）",
                      subtitle = "适用于个别测量值的统计控制")
    
    ggsave(file.path(output_dir, "imr_chart.png"), p26_imr_combined, width = 14, height = 12, dpi = 300)
    print("✓ 生成I-MR控制图")
  }
}, error = function(e) {
  print(paste("✗ I-MR控制图生成失败:", e$message))
})

# 27. 过程能力分析直方图
if(nrow(target_analysis) > 0) {
  tryCatch({
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
    
    p27_capability <- capability_data %>%
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
      scale_fill_manual(values = custom_colors) +
      scale_color_manual(values = custom_colors) +
      facet_wrap(~target_force, scales = "free", 
                 labeller = labeller(target_force = function(x) paste("目标力值:", x, "N"))) +
      labs(title = "过程能力分析直方图",
           subtitle = "红线=规格限制，绿线=目标值，蓝线=过程均值",
           x = "力值 (N)", y = "密度", 
           fill = "目标力值", color = "目标力值")
    
    ggsave(file.path(output_dir, "capability_histogram.png"), p27_capability, width = 14, height = 10, dpi = 300)
    print("✓ 生成过程能力直方图")
  }, error = function(e) {
    print(paste("✗ 过程能力直方图生成失败:", e$message))
  })
}

# 28. 位置异常率热力图
tryCatch({
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
    p28_position_heatmap <- position_heatmap_data %>%
      ggplot(aes(x_bin, y_bin, fill = 异常率)) +
      geom_tile() +
      scale_fill_gradient2(low = "green", mid = "yellow", high = "red", 
                          midpoint = 50, name = "异常率(%)") +
      facet_wrap(~target_force, labeller = label_both) +
      labs(title = "位置-异常率热力图（按目标力值分组）",
           subtitle = "识别空间异常分布模式",
           x = "X坐标", y = "Y坐标")
    
    ggsave(file.path(output_dir, "position_heatmap.png"), p28_position_heatmap, width = 14, height = 10, dpi = 300)
    print("✓ 生成位置异常率热力图")
  }
}, error = function(e) {
  print(paste("✗ 位置异常率热力图生成失败:", e$message))
})

# 29. 质量损失瀑布图
if(nrow(target_analysis) > 0) {
  tryCatch({
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
    
    p29_waterfall <- waterfall_data %>%
      ggplot() +
      geom_col(aes(target_label, 损失率, fill = factor(target_force)), alpha = 0.7) +
      geom_step(aes(target_label, cumsum_loss, group = 1), 
                color = "red", linewidth = 1, direction = "mid") +
      geom_point(aes(target_label, cumsum_loss), color = "red", size = 3) +
      geom_text(aes(target_label, 损失率/2, label = paste0(round(损失率, 1), "%")), 
                fontface = "bold") +
      scale_fill_manual(values = custom_colors) +
      labs(title = "质量损失瀑布图（按目标力值分组）",
           subtitle = "累积质量损失分析",
           x = "目标力值", y = "损失率(%)", fill = "目标力值")
    
    ggsave(file.path(output_dir, "waterfall_chart.png"), p29_waterfall, width = 10, height = 8, dpi = 300)
    print("✓ 生成瀑布图")
  }, error = function(e) {
    print(paste("✗ 瀑布图生成失败:", e$message))
  })
}

# 30. X-bar & R控制图组合
if(exists("data_with_target") && "移动平均" %in% colnames(data_with_target)) {
  tryCatch({
    # X-bar图（均值图）
    xbar_data <- data_with_target %>%
      group_by(target_force) %>%
      mutate(
        xbar = mean(force),
        ucl_xbar = xbar + 3*sd(force)/sqrt(n()),
        lcl_xbar = xbar - 3*sd(force)/sqrt(n())
      ) %>%
      ungroup()
    
    p30a_xbar <- xbar_data %>%
      ggplot(aes(sequence, force, color = factor(target_force))) +
      geom_line(alpha = 0.7) +
      geom_point(alpha = 0.7) +
      geom_hline(aes(yintercept = xbar), color = "green") +
      geom_hline(aes(yintercept = ucl_xbar), color = "red", linetype = "dashed") +
      geom_hline(aes(yintercept = lcl_xbar), color = "red", linetype = "dashed") +
      scale_color_manual(values = custom_colors) +
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
    
    p30b_r <- r_data %>%
      ggplot(aes(sequence, range_val, color = factor(target_force))) +
      geom_line(alpha = 0.7) +
      geom_point(alpha = 0.7) +
      geom_hline(aes(yintercept = r_bar), color = "green") +
      geom_hline(aes(yintercept = ucl_r), color = "red", linetype = "dashed") +
      scale_color_manual(values = custom_colors) +
      facet_wrap(~target_force, scales = "free_y", labeller = label_both) +
      labs(title = "R控制图", x = "序号", y = "移动极差", color = "目标力值")
    
    # 组合控制图
    p30_combined_control <- p30a_xbar / p30b_r +
      plot_annotation(title = "X-bar & R 控制图组合（按目标力值分组）")
    
    ggsave(file.path(output_dir, "xbar_r_chart.png"), p30_combined_control, width = 14, height = 12, dpi = 300)
    print("✓ 生成X-bar & R控制图组合")
  }, error = function(e) {
    print(paste("✗ X-bar & R控制图组合生成失败:", e$message))
  })
}

print("所有图表生成完成")

# ============================================================================
# 6.5. 新增高级分析模块
# ============================================================================

print("开始新增高级分析...")

# 1. 空间分析 (Spatial Analysis)
print("进行空间分析...")

# 为数据添加误差值列 - 使用绝对偏差作为误差值
data_with_target <- data_with_target %>%
  mutate(error_value = abs(deviation_abs))

# 指标1：误差热力图数据 (Error Heatmap Data)
tryCatch({
  error_heatmap_data <- data_with_target %>%
    select(target_force, x, y, z, error_value) %>%
    group_nest(target_force) %>%
    rename(heatmap_points = data) %>%
    mutate(
      point_count = map_int(heatmap_points, nrow)
    )
  
  print("✓ 生成误差热力图数据")
}, error = function(e) {
  print(paste("✗ 误差热力图数据生成失败:", e$message))
  error_heatmap_data <- tibble()
})

# 指标2：误差与坐标的相关性 (Error vs. Coordinate Correlation)
tryCatch({
  spatial_correlation <- data_with_target %>%
    group_by(target_force) %>%
    summarise(
      error_vs_x = cor(error_value, x, use = "complete.obs"),
      error_vs_y = cor(error_value, y, use = "complete.obs"),
      error_vs_z = cor(error_value, z, use = "complete.obs"),
      n_points = n(),
      .groups = 'drop'
    ) %>%
    mutate_if(is.numeric, round, 4)
  
  print("✓ 计算误差与坐标相关性")
  print(spatial_correlation)
}, error = function(e) {
  print(paste("✗ 空间相关性分析失败:", e$message))
  spatial_correlation <- tibble()
})

# 生成空间相关性图表
if(nrow(spatial_correlation) > 0) {
  tryCatch({
    # 相关性系数热力图
    correlation_long <- spatial_correlation %>%
      select(target_force, error_vs_x, error_vs_y, error_vs_z) %>%
      pivot_longer(cols = c(error_vs_x, error_vs_y, error_vs_z), 
                   names_to = "coordinate", values_to = "correlation") %>%
      mutate(
        coordinate = case_when(
          coordinate == "error_vs_x" ~ "X坐标",
          coordinate == "error_vs_y" ~ "Y坐标", 
          coordinate == "error_vs_z" ~ "Z坐标"
        )
      )
    
    p31_spatial_corr <- correlation_long %>%
      ggplot(aes(coordinate, factor(target_force), fill = correlation)) +
      geom_tile(color = "white", linewidth = 1) +
      geom_text(aes(label = round(correlation, 3)), color = "black", fontface = "bold") +
      scale_fill_gradient2(low = "blue", mid = "white", high = "red", 
                          midpoint = 0, name = "相关系数") +
      labs(title = "误差与坐标相关性矩阵",
           subtitle = "红色=正相关，蓝色=负相关，数值越接近±1相关性越强",
           x = "坐标轴", y = "目标力值(N)") +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
    
    ggsave(file.path(output_dir, "spatial_correlation_matrix.png"), p31_spatial_corr, 
           width = 8, height = 6, dpi = 300)
    print("✓ 生成空间相关性矩阵图")
  }, error = function(e) {
    print(paste("✗ 空间相关性图表生成失败:", e$message))
  })
}

# 生成误差分布3D散点图
tryCatch({
  p32_error_3d <- data_with_target %>%
    ggplot(aes(x, y)) +
    geom_point(aes(color = error_value, size = error_value), alpha = 0.7) +
    scale_color_gradient(low = "green", high = "red", name = "误差值") +
    scale_size_continuous(range = c(1, 4), name = "误差值") +
    facet_wrap(~target_force, labeller = label_both) +
    labs(title = "误差空间分布图（XY平面）",
         subtitle = "颜色和大小表示误差大小",
         x = "X坐标", y = "Y坐标")
  
  ggsave(file.path(output_dir, "error_spatial_distribution.png"), p32_error_3d, 
         width = 12, height = 8, dpi = 300)
  print("✓ 生成误差空间分布图")
}, error = function(e) {
  print(paste("✗ 误差空间分布图生成失败:", e$message))
})

# 2. 误差分布特性分析 (Error Distribution Analysis)
print("进行误差分布特性分析...")

# 指标3：误差正态性检验 (Error Normality Test)
# 检查是否有shapiro包，如果没有则使用基础R的shapiro.test
tryCatch({
  normality_tests <- data_with_target %>%
    group_by(target_force) %>%
    summarise(
      n_points = n(),
      shapiro_p_value = if(n() >= 3 && n() <= 5000) {
        shapiro.test(error_value)$p.value
      } else {
        NA_real_  # Shapiro-Wilk test requires 3 <= n <= 5000
      },
      mean_error = mean(error_value),
      std_error = sd(error_value),
      skewness = if(n() > 2) {
        sum((error_value - mean(error_value))^3) / (n() * sd(error_value)^3)
      } else NA_real_,
      kurtosis = if(n() > 3) {
        sum((error_value - mean(error_value))^4) / (n() * sd(error_value)^4) - 3
      } else NA_real_,
      is_normal = ifelse(is.na(shapiro_p_value), NA, shapiro_p_value > 0.05),
      .groups = 'drop'
    ) %>%
    mutate_if(is.numeric, round, 6)
  
  print("✓ 完成误差正态性检验")
  print(normality_tests)
}, error = function(e) {
  print(paste("✗ 正态性检验失败:", e$message))
  normality_tests <- tibble()
})

# 生成误差分布特性图表
if(nrow(normality_tests) > 0) {
  tryCatch({
    # 误差分布直方图 + 正态拟合
    p33_error_dist <- data_with_target %>%
      ggplot(aes(x = error_value)) +
      geom_histogram(aes(y = after_stat(density)), bins = 15, 
                     alpha = 0.7, fill = "lightblue", color = "white") +
      geom_density(color = "blue", linewidth = 1.2) +
      stat_function(fun = function(x) {
        dnorm(x, mean = mean(data_with_target$error_value), 
              sd = sd(data_with_target$error_value))
      }, color = "red", linewidth = 1, linetype = "dashed") +
      facet_wrap(~target_force, scales = "free", labeller = label_both) +
      labs(title = "误差分布特性分析",
           subtitle = "蓝线=实际密度，红虚线=正态分布拟合",
           x = "误差值", y = "密度")
    
    ggsave(file.path(output_dir, "error_distribution_analysis.png"), p33_error_dist, 
           width = 12, height = 8, dpi = 300)
    print("✓ 生成误差分布分析图")
  }, error = function(e) {
    print(paste("✗ 误差分布分析图生成失败:", e$message))
  })
}

# QQ图分析（误差的正态性）
tryCatch({
  p34_error_qq <- data_with_target %>%
    ggplot(aes(sample = error_value)) +
    stat_qq() +
    stat_qq_line(color = "red", linewidth = 1) +
    facet_wrap(~target_force, scales = "free", labeller = label_both) +
    labs(title = "误差分布QQ图",
         subtitle = "检验误差是否符合正态分布",
         x = "理论分位数", y = "样本分位数")
  
  ggsave(file.path(output_dir, "error_qq_plot.png"), p34_error_qq, 
         width = 12, height = 8, dpi = 300)
  print("✓ 生成误差QQ图")
}, error = function(e) {
  print(paste("✗ 误差QQ图生成失败:", e$message))
})

# 3. 可移动式压力采集装置多维分析 (Robot Pressure Testing Multi-dimensional Analysis)
print("进行可移动式压力采集装置多维分析...")

# 适配机器人压力测试场景的分析
tryCatch({
  # 创建位置区域分组（基于X、Y坐标分区）
  data_with_category <- data_with_target %>%
    mutate(
      # 基于X、Y坐标创建位置区域（四象限分区）
      position_group = case_when(
        x < 100 & y < 100 ~ "位置区域-A(X<100, Y<100)",
        x >= 100 & y < 100 ~ "位置区域-B(X>=100, Y<100)",
        x < 100 & y >= 100 ~ "位置区域-C(X<100, Y>=100)",
        TRUE ~ "位置区域-D(X>=100, Y>=100)"
      )
    )
  
  # 按位置区域分组的性能统计
  performance_by_position <- data_with_category %>%
    group_by(position_group, target_force) %>%
    summarise(
      数据点数 = n(),
      成功率 = round(mean(within_tolerance) * 100, 2),
      平均误差 = round(mean(error_value), 3),
      误差标准差 = round(sd(error_value), 3),
      最大误差 = round(max(error_value), 3),
      平均力值 = round(mean(force), 2),
      .groups = 'drop'
    )
  
  # 机器人施压一致性分析
  robot_consistency_analysis <- list(
    # 力控重复性（各目标力值的变异系数）
    force_repeatability = data_with_target %>%
      group_by(target_force) %>%
      summarise(cv = round(sd(force) / mean(force) * 100, 2), .groups = 'drop') %>%
      deframe() %>%
      setNames(paste0(names(.), "N_cv")),
    
    # 位置精度（X、Y、Z坐标的标准差）
    position_accuracy = list(
      x_std = round(sd(data_with_target$x), 1),
      y_std = round(sd(data_with_target$y), 1),
      z_std = round(sd(data_with_target$z), 1)
    )
  )
  
  print("✓ 完成可移动式压力采集装置多维分析")
  print("按位置区域分组性能:")
  print(performance_by_position)
  print("机器人一致性分析:")
  print(robot_consistency_analysis)
}, error = function(e) {
  print(paste("✗ 可移动式压力采集装置多维分析失败:", e$message))
  performance_by_position <- tibble()
  robot_consistency_analysis <- list()
})

# 生成可移动式压力采集装置多维分析图表
if(nrow(performance_by_position) > 0) {
  tryCatch({
    # 位置区域性能对比图
    p35_position_perf <- performance_by_position %>%
      ggplot(aes(position_group, 成功率, fill = factor(target_force))) +
      geom_col(position = "dodge", alpha = 0.7) +
      geom_text(aes(label = paste0(成功率, "%")), 
                position = position_dodge(width = 0.9), vjust = -0.5, size = 3) +
      geom_hline(yintercept = 90, color = "orange", linetype = "dashed") +
      geom_hline(yintercept = 95, color = "green", linetype = "dashed") +
      scale_fill_manual(values = custom_colors) +
      theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
      labs(title = "各位置区域性能对比（成功率）",
           subtitle = "橙线=90%基准，绿线=95%优秀",
           x = "位置区域", y = "成功率(%)", fill = "目标力值")
    
    ggsave(file.path(output_dir, "position_performance_comparison.png"), p35_position_perf, 
           width = 12, height = 8, dpi = 300)
    print("✓ 生成位置区域性能对比图")
  }, error = function(e) {
    print(paste("✗ 位置区域性能对比图生成失败:", e$message))
  })
  
  tryCatch({
    # 机器人一致性分析图
    if(length(robot_consistency_analysis$force_repeatability) > 0) {
      repeatability_data <- data.frame(
        target_force = as.numeric(gsub("N_cv", "", names(robot_consistency_analysis$force_repeatability))),
        cv = as.numeric(robot_consistency_analysis$force_repeatability)
      )
      
      p36_robot_consistency <- repeatability_data %>%
        ggplot(aes(factor(target_force), cv, fill = factor(target_force))) +
        geom_col(alpha = 0.7) +
        geom_text(aes(label = paste0(round(cv, 1), "%")), vjust = -0.5, size = 4) +
        geom_hline(yintercept = 5, color = "green", linetype = "dashed") +
        geom_hline(yintercept = 10, color = "orange", linetype = "dashed") +
        scale_fill_manual(values = custom_colors) +
        labs(title = "机器人力控重复性分析（变异系数）",
             subtitle = "绿线=5%优秀，橙线=10%合格",
             x = "目标力值(N)", y = "变异系数(%)", fill = "目标力值")
      
      ggsave(file.path(output_dir, "robot_consistency_analysis.png"), p36_robot_consistency, 
             width = 10, height = 8, dpi = 300)
      print("✓ 生成机器人一致性分析图")
    }
  }, error = function(e) {
    print(paste("✗ 机器人一致性分析图生成失败:", e$message))
  })
}

# 生成位置相关变异分析
if(nrow(performance_by_position) > 0) {
  tryCatch({
    # ANOVA分析 - 识别位置对精度的影响
    anova_results <- list()
    
    for(tf in unique(data_with_category$target_force)) {
      subset_data <- data_with_category %>% filter(target_force == tf)
      
      if(nrow(subset_data) > 10 && length(unique(subset_data$position_group)) > 1) {
        # 位置区域对精度的影响
        anova_position <- aov(error_value ~ position_group, data = subset_data)
        anova_results[[paste0("target_", tf, "_position")]] <- summary(anova_position)[[1]]$`Pr(>F)`[1]
      }
    }
    
    print("✓ 完成位置相关方差分析")
  }, error = function(e) {
    print(paste("✗ 位置相关ANOVA分析失败:", e$message))
    anova_results <- list()
  })
}

print("✓ 新增高级分析完成")

# ============================================================================
# 7. 保存分析结果
# ============================================================================

print("保存分析结果...")

# 保存清理后的数据
write_csv(data_with_target, file.path(output_dir, "cleaned_data.csv"))

# 整合所有分析结果
analysis_results <- list(
  # 基础统计
  data_summary = as.data.frame(data_summary),
  overall_stats = as.data.frame(overall_stats),
  target_analysis = as.data.frame(target_analysis),
  
  # 趋势分析
  trend_stats = as.data.frame(trend_stats),
  
  # 高级分析
  outlier_summary = as.data.frame(outlier_summary),
  stability_analysis = as.data.frame(stability_analysis),
  change_point_analysis = as.data.frame(change_point_analysis),
  autocorr_analysis = as.data.frame(autocorr_analysis),
  process_capability = if(exists("process_capability")) as.data.frame(process_capability) else NULL,
  
  # 新增高级分析结果
  spatial_analysis = list(
    # 误差热力图数据
    error_heatmap_data = if(exists("error_heatmap_data") && nrow(error_heatmap_data) > 0) {
      # 将嵌套数据转换为可序列化的格式
      error_heatmap_data %>%
        mutate(heatmap_points = map(heatmap_points, as.data.frame)) %>%
        as.data.frame()
    } else NULL,
    # 误差与坐标相关性
    spatial_correlation = if(exists("spatial_correlation") && nrow(spatial_correlation) > 0) {
      as.data.frame(spatial_correlation)
    } else NULL
  ),
  
  error_distribution_analysis = list(
    # 误差正态性检验
    normality_tests = if(exists("normality_tests") && nrow(normality_tests) > 0) {
      as.data.frame(normality_tests)
    } else NULL
  ),
  
  multi_source_variation_analysis = list(
    # 按位置区域分组的性能统计
    performance_by_position = if(exists("performance_by_position") && nrow(performance_by_position) > 0) {
      as.data.frame(performance_by_position)
    } else NULL,
    # 机器人一致性分析
    robot_consistency_analysis = if(exists("robot_consistency_analysis") && length(robot_consistency_analysis) > 0) {
      robot_consistency_analysis
    } else NULL,
    # ANOVA分析结果
    anova_results = if(exists("anova_results") && length(anova_results) > 0) {
      anova_results
    } else NULL
  ),
  
  # 总结信息
  summary = list(
    total_records = nrow(data_with_target),
    success_rate = round(mean(data_with_target$within_tolerance) * 100, 2),
    mean_force = round(mean(data_with_target$force), 2),
    std_force = round(sd(data_with_target$force), 2),
    cv_percent = round(sd(data_with_target$force) / mean(data_with_target$force) * 100, 2),
    analysis_complete = TRUE,
    # 新增分析模块状态
    spatial_analysis_enabled = exists("spatial_correlation"),
    error_distribution_analysis_enabled = exists("normality_tests"),
    multi_source_analysis_enabled = exists("performance_by_position"),
    test_positions = if(exists("performance_by_position") && nrow(performance_by_position) > 0) {
      length(unique(performance_by_position$position_group))
    } else 0
  )
)

# 保存为JSON格式供Python读取
write_json(analysis_results, file.path(output_dir, "analysis_results.json"), auto_unbox = TRUE)

# 生成文本报告
# 设置时区为上海时区
Sys.setenv(TZ = "Asia/Shanghai")
report_text <- paste0(
  "压力采集数据分析报告\n",
  "==================\n",
  "分析时间: ", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"), "\n",
  "数据文件: ", data_file, "\n",
  "数据点数量: ", nrow(data_with_target), "\n\n",
  
  "数据概览:\n",
  "- 力值范围: ", round(min(data_with_target$force), 2), " - ", round(max(data_with_target$force), 2), " N\n",
  "- 平均力值: ", round(mean(data_with_target$force), 2), " N\n",
  "- 标准差: ", round(sd(data_with_target$force), 2), " N\n",
  "- 变异系数: ", round(sd(data_with_target$force)/mean(data_with_target$force)*100, 2), " %\n\n",
  
  "目标力值分析:\n"
)

for(i in 1:nrow(target_analysis)) {
  row <- target_analysis[i, ]
  report_text <- paste0(report_text,
    "- 目标 ", row$target_force, " N: 数据点 ", row$数据点数, " 个, 综合成功率 ", row$成功率_综合, " %\n"
  )
}

# 保存文本报告
writeLines(report_text, file.path(output_dir, "analysis_report.txt"))

print("=== 完整分析完成 ===")
print(paste("总数据点:", nrow(data_with_target)))
print(paste("整体成功率:", round(mean(data_with_target$within_tolerance) * 100, 2), "%"))
print(paste("输出文件保存至:", output_dir))

# 返回成功标志
cat("ANALYSIS_COMPLETE\n") 