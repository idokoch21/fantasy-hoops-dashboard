import streamlit as st
import plotly.express as px
import pandas as pd
from data_loader import get_full_data

# הגדרות דף
st.set_page_config(page_title="Punt Strategy Dashboard", page_icon="🏀", layout="wide")

st.title("🏀 NBA Fantasy Strategic Dashboard")
st.markdown("Optimization for **Punt Blocks & Turnovers** Strategy")

# טעינת נתונים עם Caching למניעת ריענון מיותר
df_team, df_fa = get_full_data()

# הגדרת עיצוב עמודות (תמונות ויישור לשמאל)
cat_cols = ["PTS", "REB", "AST", "STL", "BLK", "TO", "3PM", "FG%", "FT%"]
table_config = {col: st.column_config.TextColumn(col) for col in cat_cols}
table_config["Img"] = st.column_config.ImageColumn("Photo")

tab1, tab2, tab3 = st.tabs(["📋 My Team", "🚀 Waiver Wire Radar", "💡 Smart AI & Comparison"])

with tab1:
    st.header("My Roster Overview")
    if not df_team.empty:
        st.dataframe(df_team, column_config=table_config, use_container_width=True, hide_index=True)
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Points Distribution")
            st.bar_chart(df_team.sort_values("PTS", ascending=False), x="Name", y="PTS", color="#f54242")
        with c2:
            st.write("### Roster Composition")
            fig_pie = px.pie(df_team, names='Pos', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.header("Waiver Wire Radar")
    if not df_fa.empty:
        st.dataframe(df_fa.sort_values("PTS", ascending=False), column_config=table_config, use_container_width=True, hide_index=True)
        st.divider()
        st.write("### 📈 Strategic Photo Mapping: Points vs Assists")
        
        # יצירת גרף ממופה עם תמונות (25 הראשונים)
        top_fa = df_fa.head(25)
        fig_scatter = px.scatter(top_fa, x="AST", y="PTS", text="Name", title="Top Waiver Wire Targets")
        
        # --- התיקון כאן ---
        for i, row in top_fa.iterrows():
            fig_scatter.add_layout_image(
                dict(
                    source=row["Img"],
                    xref="x", yref="y",
                    x=row["AST"], y=row["PTS"],
                    sizex=40, sizey=40, # גודל קבוע בפיקסלים
                    xanchor="center", yanchor="middle",
                    sizing="contain", 
                    opacity=0.9,
                    layer="above"
                )
            )
        
        # הסתרת הנקודות המקוריות ועדכון הצירים כדי שיתאימו לתמונות
        fig_scatter.update_traces(marker=dict(size=0), textposition='top center', textfont=dict(size=10))
        fig_scatter.update_xaxes(showgrid=False, zeroline=False)
        fig_scatter.update_yaxes(showgrid=False, zeroline=False)
        fig_scatter.update_layout(height=600, template="plotly_white")
        # -------------------

        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.header("💡 Strategic Head-to-Head")
    mode = st.radio("Mode:", ["Automatic Recommendation", "Manual Comparison"], horizontal=True)
    
    relevant_cats = ["PTS", "REB", "AST", "STL", "3PM", "FG%", "FT%"]

    if mode == "Automatic Recommendation":
        df_team['Score'] = df_team[relevant_cats].sum(axis=1)
        df_fa['Score'] = df_fa[relevant_cats].sum(axis=1)
        p1 = df_team.sort_values("Score").iloc[0]
        p2 = df_fa.sort_values("Score", ascending=False).iloc[0]
    else:
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            name1 = st.selectbox("Drop Player (My Team):", df_team['Name'].tolist())
            p1 = df_team[df_team['Name'] == name1].iloc[0]
        with col_sel2:
            name2 = st.selectbox("Add Player (Waiver Wire):", df_fa['Name'].tolist())
            p2 = df_fa[df_fa['Name'] == name2].iloc[0]

    st.divider()
    img_c1, img_c2, img_c3 = st.columns([1, 0.5, 1])
    with img_c1:
        st.image(p1['Img'], width=150)
        st.subheader(f"DROP: {p1['Name']}")
        st.caption(f"Current Value Score: {round(p1[relevant_cats].sum(), 1)}")
    with img_c2:
        st.markdown("<h1 style='text-align: center; padding-top: 40px;'>VS</h1>", unsafe_allow_html=True)
    with img_c3:
        st.image(p2['Img'], width=150)
        st.subheader(f"ADD: {p2['Name']}")
        st.caption(f"Potential Value Score: {round(p2[relevant_cats].sum(), 1)}")

    comp_list = []
    up_count = 0
    for cat in relevant_cats:
        v1 = p1[cat]
        v2 = p2[cat]
        diff = round(v2 - v1, 2)
        
        if diff > 0:
            status = "✅ Upgrade"
            up_count += 1
        elif diff < 0:
            status = "❌ Downgrade"
        else:
            status = "➖ Even"
            
        comp_list.append({
            "Category": cat,
            f"{p1['Name']}": str(v1),
            f"{p2['Name']}": str(v2),
            "Delta": str(diff),
            "Comparison": status
        })
    
    comp_df = pd.DataFrame(comp_list)
    
    h2h_config = {
        f"{p1['Name']}": st.column_config.TextColumn(p1['Name']),
        f"{p2['Name']}": st.column_config.TextColumn(p2['Name']),
        "Delta": st.column_config.TextColumn("Delta"),
        "Comparison": st.column_config.TextColumn("Status")
    }
    
    st.dataframe(comp_df, column_config=h2h_config, use_container_width=True, hide_index=True)
    
    if up_count >= 4:
        st.success(f"🔥 Strategic Verdict: This move improves your team in **{up_count} out of 7** core categories!")
    else:
        st.warning(f"⚠️ Caution: This move only improves **{up_count} out of 7** categories.")