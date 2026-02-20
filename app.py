import streamlit as st
import plotly.express as px
import pandas as pd
from data_loader import get_my_team_data, get_free_agents

# Page Config
st.set_page_config(page_title="Punt Strategy Dashboard", page_icon="🏀", layout="wide")

st.title("🏀 NBA Fantasy Strategic Dashboard")
st.markdown("Optimization for **Punt Blocks & Turnovers** Strategy")

# Global Data Loading
with st.spinner("Fetching live data from ESPN..."):
    df_team = get_my_team_data()
    df_fa = get_free_agents(size=100)

# Config for left alignment
cat_cols = ["PTS", "REB", "AST", "STL", "BLK", "TO", "3PM", "FG%", "FT%"]
left_align_config = {col: st.column_config.TextColumn(col) for col in cat_cols}

tab1, tab2, tab3 = st.tabs(["📋 My Team", "🚀 Waiver Wire Radar", "💡 Smart AI & Comparison"])

with tab1:
    st.header("My Roster Overview")
    if not df_team.empty:
        st.dataframe(df_team, column_config=left_align_config, use_container_width=True, hide_index=True)
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Points Distribution")
            st.bar_chart(df_team.sort_values("PTS", ascending=False), x="Name", y="PTS", color="#f54242")
        with c2:
            st.write("### Roster Composition")
            fig_pie = px.pie(df_team, names='Pos', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.error("Team data not found.")

with tab2:
    st.header("Waiver Wire Radar")
    if not df_fa.empty:
        st.dataframe(df_fa.sort_values("PTS", ascending=False), column_config=left_align_config, use_container_width=True, hide_index=True)
        st.divider()
        st.write("### 📈 Strategic Mapping: Points vs Assists")
        fig_scatter = px.scatter(df_fa, x="AST", y="PTS", text="Name", size="REB", color="Pos", title="Waiver Wire Mapping")
        fig_scatter.update_traces(textposition='top center')
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.header("💡 Strategic Decisions")
    mode = st.radio("Choose Mode:", ["Automatic Recommendation", "Manual Comparison"])
    relevant_cats = ["PTS", "REB", "AST", "STL", "3PM", "FG%", "FT%"]

    if mode == "Automatic Recommendation":
        st.subheader("System Pick for Your Strategy")
        df_team['Score'] = df_team[relevant_cats].sum(axis=1)
        df_fa['Score'] = df_fa[relevant_cats].sum(axis=1)
        weakest = df_team.sort_values("Score").iloc[0]
        best_add = df_fa.sort_values("Score", ascending=False).iloc[0]
        
        p1, p2 = weakest, best_add
        st.info(f"Recommended: Drop **{p1['Name']}** ➡️ Add **{p2['Name']}**")
    
    else:
        st.subheader("Head-to-Head Manual Comparison")
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            name1 = st.selectbox("Drop (My Team):", df_team['Name'].tolist())
            p1 = df_team[df_team['Name'] == name1].iloc[0]
        with col_sel2:
            name2 = st.selectbox("Add (Free Agent):", df_fa['Name'].tolist())
            p2 = df_fa[df_fa['Name'] == name2].iloc[0]

    # Comparison Table Logic (Shared for both modes)
    comp_data = []
    up_count = 0
    for cat in relevant_cats:
        diff = round(p2[cat] - p1[cat], 2)
        if diff > 0: up_count += 1
        comp_data.append({"Category": cat, p1['Name']: str(p1[cat]), p2['Name']: str(p2[cat]), "Delta": str(diff)})
    
    comp_df = pd.DataFrame(comp_data)
    comp_config = {p1['Name']: st.column_config.TextColumn(p1['Name']), p2['Name']: st.column_config.TextColumn(p2['Name']), "Delta": st.column_config.TextColumn("Delta")}
    st.dataframe(comp_df, column_config=comp_config, use_container_width=True, hide_index=True)
    st.success(f"This move improves **{up_count} out of 7** core categories.")