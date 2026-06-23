from visualizations.charts import bar_chart, horizontal_bar
from analysis.experience_analysis import salary_by_bracket
from analysis.market_trends import most_versatile_skills, steepest_experience_curves, emerging_skill_combo
from utils.constants import COL_EXP_BRACKET

def salary_by_bracket_bar(df):
    data = salary_by_bracket(df).dropna(subset=["avg_salary"])
    return bar_chart(data, x=COL_EXP_BRACKET, y="avg_salary", title="Average Salary by Experience Bracket")

def versatile_skills_bar(df, top_n=10):
    return horizontal_bar(most_versatile_skills(df, top_n), x="Roles_Covered", y="Skill", title="Most Versatile Skills")

def experience_curve_bar(df, top_n=5):
    data = steepest_experience_curves(df, top_n)
    return horizontal_bar(data, x="Growth_%", y="Job_Title", title="Steepest Pay Growth by Role") if not data.empty else None

def skill_combo_bar(df, top_n=8):
    data = emerging_skill_combo(df, top_n)
    return horizontal_bar(data, x="Count", y="Pair", title="Most Common Skill Pairings") if not data.empty else None
