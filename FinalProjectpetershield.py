"""
Class: CS230-5
Name: Peter Shield
Description: Final Project- Displaying data from the volcanoes csv file
"""

import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import pandas as pd
import random

st.set_page_config(initial_sidebar_state="collapsed")
VOLCANO_FILE = "volcanoes.csv"
df_volcano = pd.read_csv(VOLCANO_FILE)

# needed to clean up hanging (es) and (s) to compile data
for i in df_volcano['Primary Volcano Type']:
    if i[-4:] == "(es)":
        df_volcano['Primary Volcano Type'] = df_volcano['Primary Volcano Type'].replace(i, i[:-4])
    elif i[-3:] == "(s)":
        df_volcano['Primary Volcano Type'] = df_volcano['Primary Volcano Type'].replace(i, i[:-3])
    else:
        df_volcano['Primary Volcano Type'] = df_volcano['Primary Volcano Type'].replace(i, i.strip("?"))
# needed to format these columns in order for all of the words in the multi-word values to be title case
cols_with_probs = ["Country", "Primary Volcano Type", "Activity Evidence", "Region", "Subregion", "Dominant Rock Type"]
for col in cols_with_probs:
    df_volcano[col] = df_volcano[col].str.title()
df_volcano.rename(columns={"Latitude": 'lat', "Longitude": 'lon'}, inplace=True)
df_volcano = df_volcano.dropna()

st.title("Final Project")

st.sidebar.title("Data Selector")


# returns a dictionary with the unique values as keys and the frequency as values
def dict_count_items(sdf):
    unique_list = []
    for dat in sdf.str.lower().tolist():
        if dat.lower() not in unique_list:
            unique_list.append(dat.lower())
    res_dct = {j.title(): sdf.str.lower().tolist().count(j) for j in unique_list}
    return res_dct


# Creates a list of layers for st.pydeck_chart for each element from dataframes filtered by column or selected element
def create_layers(list_of_df, colors):
    return [pdk.Layer(type='ScatterplotLayer',
                           data=list_of_df[i],
                           get_position='[lon, lat]',
                           radius_scale=6,
                           radius_min_pixels=7,
                           radius_max_pixels=7,
                           pickable=True,
                           filled=True,
                           opacity=0.8,
                           get_fill_color=[255*j for j in colors[i]])
            for i in range(len(list_of_df))]


# Returns a list of dataframes split up by unique element in a given column- to be used in create_layers()
def filter_by_column(df, column_name):
    return [df.loc[(df == i).any(axis=1)] for i in dict_count_items(df[column_name]).keys()]


# Returns a list of top n most frequent items in a dictionary
def top_n_ele(d, n=10):
    out = list(dict(sorted(d.items(), key=lambda item: item[1])).items())[-n:]
    return out


# Returns a list of dataframes split up by selected unique elements in a given column- to be used in create_layers()
def filter_by_ele(df, ele_list):
    return [df.loc[(df == i).any(axis=1)] for i in ele_list]

def main():
    selected_column = st.sidebar.selectbox("Please select the column you want to show data and map for:",
                                           ["", "Country", "Primary Volcano Type", "Activity Evidence",
                                            "Region", "Subregion", "Dominant Rock Type"])

    if selected_column == "":
        st.write("Please select data to view in the sidebar")
    else:
        st.header("Charts")
        stmap = True
        selected_data_view = st.sidebar.selectbox("How would you like to view?",
                                                  ["All Data", "10 Most Frequent", "Select Data Point"])
        if selected_data_view == "Select Data Point":
            stmap = False
            selected_data_points = st.sidebar.multiselect("Which data points would you like to display",
                                                          sorted(dict_count_items(df_volcano[selected_column]).keys()))
            if len(selected_data_points) == 0:
                st.sidebar.warning("Please select at least one data point")
            dict_selected_points = {i: dict_count_items(df_volcano[selected_column])[i] for i in selected_data_points}
            data_point_bool = st.sidebar.radio("Show graph and map with only selected data points?", ["No", "Yes"])

        selected_chart = st.sidebar.radio("Please select the chart you want to show",
                                          ["No Chart", "Bar Chart", "Pie Chart"])
        c = [[random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)] for i
             in dict_count_items(df_volcano[selected_column]).keys()]
        if selected_chart == "Bar Chart":
            if selected_data_view == "10 Most Frequent":
                if len(filter_by_column(df_volcano, selected_column)) >= 10:
                    fig, ax = plt.subplots()
                    ax.bar([i[0] for i in top_n_ele(dict_count_items(df_volcano[selected_column]))],
                           [i[1] for i in top_n_ele(dict_count_items(df_volcano[selected_column]))], color=c)
                    plt.xticks(rotation=30, ha='right')
                    plt.ylabel("Frequency")
                    st.pyplot(fig)
                else:
                    stmap = False
                    st.warning("Unable to show chart; The column you selected has fewer than 10 unique values")
            elif selected_data_view == "Select Data Point" and data_point_bool == "Yes":
                if len(dict_selected_points) == 0:
                    st.warning("Please select at least one data point to display the chart")
                else:
                    fig, ax = plt.subplots()
                    ax.bar(dict_selected_points.keys(),
                           dict_selected_points.values(), color=c)
                    plt.xticks(rotation=30, ha='right')
                    plt.ylabel("Frequency")
                    st.pyplot(fig)
            else:
                fig, ax = plt.subplots()
                ax.bar(dict_count_items(df_volcano[selected_column]).keys(),
                       dict_count_items(df_volcano[selected_column]).values(), color=c)
                plt.xticks(rotation=30, ha='right')
                plt.ylabel("Frequency")
                st.pyplot(fig)
                if len(dict_count_items(df_volcano[selected_column]).keys()) > 20:
                    st.warning("Caution! There many be too many datapoints in the chart. Select the '10 Most Frequent' \
                    view or try selecting fewer data points for better results.")
        elif selected_chart == "Pie Chart":
            if selected_data_view == "10 Most Frequent":
                if len(filter_by_column(df_volcano, selected_column)) >= 10:
                    fig, ax = plt.subplots()
                    ax.pie([i[1] for i in top_n_ele(dict_count_items(df_volcano[selected_column]))],
                           labels=[i[0] for i in top_n_ele(dict_count_items(df_volcano[selected_column]))],
                           autopct="%.1f%%", colors=c)
                    # ax.legend(loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
                    st.pyplot(fig)
                else:
                    stmap = False
                    st.warning("Unable to show chart; The column you selected has fewer than 10 unique values")
            elif selected_data_view == "Select Data Point" and data_point_bool == "Yes":
                if len(dict_selected_points) == 0:
                    st.warning("Please select at least one data point to display the chart")
                elif sum(dict_selected_points.values()) == 0:
                    st.warning("Warning! The data points you have selected all have a value of 0")
                else:
                    fig, ax = plt.subplots()
                    ax.pie(dict_selected_points.values(),
                           labels=dict_selected_points.keys(),
                           autopct="%.1f%%", colors=c)
                    st.pyplot(fig)
            else:
                fig, ax = plt.subplots()
                ax.pie(dict_count_items(df_volcano[selected_column]).values(),
                       labels=dict_count_items(df_volcano[selected_column]).keys(), autopct="%.1f%%", colors=c)
                st.pyplot(fig)
                if len(dict_count_items(df_volcano[selected_column]).keys()) > 20:
                    st.warning("Caution! There many be too many datapoints in the chart. Select the '10 Most Frequent' \
                    view or try selecting fewer data points for better results.")
        elif selected_chart == "No Chart":
            st.write("No chart is currently being displayed")
        if selected_data_view == "Select Data Point":
            if len(dict_selected_points.keys()) > 20:
                st.warning("Caution! There many be too many datapoints in the chart. Select the '10 Most Frequent' \
                view or try selecting fewer data points for better results.")
            st.write("Totals for above")
            for i in dict_selected_points.keys():
                st.caption(f"{i}: {dict_selected_points[i]}")

        selected_map = st.sidebar.radio("Please select the map", ["No Map", "Simple", "Info", "Selected Data"])

        if selected_map == "Simple":
            st.title('Simple Map')
            st.map(df_volcano)
        elif selected_map == "Info":

            st.title("Informational")

            # Create custom icons
            ICON_URL = "https://cdn4.iconfinder.com/data/icons/nature-life-in-color/128/volcano-eruption-color-512.png"

            # Format your icon
            icon_data = {
                "url": ICON_URL,
                "width": 75,
                "height": 75,
                "anchorY": 0
            }

            # Add icons to your dataframe
            df_volcano["icon_data"] = None
            for i in df_volcano.index:
                df_volcano["icon_data"][i] = icon_data

            # Create a layer with your custom icon
            icon_layer = pdk.Layer(type="IconLayer",
                                   data=df_volcano,
                                   get_icon="icon_data",
                                   get_position='[lon,lat]',
                                   get_size=4,
                                   size_scale=10,
                                   pickable=True)

            # Create a view of the map: https://pydeck.gl/view.html
            view_state = pdk.ViewState(
                latitude=df_volcano["lat"].mean(),
                longitude=df_volcano["lon"].mean(),
                zoom=1,
                pitch=0
            )

            # stylish tool tip: https://pydeck.gl/tooltip.html?highlight=tooltip
            tool_tip = {
                "html": "Name: <b>{Volcano Name}</b><br>Location: <b>{Country}</b><br>Elevation (m): <b>{Elevation (m)}</b>",
                "style": {"backgroundColor": "blue",
                          "color": "white"}
                }

            icon_map = pdk.Deck(
                map_style='mapbox://styles/mapbox/navigation-day-v1',
                layers=[icon_layer],
                initial_view_state=view_state,
                tooltip=tool_tip)

            st.pydeck_chart(icon_map)
        elif selected_map == "Selected Data":

            st.header("Selected Data")

            # Create a layer with your custom icon
            if selected_data_view == "All Data":
                layer1 = create_layers(filter_by_column(df_volcano, selected_column), c)
            elif selected_data_view == "10 Most Frequent":
                if len(filter_by_column(df_volcano, selected_column)) >= 10:
                    layer1 = create_layers(filter_by_ele(df_volcano, [i[0] for i in top_n_ele(dict_count_items(df_volcano[selected_column]))]), c)
                else:
                    stmap = False
                    st.warning("The column you selected has fewer than 10 unique values")
            elif selected_data_view == "Select Data Point":
                stmap = True
                if data_point_bool == "Yes":
                    layer1 = create_layers(filter_by_ele(df_volcano, dict_selected_points.keys()), c)
                else:
                    layer1 = create_layers(filter_by_column(df_volcano, selected_column), c)
            else:
                layer1 = pdk.Layer(type='ScatterplotLayer',
                                   data=df_volcano,
                                   get_position='[lon, lat]',
                                   radius_scale=6,
                                   radius_min_pixels=7,
                                   radius_max_pixels=7,
                                   pickable=True,
                                   filled=True,
                                   opacity=0.8,
                                   get_fill_color=[0,0,255])
            # Create a view of the map
            view_state = pdk.ViewState(
                latitude=df_volcano["lat"].mean(),
                longitude=df_volcano["lon"].mean(),
                zoom=1,
                pitch=0
            )
            if stmap:
                # stylish tool tip
                html = ("Name: <b>{Volcano Name}</b><br>Location: <b>{Country}</b><br>Elevation (m): <b>{Elevation (m)}</b>"
                        + f"<br>{selected_column}: <b>"+"{"+f"{selected_column}"+"}</b>")
                tool_tip = {
                    "html": html,
                    "style": {"backgroundColor": "red",
                              "color": "white"}
                    }

                data_map = pdk.Deck(
                    map_style='mapbox://styles/mapbox/navigation-day-v1',
                    layers=[layer1],
                    initial_view_state=view_state,
                    tooltip=tool_tip)

                st.pydeck_chart(data_map)
    st.header("Volcano Comparison")
    search = [st.text_input("Please enter a name to search by:").title()]
    st.write("To view entire dataframe, enter nothing above.")
    st.dataframe(df_volcano[df_volcano['Volcano Name'].str.findall('^(?:'+'|'.join(search) + ')').apply(len) > 0])
    selected_volcano = st.multiselect("Please choose 2 Volcanoes to compare", sorted(dict_count_items(df_volcano["Volcano Name"]).keys()))
    show_res = st.button("Show comparison", disabled=False)

    if show_res:
        if len(selected_volcano) == 2:
            frame1 = df_volcano[df_volcano['Volcano Name'].str.endswith(tuple([selected_volcano[0]]))]
            frame2 = df_volcano[df_volcano['Volcano Name'].str.endswith(tuple([selected_volcano[1]]))]
            st.dataframe(pd.concat([frame1, frame2]))
        else:
            st.warning("You have to select exactly 2 volcanoes")

    show_comp_map = st.radio("Show map of two volcanoes?", ["No", "Yes"])
    if show_comp_map == "Yes":
        if len(selected_volcano) == 2:
            df1 = pd.concat([df_volcano[df_volcano['Volcano Name'].str.endswith(tuple([selected_volcano[0]]))],
                             df_volcano[df_volcano['Volcano Name'].str.endswith(tuple([selected_volcano[1]]))]])
            # Create a layer with your custom icon
            comp_layer = pdk.Layer(type='ScatterplotLayer',
                                   data=df1,
                                   get_position='[lon, lat]',
                                   radius_scale=6,
                                   radius_min_pixels=7,
                                   radius_max_pixels=7,
                                   pickable=True,
                                   filled=True,
                                   opacity=0.8,
                                   get_fill_color=[255, 165, 0])

            # Create a view of the map: https://pydeck.gl/view.html
            view_state = pdk.ViewState(
                latitude=df1["lat"].mean(),
                longitude=df1["lon"].mean(),
                zoom=1,
                pitch=0
            )
            # stylish tool tip: https://pydeck.gl/tooltip.html?highlight=tooltip
            tool_tip = {
                "html": "Name: <b>{Volcano Name}</b><br>Location: <b>{Country}</b><br>Elevation (m): <b>{Elevation (m)}</b>",
                "style": {"backgroundColor": "purple",
                          "color": "white"}
            }
            data_map = pdk.Deck(
                map_style='mapbox://styles/mapbox/navigation-day-v1',
                layers=[comp_layer],
                initial_view_state=view_state,
                tooltip=tool_tip)

            st.pydeck_chart(data_map)

            fig, ax = plt.subplots()

            comp_colors = ["", ""]
            for i in df1["Elevation (m)"]:
                st.write()
                if i < 0:
                    comp_colors[df1["Elevation (m)"].tolist().index(i)] = "blue"
                else:
                    comp_colors[df1["Elevation (m)"].tolist().index(i)] = "red"
            ax.bar(df1["Volcano Name"],
                   df1["Elevation (m)"], color=comp_colors)
            plt.ylabel("Elevation (m)")
            st.pyplot(fig)
        else:
            st.warning("You have to select exactly 2 volcanoes")

    st.markdown("***"
                "***")

    balloons = st.button("Celebrate!", disabled=False)
    if balloons:
        st.balloons()


if __name__ == "__main__":
    main()
