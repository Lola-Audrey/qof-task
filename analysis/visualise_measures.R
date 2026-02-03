library(tidyverse)
library(here)
library(scales)
library(patchwork)

dm_measure_prevalence <- read_csv(
    here("output", "dm017", "dm017_register_prevalence.csv")
)
dm_measure_age_group <- read_csv(
    here("output", "dm017", "dm017_register_composition_by_age.csv")
)
dm_measure_sex <- read_csv(
    here("output", "dm017", "dm017_register_composition_by_sex.csv")
)

prevalence_plot <- ggplot(dm_measure_prevalence, aes(x = interval_start, y = ratio)) +
    geom_line() +
    geom_point() +
    scale_x_date(
        date_breaks = "1 months",
        labels = label_date_short()
    ) +
    scale_y_continuous(
        labels = percent_format(accuracy = 1),
        limits = c(0, 1)
    ) +
    labs(
        x = " ",
        y = "Prevalence",
        title = "Diabetes Mellitus Register",
        subtitle = "(DM017, Total Population)"
    ) +
    theme_light()



age_plot <-  ggplot(dm_measure_age_group, aes(x = interval_start, y = numerator, color = age_band)) +
    geom_line() +
    geom_point() +
    scale_x_date(
        date_breaks = "1 month",
        labels = label_date_short()
    ) +
    scale_y_continuous(
        limits = c(10, 220)
    ) +
    labs(
        x = " ",
        y = "Count",
        title = "Diabetes Mellitus Register by Age",
        subtitle = "(DM017)"
    ) +
    theme_light()



sex_plot <-  ggplot(dm_measure_sex, aes(x = interval_start, y = numerator, color = sex)) +
    geom_line() +
    geom_point() +
    scale_x_date(
        date_breaks = "1 month",
        labels = label_date_short()
    ) +
    scale_y_continuous(
        limits = c(10, 220)
    ) +
    labs(
        x = " ",
        y = "Count",
        title = "Diabetes Mellitus Register by Sex",
        subtitle = "(DM017)"
    ) +
    theme_light()

measures_plot <- (prevalence_plot/ age_plot /sex_plot) + 
    plot_annotation(tag_levels = 'A')

ggsave(filename = here("output", "figures", "measures_plot.png"), 
    plot = measures_plot, 
    width = 12, 
    height = 5)