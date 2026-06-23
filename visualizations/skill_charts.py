from visualizations.charts import horizontal_bar, heatmap_chart, bar_chart
from analysis.skill_analysis import top_skills, skill_cooccurrence_matrix, skill_salary_premium

def top_skills_bar(df, top_n=15):
    return horizontal_bar(top_skills(df,top_n), x="Count", y="Skill", title=f"Top {top_n} In-Demand Skills")

def skill_cooccurrence_heatmap(df, top_n=10):
    skills, matrix = skill_cooccurrence_matrix(df, top_n)
    return heatmap_chart(matrix, skills, skills, title="Skill Co-occurrence Heatmap")

def skill_premium_bar(df, top_n=10):
    data = skill_salary_premium(df, top_n)
    if data.empty: return None
    return bar_chart(data, x="Skill", y="Premium_%", title="Salary Premium by Skill (% vs market avg)")
